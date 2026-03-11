# OpenClaw-Godot

**Autonomous agentic development for Godot Engine.**

This project closes the gap between AI agents and Godot game development, enabling OpenClaw Orchestrator agents to implement, test, and iterate on features without human intervention.

## The Problem

Current AI-assisted Godot development looks like this:

```
Agent writes code → Human tests → Human reports issues → Agent fixes → Human tests again...
```

The human is the bottleneck. Logs, screenshots, debugger output, and testing feedback all require manual intervention.

## The Solution

OpenClaw-Godot provides the infrastructure for a fully autonomous loop:

```
Orchestrator → Coder Worker → Godot (via MCP) → Tester Worker → Visual Worker
                    ↑                                              │
                    └──────────── Fix & iterate ←──────────────────┘
```

## Components

| Component | Purpose | Status |
|-----------|---------|--------|
| `mcp-server/` | Extended MCP server for Godot | 📋 Planned |
| `godot-plugin/` | Editor plugin for introspection | 📋 Planned |
| `screenshotd/` | Screenshot capture service | 📋 Planned |
| `inputd/` | Input injection service | 📋 Planned |
| `workers/` | Worker agent definitions | 📋 Planned |
| `orchestrator/` | Orchestrator workflows | 📋 Planned |

## Quick Start

(TODO: Add setup instructions once Phase 1 is complete)

## Documentation

- [PLAN.md](PLAN.md) — Full architecture and implementation plan

## Related Projects

- [Coding-Solo/godot-mcp](https://github.com/Coding-Solo/godot-mcp) — Base MCP server we tested
- [ee0pdt/Godot-MCP](https://github.com/ee0pdt/Godot-MCP) — Alternative with script editing
- [GDAI MCP](https://gdaimcp.com) — Commercial solution with screenshots (inspiration)
- [UnityMCP](https://github.com/jackwrichards/UnityMCP) — Unity equivalent (architecture reference)

## License

MIT — See LICENSE.md

---

Built with 🍪 by Cookie for Derrick's OpenClaw setup.
