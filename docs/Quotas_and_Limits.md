# Quotas & Limits

To keep a shared teaching server healthy — and stop one runaway `_process()` loop from
filling the disk — every registered game has two independent limits.

## 1. Rate limit (events per minute)

A DB-backed **fixed-window** counter (`usage_counters`, one row per game per minute) counts
incoming events. The effective ceiling per minute is `max(rate_per_min, burst)` so legitimate
**batch flushes** are allowed while sustained spam is rejected.

- Exceed it → **HTTP 429** with a `Retry-After: 60` header.
- The SDKs (Godot + web) catch the 429, **back off 60 seconds**, and keep events queued.

No Redis required — the counter lives in PostgreSQL and survives restarts.

## 2. Total storage cap (bytes per game)

Each game has `max_bytes`. Before any write the server estimates the batch size
(serialized payload + a fixed per-row overhead) and checks `bytes_used + incoming ≤ max_bytes`.

- Exceed it → **HTTP 429**, and **nothing is written**.
- **Existing data is preserved** (we never auto-delete — important for research integrity).
- The student sees a clear "storage quota exceeded" message and can delete old data, or ask
  the instructor to raise the cap.

`bytes_used` and `events_stored` are denormalised counters on the `games` row, so quota checks
and the dashboard usage bars are cheap (no `COUNT(*)` over millions of events).

## Default tier ("Modest")

| Scope | Limit |
|---|---|
| Per game — rate | **60 events/min** (burst **600**) |
| Per game — storage | **100 MB** (~500k events) |
| Per student — storage (all games) | **250 MB** |

Defaults come from environment variables (see `.env.example`):
`WEBTICS_DEFAULT_RATE_PER_MIN`, `WEBTICS_DEFAULT_BURST`, `WEBTICS_DEFAULT_MAX_BYTES`,
`WEBTICS_DEFAULT_USER_MAX_BYTES`.

## Per-game overrides (instructor)

Raise or lower any game's limits without redeploying:

- **Admin UI:** *(planned in the admin page)* or
- **API:** `PATCH /api/v1/admin/games/{game_id}/quota`
  ```json
  { "rate_per_min": 300, "burst": 1000, "max_bytes": 524288000 }
  ```

## Monitoring disk pressure

`GET /api/v1/admin/usage` (and the **Server usage** panel on `/app/admin`) lists every game
sorted by storage used, with totals — your first stop if the server disk starts filling.

## Tips for students to stay under limits

- **Batch** events (the SDKs already do) instead of one HTTP request per event.
- Don't log every frame — log **meaningful moments** (deaths, level changes, scores).
- Put high-frequency detail in **parameters** of one event rather than many events.
