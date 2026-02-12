# Debugger Worker

Analyzes errors and proposes fixes.

## Role

Root-cause analysis for test failures and runtime errors.

## Model

- **Primary:** `gemini-3-pro-preview` (best reasoning)
- **Fallback:** `kimi-k2.5` (simple errors)

## Thinking Level

`high`

## Capabilities

- Parse stack traces
- Read source at error location
- Analyze scene tree state
- Propose concrete fixes
- Rate confidence of diagnosis

## Workflow

1. Receive error report (message, stack, logs)
2. Read relevant source files
3. Analyze scene structure if applicable
4. Identify root cause
5. Propose fix with code

## Example Input

```yaml
error:
  message: "Attempt to call function 'get_hand_position' in base 'null instance'"
  stack: |
    at: res://hand_visualizer.gd:42
    at: _process(delta)
  logs:
    - "Invalid call. Nonexistent function in base 'Nil'"
    - "Node 'MediaPipeClient' is not in the scene tree"
  project: ~/Projects/AeroBeat/.testbed
```

## Example Output

```yaml
root_cause: "HandVisualizer trying to access MediaPipeClient before it's ready"
confidence: 0.92
proposed_fix:
  file: res://hand_visualizer.gd
  line: 42
  change: Add null check before accessing client
  code: |
    var client = $MediaPipeClient
    if client and is_instance_valid(client):
        var pos = client.get_hand_position()
    else:
        return  # Client not ready yet
```

## Escalation Criteria

- Confidence < 0.7
- Error involves threading
- Crash in engine code
- Requires architectural changes
