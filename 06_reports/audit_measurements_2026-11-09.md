# Measurement audit — existing scheme (2026-11-09)

Requested by the user: "analyze again so all measurements are correct, double check everything".

## Method
1. **New tool `tools/project_outlines.py`**: draws every building's model outline (roof edge, base, corner verticals) and the
   surrounding buildings (OSM/archiMap footprints + heights) through each camera onto the client image
   (`03_existing/overlays/outline_*.jpg`). Checked on our own render first: the outlines sit exactly on the model.
2. **Problem found:** the earlier cameras had been tuned to match *our* buildings, so they absorbed our modelling errors.
   In the aerial (render-000) the real surroundings (drum towers, slab blocks, shopping centre) were 70–150 px off.
3. **Aerial camera re-calibrated on reference geometry only** — 6 roof corners of the 8-storey slab blocks south of the
   street, 2 drum-tower roofs, edges of the 104 m tower; none of our buildings used. Result: **4.4 px RMS**,
   37 mm lens from (−94, −256, 219) (the old camera was 76 mm from 640 m away).
4. With the calibrated camera, client roof/base corners were **back-projected** to plan positions at their verified heights;
   where a base and a roof corner of the same vertical edge were both visible, the height was solved independently.
5. Cross-checks: ČÚZK orthophoto (`00_site/survey/grid_ortho.jpg`, today's site) and the client's top-view board
   (registered to the survey grid, 2.4 m RMS, corrected for the lean of tall roofs).

## Results per building
| Building | Check | Finding | Action |
|---|---|---|---|
| **A** diagrid tower | calibrated aerial: SW vertical edge base on podium + roof → height **86.3 m**, centre (2.7, 14.4); board (lean-corrected): centre (4.6, 11.2) | model centre (7.8, −0.5) was **~13 m too far south, ~4 m too far east**; height 83.8 m confirmed within ~2.5 m | moved **4.15 m W, 10.0 m N** (limited so the facade keeps 3 m to D; residual ≈3 m is inside the measurement spread) |
| **A0** podium | follows A | — | re-drawn around the moved tower + original link strip |
| **B** tower | roof back-projected at 68.9 m: 26.2 × 37.1 m rectangle, corners within 2–3 m of model | OK (22 storeys verified earlier) | none |
| **B2** terraced block | terrace corners + independent vertical check (25.8 m) | south face **~8 m too far south** (53 m² was outside the official plot), east end ~5 m too far east; PV penthouse is a 26 × 9.5 m box **along tower B's south face**, not in the SE corner | footprint + penthouse moved; outside-plot area now 9 m² |
| **B3** | hidden behind B in all views | not measurable | none |
| **C1 / C2** | outlines coincide with the client image in the calibrated aerial; window rows verified (iteration 5) | OK | none |
| **D** | west wing roof/base corners within 1–2 m | OK (8 storeys, 32.3 m, iteration 7) | none |
| **E** existing office | ČÚZK orthophoto + render-002 | OSM polygon included a **45 m wedge south to (106.7, −53.2)** that is ramp/greenery on the orthophoto, not building | trimmed at y ≈ −6.9 |

## Metrics change
GFA 98,225 → **91,483 m²** (E −4,019, B2 −3,138, A0 +416); built-up ratio 0.531 → 0.502; FAR 5.96 → 5.55;
footprint outside plot 53.2 → 9.1 m².

## Cameras
* render-000 aerial: **calibrated on context** (above). Its edge score went down (0.279 → 0.249 Workbench) while the visual
  alignment of *everything* (our buildings and the real surroundings) is clearly better — the edge score also counts
  generated trees and ground textures, so it is weaker evidence than the reference-point calibration.
* render-004 / -005 / -006: re-tuned with `tools/cam_search.py` after A/B2 moved (they have too little context to calibrate
  independently).
* render-003 park: calibrated on D earlier; still valid. The client image does **not show tower A** at all although it must
  be visible above D from that point (marketing render omits it) — so that camera's score is capped.

## Open points / uncertainty
* A: ±3 m in plan; the 3 m gap to D is an assumption (the board shows A's roof almost touching D).
* A's plan size: aerial suggests a slightly smaller diagrid ring (~35 m), the board slightly larger (~42 m) → kept 33.6 × 35.3 m.
* B2 east face: the aerial and render-002 show terraces stepping back on the **road side**; kept straight per the user's
  instruction (2026-11-09) — confirm.
* render-002 (from the SE) is the best second view for a full two-view triangulation; E's inset courtyard face makes its
  calibration harder — next step if more precision is needed.
