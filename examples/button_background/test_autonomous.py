#!/usr/bin/env python3
"""
Phase 0 Test: Button That Changes Background

Proves the autonomous loop works end-to-end:
1. Start Godot project
2. Capture "before" screenshot
3. Click button via PyAutoGUI
4. Capture "after" screenshot
5. Verify color changed

Usage:
    python test_autonomous.py

Expected: PASS with green checkmark at end
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from godot_bridge import GodotProject, GodotRunner, ScreenshotCapture, InputInjector


def main():
    print("=" * 60)
    print("OpenClaw-Godot: Phase 0 - Button Background Test")
    print("=" * 60)
    
    # Setup paths
    repo_root = Path(__file__).parent.parent.parent
    project_path = repo_root / "godot" / "button_background"
    screenshot_path = repo_root / "test_outputs" / "button_background"
    screenshot_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Project: {project_path}")
    print(f"📁 Screenshots: {screenshot_path}")
    
    # Verify project exists
    if not (project_path / "project.godot").exists():
        print(f"\n❌ ERROR: project.godot not found at {project_path}")
        return 1
    
    # Step 1: Run the test scenario
    print("\n🎮 Running test scenario...")
    try:
        screenshot_before, screenshot_after = run_test(project_path, screenshot_path)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 2: Visual verification (pixel-based for Phase 0)
    print("\n👁️  Verifying screenshots...")
    result = verify_color_change(screenshot_before, screenshot_after)
    
    # Results
    print("\n" + "=" * 60)
    if result:
        print("✅ TEST PASSED - Color changed as expected")
        print(f"📸 Before: {screenshot_before}")
        print(f"📸 After:  {screenshot_after}")
        return 0
    else:
        print("❌ TEST FAILED - Color did not change")
        print(f"📸 Before: {screenshot_before}")
        print(f"📸 After:  {screenshot_after}")
        return 1


def run_test(project_path: Path, screenshot_path: Path) -> tuple[Path, Path]:
    """Run Godot and capture before/after screenshots."""
    
    # Initialize tools
    runner = GodotRunner()
    capture = ScreenshotCapture()
    input_ctl = InputInjector()
    
    # Verify Godot is available
    if not runner.verify_godot():
        raise RuntimeError("Godot not found in PATH. Install Godot 4.6 and ensure 'godot' command works.")
    
    # Load project
    project = GodotProject(project_path)
    print(f"   ✓ Project loaded: {project.name}")
    
    # Run with display
    print("   Starting Godot (this may take 2-3 seconds)...")
    process = runner.run_with_display(project, "main.tscn")
    
    # Wait for window to appear and render
    print("   Waiting for window...")
    time.sleep(3)
    
    # Capture "before" screenshot
    print("   Capturing initial state...")
    img_before = capture.capture_screen()  # Use full screen for reliability
    path_before = screenshot_path / "before.png"
    capture.save_screenshot(img_before, path_before)
    print(f"   ✓ Saved: {path_before.name}")
    
    # Click the button (center of Button node: 540+100, 320+25)
    button_x = 640
    button_y = 345
    print(f"   Clicking button at ({button_x}, {button_y})...")
    input_ctl.click(button_x, button_y)
    
    # Wait for color change
    time.sleep(0.5)
    
    # Capture "after" screenshot
    print("   Capturing after click...")
    img_after = capture.capture_screen()
    path_after = screenshot_path / "after.png"
    capture.save_screenshot(img_after, path_after)
    print(f"   ✓ Saved: {path_after.name}")
    
    # Stop Godot
    print("   Stopping Godot...")
    result = runner.stop()
    print(f"   ✓ Exit code: {result['returncode']}")
    
    # Cleanup
    capture.close()
    
    return path_before, path_after


def verify_color_change(before: Path, after: Path) -> bool:
    """Verify that background color changed between screenshots.
    
    Phase 0 uses simple pixel comparison. Future phases will use VLM.
    """
    from PIL import Image
    
    img_before = Image.open(before)
    img_after = Image.open(after)
    
    # Sample pixels from center-left area (background, not UI)
    # Use multiple samples for robustness
    samples = [
        (200, 360),  # Left middle
        (320, 240),  # Upper left quadrant
        (320, 480),  # Lower left quadrant
    ]
    
    total_difference = 0
    for x, y in samples:
        color_before = img_before.getpixel((x, y))
        color_after = img_after.getpixel((x, y))
        
        # Calculate RGB difference
        diff = sum(abs(a - b) for a, b in zip(color_before[:3], color_after[:3]))
        total_difference += diff
        print(f"   Pixel ({x},{y}): {color_before} → {color_after} (diff: {diff})")
    
    avg_difference = total_difference / len(samples)
    print(f"   Average difference: {avg_difference:.1f}")
    
    # Threshold: significant color change should be > 50 per channel average
    return avg_difference > 100


if __name__ == "__main__":
    sys.exit(main())
