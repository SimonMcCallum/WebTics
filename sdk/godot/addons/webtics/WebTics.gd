extends Node
## WebTics Telemetry SDK for Godot
##
## Lightweight telemetry and metrics system for game analytics.
## Provides async event logging with automatic session management.
##
## Usage:
##   WebTics.configure("http://localhost:8013")
##   WebTics.open_metric_session("player_123", "1.0.0")
##   WebTics.start_play_session()
##   WebTics.log_event(EventTypes.Type.PLAYER_DEATH, EventTypes.DeathSubtype.FALLING)
##   WebTics.close_play_session()
##   WebTics.close_metric_session()

## Signals for async operations
signal session_created(session_id: int)
signal play_session_created(play_session_id: int)
signal event_logged(success: bool)
signal error_occurred(error_message: String)

## Configuration
var base_url: String = "http://localhost:8013"
var api_version: String = "v1"

## Session state
var metric_session_id: int = -1
var play_session_id: int = -1
var is_session_active: bool = false
var is_play_session_active: bool = false

## HTTP client
var http_client: HTTPRequest

## Event queue for offline support (future enhancement)
var event_queue: Array = []


func _ready():
	# Create HTTP client
	http_client = HTTPRequest.new()
	add_child(http_client)
	http_client.request_completed.connect(_on_request_completed)


## Configure the WebTics backend URL
func configure(url: String) -> void:
	base_url = url.trim_suffix("/")
	print("[WebTics] Configured with base URL: ", base_url)


## Open a new metric session
func open_metric_session(unique_id: String, build_number: String = "") -> void:
	if is_session_active:
		push_warning("[WebTics] Session already active. Close existing session first.")
		return

	var url = "%s/api/%s/sessions" % [base_url, api_version]
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({
		"unique_id": unique_id,
		"build_number": build_number
	})

	print("[WebTics] Opening metric session for: ", unique_id)
	var err = http_client.request(url, headers, HTTPClient.METHOD_POST, body)
	if err != OK:
		error_occurred.emit("Failed to create session: " + str(err))


## Close the current metric session
func close_metric_session() -> void:
	if not is_session_active:
		push_warning("[WebTics] No active session to close.")
		return

	if is_play_session_active:
		close_play_session()

	var url = "%s/api/%s/sessions/%d/close" % [base_url, api_version, metric_session_id]
	var headers = ["Content-Type: application/json"]

	print("[WebTics] Closing metric session: ", metric_session_id)
	http_client.request(url, headers, HTTPClient.METHOD_POST, "")

	is_session_active = false
	metric_session_id = -1


## Start a new play session
func start_play_session() -> void:
	if not is_session_active:
		push_error("[WebTics] Cannot start play session without active metric session.")
		return

	if is_play_session_active:
		push_warning("[WebTics] Play session already active.")
		return

	var url = "%s/api/%s/play-sessions" % [base_url, api_version]
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({
		"metric_session_id": metric_session_id
	})

	print("[WebTics] Starting play session for metric session: ", metric_session_id)
	http_client.request(url, headers, HTTPClient.METHOD_POST, body)


## Close the current play session
func close_play_session() -> void:
	if not is_play_session_active:
		push_warning("[WebTics] No active play session to close.")
		return

	var url = "%s/api/%s/play-sessions/%d/close" % [base_url, api_version, play_session_id]
	var headers = ["Content-Type: application/json"]

	print("[WebTics] Closing play session: ", play_session_id)
	http_client.request(url, headers, HTTPClient.METHOD_POST, "")

	is_play_session_active = false
	play_session_id = -1


## Log a single event
func log_event(
	event_type: int,
	event_subtype: int = 0,
	x: int = 0,
	y: int = 0,
	z: int = 0,
	magnitude: float = 0.0,
	data: Dictionary = {}
) -> void:
	if not is_play_session_active:
		push_error("[WebTics] Cannot log event without active play session.")
		return

	var url = "%s/api/%s/events?play_session_id=%d" % [base_url, api_version, play_session_id]
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify({
		"event_type": event_type,
		"event_subtype": event_subtype,
		"x": x,
		"y": y,
		"z": z,
		"magnitude": magnitude,
		"data": data if data.size() > 0 else null
	})

	http_client.request(url, headers, HTTPClient.METHOD_POST, body)


## Log multiple events in a batch
func log_events_batch(events: Array) -> void:
	if not is_play_session_active:
		push_error("[WebTics] Cannot log events without active play session.")
		return

	var url = "%s/api/%s/events/batch?play_session_id=%d" % [base_url, api_version, play_session_id]
	var headers = ["Content-Type: application/json"]
	var body = JSON.stringify(events)

	http_client.request(url, headers, HTTPClient.METHOD_POST, body)


## HTTP request completion handler
func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS:
		error_occurred.emit("HTTP request failed: " + str(result))
		return

	if response_code >= 400:
		var error_msg = body.get_string_from_utf8()
		error_occurred.emit("Server error %d: %s" % [response_code, error_msg])
		return

	# Parse response
	var json = JSON.new()
	var parse_result = json.parse(body.get_string_from_utf8())
	if parse_result != OK:
		error_occurred.emit("Failed to parse response JSON")
		return

	var response = json.data

	# Handle different response types
	if response.has("unique_id"):
		# Metric session created
		metric_session_id = response["id"]
		is_session_active = true
		session_created.emit(metric_session_id)
		print("[WebTics] Metric session created: ", metric_session_id)

	elif response.has("metric_session_id") and not response.has("status"):
		# Play session created
		play_session_id = response["id"]
		is_play_session_active = true
		play_session_created.emit(play_session_id)
		print("[WebTics] Play session created: ", play_session_id)

	elif response.has("status"):
		# Session closed or event logged
		print("[WebTics] Operation completed: ", response.get("status", "success"))

	elif response.has("event_type"):
		# Single event logged
		event_logged.emit(true)

	elif response.has("events_logged"):
		# Batch events logged
		print("[WebTics] Batch logged: ", response["events_logged"], " events")
		event_logged.emit(true)
