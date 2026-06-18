# Future: Discord-Managed Signup (Design)

> **Status: not implemented.** This is the design for a future phase. Today, accounts are
> pre-created from a roster and credentials are emailed manually (see
> [Admin_Guide.md](Admin_Guide.md)). This document captures the intended replacement so the
> data model and decisions are recorded.

## Goal

Replace manual credential emailing with **self-service signup through Discord**, locked to the
**course's Discord server(s)**. A student in the right Discord guild can claim an account
without the instructor mailing passwords.

## Why Discord

The courses already run community Discord servers. Guild membership + roles are a reasonable
proxy for "is enrolled / belongs to this course", and a bot can verify it automatically. This
mirrors the existing **PVEbot** pattern on the same home server
(`/home/simon/git/PVEbot`, TypeScript + Discord.js).

## How it locks to a course

`Course.discord_guild_ids` (already in the schema, comma-separated) lists the Discord guild
IDs allowed to claim accounts for that course. The bot only acts on those guilds and can
additionally require a specific **role** (e.g. `@CGRA350-2026`).

## Proposed flow

1. Student runs `/claim-analytics` (or clicks a button) in the course Discord server.
2. The bot checks: member of an allowed guild? has the required role? not already claimed?
3. The bot calls a new **bot-only backend endpoint** with a shared service token:
   `POST /api/v1/discord/claim` `{ discord_user_id, discord_guild_id, email? }`.
4. The backend verifies the guild is registered to a course, creates/links a `User`
   (`expires_at = course.ends_at`), and returns a **one-time claim link or temp password**.
5. The bot DMs the student the link; they set a password at `/app/claim`.

## Backend changes required (when built)

- New `discord_user_id` column on `User` (nullable, unique) to link Discord ↔ account.
- A `bot_service_token` (separate from student JWTs) checked on `/api/v1/discord/*`.
- An allow-list check: `discord_guild_id ∈ course.discord_guild_ids`.
- Rate-limit + audit the claim endpoint (prevent guild members mass-creating accounts).

## Bot changes (reuse PVEbot infra)

- A new slash command + guild/role gate, sharing PVEbot's Discord.js setup and `.env` secret
  management on the home server.
- Config: map `guild_id → course_code` (or read it from the backend).

## Security notes

- Verify guild membership **server-side via the Discord API**, not just from the interaction
  payload, to prevent spoofing.
- Keep the bot service token out of the client; store it in `/home/simon/docker/.env`.
- Treat the claim endpoint as sensitive: log every claim with the Discord user id for audit.

## Not in scope even then

- Public/open signup outside a course Discord.
- Replacing JWT auth for the portal (Discord is for *onboarding*, not session auth).
