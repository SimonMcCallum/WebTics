# WebTics / Ludogogy Logging — Knowledge Base (for the support bot)

This is the authoritative reference the assistant uses to answer student questions.
"Ludogogy Logging" is the student-facing brand; "WebTics" is the underlying service.
They are the SAME system. It is a self-hosted, GA4-style game analytics service.

## What it is
- Students add telemetry/analytics to their games (Godot, web, etc.).
- Events are **named** with a **parameters** map — exactly like Google Analytics 4
  (`gtag`) and Apple App Analytics. Skills transfer to those paid tools.
- Self-hosted on the course/university server (data stays local; runs on green energy).

## Core workflow (tell students this order)
1. **Claim account** at `PORTAL/claim` using the email + temporary password the instructor
   emailed. Set your own password + display name. Access is time-limited to the course.
2. **Log in** at `PORTAL/login`.
3. **Register a game** on the dashboard (`PORTAL/dashboard`). You receive:
   - `measurement_id` — public id like `WT-AB12CD34`.
   - `api_secret` — your write key, shown ONCE. Save it. If lost, use "Rotate secret".
4. **Add the SDK** to your game and send events.
5. **Check the dashboard** for stored events + storage usage.

## Godot integration (the main path for class)
- Copy the `ludogogy_logging` addon folder into `res://addons/`.
- Enable it: Project → Project Settings → Plugins.
- This creates the `LudogogyLogging` autoload singleton.
- Code:
```gdscript
func _ready():
    # 3rd arg (server URL) is optional; needed only for local testing.
    LudogogyLogging.start("WT-AB12CD34", "your-api-secret", "http://192.168.1.64:8013")
    LudogogyLogging.event("level_start", { "level": 1 })

func _on_player_died():
    LudogogyLogging.event("player_death", { "x": position.x, "y": position.y })

func _on_level_complete(score):
    LudogogyLogging.event("level_up", { "level": 2 })
    LudogogyLogging.post_score(score)   # convenience helper
```
- The plugin batches events, flushes every few seconds, and auto-backs-off on 429.
- It stores a stable `client_id` in `user://` so a player's events group together.

## Web integration (HTML5 / JS)
```html
<script src="http://192.168.1.64:8013/sdk/webtics.js"></script>
<script>
  webtics('config', 'WT-AB12CD34', { api_secret: 'your-api-secret' });
  webtics('event', 'level_up', { level: 5, character: 'mage' });
</script>
```
- It's a `gtag`-style API: `webtics('config', measurement_id, {api_secret})` then
  `webtics('event', name, params)`.

## Raw HTTP (advanced / other engines)
`POST PORTAL/../mp/collect?measurement_id=WT-XXXX&api_secret=SECRET`
```json
{ "client_id": "player-1", "events": [ { "name": "level_up", "params": { "level": 5 } } ] }
```
Success returns 200/204. This is the GA4 Measurement Protocol shape.

## Recommended event names (GA4/Apple-aligned)
session_start, session_end, screen_view, level_start, level_end, level_up,
level_complete, level_failed, post_score, unlock_achievement, tutorial_begin,
tutorial_complete, player_death, player_respawn, player_shoot, player_hit,
purchase, correct_response, incorrect_response, timeout.
- Any OTHER name is fine too — it's stored as a custom event, original name preserved.
- Special params `x`, `y`, `z` and `score`/`value` are promoted to queryable columns.
- Live list: `PORTAL/../mp/event-registry`.

## Limits / quotas (why students get 429)
- Each game has a **rate limit** (default ~60 events/minute, burst 600) and a **total
  storage cap** (default ~100 MB per game; ~250 MB across all a student's games).
- Over the rate limit OR storage cap → **HTTP 429**. Existing data is always preserved
  (the server never auto-deletes). The SDKs catch 429 and back off 60s automatically.
- Fixes: batch events (the SDK already does), log meaningful moments (deaths, level
  changes, scores) not every frame, put detail in params of ONE event rather than many
  events. Ask the instructor to raise the quota if genuinely needed.

## Troubleshooting
- **401 / "Invalid measurement_id or api_secret"** → wrong credentials. Re-copy from the
  dashboard, or rotate the secret and update the game.
- **403 / "Account has expired"** → the course access window has ended; contact the
  instructor.
- **403 on /api/v1/events or /api/v1/sessions** → those legacy endpoints are disabled in
  production; use `/mp/collect` (which the SDKs use). Nothing to fix in the SDK path.
- **429** → rate or storage limit; slow down / batch / request more quota.
- **No data showing** → ensure `start(...)`/`config(...)` ran BEFORE any `event(...)`,
  the server URL is correct, and the game actually fired events. Check the dashboard
  usage bar a few seconds after playing.
- **Lost api_secret** → use "Rotate secret" on the dashboard (old secret stops working).

## What the bot should NOT do
- Do not invent endpoints, parameters, or quota numbers beyond this document.
- Do not reveal other students' data or any secrets.
- If unsure, tell the student to check the portal docs page (`PORTAL/docs`) or ask the
  instructor. Keep answers short, practical, and include a code snippet when relevant.
