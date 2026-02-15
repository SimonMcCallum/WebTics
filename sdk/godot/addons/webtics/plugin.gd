@tool
extends EditorPlugin


func _enter_tree():
	# Add the autoload singleton
	add_autoload_singleton("WebTics", "res://addons/webtics/WebTics.gd")


func _exit_tree():
	# Remove the autoload singleton
	remove_autoload_singleton("WebTics")
