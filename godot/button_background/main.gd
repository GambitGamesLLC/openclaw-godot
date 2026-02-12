extends Node2D

var is_red := false

@onready var button: Button = $Button
@onready var status_label: Label = $StatusLabel

func _ready():
	print("✓ Main scene ready")
	button.pressed.connect(_on_button_pressed)
	_update_status()
	
	# Start with blue background
	RenderingServer.set_default_clear_color(Color.DARK_BLUE)
	print("✓ Background set to BLUE")

func _on_button_pressed():
	is_red = !is_red
	
	if is_red:
		RenderingServer.set_default_clear_color(Color.DARK_RED)
		print("✓ Background changed to RED")
	else:
		RenderingServer.set_default_clear_color(Color.DARK_BLUE)
		print("✓ Background changed to BLUE")
	
	_update_status()

func _update_status():
	if is_red:
		status_label.text = "Status: RED"
		status_label.modulate = Color.RED
	else:
		status_label.text = "Status: BLUE"
		status_label.modulate = Color.BLUE
