"""User authentication: login, first-login claim, password change, profile."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models_accounts import User
from ..schemas_accounts import (
    LoginRequest, ClaimRequest, ChangePasswordRequest, TokenResponse, UserResponse,
)
from ..auth import (
    verify_password, hash_password, create_access_token, get_current_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _reject_if_unusable(user: User) -> None:
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")
    if user.expires_at is not None and user.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has expired. Contact your course instructor.",
        )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email + password. Expired/disabled accounts are rejected."""
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password."
        )
    _reject_if_unusable(user)

    user.last_login_at = datetime.utcnow()
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user),
        must_change_password=user.must_change_password,
        expires_at=user.expires_at,
    )


@router.post("/claim", response_model=TokenResponse)
async def claim(body: ClaimRequest, db: Session = Depends(get_db)):
    """First-login claim: authenticate with the emailed temp password, set a real one.

    This is how a student "claims their name": the account was pre-created from the
    roster Simon supplied; the student proves ownership of the emailed credential and
    chooses their own password + display name.
    """
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is None or not verify_password(body.temp_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or temporary password."
        )
    _reject_if_unusable(user)

    user.password_hash = hash_password(body.new_password)
    user.is_claimed = True
    user.must_change_password = False
    if body.display_name:
        user.display_name = body.display_name
    user.last_login_at = datetime.utcnow()
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user),
        must_change_password=False,
        expires_at=user.expires_at,
    )


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect."
        )
    user.password_hash = hash_password(body.new_password)
    user.must_change_password = False
    db.commit()
    return {"status": "password_changed"}


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
