#!/usr/bin/env python3
"""Import a course roster and pre-create student accounts (CLI alternative to the admin UI).

CSV needs an ``email`` column; an optional ``name`` column is used as the display/roster name.
The course is created if it doesn't exist. A CSV of ``email,name,temp_password`` is written so
you can mail credentials out. Re-running is idempotent (existing emails are skipped).

    docker compose exec backend python /app/scripts/import_roster.py \
        /app/scripts/roster.csv --course CGRA350 --ends 2026-11-15 --out creds.csv
"""
import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database import SessionLocal, engine  # noqa: E402
from app import models_accounts  # noqa: E402
from app.auth import hash_password, generate_temp_password  # noqa: E402
from app.models_accounts import User, Course  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Import a course roster")
    parser.add_argument("csv_path", help="roster CSV with an 'email' column")
    parser.add_argument("--course", required=True, help="course code, e.g. CGRA350")
    parser.add_argument("--name", default=None, help="human course name")
    parser.add_argument("--ends", default=None, help="account expiry date YYYY-MM-DD")
    parser.add_argument("--out", default="credentials.csv", help="where to write temp passwords")
    args = parser.parse_args()

    models_accounts.Base.metadata.create_all(bind=engine)
    ends_at = datetime.fromisoformat(args.ends) if args.ends else None

    db = SessionLocal()
    created = []
    try:
        course = db.query(Course).filter(Course.code == args.course).first()
        if course is None:
            course = Course(code=args.course, name=args.name, ends_at=ends_at)
            db.add(course)
            db.flush()
        elif ends_at is not None:
            course.ends_at = ends_at

        with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = {(k or "").lower().strip(): (v or "").strip() for k, v in row.items()}
                email = row.get("email", "").lower()
                if not email or db.query(User).filter(User.email == email).first():
                    continue
                temp = generate_temp_password()
                name = row.get("name") or None
                db.add(User(
                    email=email, roster_name=name, display_name=name,
                    password_hash=hash_password(temp), role="student",
                    is_claimed=False, must_change_password=True,
                    expires_at=course.ends_at, course_id=course.id,
                ))
                created.append({"email": email, "name": name or "", "temp_password": temp})
        db.commit()
    finally:
        db.close()

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["email", "name", "temp_password"])
        writer.writeheader()
        writer.writerows(created)

    print(f"Course '{args.course}' — created {len(created)} accounts.")
    print(f"Credentials written to {args.out} (email these to students, then delete the file).")


if __name__ == "__main__":
    main()
