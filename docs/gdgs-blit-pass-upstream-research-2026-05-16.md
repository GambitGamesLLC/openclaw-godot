# GDGS-shaped `BLIT_PASS` / Vulkan device-loss upstream research

**Date:** 2026-05-16  
**Repo:** `/home/derrick/.openclaw/workspace/projects/openclaw-godot`  
**Question:** Has the GDGS-shaped Godot 4.6.2 `BLIT_PASS` / Vulkan device-loss failure already been reported, discussed, or fixed upstream?

## Short answer

**No exact upstream match turned up.** I found several **adjacent** Godot issues around `CompositorEffect`, `RenderingDevice`, storage/texture usage, and generic Vulkan `BLIT_PASS` device-loss crashes, but **no strong prior report that matches the current shape closely enough**:

- custom `CompositorEffect`
- GDGS-owned `RenderingDevice` compute work
- valid compositor texture production
- crash still reproducing in a **No Present** path
- late engine breadcrumb remaining `BLIT_PASS`
- Intel Iris Xe / Linux / Wayland / Vulkan sensitivity

## Strongest evidence found

### 1. Upstream has real `CompositorEffect` / `RenderingDevice` bugs, but mostly not this crash shape

1. **`CompositorEffect` in Mobile renderer throws `TEXTURE_USAGE_STORAGE_BIT` error**  
   <https://github.com/godotengine/godot/issues/96737>
   - Open.
   - Confirms that Godot's compositor/render-buffer setup has had real storage-usage flag gaps.
   - Relevant because GDGS also depends on engine-managed textures and storage usage expectations.
   - **But** this issue is about explicit uniform/storage-flag errors, not a late `BLIT_PASS` device loss after valid texture output.

2. **Linux C# Compositor Effect cannot use color texture/layer because storage bit is missing**  
   <https://github.com/godotengine/godot/issues/108781>
   - Closed as duplicate of #96737.
   - Shows the same engine-side storage-usage class also exists on Linux.
   - **Still not a direct match** to the GDGS failure.

3. **`[Compositor] unable to access depth texture in shader`**  
   <https://github.com/godotengine/godot/issues/99493>
   - Closed as duplicate of #96737.
   - Relevant because GDGS touches compositor color/depth textures.
   - **But** again, this is an explicit usage-flag/access problem, not the observed “valid textures first, device lost later” pattern.

4. **`Mutating a published Texture2DRD's texture_rd_rid from a CompositorEffect callback invalidates dependent material uniform sets`**  
   <https://github.com/godotengine/godot/issues/118292>
   - Open.
   - Reproduced on **4.6.1**, **4.5**, **4.7 dev 3**, and **master** per report/comment.
   - Important because it shows **CompositorEffect + RD resource mutation remains a live upstream problem even in newer builds**.
   - **But** its failure mode is invalidated uniform sets, not Vulkan device loss.

5. **`RenderingDevice.uniform_buffer_create` fails after running a CompositorEffect for a couple minutes**  
   <https://github.com/godotengine/godot/issues/103400>
   - Closed as usage error / RID leak in user code.
   - Useful mainly as a caution that some compositor/RD issues are plugin misuse rather than engine bugs.

### 2. `BLIT_PASS` / Vulkan device loss exists upstream, but as a broad symptom across unrelated bugs

1. **Tracker: Vulkan swapchain/device-lost crashes happening randomly**  
   <https://github.com/godotengine/godot/issues/71929>
   - Long-running tracker for generic Vulkan device-loss behavior.
   - Confirms Godot has a broader history of device-loss incidents across vendors and scenes.
   - **Too generic** to treat as a match.

2. **Editor crashes with SIGILL after `Vulkan device was lost` on Linux Intel iGPU**  
   <https://github.com/godotengine/godot/issues/106192>
   - Linux + Intel integrated GPU.
   - Breadcrumbs include `BLIT_PASS` and `UI_PASS`.
   - Good evidence that **Linux Intel Vulkan device loss with `BLIT_PASS` breadcrumbs is not unique to GDGS**.
   - **But** it is not tied to `CompositorEffect` or custom RD compute.

3. **Windows build crashes on RX 7900 XT (`Vulkan device was lost`)**  
   <https://github.com/godotengine/godot/issues/110222>
   - Also shows repeated `BLIT_PASS` breadcrumbs.
   - Useful mainly to show `BLIT_PASS` is **not specific enough** on its own to identify the root cause.

4. **Crash issues Godot 4.5 & 4.6 Vulkan Forward+ (SDFGI)**  
   <https://github.com/godotengine/godot/issues/116172>
   - Another unrelated rendering path still surfacing `BLIT_PASS` breadcrumbs.

5. **Godot crashes with signal 4 when configuring GPUParticles3D**  
   <https://github.com/godotengine/godot/issues/118852>
   - Reported on **4.6.2** with Intel iGPU and `BLIT_PASS` breadcrumbs.
   - Again: useful evidence that `BLIT_PASS` is a shared endpoint, not a fingerprint for this compositor/RD bug.

### 3. Landed PRs/releases do not show a clear post-4.6.2 fix for this exact boundary

#### Relevant historical PRs

1. **Renderer hooks / `CompositorEffect` introduction**  
   <https://github.com/godotengine/godot/pull/80214>
   - Merged in 2024.
   - Establishes the feature surface GDGS is using.

2. **Fix `CompositorEffect` not setting post-transparent callback on init**  
   <https://github.com/godotengine/godot/pull/110249>
   - Merged 2025-09-23.
   - Real compositor fix, but narrowly about callback initialization.
   - **Not a likely fix** for the GDGS-shaped device-loss path.

3. **Check for pending clears in every RD texture function**  
   <https://github.com/godotengine/godot/pull/113236>
   - Merged 2025-11-27.
   - Potentially the most interesting adjacent rendering-resource fix.
   - Fix description: missing pending-clear checks could allow a later clear to wipe a texture after a command already wrote to it.
   - That is **resource-ordering adjacent**, but the PR explicitly says it fixes a regression from D3D12 auto-clears and **Voxel GI on D3D12**, not Vulkan compositor/RD device loss.
   - So it is **plausibly adjacent, not strongly matching**.

4. **Wayland: Improve mapping robustness and synchronization**  
   <https://github.com/godotengine/godot/pull/117385>
   - Merged into 4.6.2.
   - Real Wayland fix, but about window mapping/synchronization, not render-resource hazards.
   - **Unlikely** to explain the GDGS render-path crash.

5. **RenderingDevice: Wait for present if supported (Vulkan Windows/X11/Wayland - needs testing)**  
   <https://github.com/godotengine/godot/pull/94973>
   - Still open, not merged.
   - Interesting as a general Vulkan/Wayland present-timing experiment, but **not something available to rely on today**.

#### 4.6 / 4.6.1 / 4.6.2 changelog scan

Release pages:
- 4.6: <https://github.com/godotengine/godot/releases/tag/4.6-stable>
- 4.6.1: <https://github.com/godotengine/godot/releases/tag/4.6.1-stable>
- 4.6.2: <https://github.com/godotengine/godot/releases/tag/4.6.2-stable>

Findings from changelog/release-note scanning:
- `4.6` includes the compositor callback-init fix `GH-110249`, Intel-driver workaround `GH-110363`, and various Vulkan / RD housekeeping items.
- `4.6.1` does **not** add a clearly matching compositor/RD/Vulkan device-loss fix for this shape.
- `4.6.2` adds several **Wayland windowing** fixes, but **nothing that reads like a compositor compute / resource hazard / Vulkan device-loss fix**.
- I did **not** find a release-note/changelog entry after `4.6.2` that strongly suggests “this probably already fixes the GDGS-shaped crash.”

## What this means

### Confidence assessment

- **High confidence:** there is **no obvious exact prior upstream report** for the GDGS-shaped failure.
- **Medium confidence:** the nearest upstream family is **CompositorEffect / RenderingDevice texture-usage and resource-lifetime bugs**, not a known `BLIT_PASS`-specific regression.
- **Low confidence:** that any already-landed post-4.6.2 change definitely fixes the issue.

### Best current interpretation

The current AeroBeat/GDGS evidence still points to one of two buckets:

1. **A GDGS-side misuse/edge case** in its custom RD compute/resource sequencing that Godot/Vulkan/Intel exposes harshly; or
2. **A real Godot backend bug** triggered by a valid or near-valid compositor/RD usage pattern.

Upstream history does **not** currently let us collapse that to “already known and already fixed.”

## Recommended next move

1. **Do one cheap validation pass on a newer Godot build anyway**
   - Prefer **latest 4.7 dev/nightly or current master export/editor build**.
   - Reason: it is still the fastest way to detect an unadvertised engine-side fix.
   - But do **not** assume success; the research does not justify high confidence that newer Godot already fixes it.

2. **If it still reproduces, open a focused upstream Godot issue**
   - Include the existing GDGS issue and the three AeroBeat docs.
   - Emphasize the strongest narrowing fact: **valid compositor textures are produced, `No Present` still crashes, and the final compositor shader path is not required**.
   - Also include exact hardware/software context: **Intel Iris Xe, Linux, Wayland, Vulkan, Godot 4.6.2**.

3. **Treat the test-newer-version step as a sanity check, not the answer**
   - Because open issue #118292 shows that **CompositorEffect + RD edge cases still exist in newer builds**, a successful upgrade is possible but **not strongly predicted by upstream history**.

## Bottom line

**Plain answer:** no strong prior art found, no clearly landed fix found, and no release-note evidence that post-4.6.2 already solves this exact boundary.  
**Best next move:** test latest 4.7 dev/master once, then likely file a new upstream Godot issue if the repro survives.
