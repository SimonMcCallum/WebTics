# Add Analytics to Your Game — Student Handout

*Powered by **Ludogogy Logging** (the friendly name) / **WebTics** (the service). Uses
GA4-style named events, so what you learn here transfers to Google Analytics & Apple
App Analytics.*

Your instructor will give you the **portal URL** (e.g. `http://192.168.1.64:8013/app` on
the class network, or `https://analytics.<domain>/app`). Use that wherever you see
`PORTAL` below.

---

## 1. Claim your account
Your instructor emails you an **email** + a **temporary password**.
1. Go to `PORTAL/claim`.
2. Enter them, set your **own password**, and choose your **display name**.
3. Done — your access lasts for the duration of the course.

(Already claimed? Just log in at `PORTAL/login`.)

## 2. Register your game
On your **dashboard** (`PORTAL/dashboard`):
1. Enter a name + platform → **Register game**.
2. Copy the **`measurement_id`** (e.g. `WT-AB12CD34`) and **`api_secret`**.
   ⚠️ The secret is shown **once** — save it. Lost it? Use *Rotate secret*.

## 3a. Godot
1. Copy the `ludogogy_logging` addon into your project's `res://addons/`.
2. Enable it: **Project → Project Settings → Plugins**.
3. In your code:
```gdscript
func _ready():
    LudogogyLogging.start("WT-AB12CD34", "your-api-secret")   # add server URL as 3rd arg for local testing
    LudogogyLogging.event("level_start", { "level": 1 })

func _on_player_died():
    LudogogyLogging.event("player_death", { "x": position.x, "y": position.y })

func _on_level_complete(score):
    LudogogyLogging.event("level_up", { "level": 2 })
    LudogogyLogging.post_score(score)
```

## 3b. Web (HTML5 / JS)
```html
<script src="PORTAL/../sdk/webtics.js"></script>
<script>
  webtics('config', 'WT-AB12CD34', { api_secret: 'your-api-secret' });
  webtics('event', 'level_up', { level: 5, character: 'mage' });
</script>
```

## 4. See your data
Your dashboard shows **events stored** and a **storage usage bar** per game.

---

## Event names to use
Prefer these (GA4/Apple-aligned) so your skills transfer; any other name also works as a
**custom event**:

`session_start` · `session_end` · `screen_view` · `level_start` · `level_up` ·
`level_complete` · `level_failed` · `post_score` · `unlock_achievement` ·
`tutorial_begin` · `tutorial_complete` · `player_death` · `player_respawn` ·
`correct_response` · `incorrect_response`

Live list: `PORTAL/../mp/event-registry`.

## Limits (so the shared server doesn't fill up)
Each game has a **rate limit** (events/minute) and a **total storage cap**. If you exceed
them you get **HTTP 429** and the SDK automatically backs off — your existing data is kept
safe. Watch the usage bar; ask your instructor if you genuinely need more.

## Stuck?
- **401 / auth rejected** → wrong `measurement_id` or `api_secret`; re-check or rotate.
- **429** → you hit the rate or storage limit; slow down / batch fewer events.
- **Nothing arrives** → confirm you called `start(...)` before any `event(...)`, and that
  you're using the correct server URL.
- **Ask the Discord bot!** Type `/webtics <your question>` in the course Discord — it knows
  this service and can help.
