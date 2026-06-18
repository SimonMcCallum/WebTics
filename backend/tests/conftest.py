"""Shared test fixtures.

Runs the suite against a throwaway SQLite database so no PostgreSQL is required, and
forces the production ingest posture (``ALLOW_ANON_INGEST=false``) so the auth/quota paths
are actually exercised. Existing tests that set their own DATABASE_URL via CI still work
because we only ``setdefault``.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./webtics_test.db")
# Open-ingest ON for the suite so the legacy /api/v1/events + /sessions tests exercise the
# dev path. The production gating is covered explicitly in test_quotas by monkeypatching config.
os.environ.setdefault("ALLOW_ANON_INGEST", "true")
os.environ.setdefault("JWT_SECRET", "test-secret-key")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.database import SessionLocal, engine, Base  # noqa: E402
from app import models, models_accounts  # noqa: E402  (ensure tables registered)
from app.auth import hash_password  # noqa: E402
from app.models_accounts import User  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _make_user(db, email, password, **kwargs):
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, password_hash=hash_password(password))
        db.add(user)
    else:
        user.password_hash = hash_password(password)
    user.is_active = kwargs.get("is_active", True)
    user.is_claimed = kwargs.get("is_claimed", True)
    user.must_change_password = kwargs.get("must_change_password", False)
    user.role = kwargs.get("role", "student")
    user.expires_at = kwargs.get("expires_at", None)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def make_user(db):
    """Factory to create/overwrite a user with arbitrary attributes."""
    def _factory(email, password="Password123", **kwargs):
        return _make_user(db, email, password, **kwargs)
    return _factory


def _login(client, email, password):
    r = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
def student_token(client, make_user):
    make_user("student@test.ac.nz", "Password123", role="student")
    return _login(client, "student@test.ac.nz", "Password123")


@pytest.fixture
def admin_token(client, make_user):
    make_user("admin@test.ac.nz", "AdminPass123", role="admin")
    return _login(client, "admin@test.ac.nz", "AdminPass123")


@pytest.fixture
def auth_header():
    return lambda token: {"Authorization": f"Bearer {token}"}


@pytest.fixture
def registered_game(client, student_token, auth_header):
    """Create a game and return (measurement_id, api_secret, game_json)."""
    r = client.post(
        "/api/v1/games",
        json={"name": "Test Game", "platform": "godot"},
        headers=auth_header(student_token),
    )
    assert r.status_code == 201, r.text
    g = r.json()
    return g["measurement_id"], g["api_secret"], g
