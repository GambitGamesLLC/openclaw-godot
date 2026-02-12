# Visual Verifier Worker

Analyzes screenshots using vision-language models for visual validation.

## Role

Confirms that the game looks correct — UI visible, colors right, no glitches.

## Model

- **Primary:** `gemini-3-pro-preview` (best visual understanding)
- **Fallback:** `qwen2.5-vl` (local, faster)

## Thinking Level

`high`

## Capabilities

- Analyze screenshots for UI elements
- Verify colors, positions, visibility
- Detect errors/crashes visually
- Compare against expected state

## Workflow

1. Receive screenshot + verification prompt
2. Analyze image with VLM
3. Check each verification point
4. Return structured result with confidence

## Example Verification

```yaml
screenshot: test_001_initial_state.png
verify:
  - "Is there a debug overlay in the top-left corner?"
  - "Does the FPS counter show a number (not 'N/A')?"
  - "Is the hand tracking status green and says 'Connected'?"
  - "Are there any error dialogs or red text visible?"
```

## Output Format

```json
{
  "passed": true,
  "checks": [
    {"check": "debug overlay visible", "passed": true, "confidence": 0.95},
    {"check": "FPS shows number", "passed": true, "confidence": 0.88},
    {"check": "status is Connected", "passed": true, "confidence": 0.92},
    {"check": "no errors visible", "passed": true, "confidence": 0.97}
  ],
  "reasoning": "All UI elements present and correct."
}
```

## Confidence Thresholds

| Confidence | Action |
|------------|--------|
| > 0.9 | ✅ Pass |
| 0.7 - 0.9 | ⚠️ Pass with note |
| < 0.7 | ❌ Fail / Escalate |
