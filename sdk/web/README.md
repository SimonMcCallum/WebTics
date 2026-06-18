# WebTics Web SDK (`webtics.js`)

A tiny, dependency-free, **gtag-style** analytics client for browser games. The API
deliberately mirrors Google Analytics 4 so the skills students build transfer to GA4 and
Apple App Analytics.

> The canonical copy is served by the backend at **`/sdk/webtics.js`** — students should
> load it from the live server so updates ship automatically. This file in `sdk/web/` is
> the source mirror.

## Usage

```html
<script src="https://analytics.example.nz/sdk/webtics.js"></script>
<script>
  // measurement_id + api_secret come from your dashboard.
  webtics('config', 'WT-XXXXXXXX', { api_secret: 'your-api-secret' });

  webtics('event', 'level_up', { level: 5, character: 'mage' });
  webtics('event', 'post_score', { score: 1280 });
</script>
```

`base_url` defaults to the origin that served the script; override it for local testing:

```js
webtics('config', 'WT-XXXXXXXX', { api_secret: '...', base_url: 'http://localhost:8013' });
```

## Behaviour

- Buffers events and flushes in batches (default every 5s / 50 events).
- Uses `navigator.sendBeacon` on tab-hide so the last batch isn't lost.
- On HTTP `429` (rate or storage limit) it backs off 60s and keeps events queued.
- Persists a `client_id` in `localStorage` so a player's events group together.

See the recommended event names at `<server>/mp/event-registry`.
