# Option A — hotel tower + residential blocks — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 6 |
| storeys_above_ground | 27 |
| gfa_below_ground_m2 | 27575.9 |
| height_top_of_parapet_m | 95.2 |
| footprint_area_m2 | 6300.5 |
| gfa_m2 | 79769.7 |
| net_floor_area_m2 | 76100.7 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.382 |
| plot_ratio_far | 4.837 |
| unbuilt_ratio | 0.618 |
| footprint_outside_plot_m2 | 2.7 |
| min_setback_m | 0.0 |
| parking_zone | 02 |
| parking_required_min | 646 |
| parking_required_max | 703 |
| parking_capacity_est | 781 |
| parking_capacity_method | area |
| parking_margin | 135 |
| gfa_by_use_m2 | {'hotel': 24000.9, 'congress': 1200.0, 'residential': 33554.1, 'retail': 2704.2, 'office': 11397.9} |
| flats_est | 402 |
| hotel_keys_est | 441 |
| hotel_programme | {'keys': 441, 'keys_by_type': {'standard': 309, 'superior': 88, 'suite': 44}, 'areas_m2': {'lobby_fnb': 1200, 'meeting': 720, 'spa': 480, 'rooms': 22801}, 'm2_per_key': {'lobby_fnb': 2.72, 'meeting': 1.63, 'spa': 1.09}, 'flags': [], 'assumptions': '4* city hotel mix 70/20/10 (28/34/56 m² net), 62 % room-floor efficiency; ASSUMED'} |
| psp22_min_boundary_distance_m | 2.26 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 324 |
| daylight_proxy_fail_ratio | 0.194 |
| vsc_mean | 0.273 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 2.04 |
| courtyard_area_2h_sun_ratio | 0.449 |
| open_ground_m2 | 9361.9 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| H | Hotel tower | Hotel | 27 | 95.2 |  | 1200.0 | 32401.2 | 31091.4 |
| S | Street bar (Milevská) | Residential | 10 | 33.7 |  | 1696.0 | 16959.6 | 16110.5 |
| R | East bar | Residential | 12 | 39.9 |  | 1008.2 | 12098.4 | 11440.7 |
| O | North office wing | Office | 7 | 27.6 |  | 1628.3 | 11397.9 | 10930.9 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 29.2 | 29.2 | 768.1 | 6912.6 | 6527.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 13788.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 95.2 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 27 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 79769.7 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 2.26 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 135 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — zone 02 (verified 2026-11-11: gs-pub.praha.eu dop/psp_zony_parkovani/MapServer layer 0 (Zóny parkování města (PSP), HMP-IPR), plot polygon intersects only OBJECTID 23, ZONA 02 — raw/psp_parking_zones_plot.geojson; bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
