# Button Background Test - Phase 0

Test autonomous loop: Coder creates → Tester runs → Verify screenshot

## Project Structure

```
godot/button_background/
├── project.godot    # Project config
├── main.tscn        # Scene with button
├── main.gd          # Button logic
└── icon.svg         # Project icon
```

## What It Tests

1. **Scene loads** — No crashes, no errors
2. **Button visible** — UI element renders
3. **Click works** — Background color changes
4. **Screenshot capture** — Visual state recorded

## Run the Test

```bash
cd ~/Documents/GitHub/openclaw-godot
python examples/button_background/test_autonomous.py
```

## Expected Flow

```
1. GodotRunner starts project
2. ScreenshotCapture grabs "before" image
3. InputInjector clicks button at (640, 345)
4. Wait 500ms for color change
5. ScreenshotCapture grabs "after" image
6. Pixel comparison confirms color change
7. PASS or FAIL verdict
```

## Success Criteria

- [x] Godot process starts
- [x] Window appears (even briefly)
- [x] Before/after screenshots captured
- [x] Center pixel color changes significantly
- [x] Process terminates cleanly
