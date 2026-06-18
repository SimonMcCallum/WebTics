"""Pydantic schemas for auth, game registration, admin and the GA4 ingest layer."""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, Any, List


# --- Auth -------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ClaimRequest(BaseModel):
    """First-login claim: authenticate with the emailed temp password and set a new one."""
    email: EmailStr
    temp_password: str
    new_password: str = Field(min_length=8, max_length=128)
    display_name: Optional[str] = Field(None, max_length=200)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool = False
    expires_at: Optional[datetime] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    display_name: Optional[str]
    roster_name: Optional[str]
    role: str
    is_claimed: bool
    is_active: bool
    expires_at: Optional[datetime]
    course_id: Optional[int]

    class Config:
        from_attributes = True


# --- Games ------------------------------------------------------------------
class GameCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    platform: Optional[str] = Field(None, max_length=50)


class GameResponse(BaseModel):
    id: int
    name: str
    platform: Optional[str]
    measurement_id: str
    rate_per_min: int
    burst: int
    max_bytes: int
    bytes_used: int
    events_stored: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GameSecretResponse(GameResponse):
    """Returned only at creation / rotation — includes the plaintext secret ONCE."""
    api_secret: str


class GameUsageResponse(BaseModel):
    measurement_id: str
    name: str
    bytes_used: int
    max_bytes: int
    percent_used: float
    events_stored: int
    rate_per_min: int
    burst: int
    events_last_minute: int


# --- Admin ------------------------------------------------------------------
class CourseCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    ends_at: Optional[datetime] = None
    discord_guild_ids: Optional[str] = None


class QuotaUpdate(BaseModel):
    rate_per_min: Optional[int] = Field(None, ge=1)
    burst: Optional[int] = Field(None, ge=1)
    max_bytes: Optional[int] = Field(None, ge=1024)


class UserAdminUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


# --- GA4 Measurement Protocol ingest ----------------------------------------
class GA4Event(BaseModel):
    """A GA4-style named event with an arbitrary params map (mirrors gtag/Apple)."""
    name: str = Field(min_length=1, max_length=64)
    params: dict[str, Any] = Field(default_factory=dict)


class GA4CollectRequest(BaseModel):
    client_id: str = Field(min_length=1, max_length=128)
    user_id: Optional[str] = Field(None, max_length=128)
    events: List[GA4Event] = Field(..., min_length=1, max_length=100)
