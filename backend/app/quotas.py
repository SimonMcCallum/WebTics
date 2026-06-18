"""Rate-limiting and storage-quota enforcement.

Two independent protections keep the shared server's disk from exploding:

  * **Rate limit** — a DB-backed fixed-window counter (one row per game per minute).
    Survives restarts and needs no Redis. Rejects bursts beyond the game's allowance.
  * **Storage quota** — a denormalised ``bytes_used`` counter per game compared against
    ``max_bytes`` before each write. On overflow we reject (HTTP 429) and preserve all
    existing data (research-integrity choice — never auto-delete).

Both raise ``HTTPException(429)`` so callers can surface a clear message to students.
"""
import json
from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import config
from .models_accounts import Game, UsageCounter


def _current_window() -> datetime:
    now = datetime.utcnow()
    return now.replace(second=0, microsecond=0)


def check_rate_limit(game: Game, db: Session, incoming: int = 1) -> None:
    """Increment the current minute window and reject if it exceeds the burst allowance.

    The effective per-minute ceiling is ``max(rate_per_min, burst)`` — ``burst`` lets a
    game send a short spike (e.g. a batch flush) while ``rate_per_min`` documents the
    sustained intent. We gate on ``burst`` to allow legitimate batching.
    """
    window = _current_window()
    counter = (
        db.query(UsageCounter)
        .filter(UsageCounter.game_id == game.id, UsageCounter.window_start == window)
        .first()
    )
    if counter is None:
        counter = UsageCounter(game_id=game.id, window_start=window, count=0)
        db.add(counter)
        db.flush()

    ceiling = max(game.rate_per_min, game.burst)
    if counter.count + incoming > ceiling:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded for this game ({ceiling} events/min). "
                "Slow down or batch fewer events. Contact your instructor to raise the limit."
            ),
            headers={"Retry-After": "60"},
        )
    counter.count += incoming


def estimate_event_bytes(payload: Any) -> int:
    """Approximate on-disk size of one event: serialized payload + fixed row overhead."""
    try:
        size = len(json.dumps(payload, default=str).encode("utf-8"))
    except (TypeError, ValueError):
        size = 0
    return size + config.EVENT_ROW_OVERHEAD_BYTES


def enforce_storage(game: Game, incoming_bytes: int) -> None:
    """Reject the write if it would push the game over its storage cap."""
    if game.bytes_used + incoming_bytes > game.max_bytes:
        used_mb = game.bytes_used / (1024 * 1024)
        cap_mb = game.max_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Storage quota exceeded ({used_mb:.1f} MB / {cap_mb:.0f} MB used). "
                "Existing data is preserved. Delete old data or ask your instructor "
                "to raise the quota."
            ),
        )


def record_storage(game: Game, accepted_bytes: int, accepted_events: int) -> None:
    """Update the denormalised counters after a successful write."""
    game.bytes_used += accepted_bytes
    game.events_stored += accepted_events


def events_last_minute(game: Game, db: Session) -> int:
    counter = (
        db.query(UsageCounter)
        .filter(UsageCounter.game_id == game.id, UsageCounter.window_start == _current_window())
        .first()
    )
    return counter.count if counter else 0
