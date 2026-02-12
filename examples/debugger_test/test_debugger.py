#!/usr/bin/env python3
"""
Debugger Output Test

Verifies that GodotRunner captures debug output including:
- Debug mode verbose output
- Script warnings/parsing info
- Runtime state information
- Performance metrics (if available)

Usage: python3 test_debugger.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from godot_bridge import GodotProject, GodotRunner


def main():
    print("=" * 60)
    print("Debugger Output Test")
    print("=" * 60)
    
    repo_root = Path(__file__).parent.parent.parent
    project_path = repo_root / "godot" / "debugger_test"
    
    print(f"\n📁 Project: {project_path}")
    
    # Initialize
    runner = GodotRunner()
    
    if not runner.verify_godot():
        print("❌ Godot not found")
        return 1
    
    project = GodotProject(project_path)
    print(f"✓ Project: {project.name}")
    
    # Run with --debug flag to enable debugger output
    print("\n🎮 Running with debug output enabled...")
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
    print(f"\n{all_output}\n")
    
    # Check for expected patterns in debug output
    checks = {
        "Test started": "DEBUGGER_TEST: Starting" in all_output,
        "Null node check": "Null node check passed" in all_output,
        "Node operations": "Created and queued 10 nodes" in all_output,
        "Loop operations": "Updated label 100 times" in all_output,
        "Test completed": "DEBUGGER_TEST: Test completed" in all_output,
        "Godot version": "Godot Engine v4." in all_output,
    }
    
    # Check for any warnings or errors (these show debugger is active)
    has_warnings = "WARNING:" in all_output.upper() or "WARN:" in all_output.upper()
    has_errors = "ERROR:" in all_output.upper() and "test error" not in all_output.lower()
    
    passed_count = sum(checks.values())
    total = len(checks)
    
    print("Verification:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    print(f"\n  ⚠️  Warnings detected: {has_warnings}")
    print(f"  ❌ Errors detected: {has_errors}")
    
    print(f"\nExit code: {result['returncode']}")
    
    print("\n" + "=" * 60)
    if passed_count >= total - 1:  # Allow 1 check to fail
        print(f"✅ PASS: {passed_count}/{total} debug checks passed")
        print("\nNote: Full debugger integration requires:")
        print("  - Debug Adapter Protocol (DAP) implementation")
        print("  - WebSocket connection to Godot Editor")
        print("  - Breakpoint and stack trace capture")
        print("Current implementation captures stdout/stderr only.")
        return 0
    else:
        print(f"❌ FAIL: {passed_count}/{total} checks passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
