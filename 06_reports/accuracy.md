# Accuracy of the existing-scheme model — per building (P5, 2026-11-12)

Goal set by the user (2026-11-11): every position and height to **±1 m** where the client images allow it.
Values are 1-σ estimates. "Plan" is horizontal position of the outline, "height" the roof/parapet edge above the site
ground floor (z = 0 = 267.70 m a.s.l., ČÚZK DMR 5G).

## Reference frame and camera
| Item | Source | Accuracy |
|---|---|---|
| Plot, parcels | ČÚZK cadastre (WFS), official | ±0.1–0.3 m |
| Neighbour heights | ČÚZK DMP 1G surface model (main roof plane) | ±0.4 m |
| Neighbour outlines | RÚIAN building register | ±0.3 m |
| Aerial camera (render-000 = render-001) | 14 checked roof corners of 11 RÚIAN references (`tools/calibrate_camera.py --points`) | **1.64 px = 0.42 m** at the site |
| Second view (render-002) | client CG massing not survey-consistent | **not available** (P2 blocked) |

With one calibrated view a roof corner is fixed **across** the line of sight to ≈ ±0.35 m regardless of height; **along**
the line of sight it moves 1.2–2.2 m per metre of height error, so plan accuracy there depends on how well the height
is known (storey counts, vertical edges).

## Per building
| Building | Plan | Height | Method / evidence | Views | Within ±1 m? |
|---|---|---|---|---|---|
| **B** tower | ±0.4 m across, ±1.2 m along | ±1.0 m (22 storeys, 68.9 m) | 4 measured roof corners agree to 0.66 m; moved 3.9 m (iteration 28) | 1 (+ street views for storeys) | **yes across, ≈ along** |
| **B2** terraces + PH | PH ±1.0 m; terrace block ±2 m | ±0.8 m (8 storeys) | PH: 2 measured corners (iteration 28); terraces from the audit (old camera) + vertices on B's walls follow B | 1 | PH yes; block no |
| **B3** | ±3–5 m | ±1.5 m | never visible; moves with B (ASSUMED) | 0 | no |
| **C1** | SW corner ±0.4 m across / ±0.8 m along; NW within 0.5 m across | **±0.6 m** (31.05 m) | SW vertical edge (base + roof), storeys re-counted in render-005 and render-000 (iterations 29–30) | 2 (aerial + street, for height) | **yes** |
| **C2** | ±2 m (east part not measured) | ±0.6 m (same levels as C1) | cornice/window rows continuous with C1 | 2 (height) | height yes, plan no |
| **D** butterfly office | west edge orientation matches; ±1–2 m across, **±5 m along** | ±0.5 m (8 storeys, 32 m; 6 visible bands confirm) | 2 parapet corners; along-view offset not separable from the butterfly roof's varying parapet height (iteration 31) | 1 (+ render-003 for height) | height yes, plan **no** |
| **A** diagrid tower | ≈ ±1.8 m across, **±4 m along** | ±2.5 m (83.8 m, 7 diagrid modules) | crown corners: near and far disagree by 8.7 m along the view → crown size vs height ambiguous (iterations 28–29) | 1 | **no** |
| **A0** podium | ±3 m | ±0.5 m (one storey, 5–6 m) | back-projected podium edges (iteration 24, previous camera) | 1 | no |
| **E** existing office | **±0.3 m** (RÚIAN outline) | ±1.0 m (roof edge 29.2 m; NE 30.0 / SE 28.3) | cadastral outline + roof edge on the surveyed corners' verticals (iteration 32); ground level unknown | 1 | **yes** (roof); ground no |
| **U** basement | ASSUMED | ASSUMED | 2 levels assumed from the top view | 0 | no |

## What would close the gaps
1. **Client drawings** (site plan DWG/PDF, sections) — would fix A, A0, B2, B3, C2 and D directly; best option.
2. **A second calibrated view**: the client's camera data for render-002 (3ds Max / Lumion) or their context model,
   or another photo-based client image → true two-view triangulation for A and D (LOOP P2/P3b).
3. A site photo of office E's ground floor (or the building permit) → E's ground level.

## Reproduce
```bash
.venv/bin/python tools/calibrate_camera.py 03_existing aerial_S_like_render000 --points --only-manual \
    --manual 03_existing/overlays/calib_render000_points.json
.venv/bin/python tools/triangulate.py 03_existing aerial_S_like_render000 \
    --solve 03_existing/overlays/measure_render000_corners.json
```
Detailed measurements: `06_reports/measure_render000.md`; history: `06_reports/improvement_log.md` (iterations 25–32).
