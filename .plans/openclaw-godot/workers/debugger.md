# Worker: Debugger

## Role

Analyzes errors, crashes, and unexpected behavior to propose fixes.

## Model

- **Primary:** `gemini-3-pro-preview` (best reasoning)
- **Fallback:** `kimi-k2.5` (faster for simple errors)

## Thinking Level

`high`

## MCP Tools Used

- `get_debugger_state` — Stack trace, variables, breakpoints
- `get_scene_tree` — Current scene structure
- `get_node_properties` — Specific node state
- `read_script` — Source code at error location
- `get_structured_logs` — Filtered log history

## Workflow

```yaml
input:
  error_report:
    type: "runtime_error"
    message: "Attempt to call function 'get_hand_position' in base 'null instance' on a null instance"
    stack_trace: |
      at: res://hand_visualizer.gd:42
      at: _process(delta)
    logs:
      errors: ["Invalid call. Nonexistent function 'get_hand_position' in base 'Nil'"]
      warnings: ["Node 'MediaPipeClient' is not in the scene tree"]
    scene_state:
      current_scene: "test_scene.tscn"
      relevant_nodes: ["HandVisualizer", "MediaPipeClient"]

steps:
  1. Read the script at error location
  2. Get scene tree to understand node hierarchy
  3. Check if referenced nodes exist
  4. Analyze variable states if available
  5. Identify root cause
  6. Propose fix

output:
  root_cause: |
    The HandVisualizer script is trying to call get_hand_position() on 
    the MediaPipeClient node, but MediaPipeClient is not in the scene 
    tree (likely not yet initialized or was freed).
  
  confidence: 0.92
  
  proposed_fix:
    file: "res://hand_visualizer.gd"
    line: 42
    original: |
      var pos = $MediaPipeClient.get_hand_position()
    replacement: |
      var client = $MediaPipeClient
      if client and is_instance_valid(client):
        var pos = client.get_hand_position()
      else:
        push_warning("MediaPipeClient not available")
        return
  
  alternative_fixes:
    - "Ensure MediaPipeClient is added to scene before HandVisualizer"
    - "Use @onready to defer initialization"
  
  requires_human: false
```

## Prompt Template

```markdown
You are a senior Godot developer debugging an error.

Error: {error_message}
Stack trace: {stack_trace}
Relevant logs: {logs}
Scene: {scene_name}

Use MCP tools to investigate:
1. Read the script at the error location
2. Get the scene tree
3. Check node properties if relevant

Then:
1. Identify the root cause (be specific)
2. Propose a concrete fix with code
3. Rate your confidence (0-1)
4. If confidence < 0.8, suggest what info would help

Return structured JSON with your analysis.
```

## Error Categories

| Category | Common Causes | Typical Fix |
|----------|---------------|-------------|
| Null instance | Node not in tree, freed early | Null checks, @onready |
| Invalid call | Wrong node type, typo in method | Type checking, verify API |
| Parse error | Syntax error in GDScript | Fix syntax |
| Cyclic reference | Circular dependencies | Refactor to break cycle |
| Signal not connected | Missing connect() call | Add connection in _ready |
| Resource not found | Wrong path, missing file | Verify paths, check case |

## Escalation Criteria

Escalate to human if:
- Confidence < 0.7
- Error involves complex threading
- Crash is in engine code (not GDScript)
- Requires architectural changes
- Multiple interacting systems involved
