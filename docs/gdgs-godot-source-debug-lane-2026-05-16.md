# GDGS Godot source-debug lane for 4.7-dev/nightly repro

**Date:** 2026-05-16  
**Owning repo:** `/home/derrick/.openclaw/workspace/projects/openclaw-godot`  
**Companion source checkout:** `/home/derrick/.openclaw/workspace/projects/godot`

## Purpose

The GDGS failure still reproduces on `Godot Engine v4.7.dev5.official.a8643700c`, so the next useful lane is source-level narrowing instead of another vague upstream search. This memo records the practical local Godot source lane now available on this machine, the engine files that matter first, and the strongest current interpretation of the new push-constant diagnostics.

## Local Godot source lane

A fresh local upstream Godot source checkout was created at:

- `/home/derrick/.openclaw/workspace/projects/godot`

Current remotes:

- `origin git@github.com:godotengine/godot.git`

Local branches established for this investigation:

- `godot-47-dev5-a8643700c` -> exact upstream commit used by the successful nightly repro acquisition (`a8643700ce8affae9fed0d2688b9f7867f5b7d4e`)
- `gdgs-blit-pass-debug-master` -> latest practical local upstream `master` fetched in this environment at the time of setup (`321b8c94...`)
- `master` -> untouched tracking branch for upstream

### Branch strategy

Use a two-lane source strategy:

1. **Repro-parity lane:** inspect and, if needed, instrument `godot-47-dev5-a8643700c` first when exact alignment with the observed dev5 error stream matters.
2. **Latest-investigation lane:** do forward-looking instrumentation or candidate fixes on a new working branch cut from `gdgs-blit-pass-debug-master`, not on `master` itself.

Recommended working branch names once edits start:

- `gdgs-push-constant-instrumentation`
- `gdgs-blit-pass-debug`

That gives us one branch that matches the observed nightly and one that tracks the newest practical upstream source for confirming whether the same paths still look identical.

## Where the relevant engine paths live

### 1. `BLIT_PASS` breadcrumb path

The reported `Last known breadcrumb: BLIT_PASS` is a late breadcrumb emitted by the Vulkan device-loss reporting path, not the root cause by itself.

Key files:

- `servers/rendering/rendering_device.cpp:5527`
  - `draw_graph.add_draw_list_begin(..., RDD::BreadcrumbMarker::BLIT_PASS, ...)`
  - This is where the screen/swapchain blit pass gets tagged.
- `servers/rendering/rendering_device_commons.h:357`
  - `BLIT_PASS = 10u << 16u`
- `drivers/vulkan/rendering_device_driver_vulkan.cpp:6973`
  - breadcrumb decode path that prints `BLIT_PASS` during device-loss reporting.

Interpretation: the final crash still lands during the later swapchain/output pass, but the new dev5 diagnostics suggest the bad state may be created earlier in the GDGS compute/compositor path.

### 2. Compute push-constant validation path

The new 4.7-dev5 errors are coming from exact engine-side validation in `RenderingDevice`.

Key files:

- `servers/rendering/rendering_device.cpp:6720`
  - compute pipeline bind stores `compute_list.validation.pipeline_push_constant_size = pipeline->push_constant_size`
- `servers/rendering/rendering_device.cpp:6763-6779`
  - `compute_list_set_push_constant()`
  - hard check: supplied byte count must exactly equal the pipeline's reflected push-constant size
- `servers/rendering/rendering_device.cpp:6808-6812`
  - `compute_list_dispatch()` rejects dispatch if required push constants were not successfully supplied
- `servers/rendering/rendering_shader_container.cpp:632-638`
  - SPIR-V reflection captures push-constant block size directly from the shader module (`pconstants[0]->size`)

This means the 4/8/12-byte expectations are not arbitrary. They are the reflected sizes of the shader-declared push-constant blocks.

### 3. Compositor effect callback path

GDGS is entering Godot through `CompositorEffect`, then using `RenderingDevice` compute work inside the callback.

Key files:

- `scene/resources/compositor.cpp`
  - high-level `CompositorEffect` resource and callback binding
- `servers/rendering/storage/compositor_storage.cpp`
  - stores effect callbacks and flags
- `servers/rendering/renderer_rd/renderer_scene_render_rd.cpp:298-315`
  - `_process_compositor_effects(...)` calls the user callback on the render thread
- `servers/rendering/renderer_rd/forward_clustered/render_forward_clustered.cpp`
  - concrete callback injection points:
    - pre-opaque around `2173`
    - post-opaque around `2266`
    - post-sky around `2328`
    - pre-transparent around `2404`
    - post-transparent around `2454`

For this bug, `post-transparent` remains the most relevant callback boundary because that is where GDGS is currently executing the compositor path that later precedes the `BLIT_PASS` device loss.

### 4. Render-buffer / texture usage paths relevant to compositor RD access

The earlier upstream research already pointed to texture usage / storage / resolve issues as an adjacent bug family. The current source still shows those decisions concentrated here:

- `servers/rendering/renderer_rd/renderer_scene_render_rd.cpp:342-415`
  - screen/depth helper texture creation with storage/copy usage flags
- `servers/rendering/renderer_rd/storage_rd/render_scene_buffers_rd.cpp:722-833`
  - color/depth usage-bit construction for internal and resolved textures
- `servers/rendering/renderer_rd/storage_rd/render_scene_buffers_rd.h:384-423`
  - `_get_color_layer(...)`, `_get_depth_layer(...)`, and related accessors exposed to compositor users
- `servers/rendering/rendering_device.cpp:4555-4556`
  - explicit validation that images used as uniforms must have `TEXTURE_USAGE_STORAGE_BIT`

These remain engine-side inspection targets even if the immediate push-constant issue is plugin-side, because the later device loss still manifests after compositor work has touched engine-managed textures.

## New 4.7-dev5 clue: likely meaning

The nightly repro added repeated errors of this shape before the later crash:

- pipeline expects `8` bytes, supplied `16`
- pipeline expects `4` bytes, supplied `16`
- pipeline expects `12` bytes, supplied `16`
- later `compute_list_dispatch()` says the required push constant was not present

That new signal strongly suggests **GDGS is still violating the engine's push-constant contract in at least part of its compute path**.

### Why this points at GDGS first

GDGS currently pads every push-constant payload to a 16-byte boundary in:

- `/home/derrick/.openclaw/workspace/projects/aerobeat/aerobeat-vendor-gdgs/addons/gdgs/runtime/render/gaussian_rendering_device_context.gd:127-140`

That helper returns 16-byte payloads even for smaller shader declarations.

The radix-sort shaders declare smaller push-constant blocks:

- `radix_sort_spine.glsl` -> `int pass;` => reflected size likely `4`
- `radix_sort_upsweep.glsl` -> `int pass; uint in_offset;` => reflected size likely `8`
- `radix_sort_downsweep.glsl` -> `int pass; uint in_offset; uint out_offset;` => reflected size likely `12`

But GDGS builds one padded 16-byte push-constant blob for all three passes in `gaussian_renderer.gd`:

- `addons/gdgs/runtime/render/gaussian_renderer.gd:94-101`

So the new dev5 validation is consistent with the plugin passing a single padded 16-byte payload to pipelines whose reflected push-constant sizes are 4, 8, and 12 bytes.

### Why engine-side work is still warranted

Even if GDGS is mis-sizing push constants, the later crash still reaches the compositor/output lane and still ends in `BLIT_PASS` device loss. That means at least one of these may be true:

1. the invalid push-constant sequence causes follow-on compute/resource corruption that only detonates later;
2. Godot's render-graph / compositor / RD path still has a secondary hazard after the rejected dispatches; or
3. both are true: GDGS violates the contract, and the engine/backend fails ungracefully afterward on Intel Vulkan.

So the safest reading is **both plugin-contract audit and engine-side mapping are justified**, but the first narrow patch candidate now sits on the GDGS side.

## First concrete investigation targets

### Highest-value target A: confirm and fix GDGS push-constant contract

Narrowest first check:

- stop using one generic padded 16-byte payload for all radix-sort pipelines
- instead supply per-shader byte counts that match reflected shader block sizes exactly

Expected sizes to verify first:

- spine -> `4`
- upsweep -> `8`
- downsweep -> `12`

If fixing those sizes removes the dev5 validation errors and also removes the later device loss, the main root cause is probably GDGS-side misuse.

### Highest-value target B: instrument Godot around rejected compute dispatches

If the GDGS-side size fix does **not** fully remove the later crash, inspect/instrument:

- `servers/rendering/rendering_device.cpp`
  - `compute_list_set_push_constant()`
  - `compute_list_dispatch()`
  - `compute_list_add_barrier()` / compute-list restart logic nearby
- add temporary logging around pipeline RID/shader identity and reflected push-constant size
- verify whether rejected `compute_list_set_push_constant()` / dispatch failures leave later graph state or barriers in a problematic condition

### Highest-value target C: inspect post-transparent compositor sequencing and texture usage

If push-constant fixes reduce errors but `BLIT_PASS` survives, inspect:

- `servers/rendering/renderer_rd/renderer_scene_render_rd.cpp::_process_compositor_effects(...)`
- `servers/rendering/renderer_rd/forward_clustered/render_forward_clustered.cpp` around the pre/post-transparent and resolve sections
- `servers/rendering/renderer_rd/storage_rd/render_scene_buffers_rd.cpp` usage-bit and resolved-texture setup

Specific question: after GDGS compute work in the compositor callback, are the engine-owned textures being used in a way that can still trigger a later Vulkan device loss on Intel/Wayland?

## Recommended next step

**Do both, but in order:**

1. **First:** audit/fix the GDGS push-constant contract, because the new 4.7-dev5 diagnostics point straight at a likely plugin misuse.
2. **Second:** keep the Godot source-debug lane ready and instrument `RenderingDevice` / compositor sequencing if the later `BLIT_PASS` crash remains after the GDGS fix.

So the likely next patch/debug lane is **both**, with **GDGS push-constant contract fixes first** and **Godot instrumentation immediately after if the crash persists**.

## Practical command lane

Useful local commands for the next agent:

```bash
cd /home/derrick/.openclaw/workspace/projects/godot
git switch godot-47-dev5-a8643700c
# inspect parity with repro build

git switch gdgs-blit-pass-debug-master
git switch -c gdgs-push-constant-instrumentation
# add temporary logging / instrumentation here if needed
```

## Bottom line

- We now have a practical local Godot source lane on this machine.
- The new 4.7-dev5 push-constant errors strongly suggest a real GDGS contract violation in the radix-sort compute path.
- `BLIT_PASS` still matters, but as a later crash endpoint, not as the first concrete root-cause target.
- The first narrow next move should be: **fix or experimentally bypass the GDGS push-constant size mismatch, then retest before deeper engine surgery.**
