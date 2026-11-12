# Roof-corner measurement in calibrated render-000 (P3, single view) — 2026-11-12

Camera: aerial_S_like_render000, calibrated on surveyed references (1.64 px = 0.42 m). Corners: tools/triangulate.py detect
+ visual check (03_existing/overlays/measure_render000_corners.json, 15 of 42 accepted). Plan positions back-projected at the
model roof height (±0.5 m); ellipse = 1-σ from ±1.5 px and ±0.5 m, long axis along the line of sight.
Shifts are vs. the model **before** iteration 28 (B, B3, B2 PH then moved).

| Building | corners | mean shift dx, dy (m) | max |shift| (m) | spread (m) |
|---|---|---|---|---|
| A | 3 | +0.20, +3.39 | 7.19 | 4.09 |
| B | 4 | -3.93, -0.23 | 4.62 | 0.66 |
| B2 | 2 | -1.16, -1.62 | 2.31 | 0.38 |
| C1 | 2 | +0.06, -6.13 | 6.40 | 0.31 |
| D | 1 | -0.45, -1.67 | 1.73 | nan |
| E | 3 | -2.99, -1.15 | 7.26 | 4.29 |

| Building | vertex | measured x, y | shift vs model (m) | |shift| | 1-σ ellipse (m) |
|---|---|---|---|---|---|
| A | 0 | -12.39, -7.62 | -1.38, +5.19 | 5.37 | 1.24 × 0.33 @ 72° |
| A | 1 | 26.95, 0.59 | +1.55, +7.02 | 7.19 | 1.37 × 0.35 @ 65° |
| A | 3 | -17.94, 23.23 | +0.42, -2.03 | 2.07 | 1.40 × 0.35 @ 75° |
| B | 0 | 51.78, -16.73 | -3.32, -0.07 | 3.32 | 1.23 × 0.36 @ 58° |
| B | 1 | 58.36, -53.76 | -3.40, -0.14 | 3.40 | 1.08 × 0.32 @ 53° |
| B | 2 | 84.56, -48.82 | -4.39, -0.75 | 4.45 | 1.18 × 0.33 @ 49° |
| B | 3 | 76.67, -11.67 | -4.62, +0.07 | 4.62 | 1.32 × 0.37 @ 55° |
| B2 | 0 | 70.49, -63.25 | -1.51, -1.75 | 2.31 | 0.89 × 0.34 @ 49° |
| B2 | 3 | 69.00, -54.30 | -0.80, -1.50 | 1.70 | 0.92 × 0.35 @ 50° |
| C1 | 0 | -32.34, -45.61 | +0.23, -6.40 | 6.40 | 0.78 × 0.32 @ 74° |
| C1 | 2 | -12.78, -65.48 | -0.11, -5.86 | 5.87 | 0.73 × 0.31 @ 67° |
| D | 1 | -38.50, 18.22 | -0.45, -1.67 | 1.73 | 1.03 × 0.37 @ 79° |
| E | 1 | 97.32, -2.81 | -0.95, +4.06 | 4.17 | 1.20 × 0.41 @ 53° |
| E | 8 | 119.79, -8.38 | -6.04, -4.03 | 7.26 | 1.23 × 0.40 @ 49° |
| E | 13 | 123.83, 14.55 | -1.99, -3.47 | 4.00 | 1.33 × 0.43 @ 51° |

## Reading
- **B**: 4 corners agree (spread 0.66 m): 3.0 m across the line of sight (height-independent) + 2.5 m along it → moved (−3.93, −0.23).
- **B2 PH**: 2 corners agree (0.38 m) → moved (−1.16, −1.62).
- **D**: 1.7 m (1 corner) — needs more corners before a change.
- **A**: south crown corners 5–7 m north of the model, NW corner −2 m: inconsistent → crown size / corner identity to re-check.
- **C1**: the detected 'v0' has a south facade below it, so it is not the NW corner → identity wrong; re-pick.
- **E**: inconsistent; the client's E differs from the RÚIAN outline — handled in P4.

## Iteration 29 (2026-11-12): hand-read corners and a vertical edge
| Item | image px | result | vs model |
|---|---|---|---|
| A NW crown (v3) | 449.5, 193.7 | (−20.83, 24.74) at 83.5 m | along −1.5, across −2.1 m |
| A SE crown (v1) | 674.8, 198.7 | (26.89, 0.77) at 83.5 m | along **+7.2**, across −1.5 m |
| D NW roof (v0) | 380.0, 362.5 | (−39.89, 40.95) at 32.0 m | across +2.9 m |
| D SW parapet (v1) | 400.8, 408.3 | (−40.48, 17.47) at 32.0 m | across −1.3 m |
| **C1 SW vertical edge** | base 540.4, 689.0 / roof 531.7, 595.0 | base on DMR 5G terrain (−0.45 m) → **(−31.89, −57.07)**; roof on the same vertical → **28.2–28.6 m** | 3.8 m W, 1.7 m N; roof **5.2 m lower** than 33.6 |
| C1 NW roof (v0) | 497.3, 551.7 | at 28.4 m → (−34.67, −40.90) | (−2.1, −1.7) m |

- **C1 height**: at 28.4 m the SW roof corner falls 0.6 m from its own base; at the model's 33.6 m it would be 6 m off —
  geometry alone says ≈ 28.4 m. Brightness profile down the SW edge: 9 window rows at 9.4 px (≈ 2.85 m) + a dark
  ground-floor band → 10 storeys. **Conflicts with render-005** (10 window rows over a tall glazed GF = 11 storeys,
  iteration 5). C2 shares C1's levels. → Re-count render-005 before changing (next P3 step).
- **A**: near (SE) and far (NW) crown corners disagree along the view by 8.7 m → a crown-size or height difference that
  one view cannot separate; across the view both agree on ≈ −1.8 m. Kept; needs a second view.
- **D**: the measured west wing edge runs almost N–S (1.4°), the model's at 10.5° → a rotation of D's west wing, 2 points
  only. Kept.

## Iteration 31 (2026-11-12): D west wing
| Item | image px | result at roof 32.0 m (±0.5) | vs model |
|---|---|---|---|
| D NW parapet corner (v0) | 371.3, 376.3 | (−43.66, 35.17), σ 1.1 m | cross +1.75, along −7.40 m |
| D SW parapet corner (v1) | 401.3, 410.5 | (−40.62, 16.46), σ 1.0 m | cross −0.98, along −4.18 m |
- The earlier D v0 read (380, 362.5) was the top of the sloping butterfly roof, not the parapet corner.
- West edge: bearing −9.2° (model −10.6°), length 19.0 m (model 23.2 m).
- D's SW vertical edge: with the roof at 32 m the lowest visible facade point lies at z ≈ 10.9 m — the GF and the first
  floor are hidden by the A0 podium and trees; the 6 visible bands at 3.45 m fit, so the roof height is consistent.
- Along-view offsets of 4–7 m change by 1.48 m per metre of assumed roof height, and a butterfly roof's parapet height
  varies → **not separable in one view; D unchanged.** A likewise (crown size vs height). Both → LOOP P3b.
