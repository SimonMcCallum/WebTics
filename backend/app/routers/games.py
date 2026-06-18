"""Game registration & management for the logged-in student.

A student registers each game they want to record. Registration returns a public
``measurement_id`` and a write ``api_secret`` (shown ONCE) — the GA4 "measurement id +
API secret" model students will recognise from Google Analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import config
from ..database import get_db
from ..models_accounts import User, Game
from ..schemas_accounts import (
    GameCreate, GameResponse, GameSecretResponse, GameUsageResponse,
)
from ..auth import (
    get_current_user, hash_password, generate_measurement_id, generate_api_secret,
)
from ..quotas import events_last_minute

router = APIRouter(prefix="/api/v1/games", tags=["games"])


def _owned_game_or_404(game_id: int, user: User, db: Session) -> Game:
    game = (
        db.query(Game)
        .filter(Game.id == game_id, Game.owner_user_id == user.id)
        .first()
    )
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game


def _user_bytes_used(user: User, db: Session) -> int:
    return sum(g.bytes_used for g in user.games)


def _with_secret(game: Game, secret: str) -> GameSecretResponse:
    """Build the one-time response that includes the plaintext api_secret."""
    base = GameResponse.model_validate(game).model_dump()
    return GameSecretResponse(**base, api_secret=secret)


@router.post("", response_model=GameSecretResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    body: GameCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Register a new game. Returns the api_secret in plaintext exactly once."""
    secret = generate_api_secret()
    # Ensure a unique measurement id (collisions are astronomically unlikely; retry anyway).
    for _ in range(5):
        mid = generate_measurement_id()
        if not db.query(Game).filter(Game.measurement_id == mid).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not allocate measurement id")

    game = Game(
        owner_user_id=user.id,
        name=body.name,
        platform=body.platform,
        measurement_id=mid,
        api_secret_hash=hash_password(secret),
        rate_per_min=config.DEFAULT_RATE_PER_MIN,
        burst=config.DEFAULT_BURST,
        max_bytes=config.DEFAULT_MAX_BYTES,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return _with_secret(game, secret)


@router.get("", response_model=list[GameResponse])
async def list_games(user: User = Depends(get_current_user)):
    return user.games


@router.get("/{game_id}/usage", response_model=GameUsageResponse)
async def game_usage(
    game_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    game = _owned_game_or_404(game_id, user, db)
    percent = (game.bytes_used / game.max_bytes * 100) if game.max_bytes else 0.0
    return GameUsageResponse(
        measurement_id=game.measurement_id,
        name=game.name,
        bytes_used=game.bytes_used,
        max_bytes=game.max_bytes,
        percent_used=round(percent, 2),
        events_stored=game.events_stored,
        rate_per_min=game.rate_per_min,
        burst=game.burst,
        events_last_minute=events_last_minute(game, db),
    )


@router.post("/{game_id}/rotate-secret", response_model=GameSecretResponse)
async def rotate_secret(
    game_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Issue a new write secret (invalidates the old one). Shown once."""
    game = _owned_game_or_404(game_id, user, db)
    secret = generate_api_secret()
    game.api_secret_hash = hash_password(secret)
    db.commit()
    db.refresh(game)
    return _with_secret(game, secret)


@router.delete("/{game_id}")
async def delete_game(
    game_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Delete a game and free its storage. Telemetry sessions are detached, not orphaned."""
    game = _owned_game_or_404(game_id, user, db)
    db.delete(game)
    db.commit()
    return {"status": "deleted", "game_id": game_id}
