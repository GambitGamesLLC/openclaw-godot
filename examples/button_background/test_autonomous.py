"""
Autonomous Test: Button That Changes Background

This example demonstrates the full OpenClaw-Godot loop:
1. Coder implements a button
2. Tester runs the scene and clicks it
3. VisualVerifier confirms background color changed
4. All without human intervention

Usage:
    cd examples/button_background
    python test_autonomous.py

Expected: PASS with green checkmark at end
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from godot_bridge import GodotProject, GodotRunner, ScreenshotCapture, InputInjector


def main():
    print("=" * 60)
    print("OpenClaw-Godot: Button Background Test")
    print("=" * 60)
    
    # Setup paths
    project_path = Path(__file__).parent / "test_project"
    screenshot_path = Path(__file__).parent / "screenshots"
    screenshot_path.mkdir(exist_ok=True)
    
    # Step 1: Implement feature
    print("\n📋 Step 1: Implementing button feature...")
    implement_button(project_path)
    print("✅ Code written")
    
    # Step 2: Run and test
    print("\n🎮 Step 2: Running test scenario...")
    screenshot_before, screenshot_after = run_test(project_path, screenshot_path)
    print(f"✅ Screenshots captured")
    
    # Step 3: Visual verification (placeholder - would use VLM)
    print("\n👁️  Step 3: Visual verification...")
    result = verify_screenshots(screenshot_before, screenshot_after)
    
    if result:
        print("\n✅ TEST PASSED")
        return 0
    else:
        print("\n❌ TEST FAILED")
        return 1


def implement_button(project_path: Path) -> None:
    """Create a Godot project with a button that changes background."""
    
    # Create project directory
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Create project.godot
    project_godot = """[gd_scene load_steps=2 format=3 uid="uid://testproject"]

[application]
config/name="Button Test"
run/main_scene="res://main.tscn"
config/features=["4.2"]
"""
    (project_path / "project.godot").write_text(project_godot)
    
    # Create main.gd script
    main_gd = '''extends Node2D

var is_red = false

func _ready():
    print("Main scene ready")
    $Button.pressed.connect(_on_button_pressed)
    # Start with blue background
    RenderingServer.set_default_clear_color(Color.DARK_BLUE)

func _on_button_pressed():
    is_red = !is_red
    if is_red:
        RenderingServer.set_default_clear_color(Color.DARK_RED)
        print("Background changed to RED")
    else:
        RenderingServer.set_default_clear_color(Color.DARK_BLUE)
        print("Background changed to BLUE")
'''
    (project_path / "main.gd").write_text(main_gd)
    
    # Create main.tscn
    main_tscn = '''[gd_scene load_steps=2 format=3 uid="uid://mainscene"]

[ext_resource type="Script" path="res://main.gd" id="1_script"]

[node name="Main" type="Node2D"]
script = ExtResource("1_script")

[node name="Button" type="Button" parent="."]
offset_left = 440.0
offset_top = 280.0
offset_right = 640.0
offset_bottom = 330.0
text = "Change Color"
'''
    (project_path / "main.tscn").write_text(main_tscn)


def run_test(project_path: Path, screenshot_path: Path) -> tuple[Path, Path]:
    """Run Godot and capture before/after screenshots."""
    
    import subprocess
    import time
    
    # Initialize tools
    runner = GodotRunner()
    capture = ScreenshotCapture()
    input_ctl = InputInjector()
    
    # Load project
    project = GodotProject(project_path)
    print(f"   Project: {project.name}")
    
    # Run with display
    print("   Starting Godot...")
    process = runner.run_with_display(project, "main.tscn")
    
    # Wait for window to appear
    time.sleep(3)
    
    # Capture "before" screenshot
    print("   Capturing initial state...")
    img_before = capture.capture_window("Godot")
    path_before = screenshot_path / "before.png"
    capture.save_screenshot(img_before, path_before)
    
    # Click the button (center of 440,280 to 640,330)
    print("   Clicking button...")
    button_x = 540  # (440 + 640) / 2
    button_y = 305  # (280 + 330) / 2
    input_ctl.click(button_x, button_y)
    
    # Wait for color change
    time.sleep(0.5)
    
    # Capture "after" screenshot
    print("   Capturing after click...")
    img_after = capture.capture_window("Godot")
    path_after = screenshot_path / "after.png"
    capture.save_screenshot(img_after, path_after)
    
    # Stop Godot
    print("   Stopping Godot...")
    runner.stop()
    
    # Cleanup
    capture.close()
    
    return path_before, path_after


def verify_screenshots(before: Path, after: Path) -> bool:
    """Verify that background color changed.
    
    In a real implementation, this would use a VLM (Gemini, etc).
    For now, we do a simple pixel comparison.
    """
    from PIL import Image
    
    img_before = Image.open(before)
    img_after = Image.open(after)
    
    # Sample pixel from center (should be background color)
    center_x = img_before.width // 2
    center_y = img_before.height // 2
    
    color_before = img_before.getpixel((center_x, center_y))
    color_after = img_after.getpixel((center_x, center_y))
    
    print(f"   Before: RGB{color_before}")
    print(f"   After:  RGB{color_after}")
    
    # Check if colors are different (they should be)
    difference = sum(abs(a - b) for a, b in zip(color_before, color_after))
    print(f"   Difference: {difference}")
    
    # In a real test, use VLM:
    # result = vlm_verify(after, "Is the background red?")
    
    return difference > 100  # Arbitrary threshold


if __name__ == "__main__":
    sys.exit(main())
