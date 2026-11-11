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

## 2026-11-10 — iteration 13: D3 grow option A while passing — KEPT
- Local search (1,608 layouts, 15 parameters) with the pipeline's own §21/§22/parking/daylight/courtyard-sun checks,
  scored like `score_options.py`; rules unchanged.
- Result (SPECS A): hotel tower **30 × 40 m** floorplate, 27 storeys, rect(30, −41, 60, −1); street bar rect(−20, −61,
  86, −45) **10** storeys (was 9, 4 m longer each end); east bar to v = 4 (+4 m); north wing rect(−52, 12, 22, 34)
  deeper, **7** storeys (was 8).
- Score: option A **62.02 → 79.03** (GFA 79,030 m², FAR 4.79; 568 keys + 316 flats est.; parking 637 / 1171; 6/6 hard
  rules; floors met). Rank 1. Thin margins: courtyard sun **2.01 h**, daylight proxy **0.145**.
- Flag for D8: 568 estimated keys exceeds the 300–450 range assumed for a 4* city hotel — part of the tower may become
  serviced apartments / offices.

## 2026-11-10 — iteration 14: D4 option D "client-like, compliant" — NOT DONE (attempt 1, nothing changed)
- Goal: keep as much of the client's scheme (85,310 m² new above-ground GFA) as possible while passing §21 and parking.
- Parking is easy: 2 → 3 basement levels under the client's U footprint (+~240 spaces covers the 728 – 487 gap).
- §21 diagnosis (pipeline's own check, buildings removed one at a time from the client scheme, 10 failing windows):
  - three-wing building (54, 48), 7 windows: tower **A** (84 m, ~25 m away) is the main cause; **D**'s east end (only
    ~10 m from the west wing, fails even at 4 storeys) and **B3** (19 m, 15 m south of the wing's south end — blocks the
    ground-floor window at (60, 14)) cause the rest. Trimming D's east end 8 m + B3 to 3 storeys removes those.
  - drum towers (−58, −26), 3 windows: **C1** and **A** together.
- Searched (≈1,800 layouts): A 14–20 typical storeys and shifts W/S ≤ 8 m, D 4–7 storeys + east-end trim 0–8 m,
  C1 6–10 storeys, B3 2–4 storeys. **No layout passes**: shifting A west clears the three-wing building but adds a drum
  failure; best seen = 1 failing window (drum) at 70,837 m².
- Next attempt: add levers — C1 west-end trim (drum side), A moved **south only** (toward the courtyard, away from both
  neighbours), D east trim > 8 m; search by cheapest GFA loss first. If attempt 2 fails too, mark D4 blocked (LOOP rule).

## 2026-11-10 — iteration 15: D4 option D "client scheme, made compliant" — KEPT (attempt 2)
- Added the two levers from attempt 1 (C1 west-end trim, A moved south only) and ran a local search that first
  minimises §21 failing windows, then maximises GFA, starting from attempt 1's best layout.
- Result (`tools/make_options.py` SPECS D, new `build_from_existing()` = client params + per-building edits):
  tower **A moved 8 m south at full height** (22 storeys, 83.8 m); **D** east end 10 m shorter, 8 → 7 storeys;
  **C1** 11 → 6 storeys and 4 m shorter on the drum side; **B3** 5 → 4 storeys; basement 2 → **3 levels**.
  B, B2, C2, A0, E unchanged.
- Score: option D **68.74**, rank 2 — 6/6 hard rules pass, GFA **85,928 m² = 94 % of the client's 91,483 m²**, parking
  668 / 730. Two quality floors missed (−20 %), both inherited from the client's design: daylight proxy 0.201 and
  built-up ratio 0.488.
- 4th kept D iteration → Cycles aerials (S + SE) of the top two options A and D.

## 2026-11-10 — iteration 16: D5 option E "max yield" via tools/search_options.py — KEPT
- New tool `tools/search_options.py`: random local search over a layout family (street bar, east bar, north wing,
  1–3 towers; bars 6–12 storeys, towers ≤ 27 storeys), towers can be added/removed/moved/resized; every candidate
  checked with pipeline/psp.py (§21, §22, parking, daylight proxy, courtyard sun) — rules never relaxed. Writes
  `04_proposed/options/<key>/spec.json`; `tools/make_options.py` now loads such specs as options.
- Run 1 (towers up to 40 × 40 m) reached a 40 × 40 m hotel floorplate — too deep for hotel rooms; tower sides capped
  at **22–36 m** and re-run (seed 2, 1,751 layouts).
- Finding: **adding a 2nd or 3rd tower never passed §21** — on this plot one tower is the yield maximum.
- Result: hotel tower 34 × 36 m, 27 storeys, rect(28, −39, 62, −3); street bar rect(−20, −61, 86, −45) 10 storeys;
  east bar to v = −4, 12 storeys; north wing rect(−50, 8, 22, 34) 7 storeys.
- Score: option E **79.85** (79,854 m², 580 keys + 299 flats est., parking 654 / 1171), rank 1, +1 % over option A.
  Courtyard sun exactly **2.0 h** (at the floor) and daylight proxy 0.148 — E is at the edge of the quality floors.

## 2026-11-10 — iteration 17: D6 basement sizing — KEPT
- `tools/make_options.py`: `basement_levels: "auto"` (now used by every option) writes the option with 1, 2, 3 … levels
  and keeps the first whose PSP §25 parking margin (pipeline/psp.py::parking) is ≥ 0. `tools/score_options.py` reports a
  **Basement levels** column in `06_reports/capacity_study.md`.
- Result: options **A, B, C, E → 2 levels** (were 3; capacity 781 vs need 467–654), option **D → 3 levels** (client's
  smaller U footprint: 730 vs 668). Each of A/B/C/E saves one level ≈ 13,800 m² of basement.
- Scores unchanged (score counts above-ground GFA; parking still passes 6/6 for all). Renders not redone — the change
  is below ground; model.blend files of A–E still show 3 basement levels until the next render build.

## 2026-11-10 — iteration 18: D7 daylight proxy → vertical sky component — KEPT (method change)
- `pipeline/psp.py`: `daylight_proxy_own` now computes the **vertical sky component** (CIE overcast sky, analytic
  integration per azimuth over the window's half-sky, obstruction angle per 10° ray) for the same sampled windows;
  a window fails below **VSC 15 %** (BRE 209 rule of thumb, ASSUMED, proxy for ČSN 73 0580 / EN 17037). Also reports
  `vsc_mean`. Checks: unobstructed window 0.3967 (BRE 39.6 %); continuous 25° obstruction 0.273 (BRE 27 %).
- Re-scored all schemes (the floor "fail ratio ≤ 0.15" is unchanged; only the method is):
  E 79.85 → **71.87**, A 79.03 → **71.13**, D 68.74 (already missed), B 62.85 (now the only option meeting every floor,
  fail ratio 0.096), C 61.68 → **55.52** (0.156, just over). Ranking unchanged: E, A, D, B, C. Client baseline 0.251.
- `02_regulations/summary.md` §20 row updated. `tools/search_options.py` uses the same function, so later searches
  optimise against VSC automatically. Next lever for A/E: pull the tower away from the street bar / thin the bars.

## 2026-11-10 — iteration 19: D8 hotel programme per option — KEPT (completeness)
- `pipeline/psp.py::hotel_programme()`: splits hotel storeys by use into lobby + F&B, meeting, spa and room floors;
  keys from **room floors only** (mix 70 % standard 28 m² / 20 % superior 34 m² / 10 % suites 56 m² net, 62 %
  efficiency); per-key public areas vs 4* benchmarks (lobby + F&B ≥ 2.0, meeting ≥ 1.5, spa ≥ 0.8 m²/key); flags
  outside 300–450 keys, with the number of top room floors to convert. All ASSUMED until the brief arrives.
  `hotel_keys_est` now comes from this (before: all hotel GFA incl. lobby floors at 34 m²/key).
- `06_reports/capacity_study.md` has a new "Hotel programme" table. Keys: E 592, A 581 (both > 450 → convert ≈6–7 top
  floors), B 435 (in range), C 357 (in range, no meeting/spa), D 214 and client 257 (< 300, no meeting/spa). Meeting
  space is short in every option (1.24 m²/key where present).
- Scores unchanged (GFA-based). New backlog item **D11**: apply these flags to the options and re-score.

## 2026-11-11 — iteration 20: D11 apply the hotel-programme flags — KEPT
- `tools/make_options.py`: block option **`key_cap`** (`cap_keys()`) turns the top hotel-room floors into serviced
  apartments until room floors give ≤ cap keys (same mix/efficiency as `psp.hotel_programme`); used for the hotel
  tower of A and E (also in `tools/search_options.py`). `build_from_existing` edit **`first_typical_use`**.
- `pipeline/psp.py::hotel_programme`: conference / spa floors in any new building count as hotel facilities (B's
  podium conference floor).
- Changes: A 581 → **441** keys (+86 serviced flats), E 592 → **426** keys; C gets a conference/spa floor above the lobby
  (3.2 m, same envelope — a 3.6 m version broke §21 by one window and was rejected) → 317 keys; D: C2's first upper
  floor becomes conference/spa → 196 keys (still < 300: the client's hotel is small).
- Hotel programme flags: A, B, C, E **OK**; D only "keys < 300". Scores unchanged (E 71.87, A 71.13, D 68.74,
  B 62.85, C 55.52), all hard rules pass; parking re-sized automatically (still 2 levels for A/B/C/E).

## 2026-11-11 — iteration 21: D9 presentation — client vs the two best options — KEPT (completeness)
- Cycles aerials (S + SE) of option E (A's from iteration 15 still current; the later D6/D11 changes are below ground
  or use-only). All aerials use the context-calibrated client camera, so the three images are directly comparable.
- `tools/score_options.py` now generates a **one-page comparison** at the top of `06_reports/capacity_study.md`:
  side-by-side image `06_reports/capacity_comparison.jpg` (client | #1 | #2), a metric-by-metric table and derived
  reading lines (client fails §21 + §25; E / A pass every hard rule with 87 % / 86 % of the client's GFA; option D is
  the largest legal floor area, 94 %, but misses two quality floors).
- No geometry change; scores unchanged.

## 2026-11-11 — iteration 22: D10 verify parking zone 02 — BLOCKED
- PSP §25 odst. 2 + příloha 3 point to the Atlas Prahy layer "Zóny města – parkovací stání"
  (app.iprpraha.cz/apl/app/atlas-prahy/?&service[]=zony-mesta-parkovaci-stani). app.iprpraha.cz is reachable, but the
  layer itself is an ArcGIS MapServer on **gs-pub.praha.eu** (also gs-mep.mepnet.cz / gs-prv.praha.eu), and the
  environment's egress proxy refuses those hosts (403 on CONNECT). LOOP forbids adding hosts → item marked blocked.
- Sensitivity of the ASSUMED zone (spaces of margin = capacity − required minimum, current basement levels):

  | Zone | Client | A | B | C | D | E |
  |---|---|---|---|---|---|---|
  | 01 | −142 | +220 | +377 | +348 | +157 | +203 |
  | 02 (assumed) | −241 | +135 | +314 | +281 | +66 | +116 |
  | 03 | −364 | +36 | +236 | +202 | **−50** | +14 |

  The client scheme fails in every zone; in zone 03 option D would need a 4th basement level and A/E become tight.
- To unblock: the user reads the zone for the plot (Milevská / Na Pankráci) off the public Atlas map, or allows
  gs-pub.praha.eu for this environment. No model change; scores unchanged.

## 2026-11-11 — iteration 23: A8 block C roof — KEPT
- Section D items are done or blocked (D10), so the loop is back on section A.
- Client roof features back-projected through the context-calibrated render-000 camera at roof level: C1's dark core
  box ≈ 7.5 × 9.4 m near the roof centre (ours was 4 m nearer the street and too pale — that is why it showed above the
  parapet in our street view), 7 rooftop units in two rows; C2 is a planted roof garden.
- Params: C1 core `dx 1.4, dy −0.4, 7.5 × 9.4 m, h 3.0, Roof metal`; 7 units 2.4 × 2.4 × 1.6 m at the measured spots;
  C2 roof gets three raised green planters. The roof subdivision walls in the client image are only low walls — no
  footprint change (C1/C2 massing already matched the calibrated aerial).
- Score: Workbench mean 0.4644 → 0.4656 (aerial +0.004, SW +0.002); Cycles (aerial + SW re-rendered) **0.4851 → 0.4855**.
  IFC 0 errors; test block 6/6.

## 2026-11-11 — D10 unblocked (user allowed gs-pub.praha.eu) — parking zone 02 VERIFIED
- User granted the same network access as other chats in this project; gs-pub.praha.eu added to the environment's
  allowed hosts. Queried `dop/psp_zony_parkovani/MapServer/0` (Zóny parkování města (PSP), HMP-IPR) with the official
  plot polygon in S-JTSK: one feature, OBJECTID 23, **ZONA 02** — the whole plot is in zone 02. Saved as
  `02_regulations/raw/psp_parking_zones_plot.geojson`.
- `rules.yaml` (psp25 source), `summary.md` §25 row and `pipeline/psp.py` comment now cite the verified zone instead of
  ASSUMED. No numbers change: every parking figure already used zone 02.
