#!/usr/bin/env python3
"""
Console Log Capture Test

Verifies that GodotRunner can capture stdout/stderr including:
- print() statements
- push_warning() messages  
- push_error() messages
- Multi-line output

Usage: python3 test_console_log.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from godot_bridge import GodotProject, GodotRunner


def main():
    print("=" * 60)
    print("Console Log Capture Test")
    print("=" * 60)
    
    repo_root = Path(__file__).parent.parent.parent
    project_path = repo_root / "godot" / "console_log_test"
    
    print(f"\n📁 Project: {project_path}")
    
    # Initialize
    runner = GodotRunner()
    
    if not runner.verify_godot():
        print("❌ Godot not found")
        return 1
    
    project = GodotProject(project_path)
    print(f"✓ Project: {project.name}")
    
    # Run headless and capture ALL output
    print("\n🎮 Running test (capturing logs)...")
    runner.run_headless(project, quit_after=120, fixed_fps=30)
    
    # Wait for completion
    import time
    time.sleep(5)
    
    result = runner.stop()
    
    print("\n" + "=" * 60)
    print("CAPTURED OUTPUT:")
    print("=" * 60)
    
    # Combine stdout and stderr from result
    all_output = "\n".join(result.get("stdout", []) + result.get("stderr", []))
    
    print(f"\nStdout lines: {len(result.get('stdout', []))}")
    print(f"Stderr lines: {len(result.get('stderr', []))}")
    
    # Check for expected content in combined output
    checks = {
        "TEST_START": "TEST_START" in all_output,
        "INFO message": "INFO: Scene loaded" in all_output,
        "DEBUG message": "DEBUG: Player position" in all_output,
        "WARNING message": "WARNING: This is a test warning" in all_output,
        "ERROR message": "ERROR: This is a test error" in all_output,
        "LOOP iterations": all_output.count("LOOP: Iteration") >= 3,
        "TEST_COMPLETE": "TEST_COMPLETE" in all_output,
    }
    
    passed_count = sum(checks.values())
    total = len(checks)
    
    print(f"\nCombined Output:\n{all_output}\n")
    
    print("Verification:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    print(f"\nExit code: {result['returncode']}")
    
    print("\n" + "=" * 60)
    if passed_count == total:
        print(f"✅ PASS: All {total} log checks passed")
        return 0
    else:
        print(f"❌ FAIL: {passed_count}/{total} checks passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
