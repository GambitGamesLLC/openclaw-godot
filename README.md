# OpenClaw-Godot

**Autonomous AI agent framework for Godot Engine.**

Enables OpenClaw orchestrators to implement, test, and iterate on Godot features without human intervention.

## The Problem

Current AI-assisted Godot development locks humans in the loop:

```
Agent writes code → Human tests → Human reports issues → Agent fixes → Human tests again...
```

Logs, screenshots, debugger output — all require manual handoff.

## The Solution

OpenClaw-Godot provides the infrastructure for a fully autonomous loop:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Orchestrator│────▶│   Worker    │────▶│    Godot    │
│   (Cookie)  │     │   Agents    │     │   Project   │
└──────┬──────┘     └─────────────┘     └──────┬──────┘
       ▲                                         │
       └──────────────────┬──────────────────────┘
                          │
       ┌──────────────────▼──────────────────┐
       │  Screenshots ← Logs ← State ← Game  │
       └─────────────────────────────────────┘
```

## Why This Is Different

Unlike traditional MCP servers (which bridge gap for AI without system access), OpenClaw-Godot leverages OpenClaw's **direct system access**:

- ✅ Direct file manipulation (no MCP middleman)
- ✅ Native process execution
- ✅ DiscordOrchestration worker swarm
- ✅ Vision-language model integration

## Installation

### System Dependencies

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| **Godot 4.x** | Game engine | [Download](https://godotengine.org/download) or `sudo snap install godot` |
| **Python 3.10+** | Bridge runtime | Usually pre-installed |
| **tkinter** | PyAutoGUI dependency (input injection) | `sudo apt install python3-tk python3-dev` |
| **xdotool** | Window management for screenshots | `sudo apt install xdotool` |

**Why tkinter?** PyAutoGUI uses it for mouse/keyboard control on Linux. Without it, you can still run headless tests but not interactive GUI tests.

**Why xdotool?** Used to find and focus Godot windows for targeted screenshots. Falls back to full-screen capture if unavailable.

### Python Dependencies

```bash
# Install all Python packages
pip3 install mss Pillow pyautogui

# Or install as editable package (recommended for development)
pip3 install -e .
```

| Package | Purpose |
|---------|---------|
| **mss** | Multi-screen screenshot capture (fast, no GUI deps) |
| **Pillow** | Image processing (save, analyze screenshots) |
| **PyAutoGUI** | Mouse/keyboard input injection (requires tkinter) |

### Verify Installation

```bash
# Test core functionality (no GUI needed)
cd examples/button_background
python3 test_phase0.py

# Expected output:
# ✅ PHASE 0 PASSED
# - GodotProject loads
# - ScreenshotCapture works
# - GodotRunner runs project
```

## Quick Start

```bash
# 1. Clone and enter repo
cd ~/Documents/GitHub/openclaw-godot

# 2. Install dependencies
pip3 install mss Pillow pyautogui

# 3. Run Phase 0 test (headless, no GUI needed)
cd examples/button_background
python3 test_phase0.py

# 4. (Optional) Install tkinter for interactive tests
sudo apt install python3-tk python3-dev
python3 test_autonomous.py  # Full test with button clicking
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'mss'"
```bash
pip3 install mss Pillow pyautogui
```

### "NOTE: You must install tkinter"
PyAutoGUI requires tkinter for Linux. Install it:
```bash
sudo apt install python3-tk python3-dev
```
Or use `test_phase0.py` which doesn't need tkinter.

### "Godot not found in PATH"
Ensure `godot` command works:
```bash
which godot
# If not found, create symlink:
sudo ln -s /path/to/Godot_v4.6 /usr/local/bin/godot
```

## Components

| Component | Purpose | Status |
|-----------|---------|--------|
| `src/godot_bridge/` | Python interface to Godot | 🚧 WIP |
| `src/plugin/` | GDScript editor plugin | 📋 Planned |
| `workers/` | Agent definitions | ✅ Defined |
| `examples/` | Demo workflows | 🚧 WIP |

## Worker Types

- **Coder** — Writes/modifies GDScript via direct file access
- **Tester** — Runs project, injects input, captures output
- **VisualVerifier** — VLM-based screenshot analysis
- **Debugger** — Error analysis + fix proposals

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — Technical design
- [Workers](workers/) — Agent specifications

## License

MIT — See [LICENSE](LICENSE)

---

Built with 🍪 for Derrick's OpenClaw setup.
