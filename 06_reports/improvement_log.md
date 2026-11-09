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
