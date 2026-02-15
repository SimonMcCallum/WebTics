# WebTics Godot SDK

Lightweight telemetry and metrics system for Godot games.

## Installation

1. Copy the `addons/webtics` folder to your Godot project's `addons/` directory
2. Enable the plugin in Project Settings → Plugins
3. The `WebTics` singleton will be automatically available

## Quick Start

```gdscript
extends Node

func _ready():
	# Configure backend URL
	WebTics.configure("http://localhost:8000")

	# Open metric session (unique player ID and build version)
	WebTics.open_metric_session("player_123", "1.0.0")

	# Wait for session to be created
	await WebTics.session_created

	# Start a play session
	WebTics.start_play_session()
	await WebTics.play_session_created

	# Log events
	WebTics.log_event(
		EventTypes.Type.TASK_START,
		EventTypes.AssessmentSubtype.REACTION_TIME
	)

	# Log event with position and magnitude
	WebTics.log_event(
		EventTypes.Type.BUTTON_CLICK,
		EventTypes.UISubtype.PLAY_BUTTON,
		100, 200, 0,  # x, y, z coordinates
		1.5,          # magnitude (e.g., reaction time)
		{"level": 1}  # additional data
	)

	# Close sessions when done
	WebTics.close_play_session()
	WebTics.close_metric_session()
```

## Event Types

See [EventTypes.gd](EventTypes.gd) for predefined event types.

Common event types:
- `EventTypes.Type.PLAYER_DEATH` - Player death
- `EventTypes.Type.BUTTON_CLICK` - UI interaction
- `EventTypes.Type.TASK_START` - Assessment task started
- `EventTypes.Type.CORRECT_RESPONSE` - Correct answer given
- `EventTypes.Type.ATTENTION_TASK` - ADHD assessment event

## Signals

Connect to these signals for async feedback:

```gdscript
func _ready():
	WebTics.session_created.connect(_on_session_created)
	WebTics.error_occurred.connect(_on_error)

func _on_session_created(session_id: int):
	print("Session created: ", session_id)

func _on_error(error_message: String):
	print("Error: ", error_message)
```

## API Reference

### configure(url: String)
Set the backend URL.

### open_metric_session(unique_id: String, build_number: String = "")
Create a new metric session. Emits `session_created` signal.

### close_metric_session()
Close the current metric session.

### start_play_session()
Start a new play session within the current metric session. Emits `play_session_created` signal.

### close_play_session()
Close the current play session.

### log_event(event_type: int, event_subtype: int = 0, x: int = 0, y: int = 0, z: int = 0, magnitude: float = 0.0, data: Dictionary = {})
Log a single telemetry event.

### log_events_batch(events: Array)
Log multiple events in a single request (more efficient).

## License

MIT License - See LICENSE file for details
