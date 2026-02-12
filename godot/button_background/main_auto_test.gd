extends Node2D

## Standalone auto-test - no dependencies on other scripts

var is_red := false
@onready var button: Button = $Button
@onready var status_label: Label = $StatusLabel

func _ready():
	print("AUTO-TEST: Starting...")
	status_label.text = "Waiting..."
	
	# Set initial blue background
	RenderingServer.set_default_clear_color(Color(0, 0, 0.5))  # Dark blue
	print("AUTO-TEST: Background set to BLUE")
	
	# Connect button
	button.pressed.connect(_on_button_pressed)
	
	# Wait then auto-click
	await get_tree().create_timer(2.0).timeout
	print("AUTO-TEST: Clicking button...")
	_on_button_pressed()
	
	# Wait for change
	await get_tree().create_timer(1.0).timeout
	
	# Check result
	var final_color = RenderingServer.get_default_clear_color()
	print("AUTO-TEST: Final color = ", final_color)
	
	if final_color.r > 0.3:  # Red component high
		print("✅ AUTO-TEST PASSED")
		status_label.text = "✅ TEST PASSED"
		status_label.modulate = Color.GREEN
	else:
		print("❌ AUTO-TEST FAILED")
		status_label.text = "❌ TEST FAILED"
		status_label.modulate = Color.RED
	
	# Keep open for screenshot
	await get_tree().create_timer(2.0).timeout

func _on_button_pressed():
	is_red = !is_red
	if is_red:
		RenderingServer.set_default_clear_color(Color(0.5, 0, 0))  # Dark red
		print("AUTO-TEST: Changed to RED")
		status_label.text = "RED"
	else:
		RenderingServer.set_default_clear_color(Color(0, 0, 0.5))  # Dark blue
		print("AUTO-TEST: Changed to BLUE")
		status_label.text = "BLUE"
