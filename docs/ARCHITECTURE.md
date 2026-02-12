# OpenClaw-Godot Architecture

## Overview

OpenClaw-Godot leverages the OpenClaw agent's direct system access to control Godot without traditional MCP middleware.

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator (Cookie)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐   │
│  │  Coder   │ │ Tester   │ │   Visual     │ │ Debugger │   │
│  │  Worker  │ │ Worker   │ │   Worker     │ │ Worker   │   │
│  └────┬─────┘ └────┬─────┘ └──────┬───────┘ └────┬─────┘   │
│       └─────────────┴──────────────┴──────────────┘          │
│                          │                                  │
│       ┌──────────────────▼──────────────────┐               │
│       │       OpenClaw Direct Access        │               │
│       │  - File I/O  - Process exec  - VLM  │               │
│       └──────────────────┬──────────────────┘               │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Python Bridge                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   godot.py  │  │ capture.py  │  │    input.py         │  │
│  │  Project    │  │ Screenshots │  │ PyAutoGUI injection │  │
│  │  Runner     │  │ mss/xdotool │  │ Mouse/Keyboard      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              Godot (CLI or Editor Plugin)                    │
│                     ┌─────────────┐                         │
│                     │   Project   │                         │
│                     └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. No MCP Server Required

Traditional AI tools need MCP servers because they lack system access. OpenClaw agents have direct file system and process access, so we skip the middleware.

**Benefits:**
- Simpler architecture
- Lower latency
- Direct control

### 2. Python Bridge

Core functionality in Python (not GDScript) for easier OpenClaw integration:

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `godot.py` | Project/runner management | subprocess |
| `capture.py` | Screenshots | mss, Pillow, xdotool |
| `input.py` | Input injection | PyAutoGUI |

### 3. Optional Godot Plugin

GDScript plugin for enhanced editor integration (optional):
- Debug log streaming
- Scene introspection
- Script hot-reload

Not required — Python bridge works standalone.

### 4. DiscordOrchestration Workers

Tasks distributed to specialized workers via Discord:

```
#task-queue
[worker:coder] Implement button feature
[project:examples/button_background]
```

Workers claim tasks via ✅ reaction, execute, post results.

## Data Flow

### Feature Implementation Flow

```
1. Orchestrator spawns Coder Worker via Discord
2. Coder reads existing files (direct access)
3. Coder writes new/modified files
4. Coder returns: files_changed, summary
5. Orchestrator spawns Tester Worker
6. Tester runs Godot, injects input, captures screenshots
7. Tester returns: pass/fail, logs, screenshots
8. Orchestrator spawns Visual Worker (if needed)
9. Visual analyzes screenshots, returns verification
10. Orchestrator decides: done, iterate, or escalate
```

### Error Handling Flow

```
1. Tester reports failure
2. Orchestrator spawns Debugger Worker
3. Debugger reads source at error location
4. Debugger analyzes stack trace and logs
5. Debugger proposes fix with confidence score
6. If confidence > 0.8: spawn Coder with fix
7. If confidence < 0.8: escalate to human
```

## API Reference

### GodotProject

```python
from godot_bridge import GodotProject

project = GodotProject("/path/to/project")
print(project.name)  # "MyGame"

# Read/write scripts
content = project.read_script("scripts/player.gd")
project.write_script("scripts/enemy.gd", source_code)

# List assets
scenes = project.list_scenes()  # [Path("main.tscn"), ...]
scripts = project.list_scripts()  # [Path("player.gd"), ...]
```

### GodotRunner

```python
from godot_bridge import GodotRunner, GodotProject

runner = GodotRunner()
project = GodotProject("/path/to/project")

# Run with display (for testing with input)
runner.run_with_display(project, "main.tscn")

# Run headless (for CI/testing)
runner.run_headless(project, quit_after=300, fixed_fps=60)

# Get logs
logs = runner.get_output()
print(logs["stdout"])
print(logs["stderr"])

# Stop
result = runner.stop()
```

### ScreenshotCapture

```python
from godot_bridge import ScreenshotCapture

cap = ScreenshotCapture()

# Full screen
img = cap.capture_screen()

# Specific window (uses xdotool)
img = cap.capture_window("Godot")

# Region
img = cap.capture_region(0, 0, 1920, 1080)

# Save
cap.save_screenshot(img, "screenshot.png")

cap.close()
```

### InputInjector

```python
from godot_bridge import InputInjector

inp = InputInjector()

# Mouse
inp.click(540, 305)
inp.move_to(100, 100, duration=0.5)

# Keyboard
inp.key_press("space")
inp.type_text("Hello World")
inp.hotkey("ctrl", "s")

# Wait
inp.wait(1.0)
```

## Extension Points

### Adding New Worker Types

1. Create `workers/my_worker.md` with specification
2. Add to orchestrator workflow definitions
3. Spawn via DiscordOrchestration with `model:` tag

### Custom Verifications

Extend `verify_screenshots()` in examples to use VLM:

```python
from openai import OpenAI

def vlm_verify(image_path: Path, prompt: str) -> bool:
    client = OpenAI()
    with open(image_path, "rb") as f:
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"}
                ]}
            ]
        )
    return "yes" in result.choices[0].message.content.lower()
```

## Security Considerations

- Godot processes run as user (not elevated)
- File access limited to project directories
- Input injection simulates user actions (can be interrupted)
- Screenshots capture only Godot window (not full desktop)

## Performance

| Operation | Typical Time |
|-----------|--------------|
| Start Godot | 2-3 seconds |
| Capture screenshot | 50-100ms |
| Inject input | 10-50ms |
| Script hot-reload | 100-500ms |
| Full test cycle | 5-10 seconds |

## Future Enhancements

- [ ] WebSocket protocol for persistent Godot connection
- [ ] Scene tree diff viewer
- [ ] Automated performance profiling
- [ ] Multi-project coordination
- [ ] CI/GitHub Actions integration
