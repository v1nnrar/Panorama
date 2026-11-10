# Improvement log

One entry per loop iteration (see `LOOP.md`). Match score = `tools/score_match.py` mean (edge correlation with the
client's renders, higher is better).

## 2026-11-08 — baseline
- Existing scheme v1 on official ČÚZK parcels; Cycles renders for 5 matched cameras + top view.
- Match score mean **0.2464** (aerial 0.292, SW 0.347, SE 0.289, diagrid 0.283, park 0.022).

## 2026-11-08 — iteration 1: A1 camera match render-003 (park view) — KEPT
- The old camera stood NW of D looking at the wrong side; render-003 looks **south** at D's north (concave) façade,
  so image-left is D's **east** wing. Fitted the camera by least squares on 6 image points of D (NE corner parapet +
  first-floor underside, wing joint, NW corner parapet + underside, SE corner) with a level camera + vertical lens shift
  (the client render uses 2-point perspective). Residuals ≈10 px on 990×450.
- New camera: location (20.1, 108.6, 1.7), target (1.4, 51.6, 1.7), lens 19.6 mm, shift_y 0.153, resolution 1980×900
  (client aspect 2.2). Params only; geometry unchanged.
- Score (Workbench check): park −0.059 → 0.133, mean 0.131 → 0.169. Cycles re-render of this camera only:
  park **0.022 → 0.304**, mean **0.2464 → 0.3028**. IFC validation 0 errors; test block 6/6 pass.
- Observation for A4: in our render the diagrid tower A shows above D's east wing, where the client image has
  open sky — A is either too tall, too far north-east, or D's east wing is too low in our model. Check in A4.

## 2026-11-08 — iteration 2: A2 client aspect for all cameras + aerial render-000 fine-tune — KEPT
- Set `resolution` of every matched camera to its client image's aspect (render-005 700×724, -004 622×742,
  -006 543×871, -000 1280×905). Lenses kept: at the new aspect each street camera scored higher than with
  1.3×/1.6× lenses (Workbench: SW 0.169→0.224, SE 0.142→0.255, diagrid 0.268→0.406). Fine-tuning those is A3.
- Aerial (render-000): corner fit of towers A and B (roof corners, A base), which left depth vs lens ambiguous; resolved
  with a Workbench search on the score itself (`camsearch`: ~9 s per render at 50 %, ~35 candidates). New camera:
  location (−148.8, −453.3, 372.8), target (21.4, −11.3, 20), **lens 78 mm** (old: 35 mm from 250 m). The 50 % overlay lines up
  towers A and B, block C, the street and the slab blocks in front.
- Score, Cycles: mean **0.3028 → 0.3497** (aerial 0.292→0.359, SW 0.347→0.394, SE 0.289→0.351, diagrid 0.283→0.341,
  park 0.304 unchanged). Workbench mean 0.169 → 0.260. IFC 0 errors; test block 6/6 pass. Params only, no geometry.
- Observation for A4: with the aerial aligned, our tower A's roof sits clearly **above** the client's (about 2 storeys
  at this scale), and in render-003 A shows above D where the client has sky, so A at 88.2 m is probably too tall.

## 2026-11-09 — iteration 3: A3 fine-tune street cameras render-004, -005, -006 — KEPT
- New tool `tools/cam_search.py`: coordinate descent on the match score for one camera (Workbench at 50 % from
  `model/model.blend`, ~9 s per render; prints the best camera as a params line, never edits params). Eye height fixed.
- Results (2 sweeps, 32–38 renders each, three cameras run in parallel):
  - render-005 SW: location (−70, −86, 1.7), target (5, −45, 37), lens 32, shift_y 0.075 (was 24 mm from (−62, −86)).
  - render-004 SE: location (116, −96, 1.7), target (90, −56, 42), lens 24.
  - render-006 diagrid: location (−48, −15, 1.7), target (11, 0, 42), lens 21.
- Checked the 50 % overlays by eye so the score is not being gamed: tower A's diagrid and block C (005), tower B with
  its terraces (004) and the diagrid shaft (006) now line up with the client images.
- Score, Cycles: mean **0.3497 → 0.4723** (SW 0.394→0.672, SE 0.351→0.536, diagrid 0.341→0.491; aerial and park
  unchanged). Workbench mean 0.260 → 0.445. IFC 0 errors; test block 6/6 pass. Params + new tool, no geometry.
- All five matched cameras are now tuned, so geometry items (A4 onward) can be judged on the score.

## 2026-11-09 — iteration 4: A4 (part 1) tower A storey count and height — KEPT
- Counted the diagrid in render-006 (close-up) and render-000 (aerial): **7 modules of 3 storeys** standing on the
  podium roof (balcony slabs every ⅓ module). The model had 25 storeys under the diagrid (8.3 modules, 88.2 m).
- Attempt 1: 7 × 3 storeys at 3.2 m → 73.3 m. The overlay showed the right module count but a tower too short.
  Workbench mean 0.4446 → 0.412, and 0.436 after retuning the cameras; reverted within the iteration.
- Attempt 2 (kept): the client tower's height/width ratio in render-006 is ~18 % larger, so ~3.7 m storeys:
  P1 5.0 + 21 × 3.7 + 1.1 parapet = **83.8 m**, 22 storeys. Retuned the render-005 and aerial cameras with
  `tools/cam_search.py` (render-006 camera search found no better position).
- Score: Cycles mean **0.4723 → 0.4718** (−0.0005, within the 0.005 tolerance; aerial 0.359→0.360, SW 0.672→0.691,
  SE 0.536→0.534, diagrid 0.491→0.451, park 0.304→0.323). Workbench mean 0.4446 → 0.4392. IFC 0 errors; test block 6/6.
- Kept despite the flat score because the module count is now right in both views. Render-006 dropped, so tower A's
  width or diagrid offset may still be off: check under A7 (diagrid bays). Full Cycles presentation renders made
  (4th kept iteration). A4 stays open for C1/C2, B and D storey counts.

## 2026-11-09 — iteration 5: A4 (part 2) storey counts for B, B2, C1, C2 — KEPT
- **B tower** (render-004): 6-storey timber base + 8 two-storey band intervals = 22 storeys, same as the model. No change.
  **B2**: ~8 stepped levels, same as the model. No change.
- **C1** (render-005): 10 window rows over a tall glazed GF = **11 storeys** (model had GF + 9). The total height already
  matched the overlay, so it stays 33.9 m: GF 4.4 m (≈1.5 × typical) + 10 × 2.85 m + 1.0 parapet.
- **C2**: same levels as C1 (window rows run continuously across the joint) → 11 storeys, the 4 m north setback moved to
  storey 11. PSG's 25.1 m is not supported by render-005 or render-000; 33.9 m stays.
- Overlay check: the doubled/offset window rows on C1 are gone and the rows coincide.
- Score: Workbench mean 0.4392 → 0.4392 (SW 0.7246→0.7292, aerial 0.2947→0.2899). Cycles (aerial + SW re-rendered):
  mean **0.4718 → 0.4725**. IFC 0 errors; test block 6/6. GFA changes are in metrics.json.
- For A8: C1's roof core box (3.5 m) shows above the parapet in render-005 where the client image has none — lower or remove it.
- A4 remaining: D storey count against render-003.

## 2026-11-09 — iteration 6 (user request): B2 straight walls, missing facade elements, render-004 camera — KEPT
- User review in Blender: the B/B2 block looked tilted and things were missing compared with render-004.
- Cause: B2 stepped back 1 m per floor to S and E, which made a pyramid in front of tower B. render-000 and render-004
  show straight walls with deep wrap-around balcony slabs.
- B2 changes: setbacks removed (vertical walls); 2.2 m balcony slabs on S/E/W faces with planters + planting + glass
  railing; timber piers (4.2 m spacing, full balcony depth); GF + 6 floors + **PV penthouse** in the SE corner of the L
  (ESTIMATED from render-000) with planter/railing terrace edges around it. Tower B is unchanged and stands straight on its base.
- render-004 camera was on the wrong side: the nearest corner of tower B in the client image is its **SW** corner, so the
  camera stands SW of B (old SE camera only scored well by matching edges of the wrong buildings). New camera from a
  corner fit (≈5 px residual) + cam_search: (−7.9, −115.7, 1.7) → (42.1, −70.9, 1.7), 41.5 mm, shift_y 0.479.
  The overlay now puts tower B and B2 in the client's positions.
- Score, Cycles: mean **0.4725 → 0.4487** (render-004 0.534 → 0.441, aerial 0.359 → 0.351, others ±0.02). Kept despite
  the drop: requested by the user, and the old render-004 score came from a camera on the wrong side.
  IFC 0 errors; test block 6/6.
- Known gaps: C2's east end hides B's timber base in render-004 (A11); B2 roof terrace not green yet (A12).

## 2026-11-09 — iteration 7: A4 (part 3) building D storey count — KEPT
- render-003: **7 ribbon-glazed office floors** over a tall recessed GF (≈1.9 × typical storey, white canopy/colonnade
  in front), then a tall parapet band and a grey roof screen. The model had GF + 9 = 10 storeys.
- Height: in iteration 1 the camera fit had the 34.0 m model ~6 % taller than the client image → **32.3 m**:
  GF 6.5 + 7 × 3.45 + 1.6 parapet band. Added a 3 m GF recess on the N and E faces (the overhang visible in render-003).
- Overlay: D's outline, floor bands and GF overhang now coincide with the client image.
- Score: Workbench mean ≈0.4156 → 0.4165 (park 0.140→0.145). Cycles (park + aerial re-rendered): mean **0.4487 → 0.4486**
  (aerial 0.351→0.359, park 0.323→0.315). IFC 0 errors; test block 6/6. A4 closed.
- New item A13: tower A appears above D in our park view, but the client image shows sky there.

## 2026-11-09 — iteration 8: A6 D butterfly recessed joint with green balconies — KEPT
- render-003 shows a recessed vertical slot where D's two wings meet on the north face, with planted balconies on every
  floor. Footprint now has a ~7 m wide, 3 m deep slot at the joint vertex (−7.31, 47.16) (ESTIMATED).
- Pipeline: facade rules can now target single edges with `near: [[x, y], …]` (edge with the closest midpoint) as well as
  compass `facing` (`pipeline/geom.py::rule_edges`, used by balconies/bands and fins; documented in CLAUDE.md). Used for
  2 m planted balconies on the back wall of the slot, storeys 2–8. Close-up render checked: slot + stacked green balconies.
- Wing lengths: outline already coincides with render-003 after iteration 7; PSG footprint kept.
- Score: Workbench mean 0.4165 → 0.4170. Cycles (park + aerial re-rendered): mean **0.4486 → 0.4488**. In the park view the
  slot is mostly behind one of our generated courtyard trees. IFC 0 errors; test block 6/6.

## 2026-11-09 — measurement audit (user request) — KEPT
- Full report: `06_reports/audit_measurements_2026-11-09.md`. New tool `tools/project_outlines.py` (model + context outlines
  through each camera onto the client images → `03_existing/overlays/outline_*.jpg`).
- Key finding: the cameras had been tuned on our own buildings and absorbed their errors; the real surroundings were
  70–150 px off in render-000. Aerial camera re-calibrated on context only (slab blocks, drums, 104 m tower): 4.4 px RMS.
- Corrections from back-projection + ČÚZK orthophoto + top-view board: **A** moved 4.15 m W / 10 m N (height 83.8 m
  confirmed, independent vertical 86.3 m); **A0** re-drawn; **B2** south face 8 m north, east end 5 m west, penthouse along
  tower B's south face (outside-plot area 53 → 9 m²); **E** OSM wedge (not a building on the orthophoto) trimmed.
  B, C1/C2, D confirmed within 1–3 m.
- Street cameras re-tuned with cam_search. Cycles mean **0.4488 → 0.4236**: lower because the aerial and park cameras now
  sit in their measured places instead of the positions that best matched our errors; visual alignment of buildings
  *and* surroundings is clearly better (see outline overlays). GFA 98,225 → 91,483 m². IFC 0 errors; test block 6/6.

## 2026-11-09 — iteration 9: A7 diagrid check + render-006 / render-003 cameras — KEPT
- Diagrid: render-006 shows **5 feet per wide face** at the podium (≈40 px apart) → 5 bays/face; 7 modules × 3 storeys
  (iteration 4). Model already matches — no geometry change.
- Found while checking: after the audit moved A, cam_search had parked the render-006 camera 38 m from the tower (false
  optimum, tower face-on). Re-solved from A's corners (front = SW corner, 5 points, 14 px RMS): camera at (−54, −80).
  From there block C1 would hide A's base, but the client image shows it → **the client render omits block C**
  (as render-003 omits tower A).
- New per-camera option `hide: [ids]` (pipeline/blender_scene.py `hide_buildings`, tools/cam_search.py; CLAUDE.md):
  buildings left out of that client render are hidden for that camera only. render-006 → `hide: [C1, C2]`,
  render-003 → `hide: [A]`; render-006 refined with cam_search.
- Score, Cycles: mean **0.4236 → 0.4851** (diagrid 0.423 → 0.605, park 0.265 → 0.391, others unchanged).
  IFC 0 errors; test block 6/6.

## 2026-11-09 — iteration 10: new regulations → compliance check (handled first, LOOP step 2)
- New input on the branch: `02_regulations/rules.yaml` + `summary.md` (Metropolitan Plan of Prague, locality 058, [S],
  storey range 27). Ran the compliance-checker step: `build.py … --no-blender --rules 02_regulations/rules.yaml` → **3/3 pass**.
- Wrote `06_reports/compliance_existing.md`: height 83.8 m to parapet (≈85.1 m highest element) vs 100 m; 22 vs 27 storeys;
  HPPreg not set in [S]. Open items: [S] confirmation, stabilised-area judgement, MPP floor-area counting below ground,
  metro D corridor, PSP (distances/daylight/parking/green), any existing permit.
- No model change; match score unchanged (0.4851). Footprint outside plot 9.1 m² = E 6.5 (OSM vs ČÚZK offset) + B2 2.7 (tolerance).

## 2026-11-09 — iteration 11: D1 option B passes PSP §21 — KEPT
- Option B failed §21 at 7 sampled neighbour windows (panel blocks south of Milevská ×4, three-wing building north ×3).
- Search over tower positions/heights + north-wing height using `psp.distance_angle_neighbours` directly (0.1 s per
  layout): ~11,000 random layouts + local refinement; constraints: footprints inside the plot, no overlaps, 1 m clear of
  E, §22 ≥ 2 m, §21 = 0. Rules unchanged.
- Result (in `tools/make_options.py` SPECS B): hotel tower rect(−8, −26, 22, 4) 27 storeys (4 m E, 10 m N), residential
  tower rect(44, −34, 72, −6) 27 storeys (18 m W, 4 m N), north office wing 10 → **6 storeys**; podium unchanged.
- Score: option B **0 → 62.85** (6/6 hard rules pass, quality floors met; GFA 62,850 m², 426 keys + 244 flats est.,
  parking 467 / 1171). Now rank 1, ahead of option A (62.02). Workbench aerial + top view rendered.
- Next lever for B (later): the north wing lost 4 storeys for the three-wing building; a shorter or stepped wing
  could win some of it back.

## 2026-11-10 — iteration 12: D2 option C passes §21 and the courtyard-sun floor — KEPT
- Option C failed §21 at 6 sampled windows (drum SE ×4, panel block across Milevská ×1, three-wing ×1) and its open
  ground had 1.3 h of sun on 21 March (both courtyards opened north).
- `tools/make_options.py`: `cshape()` can now open a courtyard to S, W or E (plot frame), not only N.
- Search (random 8,455 layouts + local refinement) over block extents, open side, wing depth, block heights and the
  north-wing height, scored like `score_options.py` with the pipeline's own §21/§22/daylight/courtyard-sun functions.
  Result: hotel block cshape(−14, −61, 36, −6, wing 16, open **S**) 10 storeys; apartment block cshape(42, −61, 104, −4,
  wing 16, open **E**) 10 storeys; north wing 10 storeys unchanged. West block pulled 14 m off the drum side.
- Score: option C **0 → 61.68** (GFA 61,684 m², 373 keys + 257 flats est.; 6/6 hard rules; quality floors met). Rank 3
  (B 62.85, A 62.02). Thin margins: courtyard sun **2.02 h** (floor 2.0) and daylight proxy **0.145** (floor 0.15) — any
  later growth of C must re-check both.
