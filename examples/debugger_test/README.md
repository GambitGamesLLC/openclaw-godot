# Debugger Output Test

Verifies that OpenClaw can capture debug-related output from Godot.

## What It Tests

- ✅ Debug mode output (`--debug` flag)
- ✅ Verbose logging
- ✅ Node lifecycle operations
- ✅ Performance-critical operations
- ✅ Runtime state information

## Files

- `main.gd` - Script with various runtime operations
- `test_debugger.py` - Python test that captures debug output

## Running

```bash
cd ~/Documents/GitHub/openclaw-godot
python3 examples/debugger_test/test_debugger.py
```

## Expected Output

```
============================================================
Debugger Output Test
============================================================

📁 Project: /home/derrick/.../godot/debugger_test
✓ Project: Debugger Test

🎮 Running with debug output enabled...

============================================================
CAPTURED OUTPUT:
============================================================

Stdout lines: 9
Stderr lines: 0

Godot Engine v4.6.stable.official.89cea1439...

DEBUGGER_TEST: Starting debugger visibility test
DEBUGGER_TEST: Null node check passed (no error thrown)
DEBUGGER_TEST: Created and queued 10 nodes for deletion
DEBUGGER_TEST: Updated label 100 times
DEBUGGER_TEST: Test completed
DEBUGGER_TEST: Exiting

Verification:
  ✅ Test started
  ✅ Null node check
  ✅ Node operations
  ✅ Loop operations
  ✅ Test completed
  ✅ Godot version

============================================================
✅ PASS: 6/6 debug checks passed
```

## Limitations

**Current implementation captures stdout/stderr only.**

Full debugger integration would require:
- Debug Adapter Protocol (DAP) implementation
- WebSocket connection to Godot Editor
- Breakpoint capture
- Stack trace inspection
- Variable inspection

This test demonstrates basic debug output capture. Advanced debugger features would need the Godot Editor Plugin (`src/plugin/`) with WebSocket communication.

## Use Case

This enables agents to:
1. Monitor runtime behavior
2. Detect performance issues
3. Track node lifecycle
4. Verify operations completed successfully
5. Report debug info for troubleshooting
