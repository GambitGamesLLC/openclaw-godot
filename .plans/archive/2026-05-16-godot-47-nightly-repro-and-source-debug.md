# OpenClaw-Godot

**Date:** 2026-05-16  
**Status:** Complete (archived 2026-05-26)
**Last Updated:** 2026-05-26 21:53 EDT
**Blocked Reason:** Archived on 2026-05-26 after the master Godot bug-hunt lane absorbed this completed nightly-repro/source-debug pivot slice.
**Agent:** Chip 🐱‍💻

---

## Goal

Validate the GDGS-shaped `BLIT_PASS` / Vulkan device-loss repro on the latest practical Godot 4.7-dev/nightly build, and if the failure remains, pivot immediately into source-level investigation on the latest Godot fork/branch instead of filing a weak upstream report.

---

## Overview

The upstream-history pass did not find a convincing exact match or a strong post-4.6.2 fix that likely already resolves this problem. That means the cheapest remaining sanity check is still to run the repro on a newer Godot build. If the failure disappears or materially changes there, that gives us a version-delta lane instead of blind engine surgery.

But Derrick’s caution is correct: if 4.7-dev/nightly behaves the same way, we should not jump straight to filing a vague Godot issue that only says “something fails around `BLIT_PASS`.” At that point, the stronger move is to investigate the latest Godot source ourselves on our fork/branch and narrow the failing engine/resource path enough to produce either a real fix or a materially sharper upstream report. We should also preserve the live alternative hypothesis that GDGS may still be feeding Godot an invalid or unsupported resource/state pattern that the engine is merely surfacing poorly.

So this slice has a two-stage design. Stage 1 is a cheap version-check repro against the latest practical 4.7-dev/nightly or master-derived build. Stage 2 only triggers if the bug persists: source-level investigation in the latest Godot lane, focused on the actual engine code around the `BLIT_PASS` breadcrumb and the compositor / `RenderingDevice` / texture-resource transitions that the GDGS repro exercises.

---

## REFERENCES

| ID | Description | Path |
| --- | --- | --- |
| `REF-01` | Godot upstream-history research memo | `/home/derrick/.openclaw/workspace/projects/openclaw-godot/docs/gdgs-blit-pass-upstream-research-2026-05-16.md` |
| `REF-02` | Godot upstream-history research plan/results | `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/archive/2026-05-16-godot-gdgs-blit-pass-upstream-research.md` |
| `REF-03` | GDGS ownership map | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/docs/gdgs-blit-pass-ownership-map.md` |
| `REF-04` | GDGS source trace | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/docs/gdgs-blit-pass-source-trace.md` |
| `REF-05` | GDGS direct-dispatch isolation notes | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/docs/gdgs-direct-dispatch-isolation.md` |
| `REF-06` | Active GDGS investigation plan/results | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/.plans/2026-05-16-gdgs-source-level-blit-pass-investigation.md` |
| `REF-07` | Godot-owning repo for plan/beads/source-debug lane | `/home/derrick/.openclaw/workspace/projects/openclaw-godot/` |

---

## Tasks

### Task 1: Reproduce the failure on the latest practical Godot 4.7-dev/nightly build

**Bead ID:** `openclaw-godot-ua1`  
**SubAgent:** `primary` (for `qa`)  
**Role:** `qa`  
**References:** `REF-01`, `REF-03`, `REF-04`, `REF-05`, `REF-06`, `REF-07`  
**Prompt:** Acquire or identify the latest practical Godot 4.7-dev/nightly or master-derived build available in this environment, then rerun the existing GDGS control-scene repro against it. Capture whether the failure disappears, shifts materially, or remains effectively identical. Save durable artifacts and document the exact version/build used.

**Folders Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/`
- `/home/derrick/.openclaw/workspace/.temp/`

**Files Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/archive/2026-05-16-godot-47-nightly-repro-and-source-debug.md`
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/docs/gdgs-godot-47-dev5-nightly-repro-2026-05-16.md`
- `/home/derrick/.openclaw/workspace/.temp/gdgs-godot-47-dev5-nightly-repro-2026-05-16/`

**Status:** ✅ Complete

**Results:** QA claimed `openclaw-godot-ua1`, acquired the latest practical official Godot 4.7-dev build readily available in this environment (`Godot Engine v4.7.dev5.official.a8643700c`, upstream commit `a8643700ce8affae9fed0d2688b9f7867f5b7d4e`), and reran the existing GDGS control-scene CLI repro on the real Surface Pro 8 Wayland/Vulkan path using the same per-case harness as the prior `REF-05` / `REF-06` baselines. Durable artifacts were captured under `/home/derrick/.openclaw/workspace/.temp/gdgs-godot-47-dev5-nightly-repro-2026-05-16/`, and a short result note was added at `/home/derrick/.openclaw/workspace/projects/openclaw-godot/docs/gdgs-godot-47-dev5-nightly-repro-2026-05-16.md`.

What actually happened: the failure did **not** disappear and did **not** materially improve. The case matrix remained effectively identical to 4.6.2: `compositor`, `direct_texture_world`, `direct_texture_canvas`, and `no_present` all still exited `134`, while `effect_disabled` remained the only stable branch (`0`) and still produced only the same blank/background-only baseline frame. The decisive `no_present` branch still reached valid compositor textures and then later died at `Last known breadcrumb: BLIT_PASS` with `Vulkan device was lost.`

The meaningful delta is diagnostic, not curative: 4.7-dev5 now emits repeated engine-side push-constant validation errors in the GDGS compute path before the same later `BLIT_PASS` device loss (`compute_list_set_push_constant()` / `compute_list_dispatch()` complaining that pipelines expecting `8`, `4`, or `12` bytes were supplied `16` bytes and then considered the required push constant missing). So the QA verdict is: **behavior remains effectively identical at the feature/bug level, but the newer build adds a sharper source-debug clue.** This means Task 2 should now activate, with specific attention to GDGS push-constant usage and whether 4.7-dev's stricter validation is exposing a real plugin-side contract bug versus an engine/backend handling issue.

---

### Task 2: If 4.7-dev/nightly still reproduces, establish the local Godot source-debug lane

**Bead ID:** `openclaw-godot-d5t`  
**SubAgent:** `primary` (for `research`)  
**Role:** `research`  
**References:** `REF-01`, `REF-03`, `REF-04`, `REF-05`, `REF-06`, `REF-07`  
**Prompt:** If the nightly repro still fails, establish the latest practical local Godot fork/branch lane for source-level debugging. Determine repo/remotes/branch strategy, map where the `BLIT_PASS` breadcrumb and relevant compositor / RenderingDevice / texture-transition paths live in current Godot source, and document the first concrete engine-side investigation targets.

**Folders Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/`
- `/home/derrick/.openclaw/workspace/projects/godot/`

**Files Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/archive/2026-05-16-godot-47-nightly-repro-and-source-debug.md`
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/docs/gdgs-godot-source-debug-lane-2026-05-16.md`

**Status:** ✅ Complete

**Results:** Research claimed `openclaw-godot-d5t`, then checked what was actually available locally. What we found first is important: `/home/derrick/.openclaw/workspace/projects/openclaw-godot/godot/` was **not** a Godot engine source checkout at all, just the small local example/test-project folder inside this repo. There were no existing Godot-source remotes/branches to inspect there. So the practical fix was to establish the missing source lane explicitly instead of pretending it already existed.

A fresh upstream Godot source checkout was created at `/home/derrick/.openclaw/workspace/projects/godot` using the SSH remote `git@github.com:godotengine/godot.git`. From there, two concrete investigation anchors were established: local branch `godot-47-dev5-a8643700c` pinned to the exact nightly repro commit (`a8643700ce8affae9fed0d2688b9f7867f5b7d4e`) and local branch `gdgs-blit-pass-debug-master` pinned to the latest practical local upstream `master` available during this pass (`321b8c94...`). The resulting branch strategy is: use `godot-47-dev5-a8643700c` for exact repro-parity inspection and cut future instrumentation/fix branches from `gdgs-blit-pass-debug-master`, keeping `master` clean.

Source mapping then identified the first engine-side files/subsystems to inspect. `BLIT_PASS` itself is set in `servers/rendering/rendering_device.cpp` when the swapchain/screen blit draw list is begun, defined in `servers/rendering/rendering_device_commons.h`, and decoded during Vulkan device-loss reporting in `drivers/vulkan/rendering_device_driver_vulkan.cpp`. The compositor callback path relevant to GDGS lives through `scene/resources/compositor.cpp`, `servers/rendering/storage/compositor_storage.cpp`, `servers/rendering/renderer_rd/renderer_scene_render_rd.cpp::_process_compositor_effects(...)`, and the actual callback insertion points in `servers/rendering/renderer_rd/forward_clustered/render_forward_clustered.cpp` (especially the post-transparent path). The compute/push-constant validation path that produced the new dev5 errors lives in `servers/rendering/rendering_shader_container.cpp` (SPIR-V reflection of push-constant size) and `servers/rendering/rendering_device.cpp` (`compute_list_bind_compute_pipeline`, `compute_list_set_push_constant`, and `compute_list_dispatch`).

The strongest new finding is that the 4.7-dev5 errors are very plausibly exposing a **real GDGS push-constant contract violation**, not just a random engine quirk. GDGS currently pads all push-constant payloads to 16 bytes in `addons/gdgs/runtime/render/gaussian_rendering_device_context.gd`, then reuses that padded payload across the radix-sort compute passes in `addons/gdgs/runtime/render/gaussian_renderer.gd`. But the shader declarations appear to reflect as different exact sizes: `radix_sort_spine.glsl` -> `4` bytes (`int pass`), `radix_sort_upsweep.glsl` -> `8` bytes (`int pass`, `uint in_offset`), and `radix_sort_downsweep.glsl` -> `12` bytes (`int pass`, `uint in_offset`, `uint out_offset`). That lines up directly with the dev5 validation stream complaining that pipelines expecting `4`, `8`, and `12` bytes were all supplied `16` bytes, after which dispatch reports the required push constant as missing.

That does **not** fully clear Godot, because the later crash still lands near the compositor/output lane and ends at `Last known breadcrumb: BLIT_PASS` with device loss on Intel Vulkan/Wayland. So the research conclusion is: the likely next patch/debug lane is **both**, but in order. First audit/fix the GDGS push-constant contract because the new evidence points straight at it; then, if `BLIT_PASS` / device loss survives, instrument the Godot `RenderingDevice` compute-list/compositor path and inspect the post-transparent render-buffer / texture-usage sequencing. Durable documentation for this source-debug lane was added at `/home/derrick/.openclaw/workspace/projects/openclaw-godot/docs/gdgs-godot-source-debug-lane-2026-05-16.md`. No engine patching was attempted in this task.

---

### Task 3: Audit whether we should continue into local engine debugging or stop earlier

**Bead ID:** `openclaw-godot-eby`  
**SubAgent:** `primary` (for `auditor`)  
**Role:** `auditor`  
**References:** `REF-01`, `REF-03`, `REF-04`, `REF-05`, `REF-06`, `REF-07`  
**Prompt:** Audit the nightly repro outcome and the proposed Godot source-debug lane. Decide whether the evidence supports continuing into local engine debugging, whether the version delta already answered the question, or whether a stronger upstream report is now possible without more local work.

**Folders Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/`

**Files Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/archive/2026-05-16-godot-47-nightly-repro-and-source-debug.md`
- supporting docs/notes as needed

**Status:** ⏳ Pending

**Results:** Pending.

---

## Final Results

**Archived Note:** Archived on 2026-05-26 after the master Godot bug-hunt lane absorbed this completed nightly-repro/source-debug pivot slice.

**Status:** ✅ Complete

**What We Built:** We validated the existing GDGS control-scene repro on the latest practical official Godot 4.7-dev snapshot we could acquire in this environment (`4.7.dev5.official.a8643700c`) and captured a fresh artifact package proving the bug still reproduces on the newer build.

**Reference Check:** `REF-03`, `REF-04`, `REF-05`, and `REF-06` remained valid: the same real-machine control-scene repro shape still fails at the same high-level `BLIT_PASS` / Vulkan-device-loss boundary. `REF-01` was also satisfied in the narrower sense that the newer version check was still worth doing, but it did not remove the need for source-level follow-up; instead it added a sharper push-constant validation clue for the Task 2 lane.

**Commits:**
- Pending.

**Lessons Learned:**
- A cheap version check is worth doing, but not enough reason to file a vague upstream report if the failure remains opaque.
- If nightly still fails, the next value comes from source-level narrowing in Godot, not from restating `BLIT_PASS` as if it were a root cause.

---

*Completed on 2026-05-26*
