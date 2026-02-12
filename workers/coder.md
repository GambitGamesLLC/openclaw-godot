# Coder Worker

Implements features by modifying Godot project files via direct file access.

## Role

Transforms feature specifications into working Godot code.

## Model

- **Primary:** `qwen3-coder-next` (local, fast)
- **Fallback:** `gemini-3-pro-preview` (complex refactoring)

## Thinking Level

`medium`

## Capabilities

- Read/write GDScript files directly
- Create/modify scene files
- Understand project structure
- Hot-reload changes for rapid iteration

## Workflow

1. Read relevant existing files
2. Implement feature
3. Write/modify files
4. Verify compilation (optional)
5. Return summary

## Example Task

```yaml
project: ~/Projects/AeroBeat/.testbed
task: |
  Add a debug overlay that shows:
  - FPS counter (top-left)
  - Hand tracking status (top-right)
  
  Should be visible in test_scene.tscn and update every frame.
```

## Success Criteria

- All requested features implemented
- Code follows existing patterns
- No syntax errors
- Scene runs without errors
