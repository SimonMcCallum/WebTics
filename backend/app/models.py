"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class MetricSession(Base):
    """A metric session represents a single game session."""
    __tablename__ = "metric_sessions"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String, unique=True, index=True, nullable=False)
    build_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    play_sessions = relationship("PlaySession", back_populates="metric_session")


class PlaySession(Base):
    """A play session is a single gameplay attempt within a metric session."""
    __tablename__ = "play_sessions"

    id = Column(Integer, primary_key=True, index=True)
    metric_session_id = Column(Integer, ForeignKey("metric_sessions.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    metric_session = relationship("MetricSession", back_populates="play_sessions")
    events = relationship("Event", back_populates="play_session")


class Event(Base):
    """Individual telemetry events logged during gameplay."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    play_session_id = Column(Integer, ForeignKey("play_sessions.id"), nullable=False)

    # Event data (matching original WebTics schema)
    event_type = Column(Integer, nullable=False, index=True)
    event_subtype = Column(Integer, nullable=False)
    x = Column(Integer, nullable=True)
    y = Column(Integer, nullable=True)
    z = Column(Integer, nullable=True)
    magnitude = Column(Float, nullable=True)
    data = Column(JSON, nullable=True)  # Flexible JSON for custom data

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    play_session = relationship("PlaySession", back_populates="events")
