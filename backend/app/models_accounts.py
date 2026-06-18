"""Account, course, game-registration and usage models.

These power the student-facing teaching service: roster-based accounts that expire
when a student leaves the university, per-student game registration with GA4-style
measurement IDs + API secrets, and per-game rate / storage quotas.

Kept separate from ``models.py`` (telemetry) and ``models_research.py`` (ethics) to
match the existing module split.
"""
from sqlalchemy import (
    Column, Integer, BigInteger, String, DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Course(Base):
    """A teaching course/cohort. ``ends_at`` drives default account expiry."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g. "CGRA350"
    name = Column(String(200), nullable=True)
    # Discord guild id this course is locked to (future Discord signup). Comma-separated.
    discord_guild_ids = Column(String(255), nullable=True)
    ends_at = Column(DateTime, nullable=True)  # students' accounts expire at this time
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="course")


class User(Base):
    """A student or admin account.

    Accounts are pre-created from a roster (``is_claimed=False``) and emailed a
    temporary password. The student "claims" the account on first login by setting
    their own password. ``expires_at`` enforces time-limited access.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=True)
    # The name the student claims (from the roster Simon supplies).
    roster_name = Column(String(200), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="student")  # 'student' | 'admin'

    is_claimed = Column(Boolean, nullable=False, default=False)
    must_change_password = Column(Boolean, nullable=False, default=True)
    is_active = Column(Boolean, nullable=False, default=True)
    # Time-limited access: login + ingest rejected after this instant.
    expires_at = Column(DateTime, nullable=True)

    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)

    course = relationship("Course", back_populates="users")
    games = relationship("Game", back_populates="owner", cascade="all, delete-orphan")


class Game(Base):
    """A registered game that produces telemetry.

    ``measurement_id`` is public (GA4-style, e.g. ``WT-AB12CD34``) and identifies the
    game in the ingest URL; ``api_secret_hash`` authenticates writes. The plaintext
    secret is shown to the student exactly once at creation / rotation.
    """
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=True)  # 'godot' | 'web' | 'unreal' | ...

    measurement_id = Column(String(32), unique=True, nullable=False, index=True)
    api_secret_hash = Column(String(255), nullable=False)

    # Quota knobs (admin-overridable). Defaults are applied at creation from config.
    rate_per_min = Column(Integer, nullable=False, default=60)
    burst = Column(Integer, nullable=False, default=600)
    max_bytes = Column(BigInteger, nullable=False, default=100 * 1024 * 1024)  # 100 MB

    # Denormalised running total of stored event bytes (cheap quota checks).
    bytes_used = Column(BigInteger, nullable=False, default=0)
    events_stored = Column(BigInteger, nullable=False, default=0)

    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="games")
    usage_windows = relationship(
        "UsageCounter", back_populates="game", cascade="all, delete-orphan"
    )


class UsageCounter(Base):
    """Fixed-window rate-limit counter (DB-backed, no Redis dependency).

    One row per game per minute window. The limiter increments the current window's
    ``count`` and rejects once it exceeds the game's burst allowance.
    """
    __tablename__ = "usage_counters"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    # Truncated-to-minute UTC timestamp identifying this window.
    window_start = Column(DateTime, nullable=False, index=True)
    count = Column(Integer, nullable=False, default=0)

    game = relationship("Game", back_populates="usage_windows")
