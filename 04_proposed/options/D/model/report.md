# Option D — client scheme, made compliant — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 10 |
| storeys_above_ground | 22 |
| gfa_below_ground_m2 | 25791.0 |
| height_top_of_parapet_m | 83.8 |
| footprint_area_m2 | 8019.6 |
| gfa_m2 | 86585.2 |
| net_floor_area_m2 | 74201.9 |
| rooms | 268 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.486 |
| plot_ratio_far | 5.25 |
| unbuilt_ratio | 0.514 |
| footprint_outside_plot_m2 | 2.7 |
| min_setback_m | 0.0 |
| parking_zone | 02 |
| parking_required_min | 665 |
| parking_required_max | 763 |
| parking_capacity_est | 726 |
| parking_capacity_method | layout |
| parking_margin | 61 |
| gfa_by_use_m2 | {'retail': 7194.7, 'residential': 53367.1, 'restaurant': 2248.2, 'hotel': 9182.8, 'congress': 942.5, 'office': 6737.2} |
| flats_est | 640 |
| hotel_keys_est | 177 |
| hotel_programme | {'keys': 177, 'keys_by_type': {'standard': 124, 'superior': 35, 'suite': 18}, 'areas_m2': {'lobby_fnb': 2484, 'meeting': 566, 'spa': 377, 'rooms': 9183}, 'm2_per_key': {'lobby_fnb': 14.04, 'meeting': 3.2, 'spa': 2.13}, 'flags': ['177 keys < 300: below a typical 4* city hotel'], 'assumptions': '4* city hotel mix 70/20/10 (28/34/56 m² net), 62 % room-floor efficiency; ASSUMED'} |
| psp22_min_boundary_distance_m | 3.84 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 362 |
| daylight_proxy_fail_ratio | 0.251 |
| vsc_mean | 0.246 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 3.1 |
| courtyard_area_2h_sun_ratio | 0.61 |
| open_ground_m2 | 7602.8 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| A | Diagrid tower (T2) | Residential / hotel tower | 22 | 83.8 | 83.8 | 1172.6 | 25796.6 | 22112.3 |
| A0 | Diagrid tower podium + courtyard link | Lobby / restaurant | 1 | 5.9 |  | 2248.2 | 2248.2 | 2169.4 |
| B | Green tower (E residential tower) | Residential | 22 | 68.9 | 68.9 | 1165.9 | 23243.9 | 20263.8 |
| B2 | Terraced block (E) | Residential | 8 | 26.9 | 26.9 | 1035.9 | 7482.0 | 6359.3 |
| B3 | Podium north (E) | Residential | 4 | 15.83 |  | 463.8 | 1855.4 | 1533.4 |
| C1 | Front slab — west head (T5) | Hotel / office | 6 | 19.8 |  | 369.1 | 2214.9 | 1730.4 |
| C2 | Front slab — wing (T5) | Hotel / office | 10 | 31.05 | 31.05 | 942.5 | 9222.2 | 7787.0 |
| D | Butterfly office (T1 bow-tie) | Office | 7 | 28.89 |  | 872.3 | 7609.4 | 6439.1 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 29.2 | 29.2 | 768.1 | 6912.6 | 5807.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 8597.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 83.8 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 22 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 86585.2 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 3.84 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 61 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — zone 02 (verified 2026-11-11: gs-pub.praha.eu dop/psp_zony_parkovani/MapServer layer 0 (Zóny parkování města (PSP), HMP-IPR), plot polygon intersects only OBJECTID 23, ZONA 02 — raw/psp_parking_zones_plot.geojson; bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
