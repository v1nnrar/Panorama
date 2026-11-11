# Regulations — Panorama Pankrác plot

**Governing plan:** Metropolitan Plan of Prague (Metropolitní plán, MPP), issued by Prague City Assembly
on 28 May 2026 (OOP 001/2026), **in force since 1 Sep 2026**; it replaced the 1999 zoning plan (KPP letter codes no
longer apply). A court review (MS Praha 11 A 24/2026) is pending. Raw sources in `raw/`.

## Classification of the plot (16,492 m², 11 ČÚZK parcels)
| Item | Value | Source |
|---|---|---|
| Locality | **058 / Horní Pankrác** (Krč, Michle, Nusle; 40 ha) | KLZ 058 |
| Stability | **[S] stabilised** — target character derived from existing character (čl. 69, 70) | KLZ 058, map |
| Structure | **(03) hybrid** — compact/loose blocks and solitaires forming sub-centres, varied heights (čl. 43) | KLZ 058 |
| Use | residential-buildable (admin + commercial part of the locality) | KLZ 058 |
| Transformation areas | none on the plot; T 411/058/2336 and 2235 lie east of the metro D corridor | KLZ 058 map (`klz058_plot_overlay.png`) |
| Height squares | all plot squares (S-JTSK E −742273…−741973, N −1047495…−1047295) = **storey range 27** (black = above height-stable development) | Z 02 / KLZ 058 map |

## Limits
| Rule | Limit | Client scheme (model) | Status |
|---|---|---|---|
| Max regulated height (range 27) | **100 m** | 83.8 m (A) | ✅ 16 m headroom |
| Max storeys (range 27 = 22–27 RNP) | **27** (interpretation) | 22 | ✅ |
| Regulated floor area HPPreg / Zmax | **not set** in [S] areas (čl. 95, 96 apply to [T]/[R] only) | 91,483 m² above ground (FAR 5.55) | ℹ️ no numeric cap |
| Stabilised-area condition | changes must take the existing character and surrounding heights into account (čl. 70/1, 98/2a) | neighbours: City Tower 109 m, V Tower 105 m, City Empiria 104 m, hotel today 79 m | judged by the building authority |
| Tower level XIV. Pankrác | towers max **70 m**, max 75 % of built area — **only on the pink "8 (21)" squares** by metro D, not on this plot | KLZ 058/200 | n/a |

## Floor-area benchmark (for negotiation, not binding here)
HPPreg = plot × Zz × Vz (čl. 96). If the neighbouring transformation-area values applied to this plot:
| Basis | Zz × Vz | HPPreg for 16,492 m² | with +5 pp bonus (čl. 96/6) |
|---|---|---|---|
| T 411/058/2235 | 35 % × 8.0 = 2.8 | 46,178 m² | 52,774 m² |
| T 411/058/2336 | 60 % × 8.0 = 4.8 | 79,162 m² | 85,757 m² |
| **Client scheme** | FAR 5.55 | **91,483 m²** above ground | — |
Note: MPP gross floor area also counts underground floors except garages and service spaces (čl. 96/1).

## Prague building regulations (PSP, nař. 12/2024, consolidated text 2025/01)
| Rule | Requirement | How we check it |
|---|---|---|
| §21 + příloha 1/II | No new building above 45° within a contiguous horizontal sector ≥45° (counted from 25° off the façade) in front of habitable-room windows of existing neighbours | `psp.py`: windows sampled every 8 m / 3 floors on neighbour façades facing the plot (OSM footprints + heights) |
| §22 odst. 2 | ≥ 2 m from boundaries with neighbouring plots (not public space) | ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public |
| §25 + přílohy 2, 3 | parking min/max = base count (HPP m² per space: hotel 100, housing 85, office 50, retail 70, restaurant 40) × zone % | **zone 02 verified** on the official PSP zone layer (IPR, 2026-11-11; whole plot in one zone) — bound 80 %, visitor 15–55 % |
| §20 | daylight per ČSN 73 0580 / EN 17037; direct-sunlight requirement for flats excluded in Prague | design proxy: vertical sky component (CIE overcast) on sampled own-façade windows, fail < 15 % (BRE 209 rule of thumb, ASSUMED); needs a proper daylight-factor study later |

## Open points
- Confirm with IPR/building authority that the plot is entirely [S] (the official GIS layers need an access token;
  this reading is from the binding KLZ 058 map, georeferenced on the plan's own 100 m grid, ±5 m).
- The east wedge (parcels 1133/12, 1052/244, existing office E) borders the metro D corridor (VPS 910-621/-/1, -/3).
- Prague Building Regulations (PSP/NPSP: distances, daylight, parking, green) are not yet checked.
- Any existing permit / territorial decision for the client scheme under the old plan would take precedence — ask the client.
