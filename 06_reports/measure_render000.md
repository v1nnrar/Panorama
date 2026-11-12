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
