"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any


class EventCreate(BaseModel):
    """Schema for creating a new event."""
    event_type: int = Field(..., description="Event type identifier")
    event_subtype: int = Field(default=0, description="Event subtype identifier")
    x: Optional[int] = Field(None, description="X coordinate")
    y: Optional[int] = Field(None, description="Y coordinate")
    z: Optional[int] = Field(None, description="Z coordinate")
    magnitude: Optional[float] = Field(None, description="Event magnitude")
    data: Optional[dict[str, Any]] = Field(None, description="Additional event data")


class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    event_type: int
    event_subtype: int
    x: Optional[int]
    y: Optional[int]
    z: Optional[int]
    magnitude: Optional[float]
    data: Optional[dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


class PlaySessionCreate(BaseModel):
    """Schema for creating a play session."""
    metric_session_id: int


class PlaySessionResponse(BaseModel):
    """Schema for play session response."""
    id: int
    metric_session_id: int
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class MetricSessionCreate(BaseModel):
    """Schema for creating a metric session."""
    unique_id: str = Field(..., description="Unique identifier for this session")
    build_number: Optional[str] = Field(None, description="Game build/version number")


class MetricSessionResponse(BaseModel):
    """Schema for metric session response."""
    id: int
    unique_id: str
    build_number: Optional[str]
    created_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True
