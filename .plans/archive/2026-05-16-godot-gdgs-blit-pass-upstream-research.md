# OpenClaw-Godot

**Date:** 2026-05-16  
**Status:** Complete (archived 2026-05-26)
**Last Updated:** 2026-05-26 21:53 EDT
**Blocked Reason:** Archived on 2026-05-26 after the master Godot bug-hunt lane absorbed this completed upstream-research slice.
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
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/archive/2026-05-16-godot-gdgs-blit-pass-upstream-research.md`
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
- `/home/derrick/.openclaw/workspace/projects/openclaw-godot/.plans/archive/2026-05-16-godot-gdgs-blit-pass-upstream-research.md`
- supporting docs/notes as needed

**Status:** ✅ Complete

**Results:** Independently audited the upstream-history memo against the attached AeroBeat narrowing artifacts (`REF-01` through `REF-05`) and agreed with its core negative conclusion: there is still no strong exact upstream match and no convincing post-4.6.2 landed fix signal for this specific `CompositorEffect` + custom `RenderingDevice` compute + `No Present still crashes` + `BLIT_PASS` device-loss shape. Audit verdict: the most evidence-backed next lane is a **two-step order** rather than a single bet. **First**, run one cheap confirmation pass on the latest available Godot 4.7-dev/nightly or master build, because that is the lowest-cost way to catch an unadvertised engine-side fix and removes guesswork before filing upstream. **Second**, if the repro still survives there, open a new focused upstream Godot issue immediately using the already-strong reduction package (minimal GDGS scene, `No Present` evidence, Intel Iris Xe / Linux / Wayland / Vulkan context, and links to `REF-01` through `REF-05`). I do **not** recommend starting with local engine-side investigation before that issue is filed: the current evidence is already strong enough to justify upstream review, while an engine fork/debug lane is materially more expensive and still lacks proof that the bug is locally patchable without maintainer guidance. Confidence: **medium-high** on the ordering, **high** that “just try a newer build and hope” is too weak, and **low** that a newer build is likely to already contain a fix. This recommendation beats the alternatives because it preserves the cheap sanity check, avoids overclaiming that upstream already fixed it, and avoids paying the highest-cost investigation path before using the existing narrowed repro to ask Godot maintainers whether the usage is valid or backend-buggy. Validated against `REF-01` through `REF-06`. 

---

## Final Results

**Archived Note:** Archived on 2026-05-26 after the master Godot bug-hunt lane absorbed this completed upstream-research slice.

**Status:** ✅ Complete

**What We Built:** Produced an upstream-history research memo plus an independent audit recommendation for the next Godot lane. The finished call is: **(1) test the narrowed repro once on the newest practical Godot 4.7-dev/nightly or master build, then (2) if it still reproduces, file a focused upstream Godot issue immediately with the existing reduction evidence; only after that should Derrick consider a local engine-side investigation lane unless maintainer feedback or new evidence changes the owner.**

**Reference Check:** `REF-01` through `REF-06` were used in the audit. The final recommendation matches the strongest common signal across the sources: no exact prior art, no clearly landed fix after 4.6.2, and no evidence strong enough to skip either the cheap newer-build sanity check or the upstream-report step.

**Commits:**
- No commit created in this audit/recommendation pass.

**Lessons Learned:**
- Upstream-history research can narrow confidence, but absence of a matching report is not evidence that a newer build already fixes the bug.
- Once a repro is already this tight, opening an upstream issue after one version-sanity pass is a better cost/learning trade than jumping straight into local engine surgery.

---

*Completed on 2026-05-26*
