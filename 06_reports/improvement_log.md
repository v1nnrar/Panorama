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
