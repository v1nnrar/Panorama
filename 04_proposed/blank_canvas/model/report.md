# Panorama Pankrác — blank canvas — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 0 |
| storeys_above_ground | 0 |
| gfa_below_ground_m2 | 0 |
| height_top_of_parapet_m | 0.0 |
| footprint_area_m2 | 0.0 |
| gfa_m2 | 0 |
| net_floor_area_m2 | 0 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.0 |
| plot_ratio_far | 0.0 |
| unbuilt_ratio | 1.0 |
| footprint_outside_plot_m2 | 0.0 |
| parking_zone | 02 |
| parking_required_min | 0 |
| parking_required_max | 0 |
| parking_capacity_est | 0 |
| parking_margin | 0 |
| gfa_by_use_m2 | {} |
| flats_est | 0 |
| hotel_keys_est | 0 |
| hotel_programme | None |
| psp22_min_boundary_distance_m | None |
| psp21_windows_checked | 0 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 0 |
| daylight_proxy_fail_ratio | 0.0 |
| vsc_mean | 0.0 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 7.68 |
| courtyard_area_2h_sun_ratio | 1.0 |
| open_ground_m2 | 16491.7 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 0.0 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 0 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 0 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | None | ⚪ N/A | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 0 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — zone 02 (verified 2026-11-11: gs-pub.praha.eu dop/psp_zony_parkovani/MapServer layer 0 (Zóny parkování města (PSP), HMP-IPR), plot polygon intersects only OBJECTID 23, ZONA 02 — raw/psp_parking_zones_plot.geojson; bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
