# Student Quickstart — Add Analytics to Your Game

Welcome! This guide gets gameplay analytics into your game in about five minutes. The
student-facing brand is **Ludogogy Logging**; under the hood it's the **WebTics** service.
Everything uses **GA4-style named events**, so the skills transfer to Google Analytics and
Apple App Analytics after you graduate.

> The portal lives at the URL your instructor gives you (e.g. `https://analytics.<domain>/app`).

---

## 1. Claim your account

Your instructor emails you an **email** and a **temporary password**.

1. Go to **`/app/claim`**.
2. Enter your email + temp password, pick a **new password**, and choose your **display name**
   (this is you "claiming your name").
3. You're in. Your access stays active for the length of the course and expires automatically
   afterwards.

> Already claimed? Just log in at **`/app/login`**.

---

## 2. Register your game

On your **dashboard** (`/app/dashboard`):

1. Enter a game name + platform, click **Register game**.
2. You'll receive a **`measurement_id`** (public, like `WT-AB12CD34`) and an **`api_secret`**
   (your write key). **The secret is shown once** — copy it now. If you lose it, use
   *Rotate secret*.

This is the same model as a Google Analytics property + API secret.

---

## 3a. Godot (recommended for class)

1. Copy the **`ludogogy_logging`** addon into your project's `res://addons/` folder.
2. Enable it: **Project → Project Settings → Plugins**.
3. Use the `LudogogyLogging` autoload:

```gdscript
func _ready():
    LudogogyLogging.start("WT-AB12CD34", "your-api-secret")
    LudogogyLogging.event("level_start", { "level": 1 })

func _on_enemy_killed(pos):
    LudogogyLogging.event("player_shoot", { "x": pos.x, "y": pos.y })

func _on_level_complete(score):
    LudogogyLogging.event("level_up", { "level": 2 })
    LudogogyLogging.post_score(score)
```

For local testing add the URL: `LudogogyLogging.start(id, secret, "http://localhost:8013")`.

---

## 3b. Web games (HTML5 / JavaScript)

```html
<script src="https://analytics.<domain>/sdk/webtics.js"></script>
<script>
  webtics('config', 'WT-AB12CD34', { api_secret: 'your-api-secret' });

  webtics('event', 'level_up', { level: 5, character: 'mage' });
  webtics('event', 'post_score', { score: 1280 });
</script>
```

It looks and behaves like `gtag()` — because that's the point.

---

## 4. See your data

Back on the dashboard you'll see **events stored** and a **storage usage bar** per game.
Events also flow into the existing WebTics dashboard/queries (`x`, `y`, `z`, and
`score`/`value` parameters become queryable columns automatically).

---

## Event names to use

Prefer these GA4/Apple-aligned names where they fit (full list at `/mp/event-registry`):

| Category | Names |
|---|---|
| Lifecycle | `session_start`, `session_end`, `screen_view` |
| Progression | `level_start`, `level_up`, `level_complete`, `level_failed`, `post_score`, `unlock_achievement` |
| Tutorial | `tutorial_begin`, `tutorial_complete` |
| Player | `player_death`, `player_respawn`, `player_shoot`, `player_hit` |
| Assessment | `correct_response`, `incorrect_response`, `timeout` |

Any other name works too — it's stored as a **custom event** with your name preserved.

---

## Limits (don't fill the disk!)

Each game has a **rate limit** (events/minute) and a **total storage cap**. If you exceed
them the server replies **HTTP 429** and the SDK backs off automatically — your existing data
is always kept. Watch the usage bar; email your instructor if you genuinely need more.
See [Quotas_and_Limits.md](Quotas_and_Limits.md).
