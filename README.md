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

## Quick Start

```bash
# Install Python dependencies
pip install -e .

# Run your first automated test
cd examples/button_background
python test_autonomous.py
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
