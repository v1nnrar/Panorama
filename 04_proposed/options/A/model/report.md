# Option A — hotel tower + residential blocks — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 6 |
| storeys_above_ground | 27 |
| gfa_below_ground_m2 | 27575.9 |
| height_top_of_parapet_m | 95.2 |
| footprint_area_m2 | 6218.4 |
| gfa_m2 | 79030.2 |
| net_floor_area_m2 | 75393.7 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.377 |
| plot_ratio_far | 4.792 |
| unbuilt_ratio | 0.623 |
| footprint_outside_plot_m2 | 9.1 |
| min_setback_m | 0.0 |
| parking_zone | 02 |
| parking_required_min | 637 |
| parking_required_max | 693 |
| parking_capacity_est | 781 |
| parking_margin | 144 |
| gfa_by_use_m2 | {'hotel': 31201.2, 'congress': 1200.0, 'retail': 2704.2, 'residential': 26353.8, 'office': 11397.9} |
| flats_est | 316 |
| hotel_keys_est | 581 |
| hotel_programme | {'keys': 581, 'keys_by_type': {'standard': 407, 'superior': 116, 'suite': 58}, 'areas_m2': {'lobby_fnb': 1200, 'meeting': 720, 'spa': 480, 'rooms': 30001}, 'm2_per_key': {'lobby_fnb': 2.07, 'meeting': 1.24, 'spa': 0.83}, 'flags': ['581 keys > 450: convert ≈6 top room floors (≈23 keys each) to serviced apartments / offices', 'meeting 1.24 m²/key < 1.5'], 'assumptions': '4* city hotel mix 70/20/10 (28/34/56 m² net), 62 % room-floor efficiency; ASSUMED'} |
| psp22_min_boundary_distance_m | 2.26 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 324 |
| daylight_proxy_fail_ratio | 0.194 |
| vsc_mean | 0.273 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 2.01 |
| courtyard_area_2h_sun_ratio | 0.446 |
| open_ground_m2 | 9455.5 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| H | Hotel tower | Hotel | 27 | 95.2 |  | 1200.0 | 32401.2 | 31091.4 |
| S | Street bar (Milevská) | Residential | 10 | 33.7 |  | 1696.0 | 16959.6 | 16110.5 |
| R | East bar | Residential | 12 | 39.9 |  | 1008.2 | 12098.4 | 11440.7 |
| O | North office wing | Office | 7 | 27.6 |  | 1628.3 | 11397.9 | 10930.9 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 32.0 | 32.0 | 685.9 | 6173.1 | 5820.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 13788.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 95.2 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 27 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 79030.2 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 2.26 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 144 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — ASSUMED zone 02 (bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
