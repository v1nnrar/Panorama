# Option C — mid-rise city blocks (no towers) — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 5 |
| storeys_above_ground | 10 |
| gfa_below_ground_m2 | 27575.9 |
| height_top_of_parapet_m | 38.4 |
| footprint_area_m2 | 6237.0 |
| gfa_m2 | 61683.8 |
| net_floor_area_m2 | 58580.6 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.378 |
| plot_ratio_far | 3.74 |
| unbuilt_ratio | 0.622 |
| footprint_outside_plot_m2 | 6.5 |
| min_setback_m | 0.0 |
| parking_zone | 02 |
| parking_required_min | 507 |
| parking_required_max | 548 |
| parking_capacity_est | 781 |
| parking_margin | 274 |
| gfa_by_use_m2 | {'hotel': 20479.0, 'retail': 2383.6, 'residential': 21452.2, 'office': 11195.9} |
| hotel_keys_est | 373 |
| flats_est | 257 |
| psp22_min_boundary_distance_m | 3.07 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 276 |
| daylight_proxy_fail_ratio | 0.145 |
| courtyard_sun_hours_mean_mar21 | 2.02 |
| courtyard_area_2h_sun_ratio | 0.432 |
| open_ground_m2 | 9382.3 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| HW | West block — hotel | Hotel | 10 | 35.3 |  | 2047.9 | 20479.0 | 19475.9 |
| RE | East block — apartments | Residential | 10 | 33.7 |  | 2383.6 | 23835.8 | 22685.7 |
| O | North office wing | Office | 10 | 38.4 |  | 1119.6 | 11195.9 | 10598.8 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 32.0 | 32.0 | 685.9 | 6173.1 | 5820.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 13788.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 38.4 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 10 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 61683.8 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 3.07 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 274 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — ASSUMED zone 02 (bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
