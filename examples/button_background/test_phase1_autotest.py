#!/usr/bin/env python3
"""
Phase 1 Test: Button That Changes Background (GDScript Auto-Test)

Uses built-in GDScript auto-test that clicks itself.
Avoids coordinate issues with external input tools.

This proves:
1. Godot starts with display
2. Auto-test script runs and clicks button
3. Screenshot captured after color change
4. Visual verification of result
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from godot_bridge import GodotProject, GodotRunner, ScreenshotCapture


def main():
    print("=" * 60)
    print("OpenClaw-Godot: Phase 1 - Auto-Test (GDScript)")
    print("=" * 60)
    
    # Setup paths
    repo_root = Path(__file__).parent.parent.parent
    project_path = repo_root / "godot" / "button_background"
    screenshot_path = repo_root / "test_outputs" / "button_background"
    screenshot_path.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📁 Project: {project_path}")
    print(f"📁 Screenshots: {screenshot_path}")
    
    # Initialize tools
    runner = GodotRunner()
    capture = ScreenshotCapture()
    
    # Verify Godot
    print("\n🔍 Checking Godot...")
    if not runner.verify_godot():
        print("❌ Godot not found")
        return 1
    print("✓ Godot found")
    
    # Load project
    print("\n📂 Loading project...")
    project = GodotProject(project_path)
    print(f"✓ {project.name}")
    
    # Run auto-test scene (with display)
    print("\n🎮 Running auto-test scene...")
    print("   (GDScript will auto-click button after 2 seconds)")
    process = runner.run_with_display(project, "main_auto_test.tscn")
    
    # Wait for test to complete
    print("   Waiting for auto-test (6s)...")
    time.sleep(6)
    
    # Capture result
    print("   Capturing result screenshot...")
    img_result = capture.capture_screen()
    path_result = screenshot_path / "phase1_autotest_result.png"
    capture.save_screenshot(img_result, path_result)
    print(f"   ✓ Saved: {path_result.name}")
    
    # Stop Godot
    print("   Stopping Godot...")
    result = runner.stop()
    print(f"   ✓ Exit code: {result['returncode']}")
    
    # Verify by screenshot color (since log capture has issues)
    print("\n📋 Verifying by screenshot color...")
    passed = verify_red_background(path_result)
    
    # Results
    print("\n" + "=" * 60)
    if passed:
        print("✅ PHASE 1 PASSED")
        print("\nFull autonomous loop working:")
        print("  ✓ Godot starts with auto-test scene")
        print("  ✓ GDScript auto-clicks button after 2s")
        print("  ✓ Background changes from BLUE to RED")
        print("  ✓ Screenshot captured showing RED background")
        print("  ✓ Visual verification confirms success")
    else:
        print("❌ PHASE 1 FAILED")
        print("\nScreenshot doesn't show red background")
    
    print(f"\n📸 Result: {path_result}")
    
    capture.close()
    return 0 if passed else 1


def verify_red_background(image_path: Path) -> bool:
    """Check if screenshot shows red background in Godot window."""
    from PIL import Image
    
    img = Image.open(image_path)
    
    # Sample from center area where Godot window should be
    # Based on observed window position ~ (1458, 675) with size ~ (640, 480)
    center_samples = [
        (1700, 850),  # Center of Godot window
        (1600, 800),  # Upper left of center
        (1800, 900),  # Lower right of center
    ]
    
    red_count = 0
    for x, y in center_samples:
        color = img.getpixel((x, y))
        r, g, b = color[0], color[1], color[2]
        
        # Check if red-dominant (red high, green and blue low)
        if r > 100 and r > g + 20 and r > b + 20:
            red_count += 1
            print(f"   ✓ Red pixel at ({x},{y}): RGB({r},{g},{b})")
        else:
            print(f"   ✗ Non-red at ({x},{y}): RGB({r},{g},{b})")
    
    # At least 2 of 3 samples should be red
    return red_count >= 2


if __name__ == "__main__":
    sys.exit(main())
