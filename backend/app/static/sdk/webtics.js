/*!
 * WebTics web SDK — a gtag-style analytics client for browser games.
 *
 * Deliberately mirrors Google Analytics 4's `gtag()` shape so the skills students build
 * here transfer to GA4 / Apple analytics:
 *
 *   <script src="https://analytics.example.nz/sdk/webtics.js"></script>
 *   <script>
 *     webtics('config', 'WT-XXXXXXXX', { api_secret: '...', base_url: 'https://...' });
 *     webtics('event', 'level_up', { level: 5, character: 'mage' });
 *   </script>
 *
 * Events are buffered and flushed in batches; a 429 (rate or storage limit) triggers a
 * 60-second backoff while keeping queued events. No external dependencies.
 */
(function (global) {
  var cfg = {
    measurement_id: null,
    api_secret: null,
    base_url: null,          // defaults to the origin that served this script
    flush_interval_ms: 5000,
    max_batch: 50,
  };
  var queue = [];
  var clientId = null;
  var backoffUntil = 0;
  var timer = null;
  var inFlight = false;

  function scriptOrigin() {
    try {
      var s = document.currentScript || document.querySelector('script[src*="webtics.js"]');
      if (s && s.src) return new URL(s.src).origin;
    } catch (e) {}
    return global.location ? global.location.origin : "";
  }

  function loadClientId() {
    try {
      var id = global.localStorage.getItem("webtics_client_id");
      if (!id) {
        id = Date.now() + "." + Math.floor(Math.random() * 1e9);
        global.localStorage.setItem("webtics_client_id", id);
      }
      return id;
    } catch (e) {
      return Date.now() + "." + Math.floor(Math.random() * 1e9);
    }
  }

  function config(measurementId, opts) {
    opts = opts || {};
    cfg.measurement_id = measurementId;
    cfg.api_secret = opts.api_secret || null;
    cfg.base_url = (opts.base_url || scriptOrigin()).replace(/\/$/, "");
    if (opts.flush_interval_ms) cfg.flush_interval_ms = opts.flush_interval_ms;
    if (opts.max_batch) cfg.max_batch = opts.max_batch;
    clientId = loadClientId();
    if (!timer) timer = setInterval(flush, cfg.flush_interval_ms);
    // Best-effort flush when the tab is hidden/closed.
    global.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") flush(true);
    });
    event("session_start", {});
  }

  function event(name, params) {
    if (!cfg.measurement_id) {
      console.warn("[webtics] call webtics('config', ...) before sending events");
      return;
    }
    queue.push({ name: name, params: params || {} });
    if (queue.length >= cfg.max_batch) flush();
  }

  function flush(useBeacon) {
    if (!queue.length || inFlight) return;
    if (Date.now() < backoffUntil) return;
    if (!cfg.measurement_id || !cfg.api_secret) return;

    var batch = queue.slice(0, cfg.max_batch);
    var url = cfg.base_url + "/mp/collect?measurement_id=" +
      encodeURIComponent(cfg.measurement_id) + "&api_secret=" + encodeURIComponent(cfg.api_secret);
    var payload = JSON.stringify({ client_id: clientId, events: batch });

    // On page-hide use sendBeacon so the final batch isn't dropped.
    if (useBeacon && global.navigator && navigator.sendBeacon) {
      var ok = navigator.sendBeacon(url, new Blob([payload], { type: "application/json" }));
      if (ok) queue = queue.slice(batch.length);
      return;
    }

    inFlight = true;
    fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: payload })
      .then(function (res) {
        inFlight = false;
        if (res.ok) {
          queue = queue.slice(batch.length);
        } else if (res.status === 429) {
          backoffUntil = Date.now() + 60000; // rate/storage limit — keep events, back off
          console.warn("[webtics] rate/storage limit hit (429); backing off 60s");
        } else if (res.status === 401 || res.status === 403) {
          console.error("[webtics] auth rejected (" + res.status + ") — check measurement_id/api_secret");
        }
      })
      .catch(function () { inFlight = false; });
  }

  // gtag-style dispatcher: webtics('config'|'event', ...)
  function webtics(command) {
    var args = Array.prototype.slice.call(arguments, 1);
    if (command === "config") return config(args[0], args[1]);
    if (command === "event") return event(args[0], args[1]);
    console.warn("[webtics] unknown command: " + command);
  }

  webtics.flush = flush;
  global.webtics = global.webtics || webtics;
})(typeof window !== "undefined" ? window : this);
