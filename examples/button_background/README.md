# Button Background Test

First milestone example: A button that changes background color.

## Goal

Prove the autonomous loop works end-to-end:

```
Coder → Tester → VisualVerifier → Success
```

## Files

- `test_project/` — Minimal Godot project
  - `project.godot` — Project config
  - `main.tscn` — Scene with button
  - `main.gd` — Button logic
- `test_autonomous.py` — Full automation script
- `screenshots/` — Output directory (created on run)

## Running

```bash
cd examples/button_background
python test_autonomous.py
```

## Expected Output

```
============================================================
OpenClaw-Godot: Button Background Test
============================================================

📋 Step 1: Implementing button feature...
✅ Code written

🎮 Step 2: Running test scenario...
   Project: Button Test
   Starting Godot...
   Capturing initial state...
   Clicking button...
   Capturing after click...
   Stopping Godot...
✅ Screenshots captured

👁️  Step 3: Visual verification...
   Before: RGB(0, 0, 128)
   After:  RGB(128, 0, 0)
   Difference: 256

✅ TEST PASSED
```

## Architecture

This example demonstrates:

1. **Direct file writing** — No MCP server needed
2. **Process automation** — Godot launched via Python
3. **Screenshot capture** — mss + xdotool for window
4. **Input injection** — PyAutoGUI clicks button
5. **Verification** — Pixel comparison (placeholder for VLM)

## Next Steps

- Replace pixel comparison with actual VLM call
- Extract reusable components to `godot_bridge`
- Add DiscordOrchestration worker distribution
