# Compliance — existing (client) scheme vs Metropolitan Plan of Prague

Date: 2026-11-09 · Model: `03_existing/params.yaml` (after the measurement audit and iteration 9) ·
Rules: `02_regulations/rules.yaml` (MPP in force since 1 Sep 2026; locality 058 Horní Pankrác, [S], storey range 27) ·
Build: `build.py 03_existing/params.yaml --no-blender --rules 02_regulations/rules.yaml` → **3/3 automated rules pass**.

## Automated rules
| Rule | Limit | Value | Margin | Status | Source |
|---|---|---|---|---|---|
| max_height — regulated building height, range 27 | ≤ 100 m | 83.8 m to A's parapet (metric `height_top_of_parapet_m`) | 16.2 m (16 %) | **PASS** | MPP čl. 98/3; Z 02 / KLZ 058 |
| — strict reading: highest element of A | ≤ 100 m | ≈ 85.1 m (rooftop box; diagrid crown 84.9 m) | 14.9 m (15 %) | **PASS** | as above |
| max_storeys — range 27 | ≤ 27 | 22 (A: podium level + 21) | 5 storeys | **PASS** (limit is an interpretation of the range label, see rules.yaml) | MPP čl. 98/3 |
| hppreg_info — HPPreg / Zmax | not set in [S] | GFA 91,483 m² above ground (FAR 5.55) | — | INFO | MPP čl. 96/2 |

No margin is below 5 %.

## Checklist items from `02_regulations/summary.md` (not automatable)
| Item | Status |
|---|---|
| Plot entirely in stabilised area [S] (no T/R hatch) | **unknown** — read from the binding KLZ 058 map at ±5 m; needs confirmation from IPR / building authority |
| Stabilised-area condition: respect existing character and surrounding heights (čl. 70/1, 98/2a) | **unknown** — authority judgement. Context: City Tower 109 m, V Tower 105 m, City Empiria 104 m, existing hotel 79 m; tallest new element ≈ 85 m |
| MPP gross floor area counts underground floors except garages/service (čl. 96/1) | **not shown** — model has 17,194 m² below ground (U, parking); its non-garage share is not modelled |
| East wedge (parcels 1133/12, 1052/244, existing office E) next to metro D corridor VPS 910-621 | **not shown** — corridor not in the model; E is existing and kept |
| Prague Building Regulations (PSP: distances, daylight, parking, greenery) | **not checked** — no rules yet |
| Existing permit / territorial decision under the old plan | **unknown** — ask the client |

## Model observations relevant to compliance
- `footprint_outside_plot_m2` = 9.1 m² (was 53 m² before the audit): **E 6.5 m²** (existing building; OSM outline vs
  ČÚZK parcel line — the survey README reports 0.3–0.8 m offsets in that data) and **B2 2.7 m²** (inside the ±3 m
  measurement tolerance of the audit). Neither is evidence of a real encroachment.
- `min_setback_m` = 0.0: buildings touch the plot boundary (street line) — normal for a city block, but PSP distance
  rules are not yet checked.

## What would have to change
Nothing fails. If the stricter "highest point" reading is used the margin is still 14.9 m. Open items above need
documents or authority confirmation rather than model changes.
