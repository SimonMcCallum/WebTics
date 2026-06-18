"""Authentication & authorization helpers.

Covers two distinct auth surfaces:
  * **User auth** (students/admins) for the portal + management API, via JWT bearer tokens.
  * **Game auth** for telemetry ingest, via ``measurement_id`` + ``api_secret`` (GA4-style).

Time-limited accounts are enforced on every authenticated request: a token may be
cryptographically valid yet rejected because the account's ``expires_at`` has passed.
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import config
from .database import get_db
from .models_accounts import User, Game

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# auto_error=False so we can return a clean 401 ourselves and reuse it for optional auth.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# --- Passwords --------------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return pwd_context.verify(plain, hashed)
    except ValueError:
        return False


def generate_temp_password(length: int = 12) -> str:
    """Human-friendly temp password (no ambiguous chars) for emailing to students."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# --- Game credentials -------------------------------------------------------
def generate_measurement_id() -> str:
    """GA4-style public id, e.g. ``WT-AB12CD34`` (8 unambiguous base32-ish chars)."""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "WT-" + "".join(secrets.choice(alphabet) for _ in range(8))


def generate_api_secret() -> str:
    return secrets.token_urlsafe(24)


# --- JWT --------------------------------------------------------------------
def create_access_token(user: User) -> str:
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": expire,
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def _account_is_expired(user: User) -> bool:
    return user.expires_at is not None and user.expires_at < datetime.utcnow()


# --- User dependencies ------------------------------------------------------
def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve + validate the bearer token into an active, non-expired user."""
    creds_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise creds_exc
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise creds_exc
    except JWTError:
        raise creds_exc

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None or not user.is_active:
        raise creds_exc
    if _account_is_expired(user):
        # Time-limited access: the account has lapsed (student left the university).
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has expired. Contact your course instructor.",
        )
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def require_anon_ingest() -> None:
    """Block the legacy un-authenticated ingest endpoints in production.

    The teaching server runs with ALLOW_ANON_INGEST=false so all telemetry must go
    through the authenticated, quota-enforced ``/mp/collect`` path. Self-hosted/dev
    installs set it true to use the raw session/event API directly.
    """
    if not config.ALLOW_ANON_INGEST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Direct ingest is disabled on this server. Send events to "
                "/mp/collect with your game's measurement_id and api_secret."
            ),
        )


# --- Game ingest auth -------------------------------------------------------
def verify_game_secret(measurement_id: str, api_secret: str, db: Session) -> Game:
    """Authenticate a telemetry write. Also enforces the owner's account expiry."""
    auth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid measurement_id or api_secret",
    )
    if not measurement_id or not api_secret:
        raise auth_exc

    game = db.query(Game).filter(Game.measurement_id == measurement_id).first()
    if game is None or not game.is_active:
        raise auth_exc
    if not verify_password(api_secret, game.api_secret_hash):
        raise auth_exc

    # An expired or deactivated student must not be able to keep sending data.
    owner = game.owner
    if owner is None or not owner.is_active or _account_is_expired(owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owning account is inactive or expired.",
        )
    return game
