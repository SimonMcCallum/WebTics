"""Tests for accounts: login, claim, time-limited access, and game ownership."""
from datetime import datetime, timedelta


def test_login_success_and_me(client, make_user, auth_header):
    make_user("alice@test.ac.nz", "Password123", display_name="Alice")
    r = client.post("/api/v1/auth/login", json={"email": "alice@test.ac.nz", "password": "Password123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers=auth_header(token))
    assert me.status_code == 200
    assert me.json()["email"] == "alice@test.ac.nz"


def test_login_wrong_password(client, make_user):
    make_user("bob@test.ac.nz", "Password123")
    r = client.post("/api/v1/auth/login", json={"email": "bob@test.ac.nz", "password": "nope"})
    assert r.status_code == 401


def test_expired_account_cannot_login(client, make_user):
    make_user("gone@test.ac.nz", "Password123", expires_at=datetime.utcnow() - timedelta(days=1))
    r = client.post("/api/v1/auth/login", json={"email": "gone@test.ac.nz", "password": "Password123"})
    assert r.status_code == 403
    assert "expired" in r.json()["detail"].lower()


def test_expired_token_holder_blocked_on_protected_route(client, make_user, auth_header):
    # Log in while valid, then expire the account; the existing token must stop working.
    user = make_user("soon@test.ac.nz", "Password123",
                     expires_at=datetime.utcnow() + timedelta(minutes=5))
    token = client.post("/api/v1/auth/login",
                        json={"email": "soon@test.ac.nz", "password": "Password123"}).json()["access_token"]
    assert client.get("/api/v1/games", headers=auth_header(token)).status_code == 200

    # Move expiry into the past.
    from app.database import SessionLocal
    from app.models_accounts import User
    s = SessionLocal()
    s.query(User).filter(User.id == user.id).update({"expires_at": datetime.utcnow() - timedelta(minutes=1)})
    s.commit(); s.close()

    assert client.get("/api/v1/games", headers=auth_header(token)).status_code == 403


def test_claim_flow(client, make_user):
    # Pre-created unclaimed account with a temp password.
    make_user("claimme@test.ac.nz", "TempPass99", is_claimed=False, must_change_password=True)
    r = client.post("/api/v1/auth/claim", json={
        "email": "claimme@test.ac.nz",
        "temp_password": "TempPass99",
        "new_password": "BrandNewPass1",
        "display_name": "Claimed Name",
    })
    assert r.status_code == 200
    # Old temp password no longer works; new one does.
    assert client.post("/api/v1/auth/login",
                       json={"email": "claimme@test.ac.nz", "password": "TempPass99"}).status_code == 401
    ok = client.post("/api/v1/auth/login",
                     json={"email": "claimme@test.ac.nz", "password": "BrandNewPass1"})
    assert ok.status_code == 200
    assert ok.json()["must_change_password"] is False


def test_unauthenticated_cannot_list_games(client):
    assert client.get("/api/v1/games").status_code == 401


def test_student_cannot_access_admin(client, student_token, auth_header):
    assert client.get("/api/v1/admin/users", headers=auth_header(student_token)).status_code == 403


def test_game_owner_isolation(client, make_user, auth_header):
    # Two students; one must not see/usage the other's game.
    make_user("owner@test.ac.nz", "Password123")
    make_user("intruder@test.ac.nz", "Password123")
    owner_tok = client.post("/api/v1/auth/login",
                            json={"email": "owner@test.ac.nz", "password": "Password123"}).json()["access_token"]
    intruder_tok = client.post("/api/v1/auth/login",
                               json={"email": "intruder@test.ac.nz", "password": "Password123"}).json()["access_token"]
    g = client.post("/api/v1/games", json={"name": "Owned"}, headers=auth_header(owner_tok)).json()
    gid = g["id"]
    assert client.get(f"/api/v1/games/{gid}/usage", headers=auth_header(intruder_tok)).status_code == 404
