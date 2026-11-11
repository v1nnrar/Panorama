# Option B — twin towers on a podium — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 6 |
| storeys_above_ground | 27 |
| gfa_below_ground_m2 | 27575.9 |
| height_top_of_parapet_m | 95.2 |
| footprint_area_m2 | 5733.5 |
| gfa_m2 | 62850.5 |
| net_floor_area_m2 | 59765.7 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.348 |
| plot_ratio_far | 3.811 |
| unbuilt_ratio | 0.653 |
| footprint_outside_plot_m2 | 6.5 |
| min_setback_m | 0.0 |
| parking_zone | 02 |
| parking_required_min | 467 |
| parking_required_max | 527 |
| parking_capacity_est | 781 |
| parking_margin | 314 |
| gfa_by_use_m2 | {'hotel': 23400.9, 'congress': 3143.8, 'retail': 3027.9, 'residential': 20387.3, 'office': 6717.5} |
| flats_est | 244 |
| hotel_keys_est | 435 |
| hotel_programme | {'keys': 435, 'keys_by_type': {'standard': 304, 'superior': 87, 'suite': 44}, 'areas_m2': {'lobby_fnb': 900, 'meeting': 2784, 'spa': 360, 'rooms': 22501}, 'm2_per_key': {'lobby_fnb': 2.07, 'meeting': 6.4, 'spa': 0.83}, 'flags': [], 'assumptions': '4* city hotel mix 70/20/10 (28/34/56 m² net), 62 % room-floor efficiency; ASSUMED'} |
| psp22_min_boundary_distance_m | 2.56 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 240 |
| daylight_proxy_fail_ratio | 0.096 |
| vsc_mean | 0.293 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 3.23 |
| courtyard_area_2h_sun_ratio | 0.651 |
| open_ground_m2 | 9971.7 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| H | Hotel tower | Hotel | 27 | 95.2 |  | 900.0 | 24300.9 | 23180.1 |
| T | Residential tower | Residential | 27 | 89.1 |  | 784.1 | 21171.4 | 20126.1 |
| P | Podium (retail + conference) | Retail | 2 | 10.7 |  | 2243.8 | 4487.6 | 4280.0 |
| O | North office wing | Office | 6 | 24.0 |  | 1119.6 | 6717.5 | 6359.3 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 32.0 | 32.0 | 685.9 | 6173.1 | 5820.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 13788.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 95.2 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 27 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 62850.5 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 2.56 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 314 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — ASSUMED zone 02 (bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
