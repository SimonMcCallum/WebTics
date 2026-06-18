# Instructor / Admin Guide

How to run WebTics as a course analytics service: create courses, import student rosters,
hand out credentials, manage time-limited access, and keep storage under control.

## 0. Create the first admin

Admins are created from the command line (there's no public signup). Inside the backend
container/environment:

```bash
docker compose exec backend python /app/scripts/create_admin.py \
    --email simon@university.ac.nz --password 'a-strong-password'
```

Then log in at `/app/login` and open `/app/admin`.

## 1. Create a course

A course defines the **expiry date** for its students' accounts (their access ends when the
course does — that's how access is time-limited once they leave).

- **Admin UI:** `/app/admin` → *Create a course* (set "Access ends at").
- **API:** `POST /api/v1/admin/courses`
  ```json
  { "code": "CGRA350", "name": "Computer Graphics 2026", "ends_at": "2026-11-15T23:59:00" }
  ```

## 2. Import the roster

You supply the list of students; the system pre-creates **unclaimed** accounts with temporary
passwords. Students later "claim" their account and name.

**CSV format** — one `email` column (required) and an optional `name` column:

```csv
email,name
ada.lovelace@students.example.ac.nz,Ada Lovelace
alan.turing@students.example.ac.nz,Alan Turing
```

**Admin UI:** `/app/admin` → *Import roster* → pick course code + CSV → it returns a table of
`email, name, temp_password` and a **Download CSV** button.

**CLI alternative:**
```bash
docker compose exec backend python /app/scripts/import_roster.py \
    /app/scripts/roster.csv --course CGRA350 --ends 2026-11-15 --out creds.csv
```

Re-importing is **idempotent** — existing emails are skipped, so you can add late enrolments
by re-running with an updated CSV.

## 3. Email the credentials

There's no automated email yet (by design). Mail each student their **email + temporary
password** and point them at `/app/claim`. **Delete the credentials CSV afterwards** — temp
passwords are only stored as bcrypt hashes and aren't recoverable later (you'd re-issue via a
re-import after deleting the account, or a future password-reset flow).

## 4. Manage access over time

- **Extend / shorten access:** `PATCH /api/v1/admin/users/{id}` with `{ "expires_at": "..." }`.
- **Disable an account immediately:** `{ "is_active": false }`.
- **Promote an admin:** `{ "role": "admin" }`.
- Expired or disabled accounts can't log in **and can't send telemetry** (the game's
  `api_secret` stops working too).

View all accounts and their claim/expiry status in the **Accounts** panel on `/app/admin`.

## 5. Manage storage / quotas

- **Monitor:** *Server usage* panel on `/app/admin` or `GET /api/v1/admin/usage` — games
  sorted by disk used, with totals.
- **Adjust a game's limits:** `PATCH /api/v1/admin/games/{game_id}/quota`
  ```json
  { "rate_per_min": 300, "burst": 1000, "max_bytes": 524288000 }
  ```
- Change **defaults** for new games via env vars (see [Quotas_and_Limits.md](Quotas_and_Limits.md)).

## 6. End of course

When `ends_at` passes, students lose access automatically — no action needed. To reclaim
disk, you can delete games (cascades their telemetry) or drop expired users in a maintenance
script.

## Future: Discord-managed signup

A planned phase replaces manual emailing with a Discord bot locked to the course's Discord
server(s). The `courses.discord_guild_ids` column already exists to support this. See
[Discord_Signup_Future.md](Discord_Signup_Future.md).
