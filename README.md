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

OpenClaw-Godot provides **infrastructure** plus **two integration options**:

| Approach | Best For | Status |
|----------|----------|--------|
| **DiscordOrchestration** | ✅ Distributed workers, parallel tasks, production | **Primary** |
| **OpenClaw Native** | Simple single-machine workflows, quick tests | Alternative |

### Why DiscordOrchestration is Primary

OpenClaw's built-in `sessions_spawn` sub-agent system has [known issues](https://github.com/openclaw/openclaw/issues/10467) with parallel execution and zombie processes.

**Chip's DiscordOrchestration** provides:
- ✅ Dynamic agent spawning (fresh agent per task)
- ✅ No race conditions (atomic Discord reaction claiming)
- ✅ No zombie processes (agents exit cleanly)
- ✅ Parallel execution (multiple agents simultaneously)
- ✅ Automatic retries with exponential backoff
- ✅ Screenshot proof attached to Discord results

## Architecture

### Option 1: DiscordOrchestration (Recommended)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   You       │────▶│  #task-queue │────▶│ Orchestrator │
│  Submit     │     │   (Discord)    │     │  (Cookie)    │
└─────────────┘     └──────────────┘     └───────┬──────┘
                                                  │
                       ┌──────────────────────────┘
                       │ Spawns Fresh Agent
                       │ (with worker template)
                       ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Agent     │◀───│   Workspace  │◀────│  OpenClaw    │
│  Executes   │     │  (isolated)  │     │  Gateway     │
│  GDScript   │     └──────────────┘     └──────────────┘
│  Tests      │              │
│  Captures   │              ▼
└──────┬──────┘     ┌──────────────┐
       │            │ Godot Project│
       │            │ + Auto-Test  │
       │            └──────────────┘
       │
       └────────────►┌──────────────┐
                     │ Orchestrator │
                     │ Posts        │────▶ Discord #results
                     │ SUMMARY.txt  │        + Screenshot
                     └──────────────┘
```

**Requirements:**
- Discord server with #task-queue, #results, #worker-pool channels
- Discord bot token
- Chip's DiscordOrchestration repo (`~/Documents/GitHub/discord-orchestration/`)

### Option 2: OpenClaw Native (Direct)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Orchestrator│────▶│  sessions_   │────▶│   Worker     │
│   (Cookie)  │     │   spawn()    │     │   Agent      │
└─────────────┘     └──────────────┘     └───────┬──────┘
                          │                      │
                          │    ┌─────────────────┘
                          │    │ Uses godot_bridge
                          │    ▼
                          │ ┌──────────────┐
                          │ │ Godot Project│
                          │ └──────────────┘
                          │
                          └── Returns result to Cookie
```

**Requirements:**
- Just OpenClaw (no Discord setup)
- **Note:** Limited by `sessions_spawn` bugs — avoid parallel tasks

## Installation

### System Dependencies

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| **Godot 4.x** | Game engine | [Download](https://godotengine.org/download) or `sudo snap install godot` |
| **Python 3.10+** | Bridge runtime | Usually pre-installed |
| **tkinter** | PyAutoGUI dependency | `sudo apt install python3-tk python3-dev` |
| **xdotool** | Input injection | `sudo apt install xdotool` |

### Python Dependencies

```bash
pip3 install mss Pillow pyautogui
```

### DiscordOrchestration Setup

See Chip's repo (`~/Documents/GitHub/discord-orchestration/`) for full setup:

```bash
# Link the sanitization skill (prevents Discord markdown issues)
ln -s ~/Documents/GitHub/discord-orchestration/skills/discord-sanitize \
  ~/.openclaw/skills/discord-sanitize

# Configure Discord bot token and channel IDs
cp discord-config.env.example discord-config.env
# Edit discord-config.env with your tokens
```

## Usage

### Via DiscordOrchestration (Recommended)

```bash
# Submit a task to Discord
cd ~/Documents/GitHub/discord-orchestration
./bin/submit-to-queue.sh "Run button_background auto-test" "primary" "medium"

# Orchestrator spawns agent, agent claims task, executes, posts result to #results
```

**Task format:**
```
[project:button_background]
[worker:godot-tester]
[model:primary]
[thinking:medium]

Run the auto-test scene and screenshot the result.
```

### Via OpenClaw Direct (Simple Tests)

```bash
cd ~/Documents/GitHub/openclaw-godot
python3 examples/button_background/test_phase1_autotest.py
```

## Worker Templates

### How Templates Work

When DiscordOrchestration spawns an agent, it includes the appropriate worker template as the agent's `AGENTS.md`:

```
Agent Workspace
├── AGENTS.md          ← Copied from workers/godot-tester.md
├── TOOLS.md           ← Standard tools
└── tasks/
    └── TASK-123/
        ├── TASK.txt   ← The actual task
        ├── RESULT.txt ← Agent writes full output
        └── SUMMARY.txt← Condensed for Discord
```

### Available Workers

| Worker | Template | Description |
|--------|----------|-------------|
| **godot-coder** | `workers/godot-coder.md` | Implements GDScript features |
| **godot-tester** | `workers/godot-tester.md` | Runs tests, captures screenshots |
| **godot-visual-verifier** | `workers/godot-visual-verifier.md` | VLM-based screenshot analysis |
| **godot-debugger** | `workers/godot-debugger.md` | Error analysis + fix proposals |

### Template Selection

**Method 1: Task Tag**
```
[worker:godot-tester]

Run tests on button_background project...
```

**Method 2: Submit Script**
```bash
./bin/submit-to-queue.sh \
  --worker godot-coder \
  --project button_background \
  "Implement score display UI"
```

**Method 3: Orchestrator Auto-Detect**
Orchestrator analyzes task content:
- "Debug error" → godot-debugger
- "Implement feature" → godot-coder
- "Verify screenshot" → godot-visual-verifier
- "Run tests" → godot-tester

## Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `src/godot_bridge/` | Python interface to Godot | This repo |
| `godot/*/` | Test projects with auto-test scenes | This repo |
| `workers/*.md` | Worker agent templates | This repo |
| `discord-orchestration/` | Orchestration system | Separate repo |

## Quick Start Examples

### Example 1: Simple Headless Test (Direct)

```bash
cd examples/button_background
python3 test_phase0.py
```

**Result:** Console output showing test passed

### Example 2: Interactive Auto-Test (Direct)

```bash
cd examples/button_background
python3 test_phase1_autotest.py
```

**Result:** Screenshot showing red background + ✅ TEST PASSED label

### Example 3: Full Workflow via Discord (Recommended)

```bash
# 1. Submit task
cd ~/Documents/GitHub/discord-orchestration
./bin/submit-to-queue.sh \
  --project button_background \
  --worker godot-tester \
  --model primary \
  --thinking medium \
  "Run auto-test scene and verify background changes red"

# 2. Orchestrator spawns agent
# 3. Agent claims task via Discord ✅ reaction
# 4. Agent executes test, captures screenshot
# 5. Agent writes RESULT.txt and SUMMARY.txt
# 6. Orchestrator posts SUMMARY.txt to #results channel
# 7. Screenshot attached as evidence
```

**Result in Discord #results:**
```
🧪 Test: button_background

Result: PASS
Evidence: Background changed from blue to red
Screenshot: [attached]

Key findings:
- Auto-test ran successfully
- Color verification passed
- Screenshot proof attached
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'mss'"
```bash
pip3 install mss Pillow pyautogui
```

### "Godot not found in PATH"
```bash
which godot
# If not found:
sudo ln -s /path/to/Godot_v4.6 /usr/local/bin/godot
```

### DiscordOrchestration not finding tasks
- Check `discord-config.env` has correct channel IDs
- Verify bot has permissions (Send Messages, Add Reactions, etc.)
- Check #task-queue has unclaimed tasks (no ✅ reaction)

### Markdown formatting broken in Discord
- Ensure `discord-sanitize` skill is linked: `ls ~/.openclaw/skills/`
- Verify skill loads: `openclaw skills list`
- Restart OpenClaw: `openclaw gateway restart`

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — Technical design
- [Workers](workers/) — Worker template specifications
- [DiscordOrchestration](https://github.com/GambitGamesLLC/discord-orchestration) — Orchestration system

## Contributing

### Adding New Workers

1. Create `workers/godot-[role].md`
2. Include:
   - Role definition
   - Available tools
   - Workflow steps
   - Output format (RESULT.txt + SUMMARY.txt)
3. Document in README (this file)

### Adding Test Projects

1. Create `godot/[project-name]/` with:
   - `project.godot` — Project file
   - `main_auto_test.tscn` — Auto-test scene
   - `main_auto_test.gd` — Self-clicking test script
2. Add to examples list
3. Document worker type expectations

## License

MIT — See [LICENSE](LICENSE)

---

Built with 🍪 for Derrick's OpenClaw setup.
Using Chip's DiscordOrchestration for reliable sub-agent spawning.
