@tool
extends EditorPlugin
## Ludogogy Logging — editor plugin entry point.
##
## Registers the LudogogyLogging autoload singleton so students can call
## LudogogyLogging.event(...) from anywhere in their game.

const AUTOLOAD_NAME := "LudogogyLogging"
const AUTOLOAD_PATH := "res://addons/ludogogy_logging/LudogogyLogging.gd"


func _enter_tree() -> void:
	add_autoload_singleton(AUTOLOAD_NAME, AUTOLOAD_PATH)


func _exit_tree() -> void:
	remove_autoload_singleton(AUTOLOAD_NAME)
