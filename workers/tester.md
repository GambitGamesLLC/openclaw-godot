# Tester Worker

Runs Godot projects, executes scenarios, captures output and screenshots.

## Role

Validates that code changes work as expected through automated testing.

## Model

- **Primary:** `kimi-k2.5`
- **Fallback:** `gemini-3-pro-preview` (complex test analysis)

## Thinking Level

`medium`

## Capabilities

- Run projects (headless or with display)
- Inject keyboard/mouse input
- Capture screenshots at key moments
- Collect and analyze logs
- Execute multi-step test scenarios

## Workflow

1. Start project
2. Execute test steps
3. Capture state (screenshots, logs)
4. Evaluate assertions
5. Return pass/fail with evidence

## Example Scenario

```yaml
project: ~/Projects/AeroBeat/.testbed
scenario:
  name: "Hand tracking connection"
  steps:
    - action: run_project
      scene: test_scene.tscn
    - action: wait
      duration: 3.0
      for: server_ready
    - action: capture_screenshot
      name: initial_state
    - action: press_key
      key: space
    - action: wait
      duration: 1.0
    - action: capture_screenshot
      name: after_input
    - action: stop_project
  assertions:
    - log_contains: "Server started"
    - no_errors: true
```

## Success Criteria

- All steps execute without error
- Assertions pass
- Screenshots captured
- Logs preserved for debugging
