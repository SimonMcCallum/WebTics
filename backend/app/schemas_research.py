"""Pydantic schemas for research ethics and consent management."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict


class ConsentCreate(BaseModel):
    """Schema for creating a research consent record."""
    study_id: str = Field(..., description="Research study identifier")
    privacy_level: str = Field(
        default="pseudonymous",
        description="Privacy level: anonymous, pseudonymous, or identifiable"
    )
    participant_info: Optional[Dict[str, str]] = Field(
        None,
        description="Minimal aggregate participant info (age_range, condition, etc.)"
    )
    irb_protocol: Optional[str] = Field(None, description="IRB protocol number")
    consent_version: Optional[str] = Field(None, description="Consent form version")


class ConsentResponse(BaseModel):
    """Schema for consent creation response."""
    participant_id: str = Field(..., description="Pseudonymous participant ID")
    withdrawal_code: str = Field(..., description="Unique withdrawal code (SAVE THIS)")
    consent_id: int
    study_id: str
    privacy_level: str
    consented_at: datetime

    important_notice: str = Field(
        default="SAVE THIS WITHDRAWAL CODE. You will need it to withdraw from the study. "
        "The researcher cannot retrieve it for you."
    )

    class Config:
        from_attributes = True


class WithdrawalRequest(BaseModel):
    """Schema for withdrawal request."""
    withdrawal_code: str = Field(..., description="Participant's withdrawal code")


class WithdrawalResponse(BaseModel):
    """Schema for withdrawal response."""
    success: bool
    message: str
    deleted_at: Optional[datetime]
    sessions_deleted: Optional[int]
    events_deleted: Optional[int]


class StudyStatsResponse(BaseModel):
    """Schema for study statistics (researcher view)."""
    study_id: str
    total_consented: int
    active_participants: int
    withdrawn_participants: int
    privacy_level: str
    irb_protocol: Optional[str]
    data_retention_days: int


class ParticipantDataExport(BaseModel):
    """Schema for participant data export (for participant's own access)."""
    participant_id: str
    study_id: str
    consented_at: datetime
    total_sessions: int
    total_events: int
    data: Dict  # Contains all events and sessions
