extends Node
## Ludogogy Logging — friendly GA4-style analytics for your Godot game.
##
## The student-facing front door to the WebTics service. You send *named events*
## with a dictionary of parameters — exactly like Google Analytics 4 (gtag) and Apple
## App Analytics — so the skills you build here carry over to those paid tools.
##
## Quick start (after enabling the plugin, this node is the `LudogogyLogging` autoload):
##
##     func _ready():
##         LudogogyLogging.start("WT-XXXXXXXX", "your-api-secret")
##         LudogogyLogging.event("level_start", { "level": 1 })
##
##     func _on_player_died():
##         LudogogyLogging.event("player_death", { "x": position.x, "y": position.y })
##
## Events are queued and flushed in batches to keep your game smooth, and the SDK
## automatically backs off if you hit the server's rate or storage limit.

## Emitted after each flush. `ok` is false if the server rejected the batch.
signal flushed(ok: bool, detail: String)

# --- Configuration ----------------------------------------------------------
var base_url: String = "https://analytics.ludogogy.co.nz"
var measurement_id: String = ""
var api_secret: String = ""

## A stable per-install id (the GA4 "client_id"): groups all of a player's events.
var client_id: String = ""

## How often (seconds) the queue is flushed, and the max events per batch.
@export var flush_interval: float = 5.0
@export var max_batch: int = 50

var _queue: Array = []
var _http: HTTPRequest
var _timer: Timer
var _in_flight: bool = false
var _backoff_until: float = 0.0
var _started: bool = false


func _ready() -> void:
	_http = HTTPRequest.new()
	add_child(_http)
	_http.request_completed.connect(_on_request_completed)

	_timer = Timer.new()
	_timer.wait_time = flush_interval
	_timer.autostart = false
	_timer.timeout.connect(flush)
	add_child(_timer)

	client_id = _load_or_make_client_id()


## Begin a logging session. Call once, e.g. in your main scene's _ready().
## `url` is optional — override only for local testing.
func start(p_measurement_id: String, p_api_secret: String, url: String = "") -> void:
	measurement_id = p_measurement_id
	api_secret = p_api_secret
	if url != "":
		base_url = url.trim_suffix("/")
	_started = true
	_timer.start()
	# A first event helps you confirm the wiring immediately.
	event("session_start", {})


## Log a named event with optional parameters.
## Prefer GA4/Apple names where they fit (see the docs) so your skills transfer.
func event(name: String, params: Dictionary = {}) -> void:
	if not _started:
		push_warning("[LudogogyLogging] event() called before start(); ignored.")
		return
	_queue.append({ "name": name, "params": params })
	if _queue.size() >= max_batch:
		flush()


## Convenience helpers mirroring common GA4 game events.
func level_up(level: int) -> void:
	event("level_up", { "level": level })


func post_score(score: float) -> void:
	event("post_score", { "score": score })


## Send everything queued right now (also called automatically on a timer).
func flush() -> void:
	if _queue.is_empty() or _in_flight:
		return
	if Time.get_unix_time_from_system() < _backoff_until:
		return  # honouring server rate/storage backoff

	var batch := _queue.slice(0, max_batch)
	var body := {
		"client_id": client_id,
		"events": batch,
	}
	var url := "%s/mp/collect?measurement_id=%s&api_secret=%s" % [
		base_url, measurement_id.uri_encode(), api_secret.uri_encode()
	]
	var headers := ["Content-Type: application/json"]
	var err := _http.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(body))
	if err == OK:
		_in_flight = true
		_pending_count = batch.size()
	else:
		emit_signal("flushed", false, "request failed to start")


var _pending_count: int = 0


func _on_request_completed(result: int, code: int, _headers, response_body: PackedByteArray) -> void:
	_in_flight = false
	if code == 200 or code == 204:
		# Remove the events we successfully sent.
		_queue = _queue.slice(_pending_count)
		emit_signal("flushed", true, "")
	elif code == 429:
		# Rate or storage limit — back off for a minute, keep the events queued.
		_backoff_until = Time.get_unix_time_from_system() + 60.0
		emit_signal("flushed", false, "rate/storage limit (429) — backing off 60s")
	elif code == 401 or code == 403:
		emit_signal("flushed", false, "auth rejected (%d) — check measurement_id / api_secret" % code)
	else:
		emit_signal("flushed", false, "server error (%d)" % code)


func _load_or_make_client_id() -> String:
	var path := "user://ludogogy_client_id.txt"
	if FileAccess.file_exists(path):
		var f := FileAccess.open(path, FileAccess.READ)
		if f:
			var existing := f.get_as_text().strip_edges()
			if existing != "":
				return existing
	var new_id := "%d.%d" % [Time.get_unix_time_from_system(), randi()]
	var w := FileAccess.open(path, FileAccess.WRITE)
	if w:
		w.store_string(new_id)
	return new_id
