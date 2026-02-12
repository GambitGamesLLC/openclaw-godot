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

| Approach                  | Best For                                          | Status      |
| ------------------------- | ------------------------------------------------- | ----------- |
| **Discord Orchestration** | ✅ Distributed workers, parallel tasks, production | **Primary** |
| **OpenClaw Native**       | Simple single-machine workflows, quick tests      | Alternative |

### Why DiscordOrchestration is Primary

OpenClaw's built-in `sessions_spawn` sub-agent system has https://github.com/openclaw/openclaw/issues/10467 with parallel execution and zombie processes.

**Discord Orchestration** provides:

- ✅ Dynamic agent spawning (fresh agent per task)
- ✅ No race conditions (atomic Discord reaction claiming)
- ✅ No zombie processes (agents exit cleanly)
- ✅ Parallel execution (multiple agents simultaneously)
- ✅ Automatic retries with exponential backoff
- ✅ Proof attached to Discord results

## Architecture

### Option 1: Discord Orchestration (Recommended)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   You       │────▶│  #task-queue │────▶│ Orchestrator │
│  Submit     │     │   (Discord)  │     │   (Agent)    │
└─────────────┘     └──────────────┘     └───────┬──────┘
                                                  │
                       ┌──────────────────────────┘
                       │ Spawns Fresh Agent
                       │ (with worker template)
                       ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Agent     │◀─── │   Workspace  │◀────│  OpenClaw    │
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
- Discord Orchestration repo (`~/Documents/GitHub/discord-orchestration/`)
  - [Download from Github](https://github.com/GambitGamesLLC/discord-orchestration) (FREE - MIT License)

### Option 2: OpenClaw Native (Direct)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Orchestrator│────▶│  sessions_   │────▶│   Worker     │
│ (OpenClaw)  │     │   spawn()    │     │   Agent      │
└─────────────┘     └──────────────┘     └───────┬──────┘
                          │                      │
                          │    ┌─────────────────┘
                          │    │ Uses godot_bridge
                          │    ▼
                          │ ┌──────────────┐
                          │ │ Godot Project│
                          │ └──────────────┘
                          │
                          └── Returns result to Orchestrator
```

**Requirements:**

- Just OpenClaw (no Discord setup)
- **Note:** Limited by `sessions_spawn` bugs — avoid parallel tasks with SubAgents

## Installation

### System Dependencies

| Tool             | Purpose              | Install Command                                                           |
| ---------------- | -------------------- | ------------------------------------------------------------------------- |
| **Godot 4.x**    | Game engine          | [Download](https://godotengine.org/download) or `sudo snap install godot` |
| **Python 3.10+** | Bridge runtime       | Usually pre-installed                                                     |
| **tkinter**      | PyAutoGUI dependency | `sudo apt install python3-tk python3-dev`                                 |
| **xdotool**      | Input injection      | `sudo apt install xdotool`                                                |

### Python Dependencies

```bash
pip3 install mss Pillow pyautogui
```

##### Usage

### Via Discord Orchestration (Recommended)

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

When Discord Orchestration spawns an agent, it includes the appropriate worker template as the agent's `AGENTS.md`:

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

| Worker                    | Template                           | Description                      |
| ------------------------- | ---------------------------------- | -------------------------------- |
| **godot-coder**           | `workers/godot-coder.md`           | Implements GDScript features     |
| **godot-tester**          | `workers/godot-tester.md`          | Runs tests, captures screenshots |
| **godot-visual-verifier** | `workers/godot-visual-verifier.md` | VLM-based screenshot analysis    |
| **godot-debugger**        | `workers/godot-debugger.md`        | Error analysis + fix proposals   |

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

### Advanced: Custom Orchestrator Configuration

The orchestrator supports environment variables for Godot-specific tasks:

#### Usage

```bash
cd ~/Documents/GitHub/discord-orchestration

# Run with godot-tester template and godot_bridge in PYTHONPATH
AGENTS_MD_TEMPLATE=~/Documents/GitHub/openclaw-godot/workers/godot-tester.md \
EXTRA_PYTHONPATH=~/Documents/GitHub/openclaw-godot/src \
./bin/orchestrator.sh
```

#### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AGENTS_MD_TEMPLATE` | Path to custom AGENTS.md template | `~/openclaw-godot/workers/godot-tester.md` |
| `EXTRA_PYTHONPATH` | Add godot_bridge to Python path | `~/openclaw-godot/src` |

#### How It Works

1. **Agent spawns** with custom `AGENTS.md` (copied from template)
2. **PYTHONPATH includes** `openclaw-godot/src` so agents can:
   ```python
   from godot_bridge import GodotProject, GodotRunner, ScreenshotCapture
   ```
3. **Agent executes** Godot-specific task using the bridge
4. **Results posted** to Discord with screenshots

#### Example Task with Worker Tag

Submit a task that specifies the worker type:

```bash
./bin/submit-to-queue.sh "[worker:godot-tester] Run button_background auto-test and capture screenshot"
```

The orchestrator will:
- Parse `[worker:godot-tester]` tag
- Log the worker type
- Post worker type to Discord #worker-pool
- Use custom AGENTS.md if `AGENTS_MD_TEMPLATE` is set
- Include `EXTRA_PYTHONPATH` in agent environment

## Components

| Component                | Purpose                             | Location      |
| ------------------------ | ----------------------------------- | ------------- |
| `src/godot_bridge/`      | Python interface to Godot           | This repo     |
| `godot/*/`               | Test projects with auto-test scenes | This repo     |
| `workers/*.md`           | Worker agent templates              | This repo     |
| `discord-orchestration/` | Orchestration system                | Separate repo |

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

### Discord Orchestration not finding tasks

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
- [Discord Orchestration](https://github.com/GambitGamesLLC/discord-orchestration) — Orchestration system

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

Built with 🍪Cookie for Derrick's OpenClaw setup.
Using Chip's Discord Orchestration system for reliable OpenClaw sub-agent spawning.
