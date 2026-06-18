#!/usr/bin/env python3
"""Bootstrap (or reset) an instructor admin account.

Run inside the backend environment so it can import the app and reach the database, e.g.

    docker compose exec backend python /app/scripts/create_admin.py \
        --email simon@university.ac.nz --password 'choose-a-strong-one'

If --password is omitted a strong one is generated and printed once.
"""
import argparse
import secrets
import sys
from pathlib import Path

# Allow running both as /app/scripts/create_admin.py (container) and from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.database import SessionLocal, engine  # noqa: E402
from app import models_accounts  # noqa: E402
from app.auth import hash_password  # noqa: E402
from app.models_accounts import User  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or reset an admin account")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", default=None, help="omit to auto-generate")
    parser.add_argument("--name", default="Instructor")
    args = parser.parse_args()

    models_accounts.Base.metadata.create_all(bind=engine)
    password = args.password or secrets.token_urlsafe(12)
    email = args.email.lower()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            user = User(email=email, display_name=args.name, role="admin")
            db.add(user)
            action = "Created"
        else:
            action = "Updated"
        user.password_hash = hash_password(password)
        user.role = "admin"
        user.is_active = True
        user.is_claimed = True
        user.must_change_password = False
        user.expires_at = None  # admins don't expire
        db.commit()
    finally:
        db.close()

    print(f"{action} admin account: {email}")
    if args.password is None:
        print(f"Generated password (save it now): {password}")


if __name__ == "__main__":
    main()
