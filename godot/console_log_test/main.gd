extends Node2D

## Console Log Test
## Outputs various log types for verification

func _ready():
	print("TEST_START: Console log test beginning")
	
	# Regular prints
	print("INFO: Scene loaded successfully")
	print("DEBUG: Player position: ", Vector2(100, 200))
	
	# Warnings
	push_warning("WARNING: This is a test warning message")
	
	# Errors (non-fatal)
	push_error("ERROR: This is a test error message")
	
	# Multiple prints
	for i in range(3):
		print("LOOP: Iteration ", i)
	
	# Completion marker
	print("TEST_COMPLETE: All log messages emitted")
	
	# Keep running briefly then exit
	await get_tree().create_timer(1.0).timeout
	print("TEST_EXIT: Exiting test")
