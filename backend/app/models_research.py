"""Research ethics and consent management models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class ResearchConsent(Base):
    """Research consent and withdrawal tracking."""
    __tablename__ = "research_consents"

    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(String(100), nullable=False, index=True)
    participant_id = Column(String(50), unique=True, nullable=False, index=True)

    # Cryptographic withdrawal system
    withdrawal_code_hash = Column(String(64), nullable=False, unique=True, index=True)
    withdrawal_salt = Column(String(32), nullable=False)

    # Privacy level: 'anonymous', 'pseudonymous', 'identifiable'
    privacy_level = Column(String(20), nullable=False, default='pseudonymous')

    # Minimal participant metadata (aggregate only, no PII)
    age_range = Column(String(20), nullable=True)  # e.g., "18-25"
    condition = Column(String(100), nullable=True)  # e.g., "ADHD", "control"
    recruitment_site = Column(String(100), nullable=True)  # e.g., "University A"

    # Audit trail
    consented_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    withdrawn_at = Column(DateTime, nullable=True)
    data_deleted_at = Column(DateTime, nullable=True)

    # IRB tracking
    irb_protocol = Column(String(100), nullable=True)
    consent_version = Column(String(20), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    withdrawals = relationship("WithdrawalAudit", back_populates="consent")


class WithdrawalAudit(Base):
    """Audit log for withdrawal requests (IRB compliance)."""
    __tablename__ = "withdrawal_audit"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key (nullable to support invalid withdrawal attempts)
    consent_id = Column(Integer, ForeignKey("research_consents.id"), nullable=True)

    # Audit data
    withdrawal_code_hash = Column(String(64), nullable=False)
    participant_id = Column(String(50), nullable=True)  # Null if code invalid
    events_deleted = Column(Integer, default=0)
    sessions_deleted = Column(Integer, default=0)

    # Timestamps
    requested_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Status
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)

    # IP address for abuse detection (hashed)
    request_ip_hash = Column(String(64), nullable=True)

    # Relationships
    consent = relationship("ResearchConsent", back_populates="withdrawals")


class StudyMetadata(Base):
    """Research study configuration and metadata."""
    __tablename__ = "study_metadata"

    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(String(100), unique=True, nullable=False, index=True)

    # Study information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    principal_investigator = Column(String(100), nullable=False)
    institution = Column(String(100), nullable=False)

    # IRB details
    irb_protocol = Column(String(100), nullable=False)
    irb_approval_date = Column(DateTime, nullable=True)
    irb_expiry_date = Column(DateTime, nullable=True)

    # Privacy settings
    default_privacy_level = Column(String(20), default='pseudonymous')
    data_retention_days = Column(Integer, default=365)  # Auto-delete after this period

    # Study status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Contact
    contact_email = Column(String(100), nullable=True)
    withdrawal_url = Column(String(200), nullable=True)
