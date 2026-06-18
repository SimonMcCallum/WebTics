# GA4 & Apple Analytics Compatibility

WebTics' student interface is intentionally shaped like **Google Analytics 4 (GA4)** and
**Apple App Analytics** so the skills students learn transfer to those paid services. This
document explains the mapping.

## The shared mental model

All three systems share the same core idea:

> An **event** has a **name** and a bag of **parameters**. A **client_id** identifies the
> player/device so their events group into a session.

```
GA4 (gtag):    gtag('event', 'level_up', { level: 5 });
GA4 (MP):      POST /mp/collect  { client_id, events:[{ name, params }] }
Apple:         logEvent("level_up", parameters: ["level": 5])
WebTics web:   webtics('event', 'level_up', { level: 5 });
WebTics Godot: LudogogyLogging.event("level_up", { "level": 5 })
```

## The endpoint

`POST /mp/collect?measurement_id=WT-XXXX&api_secret=...`

```json
{
  "client_id": "1736.91823",
  "user_id": "optional",
  "events": [
    { "name": "level_up", "params": { "level": 5, "character": "mage" } },
    { "name": "post_score", "params": { "score": 1280 } }
  ]
}
```

This mirrors the **GA4 Measurement Protocol** (`measurement_id` + `api_secret` query params,
a `client_id`, and an `events[]` array of `{name, params}`). Success returns `200`/`204`.

## How names map internally

WebTics stores events in its existing `Event` table (integer `event_type`/`event_subtype`).
A registry (`backend/app/event_registry.py`) maps GA4 names to those codes; unknown names go
to the **custom** bucket (`event_type = 1000`). **Nothing is lost** — the original name and the
full `params` map are always stored in the event's `data` JSON.

Common parameters are *also* promoted into typed columns so existing dashboards/queries work:

| Param key | Becomes column |
|---|---|
| `x`, `y`, `z` | `x`, `y`, `z` (integer) |
| `value`, `score`, `magnitude`, `reaction_time_ms`, `amount` | `magnitude` (float) |

## Recommended event names

The canonical list is served live at **`/mp/event-registry`**. It covers GA4 "recommended
events for games" (`level_start`, `level_up`, `post_score`, `unlock_achievement`,
`tutorial_begin/complete`, `purchase`, `ad_impression`, …) plus WebTics' research/assessment
events.

## What's deliberately *not* identical

- WebTics is **self-hosted** — your data stays on the university/NZ server, not Google's.
- There's no Google tag manager, consent-mode, or BigQuery export — but the **event-authoring
  experience** is the same, which is what transfers.
- `api_secret` is required (the teaching server runs with `ALLOW_ANON_INGEST=false`).

## Moving to the real GA4 later

When you ship a commercial game and adopt GA4, your event-naming and parameter design carries
over directly: swap the `webtics(...)` calls for `gtag(...)` (or the Firebase Analytics SDK),
point at your GA4 property, and your analytics plan still makes sense.
