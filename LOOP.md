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
3. **Check cameras on context** with `tools/project_outlines.py` (white = real surroundings) before trusting a score.
4. **Baseline.** Note the current `06_reports/match_score.json` mean (and per camera) and the metrics in
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

## Section D iterations (capacity study) — different steps 4–7
Section D is the **top priority** (user request, 9 Nov 2026). For a D item:
- **Change** `SPECS` / `PRESETS` in `tools/make_options.py` (or add a new option key), then
  `.venv/bin/python tools/make_options.py <key>` and `.venv/bin/python build.py 04_proposed/options/<key>/params.yaml --no-blender`.
- **Score** with `.venv/bin/python tools/score_options.py` (writes `06_reports/capacity_study.md`). Score = above-ground
  GFA (k m²) if every hard rule in `02_regulations/rules.yaml` passes, −10 % per missed quality floor.
- **Keep** the change if that option's score went up (or a failing option now passes); otherwise revert.
  Useful helpers: the tower-position grid search pattern (vary a block's rect, call `psp.distance_angle_neighbours`,
  keep only footprints 2 m inside the plot and not overlapping other blocks).
- **Renders** for kept changes: `build.py 04_proposed/options/<key>/params.yaml --render --engine WORKBENCH --only aerial_S top_view`;
  re-run `score_options.py` so `06_reports/capacity_study_aerials.jpg` updates. Cycles renders of the top 2 options
  every 4th kept D iteration (`--render --only aerial_S aerial_SE`).
- **Never relax a rule to make an option pass.** Rules change only with a cited source (regulations-analyst role).
  Keep the existing office E and the official plot. Footprints stay ≥ 2 m inside private plot edges.

## Backlog (ranked)
### D. Capacity study for OUR design (priority)
- [x] D1. Option B: make it pass §21 (failing: panel blocks south of Milevská, three-wing building north) — move/slim/rotate
      the towers or step the podium; then grow GFA.
- [x] D2. Option C: pass §21 (drum SE west, three-wing north) and the courtyard-sun floor (1.3 h → ≥ 2 h): open the
      courtyards to the south-west, step heights down toward the park.
- [x] D3. Option A: grow GFA while passing — rectangular tower floorplate (e.g. 28×36), taller bars where §21 allows,
      use the north wing better; re-run the tower-position search after each change.
- [x] D4. New option D "client-like, compliant": start from the client's footprints (03_existing) and fix §21 + parking
      with the smallest changes — shows how much of the client's 91,500 m² can be kept legally.
- [x] D5. New option E "max yield": parametric search (tower count 1–3, positions, bar heights 6–12 storeys) maximising
      the score; write the search as `tools/search_options.py` and keep the best result as option E.
- [x] D6. Basement sizing: choose `basement_levels` per option so parking capacity ≥ required minimum with the fewest
      levels (cost); report levels in capacity_study.md.
- [x] D7. Daylight proxy refinement: replace the own-façade 45° test with a vertical-sky-component estimate
      (ČSN 73 0580 / EN 17037 logic) and re-score all options.
- [x] D8. Hotel programme per option: lobby / restaurant / conference / spa areas on the lower floors, keys by room type;
      flag options outside 300–450 keys (typical 4* city hotel, ASSUMED until the brief arrives).
- [x] D11. Apply the D8 hotel flags: A/E convert the top ≈6–7 room floors to serviced apartments (keys ≤ 450);
      B/C/D add meeting space (≥ 1.5 m²/key) and, for C/D, a spa floor; re-score (parking need changes with use).
- [x] D9. Presentation: Cycles aerials of the top 2 options + client scheme side by side, and a one-page comparison
      in `06_reports/capacity_study.md` (no new hosts, no paid services).
- [x] D10. Verify parking zone 02 (Atlas Prahy zone map) — mark **blocked** if the map needs a token.
      (2026-11-11: user allowed gs-pub.praha.eu; official PSP zone layer → whole plot in **zone 02**.)

### A. Fidelity of the existing scheme (measurable with `score_match.py`)
- [x] A1. Camera match render-003 (park view, score 0.02): find the viewpoint (north park, looking at D's north
      façade), set location/target/lens and `resolution` to the client image's aspect ratio.
- [x] A2. Set every matched camera's `resolution` to its client image's aspect ratio, then fine-tune location/target/lens
      for render-000 (aerial) with 50 % overlays (`overlays/overlay_*.jpg`) until silhouettes align.
- [x] A3. Same fine-tuning for render-004, render-005, render-006.
- [x] A4. Verify storey counts and the C2 wing height (33.9 m vs PSG 25.1 m) against the tuned overlays; adjust.
      (A tower done in iteration 4: 7 diagrid modules × 3 storeys, 83.8 m. C1/C2 → 11 storeys and B/B2 checked in
      iteration 5. D → 8 storeys, 32.3 m in iteration 7.)
- [x] A5. B tower: overhang / alignment over its base and the B2 terrace steps against render-004.
      (iteration 6, user request: B2 straight walls + balconies/timber piers/penthouse; render-004 camera moved to SW.)
- [x] A6. D butterfly: recessed joint with green balconies (render-003), wing lengths against the top view.
      (iteration 8: joint slot + planted balconies; wing lengths left as the PSG footprint, the outline matches render-003.)
- [x] A7. A diagrid: bay count and module height against render-006 (count diamonds per face).
      (iteration 9: 5 bays/face + 7 modules confirmed; render-006 camera re-solved, client omits block C there.)
- [x] A8. C front block: roof setbacks and terraces against render-000; rooftop units positions.
- [x] A9. A0 podium / courtyard link shape and timber fascia against render-000 and render-006.
- [ ] A10. Landscape: courtyard paths, planting and trees against the top view.

- [ ] A11. C2 east end hides B's timber base in render-004 (client shows the base): check C2 length / whether the client render omits it.
- [x] A13. Tower A shows above D in render-003 where the client image has sky: the client render omits A (audit 2026-11-09).
- [ ] A14. Calibrate render-002 (SE) on context and triangulate A and B2 with render-000 (two-view check, see audit report).
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
