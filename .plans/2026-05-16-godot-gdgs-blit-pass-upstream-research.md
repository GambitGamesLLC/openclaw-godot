# OpenClaw-Godot

**Date:** 2026-05-16  
**Status:** In Progress  
**Agent:** Chip 🐱‍💻

---

## Goal

Research whether the GDGS-shaped `BLIT_PASS` / Vulkan device-loss problem on Godot 4.6.2 has already been reported, discussed, or fixed upstream, especially in issues, PRs, and post-4.6.2 beta/release work.

---

## Overview

The AeroBeat vendor-side investigation has already narrowed the failure substantially. GDGS produces valid compositor textures, `No Present` still crashes, and a narrow direct-dispatch isolation pass did not materially change the `BLIT_PASS` / Vulkan device-loss boundary. That weakens the case for a simple GDGS-side fix and strengthens the case that the remaining owner may be Godot backend behavior or a narrower GDGS↔Godot render-resource interaction.

Before opening a Godot implementation/debugging lane, the cheapest high-value move is upstream research. We should first determine whether this failure shape is already known, whether a related PR landed after Godot 4.6.2, and whether a newer beta/release likely already contains the fix. If so, the best outcome for Derrick may be to validate against a newer build instead of immediately sinking time into engine patch work.

This slice is research-first and GitHub-history-heavy: search issues, PRs, release notes, and engine/backend discussions for `BLIT_PASS`, Vulkan device loss, compositor effects, RenderingDevice texture/resource hazards, Intel Iris Xe, Wayland, and related Godot 4.6.x / beta changes. The output should be a decision memo: already-known bug, likely-fixed-upstream, still-open regression, or no strong prior art.

---

## REFERENCES

| ID | Description | Path |
| --- | --- | --- |
| `REF-01` | GDGS upstream issue with latest negative isolation update | `https://github.com/ReconWorldLab/godot-gaussian-splatting/issues/12` |
| `REF-02` | AeroBeat GDGS ownership map | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/docs/gdgs-blit-pass-ownership-map.md` |
| `REF-03` | AeroBeat GDGS source trace | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/docs/gdgs-blit-pass-source-trace.md` |
| `REF-04` | AeroBeat direct-dispatch isolation notes | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/docs/gdgs-direct-dispatch-isolation.md` |
| `REF-05` | Active AeroBeat investigation plan/results | `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/.plans/2026-05-16-gdgs-source-level-blit-pass-investigation.md` |
| `REF-06` | Godot fork lane / owning repo for research artifacts | `/home/derrick/.openclaw/workspace/projects/openclaw-godot/` |

---

## Tasks

### Task 1: Research Godot issues, PRs, and release notes for this failure shape

**Bead ID:** `openclaw-godot-m4l`  
**SubAgent:** `primary` (for `research`)  
**Role:** `research`  
**References:** `REF-01`, `REF-02`, `REF-03`, `REF-04`, `REF-05`, `REF-06`  
**Prompt:** Search upstream Godot issues, PRs, release notes, and related discussions for this problem shape: Vulkan `BLIT_PASS` device loss, compositor-effect/rendering-device texture interactions, Intel Iris Xe / Wayland sensitivity, and any post-4.6.2 fixes or betas that plausibly cover the same boundary. Produce a concise evidence-backed memo with links, candidate matching reports/PRs, and a preliminary answer on whether a newer version likely already contains the fix.

**Folders Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/`

**Files Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/2026-05-16-godot-gdgs-blit-pass-upstream-research.md`
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/docs/gdgs-blit-pass-upstream-research-2026-05-16.md`

**Status:** ✅ Complete

**Results:** Completed upstream-history research across Godot issues, PRs, and 4.6 / 4.6.1 / 4.6.2 release-changelog material. Added `/home/derrick/.openclaw/workspace/projects/openclaw-godot/docs/gdgs-blit-pass-upstream-research-2026-05-16.md` with evidence-backed links and conclusions. The strongest finding was negative: no exact upstream match for the GDGS-shaped `CompositorEffect` + `RenderingDevice` + `No Present still crashes` + `BLIT_PASS` device-loss pattern. I found adjacent compositor/RD issues (`#96737`, `#108781`, `#99493`, `#118292`) and multiple generic `BLIT_PASS` / Vulkan device-loss reports (`#71929`, `#106192`, `#110222`, `#116172`, `#118852`), but nothing that clearly says this exact bug is already reported or already fixed. Release/changelog review also did not show a strong post-4.6.2 fix candidate; the most adjacent landed PR was `#113236`, but it is D3D12/pending-clear focused rather than a clear Vulkan compositor fix. Recommendation from the memo: do one cheap repro pass on the latest 4.7-dev/master build, but if it still reproduces, treat a new focused upstream Godot issue as the likely next move. Validated against `REF-01` through `REF-06`. 

---

### Task 2: Audit the upstream-history conclusion and recommend the next lane

**Bead ID:** `openclaw-godot-gfp`  
**SubAgent:** `primary` (for `auditor`)  
**Role:** `auditor`  
**References:** `REF-01`, `REF-02`, `REF-03`, `REF-04`, `REF-05`, `REF-06`  
**Prompt:** Independently audit the research memo and determine the most evidence-backed next move: test a newer Godot beta/release, begin local engine-side investigation, or continue issue-only monitoring if the prior art is too weak. Close only when the recommendation is concrete and justified.

**Folders Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/`

**Files Created/Deleted/Modified:**
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/2026-05-16-godot-gdgs-blit-pass-upstream-research.md`
- supporting docs/notes as needed

**Status:** ⏳ Pending

**Results:** Pending.

---

## Final Results

**Status:** ⚠️ Draft

**What We Built:** Pending execution.

**Reference Check:** Pending.

**Commits:**
- Pending.

**Lessons Learned:**
- Upstream-history research is the cheapest sanity check before opening a heavy engine-debug lane.
- If the bug already has a landed fix in a newer beta/release, version validation may beat local engine surgery.

---

*Completed on Pending*
