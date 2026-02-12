#!/usr/bin/env python3
"""
Phase 1 Test: Button That Changes Background (Interactive)

Tests full autonomous loop with input injection via xdotool.
Works without tkinter/PyAutoGUI.

This proves:
1. Godot starts with display
2. Button click via xdotool
3. Screenshot before/after
4. Color change verification
"""

import sys
import subprocess
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from godot_bridge import GodotProject, GodotRunner, ScreenshotCapture


def main():
    print("=" * 60)
    print("OpenClaw-Godot: Phase 1 - Interactive Button Test")
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
    
    # Run with display
    print("\n🎮 Starting Godot with display...")
    process = runner.run_with_display(project, "main.tscn")
    
    # Wait for window to appear and stabilize
    print("   Waiting for window (4s)...")
    time.sleep(4)
    
    # Focus the Godot window first
    print("   Focusing Godot window...")
    focus_window("Button Background Test")
    time.sleep(0.5)
    
    # Capture "before"
    print("   Capturing BEFORE screenshot...")
    img_before = capture.capture_screen()
    path_before = screenshot_path / "phase1_before.png"
    capture.save_screenshot(img_before, path_before)
    print(f"   ✓ Saved: {path_before.name}")
    
    # Click button via xdotool (relative to window or screen coordinates)
    print("   Clicking button via xdotool...")
    # Try to find window and click relative to it
    click_result = click_in_window("Button Background Test", 640, 345)
    if not click_result:
        print("   ⚠️ Window-relative click failed, trying absolute coordinates...")
        click_result = click_at(640, 345)
    
    if not click_result:
        print("   ⚠️ All click methods failed")
    
    # Wait longer for color change to propagate and render
    print("   Waiting for color change (1s)...")
    time.sleep(1)
    
    # Capture "after"
    print("   Capturing AFTER screenshot...")
    img_after = capture.capture_screen()
    path_after = screenshot_path / "phase1_after.png"
    capture.save_screenshot(img_after, path_after)
    print(f"   ✓ Saved: {path_after.name}")
    
    # Stop Godot
    print("   Stopping Godot...")
    result = runner.stop()
    print(f"   ✓ Exit code: {result['returncode']}")
    
    # Verify
    print("\n👁️  Verifying color change...")
    passed = verify_color_change(path_before, path_after)
    
    # Results
    print("\n" + "=" * 60)
    if passed:
        print("✅ PHASE 1 PASSED")
        print("\nFull autonomous loop working:")
        print("  ✓ Godot starts with display")
        print("  ✓ Input injection (xdotool)")
        print("  ✓ Before/after screenshots")
        print("  ✓ Color change verified")
    else:
        print("❌ PHASE 1 FAILED")
        print("\nScreenshots captured but color didn't change")
        print("  (check screenshots to debug)")
    
    print(f"\n📸 Before: {path_before}")
    print(f"📸 After:  {path_after}")
    
    capture.close()
    return 0 if passed else 1


def focus_window(title_substring: str) -> bool:
    """Focus window by title substring."""
    try:
        # Find window ID
        result = subprocess.run(
            ["xdotool", "search", "--name", title_substring],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0 or not result.stdout.strip():
            return False
        
        window_id = result.stdout.strip().split("\n")[0]
        
        # Activate/focus window
        subprocess.run(
            ["xdotool", "windowactivate", window_id],
            check=True,
            timeout=5,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"   Focus failed: {e}")
        return False


def click_in_window(title_substring: str, x: int, y: int) -> bool:
    """Click at coordinates relative to window."""
    try:
        # Find window ID
        result = subprocess.run(
            ["xdotool", "search", "--name", title_substring],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0 or not result.stdout.strip():
            return False
        
        window_id = result.stdout.strip().split("\n")[0]
        
        # Get window geometry
        geo_result = subprocess.run(
            ["xdotool", "getwindowgeometry", window_id],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse position from output
        # Format: Window 1234567
        #   Position: 100,200 (screen: 0)
        win_x, win_y = 0, 0
        for line in geo_result.stdout.split("\n"):
            if "Position:" in line:
                # Extract "100,200" part
                pos_part = line.split("Position:")[1].split("(")[0].strip()
                coords = pos_part.split(",")
                win_x = int(coords[0])
                win_y = int(coords[1])
                break
        
        # Click at absolute position (window pos + relative pos)
        abs_x = win_x + x
        abs_y = win_y + y
        
        print(f"   Window at ({win_x}, {win_y}), clicking at ({abs_x}, {abs_y})")
        
        subprocess.run(
            ["xdotool", "mousemove", str(abs_x), str(abs_y), "click", "1"],
            check=True,
            timeout=5,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"   Window click failed: {e}")
        return False


def click_at(x: int, y: int) -> bool:
    """Click at absolute screen coordinates using xdotool."""
    try:
        subprocess.run(
            ["xdotool", "mousemove", str(x), str(y), "click", "1"],
            check=True,
            timeout=5,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"   Absolute click failed: {e}")
        return False


def verify_color_change(before: Path, after: Path) -> bool:
    """Verify background color changed."""
    from PIL import Image
    
    img_before = Image.open(before)
    img_after = Image.open(after)
    
    # Sample from left side (background, not UI)
    samples = [(200, 360), (320, 240), (320, 480)]
    
    total_diff = 0
    for x, y in samples:
        color_before = img_before.getpixel((x, y))
        color_after = img_after.getpixel((x, y))
        diff = sum(abs(a - b) for a, b in zip(color_before[:3], color_after[:3]))
        total_diff += diff
        print(f"   Pixel ({x},{y}): {color_before} → {color_after} (diff: {diff})")
    
    avg_diff = total_diff / len(samples)
    print(f"   Average difference: {avg_diff:.1f}")
    
    return avg_diff > 100


if __name__ == "__main__":
    sys.exit(main())
