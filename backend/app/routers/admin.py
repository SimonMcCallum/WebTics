"""Admin (instructor) endpoints: roster import, account lifecycle, quota overrides.

Roster import is the core instructor workflow: upload a CSV of students, the system
pre-creates unclaimed accounts with temp passwords and an expiry derived from the
course end date, and returns the temp passwords so Simon can email them out.
"""
import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models_accounts import User, Course, Game
from ..schemas_accounts import QuotaUpdate, UserAdminUpdate, UserResponse, CourseCreate
from ..auth import get_current_admin, hash_password, generate_temp_password

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/courses")
async def create_course(
    body: CourseCreate, _: User = Depends(get_current_admin), db: Session = Depends(get_db)
):
    if db.query(Course).filter(Course.code == body.code).first():
        raise HTTPException(status_code=409, detail="Course code already exists")
    course = Course(
        code=body.code, name=body.name, ends_at=body.ends_at,
        discord_guild_ids=body.discord_guild_ids,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return {"id": course.id, "code": course.code, "ends_at": course.ends_at}


@router.post("/roster")
async def import_roster(
    file: UploadFile = File(...),
    course_code: str = Form(...),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Bulk-create accounts from a CSV with headers ``email,name`` (name optional).

    Returns ``{email, name, temp_password}`` for each NEW account so the instructor can
    mail credentials. Existing emails are skipped (idempotent re-import).
    """
    course = db.query(Course).filter(Course.code == course_code).first()
    if course is None:
        raise HTTPException(status_code=404, detail=f"Course '{course_code}' not found")

    raw = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    if reader.fieldnames is None or "email" not in [f.lower() for f in reader.fieldnames]:
        raise HTTPException(status_code=400, detail="CSV must have an 'email' column")

    created, skipped = [], []
    for row in reader:
        row = {(k or "").lower().strip(): (v or "").strip() for k, v in row.items()}
        email = row.get("email", "").lower()
        if not email:
            continue
        if db.query(User).filter(User.email == email).first():
            skipped.append(email)
            continue
        temp = generate_temp_password()
        db.add(User(
            email=email,
            roster_name=row.get("name") or None,
            display_name=row.get("name") or None,
            password_hash=hash_password(temp),
            role="student",
            is_claimed=False,
            must_change_password=True,
            expires_at=course.ends_at,
            course_id=course.id,
        ))
        created.append({"email": email, "name": row.get("name", ""), "temp_password": temp})
    db.commit()
    return {"course": course_code, "created": created, "skipped": skipped,
            "created_count": len(created), "skipped_count": len(skipped)}


@router.get("/users", response_model=list[UserResponse])
async def list_users(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, body: UserAdminUpdate,
    _: User = Depends(get_current_admin), db: Session = Depends(get_db),
):
    """Extend/expire access, disable an account, or grant admin."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if body.expires_at is not None:
        user.expires_at = body.expires_at
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.role is not None:
        if body.role not in ("student", "admin"):
            raise HTTPException(status_code=400, detail="role must be 'student' or 'admin'")
        user.role = body.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/games/{game_id}/quota")
async def update_quota(
    game_id: int, body: QuotaUpdate,
    _: User = Depends(get_current_admin), db: Session = Depends(get_db),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Game not found")
    if body.rate_per_min is not None:
        game.rate_per_min = body.rate_per_min
    if body.burst is not None:
        game.burst = body.burst
    if body.max_bytes is not None:
        game.max_bytes = body.max_bytes
    db.commit()
    return {"status": "updated", "game_id": game_id,
            "rate_per_min": game.rate_per_min, "burst": game.burst, "max_bytes": game.max_bytes}


@router.get("/usage")
async def usage_overview(_: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    """Server-wide storage/usage snapshot for monitoring disk pressure."""
    games = db.query(Game).all()
    total_bytes = sum(g.bytes_used for g in games)
    return {
        "total_games": len(games),
        "total_bytes_used": total_bytes,
        "total_mb_used": round(total_bytes / (1024 * 1024), 2),
        "games": [
            {
                "measurement_id": g.measurement_id, "name": g.name,
                "owner_user_id": g.owner_user_id,
                "mb_used": round(g.bytes_used / (1024 * 1024), 2),
                "percent": round((g.bytes_used / g.max_bytes * 100) if g.max_bytes else 0, 1),
                "events_stored": g.events_stored,
            }
            for g in sorted(games, key=lambda x: x.bytes_used, reverse=True)
        ],
    }
