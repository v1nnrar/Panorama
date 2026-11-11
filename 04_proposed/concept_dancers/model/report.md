# Panorama Pankrác — proposed concept 'Dancers' (v0 massing) — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 10 |
| storeys_above_ground | 27 |
| gfa_below_ground_m2 | 25764.0 |
| height_top_of_parapet_m | 94.7 |
| footprint_area_m2 | 5214.0 |
| gfa_m2 | 50400.3 |
| net_floor_area_m2 | 47696.0 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.316 |
| plot_ratio_far | 3.056 |
| unbuilt_ratio | 0.684 |
| footprint_outside_plot_m2 | 0.0 |
| min_setback_m | 0.49 |
| parking_zone | 02 |
| parking_required_min | 447 |
| parking_required_max | 486 |
| parking_capacity_est | 729 |
| parking_margin | 282 |
| gfa_by_use_m2 | {'hotel': 21002.7, 'residential': 20583.5, 'restaurant': 1580.7, 'office': 7233.4} |
| flats_est | 247 |
| hotel_keys_est | 0 |
| hotel_programme | None |
| psp22_min_boundary_distance_m | 2.66 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 63 |
| daylight_proxy_fail_ratio | 0.159 |
| vsc_mean | 0.251 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 3.8 |
| courtyard_area_2h_sun_ratio | 0.716 |
| open_ground_m2 | 10459.9 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| T1 | Tower 1 — hotel (27 storeys) | Hotel | 27 | 94.7 |  | 800.4 | 17426.9 | 16588.4 |
| T2 | Tower 2 — hotel / serviced apartments (23 storeys) | Serviced apartments | 23 | 81.5 |  | 703.3 | 12880.6 | 12216.3 |
| BR | Sky bridge — lounge + bar | Restaurant | 2 | 69.2 |  | 321.0 | 642.1 | 585.1 |
| C1 | Front head — hotel restaurants + ballroom | Hotel | 5 | 19.1 |  | 379.3 | 1896.3 | 1768.0 |
| C2 | Front bar — serviced apartments | Residential | 7 | 25.7 |  | 788.7 | 5521.0 | 5219.8 |
| D | North crescent — conference + offices | Office | 7 | 25.7 |  | 1033.3 | 7233.4 | 6857.4 |
| B2 | East terraces — apartments | Residential | 8 | 29.0 |  | 492.6 | 2885.2 | 2669.9 |
| W | West pavilion — all-day dining | Restaurant | 2 | 10.4 |  | 469.3 | 938.6 | 883.9 |
| S | Spa pavilion | Hotel | 3 | 14.4 |  | 325.4 | 976.2 | 907.2 |
| U | Underground parking | Parking | 0 | 1.4 |  | 8588.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 94.7 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 27 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 50400.3 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 2.66 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 282 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — zone 02 (verified 2026-11-11: gs-pub.praha.eu dop/psp_zony_parkovani/MapServer layer 0 (Zóny parkování města (PSP), HMP-IPR), plot polygon intersects only OBJECTID 23, ZONA 02 — raw/psp_parking_zones_plot.geojson; bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
