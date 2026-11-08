# Site survey — grid cross-referenced with ČÚZK maps

All project geometry uses one **local survey frame**: azimuthal equidistant projection centred on
**Milevská 7, Praha 4** (50.04919 N, 14.43819 E), metres, **x = east, y = true north**, z = 0 at ground floor.
`proj4: +proj=aeqd +lat_0=50.04919 +lon_0=14.43819 +datum=WGS84 +units=m`. This is the same frame as the
psg-website overview, so website and model coordinates are interchangeable.

Conversions (pyproj): local ↔ **S-JTSK / Křovák East North (EPSG:5514)** ↔ WGS84. The S-JTSK grid is rotated
**−7.8°** from true north here (scale 1.0008), which is why the survey grid is drawn north-up in the local frame.

## Verification against the official cadastre
* 254 parcels of the PSG/archiMap data matched to ČÚZK INSPIRE parcels (WFS): mean offset **0.34 m**, max 0.84 m
  (best-fit similarity: 0.28 m mean) — the frame is correct; remaining offsets are in the third-party data.
* The plot (`00_site/site.yaml`) now uses the **official ČÚZK parcel geometry** (fetched via WFS).

## Plot — official parcels (ČÚZK)
| Parcel | Cadastral area | Official area (m²) | Geometry area (m²) |
|---|---|---|---|
| 1051/3 | Krč | 5618 | 5619.5 |
| 1090/2 | Krč | 2561 | 2561.4 |
| 1133/1 | Krč | 2346 | 2346.4 |
| 2841/1 | Nusle | 1681 | 1681.7 |
| 1133/12 | Krč | 1514 | 1514.4 |
| 1051/16 | Krč | 1020 | 1019.8 |
| 1051/5 | Krč | 600 | 600.5 |
| 1133/13 | Krč | 595 | 596.3 |
| 1052/244 | Krč | 250 | 249.7 |
| 1133/2 | Krč | 227 | 226.8 |
| 1133/21 | Krč | 75 | 75.1 |
| **Total** | | **16487** | union 16491.7 |

The two parcels the PSG data had without numbers are **1133/13** (595 m²) and **1052/244** (250 m²).

## Grid
* 10 m minor lines, 50 m major axes. Columns lettered **A, B, C…** from x = −150 (west → east), rows numbered
  **1, 2, 3…** from y = +200 (north → south). Example: grid point **D5** = (0, 0) = Milevská 7.
* `grid_ortho.jpg` — grid on the ČÚZK orthophoto (warped to the local frame, 0.2 m/px), official parcels (magenta),
  existing-scheme footprints (blue).
* `grid_cadastre.jpg` — same on the ČÚZK cadastral map (KN layer).
* `site_survey_grid.dxf` — grid, official parcels, footprints (layers GRID_*, PARCEL_OFFICIAL, FOOTPRINT).
* `control_points.csv / .md` — origin, plot hull corners and grid intersections in local, S-JTSK and WGS84.
* The model's site plan (`03_existing/model/drawings/site_plan.dxf`) carries the same grid.

## Client board (top-view render) — registration and limits
`tools/register_board.py`: similarity fit with 8 control points (neighbour roofs + existing office E):
scale **0.403 m/px**, rotation **8.0°**, RMS **2.4 m**.

| Control point | board px | local (m) | residual (m) |
|---|---|---|---|
| 3-wing building, W wing S end | [316, 240] | [57, 20] | 1.31 |
| 3-wing building, M wing S end | [386, 240] | [84, 26] | 1.62 |
| 3-wing building, E wing S end | [456, 240] | [113, 31] | 1.93 |
| E office NW corner | [394, 263] | [93, 16] | 3.16 |
| E office S tip | [400, 420] | [100, -48] | 2.37 |
| drum N roof garden centre | [28, 80] | [-68, 66] | 3.29 |
| drum NE roof garden centre | [12, 190] | [-67, 27] | 2.9 |
| drum SE roof garden centre | [25, 290] | [-54, -14] | 2.17 |

The board is a phone photo of a printed **perspective** render: tall roofs lean outward (roofs read 1.2–1.3× too
large; camera ≈400–440 m) and the photo adds keystone. Perspective-corrected **sizes** agree with the model
(A diagrid ≈34×36 m vs 33.6×35.3; B green tower ≈26×37 m vs 27.8×37.5; D butterfly ≈20–23×65–71 m vs 23.2×70.9),
but absolute **positions** of the tall blocks cannot be pinned better than ≈5–10 m from this image.
→ Footprints stay at the PSG v3 fit. **For exact scheme positions we need the client's site plan (DWG/PDF).**

## Reproduce
```bash
.venv/bin/python tools/site_survey.py all      # fetch ortho + cadastre, official parcels, grid sheets, DXF
.venv/bin/python tools/register_board.py       # board → grid overlay (board_overlay.jpg)
```
Hosts used: ags.cuzk.gov.cz (orthophoto WMS), services.cuzk.gov.cz (cadastral WMS + parcel WFS).
