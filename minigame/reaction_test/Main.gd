extends Control
## Reaction Time Test Minigame
##
## Simple ADHD assessment game that measures reaction time and accuracy.
## Logs all interactions to WebTics for analysis.

@onready var target_button: Button = $VBoxContainer/CenterContainer/TargetButton
@onready var start_button: Button = $VBoxContainer/StartButton
@onready var status_label: Label = $VBoxContainer/StatusLabel
@onready var score_label: Label = $VBoxContainer/ScoreLabel

## Game state
var is_playing: bool = false
var trial_count: int = 0
var max_trials: int = 10
var correct_clicks: int = 0
var task_start_time: int = 0

## WebTics configuration
var player_id: String = "test_player_%d" % Time.get_unix_time_from_system()
var build_version: String = "0.1.0"


func _ready():
	# Configure WebTics
	WebTics.configure("http://localhost:8013")

	# Connect signals
	WebTics.session_created.connect(_on_session_created)
	WebTics.play_session_created.connect(_on_play_session_created)
	WebTics.error_occurred.connect(_on_webtics_error)

	# Connect UI signals
	start_button.pressed.connect(_on_start_button_pressed)
	target_button.pressed.connect(_on_target_clicked)

	# Initialize UI
	target_button.visible = false
	status_label.text = "Click 'Start Test' to begin"
	score_label.text = "Score: 0 / 0"

	# Open metric session
	WebTics.open_metric_session(player_id, build_version)


func _on_session_created(session_id: int):
	print("WebTics session created: ", session_id)
	start_button.disabled = false


func _on_play_session_created(play_session_id: int):
	print("WebTics play session created: ", play_session_id)


func _on_webtics_error(error_message: String):
	push_error("WebTics error: " + error_message)
	status_label.text = "Telemetry error: " + error_message
	status_label.add_theme_color_override("font_color", Color.RED)


func _on_start_button_pressed():
	if is_playing:
		return

	# Start play session
	WebTics.start_play_session()
	await WebTics.play_session_created

	# Log test start
	WebTics.log_event(
		EventTypes.Type.TASK_START,
		EventTypes.AssessmentSubtype.REACTION_TIME,
		0, 0, 0, 0.0,
		{"test_type": "reaction_time", "max_trials": max_trials}
	)

	# Reset game state
	is_playing = true
	trial_count = 0
	correct_clicks = 0
	start_button.disabled = true

	# Start first trial
	_start_trial()


func _start_trial():
	if trial_count >= max_trials:
		_end_game()
		return

	trial_count += 1
	status_label.text = "Trial %d/%d - Click the target!" % [trial_count, max_trials]
	score_label.text = "Score: %d / %d" % [correct_clicks, trial_count - 1]

	# Random delay before showing target
	var delay = randf_range(1.0, 3.0)
	await get_tree().create_timer(delay).timeout

	# Show target at random position
	_show_target()

	# Record task start time
	task_start_time = Time.get_ticks_msec()

	# Log trial start
	WebTics.log_event(
		EventTypes.Type.ATTENTION_TASK,
		0,
		target_button.position.x,
		target_button.position.y,
		0, 0.0,
		{"trial": trial_count, "delay": delay}
	)


func _show_target():
	# Random position within safe bounds
	var margin = 100
	var x = randi_range(margin, int(get_viewport_rect().size.x) - margin - 200)
	var y = randi_range(margin + 100, int(get_viewport_rect().size.y) - margin - 100)

	target_button.position = Vector2(x, y)
	target_button.visible = true

	# Auto-hide after 2 seconds (timeout condition)
	await get_tree().create_timer(2.0).timeout
	if target_button.visible:
		_on_target_timeout()


func _on_target_clicked():
	if not is_playing or not target_button.visible:
		return

	# Calculate reaction time
	var reaction_time = (Time.get_ticks_msec() - task_start_time) / 1000.0

	# Hide target
	target_button.visible = false

	# Log correct response
	correct_clicks += 1
	WebTics.log_event(
		EventTypes.Type.CORRECT_RESPONSE,
		EventTypes.AssessmentSubtype.REACTION_TIME,
		target_button.position.x,
		target_button.position.y,
		0,
		reaction_time,
		{
			"trial": trial_count,
			"reaction_time_ms": reaction_time * 1000,
			"accuracy": "correct"
		}
	)

	# Short feedback delay
	await get_tree().create_timer(0.5).timeout

	# Next trial
	_start_trial()


func _on_target_timeout():
	if not target_button.visible:
		return

	target_button.visible = false

	# Log timeout (no response)
	WebTics.log_event(
		EventTypes.Type.TIMEOUT,
		EventTypes.AssessmentSubtype.REACTION_TIME,
		0, 0, 0, 2.0,
		{
			"trial": trial_count,
			"accuracy": "timeout"
		}
	)

	# Next trial
	await get_tree().create_timer(0.5).timeout
	_start_trial()


func _end_game():
	is_playing = false
	target_button.visible = false

	# Calculate accuracy
	var accuracy = (float(correct_clicks) / float(max_trials)) * 100.0

	# Log test completion
	WebTics.log_event(
		EventTypes.Type.TASK_COMPLETE,
		EventTypes.AssessmentSubtype.REACTION_TIME,
		0, 0, 0,
		accuracy,
		{
			"total_trials": max_trials,
			"correct": correct_clicks,
			"accuracy_percent": accuracy
		}
	)

	# Close play session
	WebTics.close_play_session()

	# Update UI
	status_label.text = "Test Complete! Accuracy: %.1f%%" % accuracy
	score_label.text = "Final Score: %d / %d" % [correct_clicks, max_trials]
	start_button.disabled = false
	start_button.text = "Start New Test"


func _exit_tree():
	# Close metric session on exit
	if WebTics.is_session_active:
		WebTics.close_metric_session()
