"""GA4 Measurement-Protocol-style ingest — the skill-transfer interface.

Students send named events with a free-form ``params`` map, exactly like Google
Analytics 4's ``gtag`` / Measurement Protocol and Apple's named-event analytics. Every
event is authenticated (game secret), rate-limited, storage-checked, then mapped onto
WebTics' existing ``MetricSession`` / ``PlaySession`` / ``Event`` tables.

A ``client_id`` (the player/device) maps to a ``MetricSession.unique_id`` so all of a
player's events group together — mirroring GA4's client_id semantics.
"""
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from .. import models, config
from ..database import get_db
from ..auth import verify_game_secret
from ..quotas import (
    check_rate_limit, enforce_storage, record_storage, estimate_event_bytes,
)
from ..event_registry import resolve_event_type, extract_columns, known_event_names
from ..schemas_accounts import GA4CollectRequest

router = APIRouter(prefix="/mp", tags=["analytics"])


def _get_or_create_session(db: Session, game_id: int, client_id: str) -> models.MetricSession:
    """One MetricSession per (game, client_id) — GA4 client_id semantics."""
    unique_id = f"{game_id}:{client_id}"
    session = (
        db.query(models.MetricSession)
        .filter(models.MetricSession.unique_id == unique_id)
        .first()
    )
    if session is None:
        session = models.MetricSession(unique_id=unique_id, game_id=game_id)
        db.add(session)
        db.flush()
    return session


def _get_or_create_play_session(db: Session, metric_session_id: int) -> models.PlaySession:
    """Reuse an open play session for the metric session, else open one."""
    play = (
        db.query(models.PlaySession)
        .filter(
            models.PlaySession.metric_session_id == metric_session_id,
            models.PlaySession.ended_at.is_(None),
        )
        .order_by(models.PlaySession.id.desc())
        .first()
    )
    if play is None:
        play = models.PlaySession(metric_session_id=metric_session_id)
        db.add(play)
        db.flush()
    return play


@router.post("/collect")
async def collect(
    payload: GA4CollectRequest,
    request: Request,
    measurement_id: str = Query(..., description="Game's public measurement id (WT-...)"),
    api_secret: str = Query(..., description="Game's write secret"),
    db: Session = Depends(get_db),
):
    """GA4 Measurement Protocol-compatible batch ingest.

    Order of checks: **auth -> rate limit -> storage -> insert**. On any quota breach
    nothing is written and a 429 is returned with a student-friendly message.
    """
    game = verify_game_secret(measurement_id, api_secret, db)

    # Size + rate are evaluated for the whole batch before any insert.
    incoming_bytes = sum(
        estimate_event_bytes({"name": e.name, "params": e.params}) for e in payload.events
    )
    check_rate_limit(game, db, incoming=len(payload.events))
    enforce_storage(game, incoming_bytes)

    metric_session = _get_or_create_session(db, game.id, payload.client_id)
    play_session = _get_or_create_play_session(db, metric_session.id)

    for ev in payload.events:
        event_type, event_subtype = resolve_event_type(ev.name)
        cols = extract_columns(ev.params)
        db.add(
            models.Event(
                play_session_id=play_session.id,
                event_type=event_type,
                event_subtype=event_subtype,
                x=cols["x"],
                y=cols["y"],
                z=cols["z"],
                magnitude=cols["magnitude"],
                # Lossless: original GA4 name + full params map retained.
                data={"name": ev.name, "params": ev.params, "user_id": payload.user_id},
            )
        )

    record_storage(game, incoming_bytes, len(payload.events))
    db.commit()

    # GA4 returns 204 No Content on success; we echo a small body for debuggability.
    return {"status": "ok", "events_received": len(payload.events)}


@router.get("/event-registry")
async def event_registry():
    """The standard GA4/Apple-aligned event names students should prefer."""
    return {
        "service": config.SERVICE_BRAND,
        "note": (
            "Use these recommended names where they fit — they map to GA4 & Apple "
            "App Analytics so your skills transfer. Any other name is accepted and "
            "stored as a custom event."
        ),
        "recommended_events": known_event_names(),
    }
