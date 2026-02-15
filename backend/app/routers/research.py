"""API endpoints for research ethics and consent management."""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .. import models_research, schemas_research, models
from ..database import get_db
from ..crypto_utils import (
    generate_consent_record,
    verify_withdrawal_code,
    hash_ip_address
)

router = APIRouter(prefix="/api/v1/research", tags=["research"])


@router.post("/consent", response_model=schemas_research.ConsentResponse)
async def create_consent(
    consent_data: schemas_research.ConsentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create a research consent record with cryptographic withdrawal code.

    This endpoint:
    1. Generates a unique withdrawal code and participant ID
    2. Stores only the hash of the withdrawal code (not the plaintext)
    3. Returns the withdrawal code to the participant (ONLY TIME IT'S VISIBLE)
    4. Researcher never sees the withdrawal code

    The withdrawal code enables GDPR Article 17 "Right to Erasure" without
    compromising participant anonymity.
    """
    # Validate privacy level
    if consent_data.privacy_level not in ['anonymous', 'pseudonymous', 'identifiable']:
        raise HTTPException(
            status_code=400,
            detail="privacy_level must be 'anonymous', 'pseudonymous', or 'identifiable'"
        )

    # Generate cryptographic components
    withdrawal_code, participant_id, salt, code_hash = generate_consent_record()

    # Extract participant info (minimal aggregate data only)
    participant_info = consent_data.participant_info or {}

    # Create consent record
    db_consent = models_research.ResearchConsent(
        study_id=consent_data.study_id,
        participant_id=participant_id,
        withdrawal_code_hash=code_hash,
        withdrawal_salt=salt,
        privacy_level=consent_data.privacy_level,
        age_range=participant_info.get('age_range'),
        condition=participant_info.get('condition'),
        recruitment_site=participant_info.get('recruitment_site'),
        irb_protocol=consent_data.irb_protocol,
        consent_version=consent_data.consent_version
    )

    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)

    # Return consent with withdrawal code
    # WARNING: This is the ONLY time the withdrawal code is ever visible
    return schemas_research.ConsentResponse(
        participant_id=participant_id,
        withdrawal_code=withdrawal_code,  # Give to participant, never store plaintext
        consent_id=db_consent.id,
        study_id=db_consent.study_id,
        privacy_level=db_consent.privacy_level,
        consented_at=db_consent.consented_at
    )


@router.post("/withdraw", response_model=schemas_research.WithdrawalResponse)
async def withdraw_participation(
    withdrawal_request: schemas_research.WithdrawalRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Withdraw participation and permanently delete all associated data.

    This endpoint:
    1. Verifies the withdrawal code via cryptographic hash
    2. Identifies the participant_id without revealing identity to researcher
    3. Deletes ALL data associated with that participant
    4. Logs the withdrawal for IRB compliance
    5. Returns success/failure WITHOUT revealing participant identity

    Supports GDPR Article 17, NZ Privacy Act 2020, and research ethics requirements.
    """
    # Get client IP for abuse detection (hashed)
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hash_ip_address(client_ip)

    # Try to find matching consent by verifying hash
    consents = db.query(models_research.ResearchConsent).filter(
        models_research.ResearchConsent.is_active == True
    ).all()

    matching_consent = None
    for consent in consents:
        if verify_withdrawal_code(
            withdrawal_request.withdrawal_code,
            consent.withdrawal_salt,
            consent.withdrawal_code_hash
        ):
            matching_consent = consent
            break

    if not matching_consent:
        # Invalid code - log the attempt for abuse detection
        audit = models_research.WithdrawalAudit(
            withdrawal_code_hash="invalid",
            success=False,
            error_message="Invalid withdrawal code",
            request_ip_hash=ip_hash,
            completed_at=datetime.utcnow()
        )
        db.add(audit)
        db.commit()

        # Don't reveal whether code exists or not (prevent enumeration)
        raise HTTPException(
            status_code=400,
            detail="Invalid withdrawal code. Please check your code and try again."
        )

    # Found valid consent - proceed with data deletion
    participant_id = matching_consent.participant_id

    # Count data to be deleted (for audit)
    metric_sessions = db.query(models.MetricSession).join(
        models_research.ResearchConsent,
        models.MetricSession.unique_id == models_research.ResearchConsent.participant_id
    ).filter(
        models_research.ResearchConsent.id == matching_consent.id
    ).all()

    sessions_count = len(metric_sessions)
    events_count = 0

    # Delete all data (CASCADE DELETE)
    for session in metric_sessions:
        play_sessions = db.query(models.PlaySession).filter(
            models.PlaySession.metric_session_id == session.id
        ).all()

        for play_session in play_sessions:
            event_count = db.query(models.Event).filter(
                models.Event.play_session_id == play_session.id
            ).count()
            events_count += event_count

            # Delete events
            db.query(models.Event).filter(
                models.Event.play_session_id == play_session.id
            ).delete()

        # Delete play sessions
        db.query(models.PlaySession).filter(
            models.PlaySession.metric_session_id == session.id
        ).delete()

        # Delete metric session
        db.delete(session)

    # Mark consent as withdrawn
    matching_consent.is_active = False
    matching_consent.withdrawn_at = datetime.utcnow()
    matching_consent.data_deleted_at = datetime.utcnow()

    # Create audit record
    audit = models_research.WithdrawalAudit(
        consent_id=matching_consent.id,
        withdrawal_code_hash=matching_consent.withdrawal_code_hash,
        participant_id=participant_id,
        events_deleted=events_count,
        sessions_deleted=sessions_count,
        success=True,
        request_ip_hash=ip_hash,
        completed_at=datetime.utcnow()
    )
    db.add(audit)

    # Commit all changes
    db.commit()

    return schemas_research.WithdrawalResponse(
        success=True,
        message="Your participation has been withdrawn. All associated data has been permanently deleted.",
        deleted_at=matching_consent.data_deleted_at,
        sessions_deleted=sessions_count,
        events_deleted=events_count
    )


@router.get("/study/{study_id}/stats", response_model=schemas_research.StudyStatsResponse)
async def get_study_stats(
    study_id: str,
    db: Session = Depends(get_db)
    # TODO: Add researcher authentication
):
    """
    Get aggregate statistics for a research study.

    Researchers can see:
    - Total number of participants consented
    - Number of active participants
    - Number of withdrawn participants
    - Privacy level
    - IRB protocol

    Researchers CANNOT see:
    - Individual participant IDs
    - Withdrawal codes
    - Personal identifiable information
    """
    # Count consents
    total_consented = db.query(models_research.ResearchConsent).filter(
        models_research.ResearchConsent.study_id == study_id
    ).count()

    active_participants = db.query(models_research.ResearchConsent).filter(
        models_research.ResearchConsent.study_id == study_id,
        models_research.ResearchConsent.is_active == True
    ).count()

    withdrawn_participants = db.query(models_research.ResearchConsent).filter(
        models_research.ResearchConsent.study_id == study_id,
        models_research.ResearchConsent.is_active == False
    ).count()

    # Get study metadata (if exists)
    study_meta = db.query(models_research.StudyMetadata).filter(
        models_research.StudyMetadata.study_id == study_id
    ).first()

    # Get common privacy level and IRB protocol from first consent
    first_consent = db.query(models_research.ResearchConsent).filter(
        models_research.ResearchConsent.study_id == study_id
    ).first()

    if not first_consent and not study_meta:
        raise HTTPException(status_code=404, detail="Study not found")

    return schemas_research.StudyStatsResponse(
        study_id=study_id,
        total_consented=total_consented,
        active_participants=active_participants,
        withdrawn_participants=withdrawn_participants,
        privacy_level=first_consent.privacy_level if first_consent else "unknown",
        irb_protocol=study_meta.irb_protocol if study_meta else (
            first_consent.irb_protocol if first_consent else None
        ),
        data_retention_days=study_meta.data_retention_days if study_meta else 365
    )


@router.get("/participant/data")
async def export_participant_data(
    withdrawal_code: str,
    db: Session = Depends(get_db)
):
    """
    Export all data for a participant (GDPR Article 15 - Right of Access).

    Participant provides their withdrawal code to:
    1. Prove ownership of the data
    2. Retrieve all their data for review
    3. Without revealing identity to researcher

    Returns JSON with all events, sessions, and metadata.
    """
    # Find matching consent
    consents = db.query(models_research.ResearchConsent).filter(
        models_research.ResearchConsent.is_active == True
    ).all()

    matching_consent = None
    for consent in consents:
        if verify_withdrawal_code(
            withdrawal_code,
            consent.withdrawal_salt,
            consent.withdrawal_code_hash
        ):
            matching_consent = consent
            break

    if not matching_consent:
        raise HTTPException(
            status_code=400,
            detail="Invalid withdrawal code"
        )

    # Retrieve all data for this participant
    metric_sessions = db.query(models.MetricSession).join(
        models_research.ResearchConsent,
        models.MetricSession.unique_id == models_research.ResearchConsent.participant_id
    ).filter(
        models_research.ResearchConsent.id == matching_consent.id
    ).all()

    sessions_data = []
    total_events = 0

    for session in metric_sessions:
        play_sessions = db.query(models.PlaySession).filter(
            models.PlaySession.metric_session_id == session.id
        ).all()

        play_sessions_data = []
        for play_session in play_sessions:
            events = db.query(models.Event).filter(
                models.Event.play_session_id == play_session.id
            ).all()

            total_events += len(events)

            events_data = [{
                "id": e.id,
                "event_type": e.event_type,
                "event_subtype": e.event_subtype,
                "x": e.x,
                "y": e.y,
                "z": e.z,
                "magnitude": e.magnitude,
                "data": e.data,
                "timestamp": e.timestamp.isoformat()
            } for e in events]

            play_sessions_data.append({
                "id": play_session.id,
                "started_at": play_session.started_at.isoformat(),
                "ended_at": play_session.ended_at.isoformat() if play_session.ended_at else None,
                "events": events_data
            })

        sessions_data.append({
            "id": session.id,
            "unique_id": session.unique_id,
            "build_number": session.build_number,
            "created_at": session.created_at.isoformat(),
            "closed_at": session.closed_at.isoformat() if session.closed_at else None,
            "play_sessions": play_sessions_data
        })

    return {
        "participant_id": matching_consent.participant_id,
        "study_id": matching_consent.study_id,
        "consented_at": matching_consent.consented_at.isoformat(),
        "privacy_level": matching_consent.privacy_level,
        "total_sessions": len(sessions_data),
        "total_events": total_events,
        "sessions": sessions_data
    }
