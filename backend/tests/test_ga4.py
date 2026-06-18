"""Tests for the GA4-style /mp/collect ingest and event-name mapping."""


def _collect_url(mid, secret):
    return f"/mp/collect?measurement_id={mid}&api_secret={secret}"


def test_collect_requires_valid_credentials(client, registered_game):
    mid, secret, _ = registered_game
    # Wrong secret rejected.
    r = client.post(_collect_url(mid, "wrong-secret"),
                    json={"client_id": "c1", "events": [{"name": "level_up", "params": {}}]})
    assert r.status_code == 401
    # Unknown measurement id rejected.
    r = client.post(_collect_url("WT-NOPE0000", secret),
                    json={"client_id": "c1", "events": [{"name": "level_up", "params": {}}]})
    assert r.status_code == 401


def test_collect_named_event_stored(client, registered_game, auth_header, student_token):
    mid, secret, game = registered_game
    r = client.post(_collect_url(mid, secret), json={
        "client_id": "player-1",
        "events": [
            {"name": "level_up", "params": {"level": 5, "x": 10, "y": 20, "score": 99.5}},
            {"name": "my_custom_thing", "params": {"foo": "bar"}},
        ],
    })
    assert r.status_code == 200
    assert r.json()["events_received"] == 2

    usage = client.get(f"/api/v1/games/{game['id']}/usage",
                       headers=auth_header(student_token)).json()
    assert usage["events_stored"] == 2
    assert usage["bytes_used"] > 0


def test_known_and_custom_event_mapping():
    from app.event_registry import resolve_event_type, CUSTOM_EVENT_TYPE, extract_columns
    assert resolve_event_type("level_up")[0] == 11
    assert resolve_event_type("player_death")[0] == 0
    # Unknown names fall into the custom bucket, never lost.
    assert resolve_event_type("totally_made_up")[0] == CUSTOM_EVENT_TYPE

    cols = extract_columns({"x": 3, "y": 4, "score": 12.5})
    assert cols["x"] == 3 and cols["y"] == 4
    assert cols["magnitude"] == 12.5


def test_event_registry_endpoint(client):
    r = client.get("/mp/event-registry")
    assert r.status_code == 200
    names = r.json()["recommended_events"]
    assert "level_up" in names and "post_score" in names


def test_validation_rejects_empty_events(client, registered_game):
    mid, secret, _ = registered_game
    r = client.post(_collect_url(mid, secret), json={"client_id": "c1", "events": []})
    assert r.status_code == 422  # pydantic min_length=1
