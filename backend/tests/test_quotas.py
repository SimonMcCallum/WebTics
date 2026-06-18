"""Tests for rate-limit and storage-quota enforcement (the disk-explosion guards)."""


def _collect_url(mid, secret):
    return f"/mp/collect?measurement_id={mid}&api_secret={secret}"


def _set_quota(client, admin_token, auth_header, game_id, **quota):
    r = client.patch(f"/api/v1/admin/games/{game_id}/quota",
                     json=quota, headers=auth_header(admin_token))
    assert r.status_code == 200, r.text


def test_rate_limit_returns_429(client, registered_game, admin_token, auth_header):
    mid, secret, game = registered_game
    # Tighten the per-minute ceiling so we can trip it quickly.
    _set_quota(client, admin_token, auth_header, game["id"], rate_per_min=2, burst=2)

    body = {"client_id": "c1", "events": [{"name": "screen_view", "params": {}}]}
    assert client.post(_collect_url(mid, secret), json=body).status_code == 200
    assert client.post(_collect_url(mid, secret), json=body).status_code == 200
    # Third event in the same minute exceeds burst=2.
    r = client.post(_collect_url(mid, secret), json=body)
    assert r.status_code == 429
    assert "rate limit" in r.json()["detail"].lower()


def test_storage_quota_returns_429_and_preserves_data(client, registered_game, admin_token, auth_header, student_token):
    mid, secret, game = registered_game
    # Accumulate >1KB (the admin quota floor), then shrink the cap below current usage.
    body = {"client_id": "c1",
            "events": [{"name": "level_up", "params": {"level": i}} for i in range(20)]}
    assert client.post(_collect_url(mid, secret), json=body).status_code == 200

    usage = client.get(f"/api/v1/games/{game['id']}/usage", headers=auth_header(student_token)).json()
    stored_before = usage["events_stored"]
    # Cap = current bytes_used (so any further write overflows).
    _set_quota(client, admin_token, auth_header, game["id"],
               max_bytes=usage["bytes_used"], rate_per_min=1000, burst=1000)

    r = client.post(_collect_url(mid, secret), json=body)
    assert r.status_code == 429
    assert "quota" in r.json()["detail"].lower()

    # Existing data must be untouched (reject-new, never auto-delete).
    after = client.get(f"/api/v1/games/{game['id']}/usage", headers=auth_header(student_token)).json()
    assert after["events_stored"] == stored_before


def test_legacy_ingest_blocked_in_production(client, monkeypatch):
    """With ALLOW_ANON_INGEST=false the open endpoints 403 (no quota bypass)."""
    from app import config
    monkeypatch.setattr(config, "ALLOW_ANON_INGEST", False)
    r = client.post("/api/v1/sessions", json={"unique_id": "x123", "build_number": "1.0"})
    assert r.status_code == 403
    assert "/mp/collect" in r.json()["detail"]


def test_quota_unit_helpers():
    from app.quotas import estimate_event_bytes
    from app import config
    size = estimate_event_bytes({"name": "x", "params": {}})
    assert size > config.EVENT_ROW_OVERHEAD_BYTES  # payload + overhead
