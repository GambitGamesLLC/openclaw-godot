#!/bin/bash
#
# orchestrator-dynamic.sh.patch - Adds dynamic AGENTS.md support
# 
# Usage with custom AGENTS.md:
#   AGENTS_MD_TEMPLATE=/path/to/godot-tester.md ./bin/orchestrator.sh
#
# Usage with extra PYTHONPATH:
#   EXTRA_PYTHONPATH=/path/to/openclaw-godot/src ./bin/orchestrator.sh
#

# Find the line where AGENTS.md is written and replace it
# Around line 160 in the original script

# Replace this block:
#     cat > "${WORKER_STATE_DIR}/AGENTS.md" << EOF
# ...hardcoded content...
# EOF

# With this block:
if [[ -n "${AGENTS_MD_TEMPLATE}" && -f "${AGENTS_MD_TEMPLATE}" ]]; then
    # Use custom AGENTS.md template
    cp "${AGENTS_MD_TEMPLATE}" "${WORKER_STATE_DIR}/AGENTS.md"
    
    # Append task-specific info to the template
    cat >> "${WORKER_STATE_DIR}/AGENTS.md" << EOF

---

## Current Task
${TASK_DESC}

## Task Directory
${TASK_DIR}

## Agent ID
${AGENT_ID}
EOF
    
    echo "[$(date '+%H:%M:%S')] Using custom AGENTS.md: ${AGENTS_MD_TEMPLATE}" >&2
else
    # Use default AGENTS.md (original content)
    cat > "${WORKER_STATE_DIR}/AGENTS.md" << EOF
# ${AGENT_ID}

## Task
${TASK_DESC}

## Model Defaults
- Primary: openrouter/moonshotai/kimi-k2.5
- Cheap: openrouter/stepfun/step-3.5-flash:free
- Coder: openrouter/qwen/qwen3-coder-next
- Research: openrouter/google/gemini-3-pro-preview

## Output Files (REQUIRED)

You MUST write TWO files:

1. **RESULT.txt** - Complete detailed result (full output)
2. **SUMMARY.txt** - Condensed summary (~2000 chars max)

### SUMMARY.txt Guidelines:
- Maximum ${SUMMARY_MAX_LENGTH:-2000} characters
- Include key findings and conclusions
- Can truncate with "... (see RESULT.txt)" if needed
- Used for Discord display (saves tokens)
- Write AFTER RESULT.txt is complete

### Why Two Files?
- RESULT.txt = Full context for future reference
- SUMMARY.txt = Quick review without loading full context
- Discord shows SUMMARY.txt (reduces token usage)
EOF
fi

# Also modify the agent spawn section to include EXTRA_PYTHONPATH
# Around line 220 where the agent is spawned

# Add after the export statements:
#     export EXTRA_PYTHONPATH="${EXTRA_PYTHONPATH:-}"

# And modify the openclaw agent command to include:
#     PYTHONPATH="${EXTRA_PYTHONPATH}:${PYTHONPATH}" timeout $AGENT_TIMEOUT openclaw agent ...
