# Ludogogy Logging (Godot)

**Easy, GA4-style game analytics for students.** Add gameplay logging to your Godot
project in two lines. Ludogogy Logging is the friendly student front-end to the
**WebTics** service — the same named-event model you'll later use in Google Analytics 4
and Apple App Analytics, so your skills transfer when you leave university.

> 🌿 **WebTics** is the professional version: simple, self-hosted analytics for New Zealand
> game developers who want their data kept **local** and running on **green energy**. Same
> API, same plugin — just point it at your own WebTics instance.

## Install

1. Copy the `ludogogy_logging` folder into your project's `res://addons/` directory.
2. Enable it in **Project → Project Settings → Plugins**.
3. That adds a `LudogogyLogging` autoload you can call from anywhere.

## Use

```gdscript
func _ready():
    # measurement_id + api_secret come from your dashboard at the course portal.
    LudogogyLogging.start("WT-XXXXXXXX", "your-api-secret")

    LudogogyLogging.event("level_start", { "level": 1 })

func _on_level_complete(score):
    LudogogyLogging.event("level_up", { "level": 2 })
    LudogogyLogging.post_score(score)   # convenience helper

func _on_player_died():
    LudogogyLogging.event("player_death", { "x": position.x, "y": position.y })
```

For local testing against a dev backend, pass a URL:

```gdscript
LudogogyLogging.start("WT-XXXXXXXX", "secret", "http://localhost:8013")
```

## Recommended event names

Use these GA4/Apple-aligned names where they fit so your analytics knowledge ports to
the paid tools (any other name also works — it's stored as a custom event):

`session_start`, `session_end`, `screen_view`, `level_start`, `level_up`, `level_complete`,
`level_failed`, `post_score`, `unlock_achievement`, `tutorial_begin`, `tutorial_complete`,
`player_death`, `player_respawn`, `purchase`, `correct_response`, `incorrect_response`.

The live list is always at `<your-server>/mp/event-registry`.

## How it behaves

- Events are **queued** and flushed in batches every few seconds (no frame hitches).
- Special params `x`, `y`, `z` and `score`/`value` are promoted to queryable columns.
- If you hit your game's **rate** or **storage** limit, the SDK receives a `429`, backs
  off for 60s, and keeps your events queued. Watch your usage on the dashboard.
- A stable `client_id` is stored in `user://` so a player's events group together.

Connect to the `flushed(ok, detail)` signal if you want to surface send status while
developing.
