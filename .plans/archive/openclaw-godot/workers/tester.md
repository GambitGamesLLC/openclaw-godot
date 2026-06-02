# Worker: Tester

## Role

Runs Godot projects, executes test scenarios, captures output and screenshots.

## Model

- **Primary:** `kimi-k2.5`
- **Fallback:** `gemini-3-pro-preview` (complex test analysis)

## Thinking Level

`medium`

## MCP Tools Used

- `run_project` — Start project in debug mode
- `get_debug_output` — Retrieve logs/errors
- `capture_screenshot` — Take screenshots
- `inject_input` — Send key/mouse input
- `get_structured_logs` — Categorized log retrieval
- `stop_project` — Clean shutdown

## Workflow

```yaml
input:
  project_path: "/home/derrick/Documents/GitHub/AeroBeat/aerobeat-input-mediapipe-python/.testbed"
  test_scenario:
    name: "Hand tracking connection test"
    steps:
      - action: "run_project"
        scene: "test_scene.tscn"
      - action: "wait"
        duration: 3.0
        for: "python_server_ready"
      - action: "capture_screenshot"
        name: "initial_state"
      - action: "inject_input"
        type: "key"
        key: "space"
      - action: "wait"
        duration: 1.0
      - action: "capture_screenshot"
        name: "after_input"
      - action: "stop_project"
    assertions:
      - type: "log_contains"
        pattern: "Server started successfully"
      - type: "no_errors"
      - type: "screenshot_comparison"
        baseline: "expected_initial.png"
        actual: "initial_state"
        tolerance: 0.05

steps:
  1. Run project with specified scene
  2. Execute step sequence
  3. Capture screenshots at marked points
  4. Collect logs
  5. Evaluate assertions
  6. Return pass/fail with evidence

output:
  passed: false
  failed_assertions:
    - "screenshot_comparison: 15% pixel difference exceeds 5% tolerance"
  logs:
    errors: []
    warnings: ["Texture size mismatch"]
    prints: ["Server started successfully", "Waiting for camera..."]
  screenshots:
    - name: "initial_state"
      path: "/tmp/test_123_initial_state.png"
    - name: "after_input"
      path: "/tmp/test_123_after_input.png"
```

## Prompt Template

```markdown
You are a QA tester running automated tests on a Godot project.

Project: {project_path}
Test scenario: {test_scenario_json}

Execute the test scenario step by step using MCP tools:
1. Run the project
2. Follow each step in sequence
3. Capture screenshots when requested
4. Check assertions
5. Return detailed results including all logs and screenshots

Be methodical. If a step fails, stop and report the failure.
```

## Screenshot Naming Convention

```
{test_id}_{step_name}_{timestamp}.png

Examples:
- test_001_initial_state_20250212_083045.png
- test_001_after_click_20250212_083048.png
```
