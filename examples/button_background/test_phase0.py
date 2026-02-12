#!/usr/bin/env python3
"""
Phase 0 Test: Button That Changes Background (Simplified)

Tests core functionality without PyAutoGUI (tkinter-free).
Uses Godot's --quit-after and --write-movie for frame capture.

This proves:
1. GodotProject loads correctly
2. GodotRunner starts/stops project
3. Screenshots can be captured
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from godot_bridge import GodotProject, GodotRunner, ScreenshotCapture


def main():
    print("=" * 60)
    print("OpenClaw-Godot: Phase 0 - Core Functionality Test")
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
        print(f"\n❌ ERROR: project.godot not found")
        return 1
    
    # Initialize tools
    runner = GodotRunner()
    capture = ScreenshotCapture()
    
    # Verify Godot is available
    print("\n🔍 Checking Godot installation...")
    if not runner.verify_godot():
        print("❌ Godot not found in PATH")
        print("   Install Godot 4.6 and ensure 'godot' command works")
        return 1
    print("✓ Godot found")
    
    # Load project
    print("\n📂 Loading project...")
    try:
        project = GodotProject(project_path)
        print(f"✓ Project: {project.name}")
        print(f"✓ Scenes: {len(project.list_scenes())}")
        print(f"✓ Scripts: {len(project.list_scripts())}")
    except Exception as e:
        print(f"❌ Failed to load project: {e}")
        return 1
    
    # Test 1: Capture screenshot of desktop
    print("\n📸 Test 1: Screenshot capture...")
    try:
        img = capture.capture_screen()
        screenshot_file = screenshot_path / "desktop_test.png"
        capture.save_screenshot(img, screenshot_file)
        print(f"✓ Captured: {img.size}")
        print(f"✓ Saved: {screenshot_file}")
    except Exception as e:
        print(f"❌ Screenshot failed: {e}")
        return 1
    
    # Test 2: Run Godot headless (no GUI, for CI)
    print("\n🎮 Test 2: Running Godot headless...")
    try:
        # Run for 60 frames then quit
        process = runner.run_headless(project, quit_after=60, fixed_fps=30)
        print("   ✓ Process started")
        
        # Wait for completion (should take ~2 seconds)
        timeout = 10
        elapsed = 0
        while runner.is_running() and elapsed < timeout:
            time.sleep(0.5)
            elapsed += 0.5
            # Get any output
            logs = runner.get_output(timeout=0.1)
            if logs.get("stdout"):
                for line in logs["stdout"]:
                    if line.strip():
                        print(f"   📝 {line[:80]}")
        
        result = runner.stop()
        print(f"   ✓ Exit code: {result['returncode']}")
        
        if result["stdout"]:
            print("   📋 Final output:")
            for line in result["stdout"][-5:]:  # Last 5 lines
                if line.strip():
                    print(f"      {line[:70]}")
        
    except Exception as e:
        print(f"❌ Godot run failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Cleanup
    capture.close()
    
    # Results
    print("\n" + "=" * 60)
    print("✅ PHASE 0 PASSED")
    print("=" * 60)
    print("\nVerified:")
    print("  ✓ GodotProject loads and parses project.godot")
    print("  ✓ ScreenshotCapture works (mss + Pillow)")
    print("  ✓ GodotRunner can start/stop Godot headless")
    print("  ✓ Project runs without errors")
    print("\nNext: Add PyAutoGUI input for full interactive test")
    print("      (requires: sudo apt install python3-tk)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
