extends Node
class_name EventTypes
## Event type definitions for WebTics telemetry
##
## Defines standard event types and subtypes for common game events.
## Extend these enumerations for custom events in your game.

## Main event categories
enum Type {
	PLAYER_DEATH = 0,
	PLAYER_RESPAWN = 1,
	PLAYER_SHOOT = 2,
	PLAYER_HIT = 3,

	# Navigation events
	WAYPOINT_REACHED = 10,
	LEVEL_COMPLETE = 11,
	LEVEL_FAILED = 12,

	# UI events
	BUTTON_CLICK = 20,
	MENU_OPEN = 21,
	MENU_CLOSE = 22,

	# Assessment events (for therapeutic/educational games)
	TASK_START = 100,
	TASK_COMPLETE = 101,
	CORRECT_RESPONSE = 102,
	INCORRECT_RESPONSE = 103,
	TIMEOUT = 104,

	# ADHD assessment specific
	ATTENTION_TASK = 200,
	IMPULSIVE_RESPONSE = 201,
	SUSTAINED_ATTENTION = 202,
	SELECTIVE_ATTENTION = 203,

	# Custom events
	CUSTOM = 1000
}

## Subtypes for player death
enum DeathSubtype {
	ENEMY = 0,
	FALLING = 1,
	ENVIRONMENT = 2,
	SELF = 3
}

## Subtypes for UI interaction
enum UISubtype {
	PLAY_BUTTON = 0,
	QUIT_BUTTON = 1,
	SETTINGS = 2,
	PAUSE = 3,
	RESUME = 4
}

## Subtypes for assessment tasks
enum AssessmentSubtype {
	GO_TASK = 0,
	NO_GO_TASK = 1,
	REACTION_TIME = 2,
	ACCURACY = 3
}
