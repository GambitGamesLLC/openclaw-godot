# Orchestrator Enhancement Documentation

The main `discord-orchestration/bin/orchestrator.sh` now supports dynamic configuration via environment variables.

## New Features

### 1. Custom AGENTS.md Template

**Environment Variable:** `AGENTS_MD_TEMPLATE`

When set, the orchestrator copies this file as the agent's `AGENTS.md` instead of using the default template.

**Usage:**
```bash
AGENTS_MD_TEMPLATE=~/openclaw-godot/workers/godot-tester.md \
./bin/orchestrator.sh
```

**What it does:**
- Copies your custom template to `${WORKER_STATE_DIR}/AGENTS.md`
- Appends task context (Task ID, Agent ID, Task Directory, Task Description)
- Logs: "Using custom AGENTS.md: [path]"

### 2. Extra PYTHONPATH

**Environment Variable:** `EXTRA_PYTHONPATH`

Adds custom Python paths to the agent's environment, enabling imports from external modules.

**Usage:**
```bash
EXTRA_PYTHONPATH=~/openclaw-godot/src \
./bin/orchestrator.sh
```

**What it does:**
- Prepends to existing PYTHONPATH: `PYTHONPATH="${EXTRA_PYTHONPATH}:${PYTHONPATH}"`
- Logs the extended PYTHONPATH to agent-output.log
- Agents can now import: `from godot_bridge import GodotProject, GodotRunner`

### 3. Worker Type Tag Parsing

**Task Format:** `[worker:worker-type]`

Tasks can include a worker type tag that gets parsed and logged.

**Usage:**
```bash
./bin/submit-to-queue.sh "[worker:godot-tester] Run button_background test"
```

**What it does:**
- Parses `[worker:xxx]` from task content
- Logs: "Worker type: xxx" when spawning agent
- Posts worker type to Discord #worker-pool channel
- Can be used with AGENTS_MD_TEMPLATE for fully custom workers

## Combined Example

Run orchestrator with Godot support:

```bash
cd ~/Documents/GitHub/discord-orchestration

AGENTS_MD_TEMPLATE=~/Documents/GitHub/openclaw-godot/workers/godot-tester.md \
EXTRA_PYTHONPATH=~/Documents/GitHub/openclaw-godot/src \
./bin/orchestrator.sh
```

Then submit Godot tasks:
```bash
./bin/submit-to-queue.sh \
  "[worker:godot-tester] [model:primary] Run button_background auto-test"
```

## Implementation Details

### parse_task() Function

Modified to extract worker type:
```bash
# Parse worker type tag [worker:godot-tester]
local WORKER_TYPE=""
if [[ "$CONTENT" =~ \[worker:([^\]]+)\] ]]; then
    WORKER_TYPE="${BASH_REMATCH[1]}"
fi

echo "$MODEL|$THINKING|$DESC|$WORKER_TYPE"
```

### spawn_agent() Function

Modified to accept and use worker type:
```bash
spawn_agent() {
    local TASK_ID="$1"
    local MODEL="$2"
    local THINKING="$3"
    local TASK_DESC="$4"
    local WORKER_TYPE="${5:-}"  # NEW
    
    # Log worker type if present
    [[ -n "$WORKER_TYPE" ]] && echo "[...] Worker type: $WORKER_TYPE"
}
```

### AGENTS.md Creation

Modified to support custom template:
```bash
if [[ -n "${AGENTS_MD_TEMPLATE:-}" && -f "${AGENTS_MD_TEMPLATE}" ]]; then
    cp "${AGENTS_MD_TEMPLATE}" "${WORKER_STATE_DIR}/AGENTS.md"
    # Append task context
else
    # Use default template
fi
```

### Agent Spawn

Modified to extend PYTHONPATH:
```bash
if [[ -n "${EXTRA_PYTHONPATH:-}" ]]; then
    export PYTHONPATH="${EXTRA_PYTHONPATH}${PYTHONPATH:+:$PYTHONPATH}"
fi
```

## Backward Compatibility

All features are **optional**:
- If `AGENTS_MD_TEMPLATE` is not set → uses default AGENTS.md
- If `EXTRA_PYTHONPATH` is not set → PYTHONPATH unchanged
- If `[worker:xxx]` tag not present → WORKER_TYPE is empty

The orchestrator works exactly as before if none of these are used.
