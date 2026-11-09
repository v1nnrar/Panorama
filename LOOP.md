# Improvement loop — protocol

A cloud session runs **one iteration** of this protocol each time it is woken by its scheduled task.
Goal: keep making the Panorama plan more accurate and more complete, one verified step at a time.
Read `CLAUDE.md` first; its conventions and agent roles apply.

## One iteration
1. **Sync.** `git fetch origin claude/gifted-lovelace-niaftb && git checkout claude/gifted-lovelace-niaftb && git pull`.
   Run `./setup.sh` if `.venv` is missing (installs Blender bpy, IfcOpenShell, Mesa EGL).
2. **Pick one item**: the highest open item in the backlog below that is not blocked. If the user left new
   instructions or files (new commits by the user, files in `01_brief/`, `02_regulations/`, `04_proposed/`),
   handle those first, using the matching agent's role.
3. **Baseline.** Note the current `06_reports/match_score.json` mean (and per camera) and the metrics in
   `03_existing/model/metrics.json`.
4. **Change** one thing, in the source of truth (`params.yaml`, `pipeline/*.py`, `tools/*.py`), never in generated files.
5. **Rebuild & check** (fast): `.venv/bin/python build.py 03_existing/params.yaml --render --engine WORKBENCH`
   then `.venv/bin/python tools/score_match.py 03_existing --json /tmp/score_new.json` and look at the renders.
   Must hold: IFC schema validation 0 errors; `build.py examples/test_block/params.yaml --no-blender` → 6/6 pass.
6. **Keep or revert.** Keep the change only if the match score did not drop by more than 0.005 (camera/geometry
   items) *or* the item is completeness work that the score cannot measure and the renders look right.
   Otherwise `git checkout -- .` and record the failed attempt in the log so it is not retried blindly.
7. **Presentation renders** (every 4th kept iteration, or when geometry changed a lot):
   `build.py 03_existing/params.yaml --render` (Cycles) → `tools/compare_renders.py 03_existing`
   → `tools/score_match.py 03_existing --json 06_reports/match_score.json`.
8. **Log & commit.** Append one entry to `06_reports/improvement_log.md` (date, item, what changed, score before → after,
   kept/reverted). Tick the backlog item. Commit with a clear message and the attribution lines, push to
   `claude/gifted-lovelace-niaftb`. Never force-push; if the push is rejected, pull --rebase and retry once.
9. **Stop** after one item. Keep each iteration under about 45 minutes.

## Guardrails
- Never edit or delete: `00_site/site.yaml` parcels (official ČÚZK data), `00_site/survey/raw/`, client files in
  `03_existing/renders/`, or anything in other repositories. Do not open pull requests.
- Every estimated number gets `# ESTIMATED from <render>: <reasoning>`; every assumption `# ASSUMED: <reason>`.
- No new network hosts, no new paid services, no Higgsfield generations unless the user asks.
- If the backlog is empty, add the next sensible items (with reasons) instead of inventing busywork; if nothing
  useful remains without user input, write that in the log and stop.
- If two iterations in a row fail on the same item, mark it **blocked** with the reason and move on.

## Backlog (ranked)
### A. Fidelity of the existing scheme (measurable with `score_match.py`)
- [x] A1. Camera match render-003 (park view, score 0.02): find the viewpoint (north park, looking at D's north
      façade), set location/target/lens and `resolution` to the client image's aspect ratio.
- [x] A2. Set every matched camera's `resolution` to its client image's aspect ratio, then fine-tune location/target/lens
      for render-000 (aerial) with 50 % overlays (`overlays/overlay_*.jpg`) until silhouettes align.
- [x] A3. Same fine-tuning for render-004, render-005, render-006.
- [ ] A4. Verify storey counts and the C2 wing height (33.9 m vs PSG 25.1 m) against the tuned overlays; adjust.
      (A tower done in iteration 4: 7 diagrid modules × 3 storeys, 83.8 m. C1/C2 → 11 storeys and B/B2 checked in
      iteration 5. Remaining: D storey count against render-003.)
- [x] A5. B tower: overhang / alignment over its base and the B2 terrace steps against render-004.
      (iteration 6, user request: B2 straight walls + balconies/timber piers/penthouse; render-004 camera moved to SW.)
- [ ] A6. D butterfly: recessed joint with green balconies (render-003), wing lengths against the top view.
- [ ] A7. A diagrid: bay count and module height against render-006 (count diamonds per face).
- [ ] A8. C front block: roof setbacks and terraces against render-000; rooftop units positions.
- [ ] A9. A0 podium / courtyard link shape and timber fascia against render-000 and render-006.
- [ ] A10. Landscape: courtyard paths, planting and trees against the top view.

- [ ] A11. C2 east end hides B's timber base in render-004 (client shows the base): check C2 length / whether the client render omits it.
- [ ] A12. B2 roof terrace: green roof + planters around the PV penthouse (aerial render-000).

### B. Completeness of the plan
- [ ] B1. Floor plans per building: cores (stairs, lifts, shafts) at plausible positions, marked ASSUMED.
- [ ] B2. Hotel/residential layout on typical floors (room module 3.6–4.2 m) for the block(s) the user names as hotel;
      if not named yet, do C front block as the likely hotel and mark ASSUMED.
- [ ] B3. Sections and elevations (drawings-producer) into `05_drawings/existing/<date>/`.
- [ ] B4. Underground parking: ramp position from the top view, parking grid, space count.
- [ ] B5. Web viewer `viewer/index.html` for `model.glb` (lightweight GLB: merge by material, no normals).

### C. Waiting on the user (do not start without input)
- [ ] C1. Regulations → `02_regulations/rules.yaml` (needs documents).
- [ ] C2. Brief → `01_brief/programme.yaml` (needs brief).
- [ ] C3. Proposed scheme `04_proposed/` (needs our design).
- [ ] C4. Client site plan (DWG/PDF) → exact footprint positions.
