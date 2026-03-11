# OpenClaw-Godot: Autonomous Agentic Development for Godot

**Vision:** Enable OpenClaw Orchestrator agents to implement, test, and iterate on Godot features without human intervention — closing the gap that currently forces humans to stay in the loop for logs, screenshots, and testing feedback.

---

## 1. Current Landscape Analysis

### 1.1 Existing MCP Servers for Godot

| Project | Status | Key Features | Gaps |
|---------|--------|--------------|------|
| **Coding-Solo/godot-mcp** | ✅ Open Source | Launch editor, run projects, scene creation, add nodes, capture console output | No screenshots, no script editing, stateless process model, can't poll debug output after run |
| **ee0pdt/Godot-MCP** | ✅ Open Source | Full project access, script editing, scene manipulation, two-way communication via WebSocket | No automated testing/verification, no visual feedback |
| **GDAI MCP** | 💰 Commercial ($) | Screenshot verification, end-to-end testing, reads debugger/errors, script editing | Closed source, paid, can't extend/modify |
| **UnityMCP** | ✅ Open Source (Unity) | Real-time editor state, WebSocket comms, C# execution, log filtering | Different engine, but architecture is inspiring |

### 1.2 What Unity/Web Dev Has That Godot Lacks

| Feature | Web (Playwright) | Unity (UnityMCP) | Godot Current | Godot Target |
|---------|-----------------|------------------|---------------|--------------|
| Element introspection | ✅ DOM queries | ✅ Editor state API | ❌ Limited | ✅ Scene tree API |
| Screenshot capture | ✅ Native | ✅ Via editor API | ❌ Not available | ✅ Frame grabber |
| Visual regression | ✅ Pixel diff | ✅ Screenshot compare | ❌ None | ✅ VLM + pixel diff |
| Automated input | ✅ Click/type | ✅ Editor commands | ❌ Manual only | ✅ PyAutoGUI + MCP |
| Console capture | ✅ Native | ✅ Log filtering | ⚠️ stdout only | ✅ Structured logs |
| Debugger integration | ✅ CDP protocol | ✅ Editor API | ❌ Not exposed | ✅ DAP bridge |
| Hot reload | ✅ HMR | ✅ Live coding | ⚠️ Limited | ✅ Script hot-swap |

---

## 2. The Problem: Why Humans Are Still in the Loop

### Current State (Painful)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Agent      │────▶│  Writes     │────▶│  Human      │
│  (Cookie)   │     │  Code       │     │  Tests      │
└─────────────┘     └─────────────┘     └──────┬──────┘
       ▲                                         │
       └─────────────────────────────────────────┘
              Human provides screenshots,
              logs, debugger output, feedback
```

### Target State (Autonomous)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Orchestrator│────▶│  Worker     │────▶│  Godot      │
│  (Cookie)   │     │  Agents     │     │  Project    │
└─────────────┘     └─────────────┘     └──────┬──────┘
       ▲                                         │
       │    ┌─────────────┐    ┌─────────────┐   │
       └────│ Screenshot  │◄───│  Running    │───┘
            │  Analysis   │    │  Game       │
            └─────────────┘    └─────────────┘
```

---

## 3. OpenClaw-Godot Architecture

### 3.1 System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OpenClaw Orchestrator (Cookie)                    │
│         ┌──────────────────────────────────────────────────┐         │
│         │         Task Queue + State Machine               │         │
│         └──────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
    ┌──────▼──────┐      ┌────────▼────────┐    ┌──────▼──────┐
    │   Coder     │      │   Tester        │    │  Research   │
    │   Worker    │      │   Worker        │    │   Worker    │
    └──────┬──────┘      └────────┬────────┘    └─────────────┘
           │                      │
           │             ┌────────▼────────┐
           │             │  Multi-Modal    │
           │             │  Worker (VLM)   │
           │             └────────┬────────┘
           │                      │
           └──────────┬───────────┘
                      │
    ┌─────────────────▼─────────────────────────────────────────┐
    │              OpenClaw-Godot Bridge                        │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
    │  │   MCP Server │  │   Screenshot │  │   Input      │   │
    │  │   (Extended) │  │   Capture    │  │   Injection  │   │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
    │         │                 │                 │            │
    │         └─────────────────┼─────────────────┘            │
    │                           │                              │
    │  ┌────────────────────────▼─────────────────────────┐   │
    │  │         Godot Editor Plugin (GDScript)           │   │
    │  │  ┌────────────┐ ┌────────────┐ ┌────────────┐   │   │
    │  │  │ Scene Tree │ │ Debug Log  │ │ Inspector  │   │   │
    │  │  │   API      │ │   Stream   │ │   Bridge   │   │   │
    │  │  └────────────┘ └────────────┘ └────────────┘   │   │
    │  └────────────────────────┬─────────────────────────┘   │
    └───────────────────────────┼──────────────────────────────┘
                                │
                      ┌─────────▼──────────┐
                      │  Godot Engine      │
                      │  (Running Project) │
                      └────────────────────┘
```

### 3.2 Component Breakdown

#### A. Extended MCP Server (`openclaw-godot-mcp`)

Fork of `ee0pdt/Godot-MCP` or `Coding-Solo/godot-mcp` with additions:

**New Tools:**
```typescript
// Screenshot capture
{
  name: "capture_screenshot",
  description: "Capture screenshot of running game or editor",
  args: { window: "game|editor", region?: Rect2 }
}

// Scene tree introspection
{
  name: "get_scene_tree",
  description: "Get full node tree with properties",
  args: { scene_path?: string, include_properties: boolean }
}

// Node property access
{
  name: "get_node_properties",
  description: "Get all properties of a specific node",
  args: { node_path: string }
}

// Script hot-reload
{
  name: "hot_reload_script",
  description: "Update a script without restarting",
  args: { script_path: string, code: string }
}

// Debug breakpoint info
{
  name: "get_debugger_state",
  description: "Get current breakpoints, stack trace, variables",
  args: {}
}

// Input injection
{
  name: "inject_input",
  description: "Send input events to running game",
  args: { type: "key|mouse|joy", action: string, pressed: boolean }
}

// Structured logging
{
  name: "get_structured_logs",
  description: "Get categorized logs (errors, warnings, prints)",
  args: { since?: timestamp, categories: string[] }
}
```

#### B. Godot Editor Plugin (`openclaw_godot_plugin`)

GDScript plugin that runs inside Godot Editor:

```gdscript
# Core capabilities
class_name OpenClawBridge
extends EditorPlugin

# HTTP/WebSocket server for MCP communication
var server: TCPServer
var connection: StreamPeerTCP

# Features:
# - Stream debug logs over WebSocket
# - Capture viewport frames on demand
# - Expose scene tree as JSON
# - Accept input injection commands
# - Hot-reload scripts via FileAccess
```

**Plugin Components:**
1. **Debug Streamer** — Captures `print()`, `push_error()`, `push_warning()` and streams to MCP
2. **Scene Introspector** — Serializes node tree with properties to JSON
3. **Screenshot Server** — Captures `Viewport.get_texture()` and encodes to PNG
4. **Input Injector** — Accepts input events and injects via `Input.parse_input_event()`
5. **Script Hot-Reloader** — Watches files and triggers `Resource.reload()`

#### C. Screenshot Capture Service (`screenshotd`)

Python service for capturing Godot window (works with or without plugin):

```python
# screenshotd.py
import mss  # Multi-screen shot
import numpy as np
from PIL import Image
import asyncio
import websockets
import json

class ScreenshotDaemon:
    def capture_window(self, window_title: str) -> bytes:
        # Use mss or X11/xdotool to find window
        # Return PNG bytes
        pass
    
    async def handle_ws(self, websocket):
        async for message in websocket:
            cmd = json.loads(message)
            if cmd["action"] == "capture":
                img = self.capture_window(cmd["window"])
                await websocket.send(img)
```

#### D. Input Injection Layer (`inputd`)

PyAutoGUI-based input for when plugin isn't available:

```python
# inputd.py
import pyautogui
import asyncio

class InputDaemon:
    def click(self, x: int, y: int):
        pyautogui.click(x, y)
    
    def keypress(self, key: str):
        pyautogui.press(key)
    
    def type(self, text: str):
        pyautogui.typewrite(text)
```

---

## 4. Worker Agent Workflows

### 4.1 Coder Worker

```yaml
role: Coder
model: qwen3-coder-next
thinking: medium

workflow:
  1. Receive feature spec from Orchestrator
  2. Use MCP tools to:
     - Get current scene structure
     - Read existing scripts
     - Create/modify scripts via MCP
  3. Hot-reload changes (no restart)
  4. Return: Files modified, summary of changes
```

### 4.2 Tester Worker

```yaml
role: Tester
model: kimi-k2.5
thinking: medium

workflow:
  1. Receive test scenario from Orchestrator
  2. Use MCP to:
     - Run project in debug mode
     - Inject input sequence (move, jump, etc.)
     - Capture screenshots at key moments
  3. Analyze:
     - Check logs for errors
     - Verify expected output
  4. Return: Pass/fail, logs, screenshots, analysis
```

### 4.3 Visual Verification Worker (Multi-Modal)

```yaml
role: VisualVerifier
model: gemini-3-pro-preview  # or local Qwen2.5-VL
thinking: high

workflow:
  1. Receive screenshot + verification prompt
  2. Analyze image:
     - "Is the player character visible?"
     - "Are all UI elements rendered correctly?"
     - "Is the background color #ff0000 as requested?"
  3. Return: Boolean pass/fail + reasoning
```

### 4.4 Debugger Worker

```yaml
role: Debugger
model: gemini-3-pro-preview
thinking: high

workflow:
  1. Receive error report from Tester
  2. Use MCP to:
     - Get full scene tree state
     - Get script source at error location
     - Get debugger state (stack, variables)
  3. Analyze root cause
  4. Propose fix or request more info
  5. Return: Root cause analysis, proposed fix
```

---

## 5. Orchestrator State Machine

```python
# Pseudo-code for Cookie's workflow
class FeatureImplementationWorkflow:
    states = [
        "SPEC_RECEIVED",
        "CODER_ASSIGNED",
        "CODE_COMPLETE",
        "TESTER_ASSIGNED", 
        "TEST_RUNNING",
        "VERIFYING_OUTPUT",
        "ITERATING",
        "COMPLETE",
        "NEEDS_HUMAN"
    ]
    
    def run(self, spec: FeatureSpec):
        # Spawn Coder Worker
        coder_result = spawn_worker("coder", spec)
        
        max_iterations = 5
        for i in range(max_iterations):
            # Spawn Tester Worker
            test_result = spawn_worker("tester", coder_result)
            
            if test_result.passed:
                # Visual verification
                visual_result = spawn_worker("visual_verifier", test_result.screenshots)
                
                if visual_result.passed:
                    return WorkflowResult(success=True)
                else:
                    # Feed back to coder
                    coder_result = spawn_worker("coder", {
                        "spec": spec,
                        "feedback": visual_result.feedback
                    })
            else:
                # Debugging needed
                debug_result = spawn_worker("debugger", test_result)
                
                if debug_result.confidence > 0.8:
                    # Auto-fix
                    coder_result = spawn_worker("coder", {
                        "spec": spec,
                        "fix": debug_result.proposed_fix
                    })
                else:
                    return WorkflowResult(success=False, needs_human=True)
        
        return WorkflowResult(success=False, max_iterations_reached=True)
```

---

## 6. Integration with DiscordOrchestration

Since we're using DiscordOrchestration (not OpenClaw's buggy `sessions_spawn`):

```
Discord Channels:
  #oc-godot-tasks     → Task queue for OpenClaw-Godot
  #oc-godot-results   → Results from workers
  #oc-godot-chat      → Orchestrator coordination

Worker Types:
  oc-godot-coder      → Code modification via MCP
  oc-godot-tester     → Run tests, capture output
  oc-godot-visual     → VLM screenshot analysis
  oc-godot-debugger   → Error analysis

Task Format:
  [project:aerobeat-input-mediapipe-python]
  [task:implement_feature]
  [feature:Add visual debug overlay for hand tracking]
  [model:coder]
  [thinking:medium]
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Fork `ee0pdt/Godot-MCP` as base
- [ ] Add WebSocket transport option (for persistent connection)
- [ ] Create `openclaw_godot_plugin` skeleton
- [ ] Implement basic debug log streaming
- [ ] Test with AeroBeat `.testbed` project

### Phase 2: Visual Layer (Week 3-4)
- [ ] Implement screenshot capture in plugin
- [ ] Create `screenshotd` fallback (mss + xdotool)
- [ ] Add MCP tool: `capture_screenshot`
- [ ] Test screenshot → VLM → action loop
- [ ] Visual verification worker prototype

### Phase 3: Input & Hot Reload (Week 5-6)
- [ ] Implement input injection in plugin
- [ ] Create `inputd` fallback (PyAutoGUI)
- [ ] Add MCP tools: `inject_input`, `hot_reload_script`
- [ ] Tester worker with input sequences
- [ ] End-to-end test: Code → Run → Verify → Iterate

### Phase 4: Scene Introspection (Week 7-8)
- [ ] Full scene tree serialization
- [ ] Node property access
- [ ] Debugger state capture (breakpoints, stack)
- [ ] Debugger worker
- [ ] Error → Debug → Fix loop

### Phase 5: Integration (Week 9-10)
- [ ] Orchestrator workflow implementation
- [ ] DiscordOrchestration integration
- [ ] Test with real AeroBeat feature
- [ ] Documentation + examples

---

## 8. First Milestone: Working Demo

**Goal:** Implement a simple feature end-to-end without human intervention

**Feature:** "Add a button that changes the background color when clicked"

**Workflow:**
1. Orchestrator spawns Coder Worker
2. Coder creates button node + script via MCP
3. Coder hot-reloads changes
4. Orchestrator spawns Tester Worker
5. Tester runs project, clicks button (input injection)
6. Tester captures screenshot
7. Orchestrator spawns Visual Worker
8. Visual Worker verifies background color changed
9. If pass → done! If fail → loop back to step 2 with feedback

---

## 9. Files to Create

```
~/Documents/GitHub/openclaw-godot/
├── README.md                           # This overview
├── PLAN.md                             # Detailed implementation plan
├── mcp-server/                         # Extended MCP server
│   ├── src/
│   ├── package.json
│   └── README.md
├── godot-plugin/                       # GDScript plugin
│   ├── addons/openclaw_bridge/
│   │   ├── openclaw_bridge.gd
│   │   ├── debug_streamer.gd
│   │   ├── screenshot_server.gd
│   │   ├── scene_introspector.gd
│   │   └── input_injector.gd
│   └── plugin.cfg
├── screenshotd/                        # Screenshot service
│   ├── screenshotd.py
│   └── requirements.txt
├── inputd/                             # Input injection service
│   ├── inputd.py
│   └── requirements.txt
├── workers/                            # Worker agent definitions
│   ├── coder.md
│   ├── tester.md
│   ├── visual_verifier.md
│   └── debugger.md
└── orchestrator/                       # Orchestrator workflows
    ├── workflows.md
    └── state_machines.md
```

---

## 10. Next Steps

1. **Evaluate ee0pdt/Godot-MCP vs Coding-Solo/godot-mcp** as base
2. **Create `openclaw-godot` repo** with initial structure
3. **Prototype screenshot capture** (plugin vs external daemon)
4. **Test with AeroBeat .testbed** for real-world validation
5. **Design DiscordOrchestration integration**

---

## UPDATE: 2026-02-12

**Repository Created:** https://github.com/derrickbarra/openclaw-godot

**Scaffolding Complete:**
- ✅ Python bridge modules (`godot_bridge/`)
- ✅ GDScript plugin (`src/plugin/`)
- ✅ Worker definitions (`workers/`)
- ✅ First example (`examples/button_background/`)
- ✅ Architecture docs (`docs/ARCHITECTURE.md`)
- ✅ pyproject.toml for pip install

**Changed Approach:**
- Skipped MCP server middleman (OpenClaw has direct access)
- Simplified to Python + direct file/process control
- Ready for Phase 0: Prove autonomous loop with button_background example

---

## UPDATE: 2026-02-12 — DiscordOrchestration Integration

After reviewing Chip's **DiscordOrchestration** system (in `~/Documents/GitHub/discord-orchestration/`), the integration approach is clear:

### Don't Reinvent — Leverage!

Chip's system already handles:
- ✅ Discord as message bus (task-queue, results channels)
- ✅ Dynamic agent spawning (fresh agent per task)
- ✅ Atomic task claiming (via Discord reactions)
- ✅ Worker workspaces (isolated directories)
- ✅ RESULT.txt + SUMMARY.txt pattern
- ✅ Retry logic with exponential backoff
- ✅ discord-sanitize skill for markdown

### OpenClaw-Godot Integration

**We don't build a new orchestrator** — we create **Godot-specific workers** that use DiscordOrchestration:

```
┌──────────────────────────────────────────────────────────────┐
│                    DiscordOrchestration                      │
│                      (Chip's System)                         │
│                                                              │
│  #task-queue ──► Orchestrator ──► Spawns Godot Worker       │
│                                      │                       │
│                                      ▼                       │
│  #results ◄───── SUMMARY.txt ◄─── Agent Workspace            │
│                      (screenshot proof)                      │
└──────────────────────────────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  godot_bridge │  ◄── Our Python modules
                    │  (Python)     │      (capture, input, runner)
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Godot Project │  ◄── Test scenes
                    │ (main_auto_   │      (button_background, etc.)
                    │  test.tscn)   │
                    └───────────────┘
```

### Worker Types for Godot

| Worker | Task | Output |
|--------|------|--------|
| **godot-coder** | Implement feature in GDScript | RESULT.txt (files changed) |
| **godot-tester** | Run scene, capture screenshot | SUMMARY.txt + screenshot.png |
| **godot-visual** | VLM-verify screenshot | SUMMARY.txt (pass/fail) |
| **godot-debugger** | Analyze errors, propose fixes | SUMMARY.txt + fix suggestions |

### Task Format

```
[project:button_background]
[worker:godot-tester]
[model:primary]
[thinking:medium]

Run the auto-test scene and verify background changes from blue to red.
Attach screenshot proof.
```

### File Locations

| Component | Location |
|-----------|----------|
| DiscordOrchestration | `~/Documents/GitHub/discord-orchestration/` |
| OpenClaw-Godot | `~/Documents/GitHub/openclaw-godot/` |
| Test Projects | `openclaw-godot/godot/*/` |
| Worker Output | `discord-orchestration/workers/agent-*/tasks/*/` |

### Next Steps

1. **Install discord-sanitize skill** (prevents Discord markdown issues)
2. **Create godot-coder worker template** (AGENTS.md + TOOLS.md)
3. **Submit first task via Discord** (test button_background)
4. **Iterate on worker definitions** based on results

---

**Status:** Scaffolding Complete → DiscordOrchestration Integration  
**Target:** First Discord-mediated task within 1 week  
**Owner:** Cookie 🍪 + Derrick + Chip's Orchestration System
