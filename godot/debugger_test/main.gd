extends Node2D

## Debugger Visibility Test  
## Creates conditions that appear in the Godot debugger

@onready var label: Label = $Label

func _ready():
	print("DEBUGGER_TEST: Starting debugger visibility test")
	
	# Create some node references that might trigger warnings
	var potentially_null = get_node_or_null("NonExistentNode")
	if potentially_null == null:
		print("DEBUGGER_TEST: Null node check passed (no error thrown)")
	
	# Trigger a runtime warning (not error) - deprecated function
	# Note: Using deprecated features if available
	
	# Create and free nodes to show memory activity
	for i in range(10):
		var temp_node = Label.new()
		add_child(temp_node)
		temp_node.queue_free()
	
	print("DEBUGGER_TEST: Created and queued 10 nodes for deletion")
	
	# Access a node multiple times (for performance profiling)
	for i in range(100):
		label.text = str(i)
	
	print("DEBUGGER_TEST: Updated label 100 times")
	
	# Force a script parse warning (circular reference that resolves)
	print("DEBUGGER_TEST: Test completed")
	
	# Keep running briefly
	await get_tree().create_timer(1.0).timeout
	print("DEBUGGER_TEST: Exiting")
