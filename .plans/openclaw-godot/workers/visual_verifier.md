# Worker: Visual Verifier

## Role

Analyzes screenshots using vision-language models to verify visual correctness.

## Model

- **Primary:** `gemini-3-pro-preview` (best vision understanding)
- **Fallback:** `qwen2.5-vl` (local, faster for simple checks)

## Thinking Level

`high` (visual reasoning requires more tokens)

## Inputs

- Screenshot(s) as image files
- Verification prompt describing what to check

## Workflow

```yaml
input:
  screenshot_path: "/tmp/test_123_initial_state.png"
  verification_prompt: |
    Verify that:
    1. The debug overlay is visible in the top-left corner
    2. The FPS counter shows a number (not "N/A")
    3. The hand tracking status shows "Connected" (green text)
    4. No error messages are visible on screen
    
    Return a JSON object:
    {
      "passed": boolean,
      "checks": [
        {"check": "debug overlay visible", "passed": boolean, "confidence": 0-1},
        ...
      ],
      "reasoning": "explain what you observed"
    }

steps:
  1. Load screenshot image
  2. Analyze using VLM with verification prompt
  3. Parse structured response
  4. Return pass/fail per check

output:
  passed: true
  checks:
    - check: "debug overlay visible"
      passed: true
      confidence: 0.95
    - check: "FPS counter shows number"
      passed: true
      confidence: 0.88
    - check: "hand tracking status is Connected"
      passed: true
      confidence: 0.92
    - check: "no error messages visible"
      passed: true
      confidence: 0.97
  reasoning: "The debug overlay is clearly visible in the top-left with all expected elements. FPS shows 60, status shows 'Connected' in green. No error dialogs or red text visible."
```

## Prompt Template

```markdown
You are a visual QA engineer analyzing a screenshot from a Godot game.

Analyze this screenshot and answer the following questions:
{verification_prompt}

Be precise. If you're unsure about something, indicate low confidence.
Return your analysis as structured JSON.
```

## Common Verification Patterns

### UI Element Presence
```yaml
prompt: "Is there a button labeled 'Start Game' in the center of the screen?"
```

### Color Verification
```yaml
prompt: "What is the background color? Is it approximately #1a1a2e (dark blue)?"
```

### Text Verification
```yaml
prompt: "Read the text in the top-left corner. Does it say 'Score: 100'?"
```

### Object Detection
```yaml
prompt: "Is the player character (red square) visible on the platform?"
```

### Error Detection
```yaml
prompt: "Are there any error dialogs, red text, or crash messages visible?"
```

## Confidence Thresholds

| Confidence | Action |
|------------|--------|
| > 0.9 | ✅ Pass |
| 0.7 - 0.9 | ⚠️ Pass with note |
| < 0.7 | ❌ Fail / Escalate to human |
