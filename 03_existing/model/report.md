# Panorama Pankrác — existing scheme (v1) — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 10 |
| storeys_above_ground | 22 |
| gfa_below_ground_m2 | 17194.0 |
| height_top_of_parapet_m | 83.8 |
| footprint_area_m2 | 8277.5 |
| gfa_m2 | 91482.8 |
| net_floor_area_m2 | 87028.2 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.502 |
| plot_ratio_far | 5.547 |
| unbuilt_ratio | 0.499 |
| footprint_outside_plot_m2 | 9.1 |
| min_setback_m | 0.0 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| A | Diagrid tower (T2) | Residential / hotel tower | 22 | 83.8 | 83.8 | 1172.6 | 25796.6 | 24752.3 |
| A0 | Diagrid tower podium + courtyard link | Lobby / restaurant | 1 | 5.9 |  | 2704.6 | 2704.6 | 2616.5 |
| B | Green tower (E residential tower) | Residential | 22 | 68.9 | 68.9 | 1165.9 | 23243.9 | 22243.8 |
| B2 | Terraced block (E) | Residential | 8 | 26.9 | 26.9 | 847.8 | 6165.3 | 5726.5 |
| B3 | Podium north (E) | Residential | 5 | 19.2 | 19.2 | 463.8 | 2319.2 | 2156.7 |
| C1 | Front slab — west head (T5) | Hotel / office | 11 | 33.9 | 33.9 | 405.4 | 4459.1 | 4150.6 |
| C2 | Front slab — wing (T5) | Hotel / office | 11 | 33.9 | 33.9 | 942.5 | 10164.8 | 9641.7 |
| D | Butterfly office (T1 bow-tie) | Office | 8 | 32.3 | 32.3 | 1061.6 | 10456.2 | 9919.9 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 32.0 | 32.0 | 685.9 | 6173.1 | 5820.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 8597.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 83.8 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 22 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 91482.8 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
