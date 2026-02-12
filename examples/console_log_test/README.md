# Console Log Test

Verifies that OpenClaw can capture Godot's console output (stdout/stderr).

## What It Tests

- ✅ `print()` statements
- ✅ `push_warning()` messages  
- ✅ `push_error()` messages
- ✅ Loop output
- ✅ Multi-line logs

## Files

- `main.gd` - Script that outputs various log types
- `test_console_log.py` - Python test that captures and verifies logs

## Running

```bash
cd ~/Documents/GitHub/openclaw-godot
python3 examples/console_log_test/test_console_log.py
```

## Expected Output

```
============================================================
Console Log Capture Test
============================================================

📁 Project: /home/derrick/.../godot/console_log_test
✓ Project: Console Log Test

🎮 Running test (capturing logs)...

============================================================
CAPTURED OUTPUT:
============================================================

Stdout lines: 11
Stderr lines: 9

Combined Output:
Godot Engine v4.6.stable.official.89cea1439...

TEST_START: Console log test beginning
INFO: Scene loaded successfully
DEBUG: Player position: (100.0, 200.0)
LOOP: Iteration 0
LOOP: Iteration 1
LOOP: Iteration 2
TEST_COMPLETE: All log messages emitted
TEST_EXIT: Exiting test

WARNING: WARNING: This is a test warning message
...
ERROR: ERROR: This is a test error message
...

Verification:
  ✅ TEST_START
  ✅ INFO message
  ✅ DEBUG message
  ✅ WARNING message
  ✅ ERROR message
  ✅ LOOP iterations
  ✅ TEST_COMPLETE

============================================================
✅ PASS: All 7 log checks passed
```

## Key Insight

Godot outputs:
- `print()` → stdout
- `push_warning()` → stderr (with stack trace)
- `push_error()` → stderr (with stack trace)

Both streams are captured and combined for verification.

## Use Case

This enables autonomous testing where agents can:
1. Run Godot tests
2. Capture console output
3. Verify expected log messages appeared
4. Detect errors/warnings automatically
5. Report results without human intervention
