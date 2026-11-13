# Panorama Pankrác — existing scheme (v1) — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 10 |
| storeys_above_ground | 22 |
| gfa_below_ground_m2 | 17194.0 |
| height_top_of_parapet_m | 83.8 |
| footprint_area_m2 | 8120.1 |
| gfa_m2 | 92021.3 |
| net_floor_area_m2 | 78983.2 |
| rooms | 317 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.492 |
| plot_ratio_far | 5.58 |
| unbuilt_ratio | 0.508 |
| footprint_outside_plot_m2 | 2.7 |
| min_setback_m | 0.0 |
| parking_zone | 02 |
| parking_required_min | 728 |
| parking_required_max | 825 |
| parking_capacity_est | 487 |
| parking_margin | -241 |
| gfa_by_use_m2 | {'retail': 7449.0, 'residential': 53831.0, 'restaurant': 2248.2, 'hotel': 12186.0, 'office': 9394.5} |
| flats_est | 645 |
| hotel_keys_est | 236 |
| hotel_programme | {'keys': 236, 'keys_by_type': {'standard': 165, 'superior': 47, 'suite': 24}, 'areas_m2': {'lobby_fnb': 2549, 'meeting': 0, 'spa': 0, 'rooms': 12186}, 'm2_per_key': {'lobby_fnb': 10.8, 'meeting': 0.0, 'spa': 0.0}, 'flags': ['236 keys < 300: below a typical 4* city hotel', 'meeting 0.0 m²/key < 1.5', 'spa 0.0 m²/key < 0.8'], 'assumptions': '4* city hotel mix 70/20/10 (28/34/56 m² net), 62 % room-floor efficiency; ASSUMED'} |
| psp22_min_boundary_distance_m | 3.64 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 9 |
| psp21_fail_ratio | 0.013 |
| psp21_failing_neighbours | [('54,48', 7), ('-58,-26', 2)] |
| daylight_proxy_windows | 381 |
| daylight_proxy_fail_ratio | 0.26 |
| vsc_mean | 0.242 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 2.96 |
| courtyard_area_2h_sun_ratio | 0.596 |
| open_ground_m2 | 7479.1 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| A | Diagrid tower (T2) | Residential / hotel tower | 22 | 83.8 | 83.8 | 1172.6 | 25796.6 | 22112.3 |
| A0 | Diagrid tower podium + courtyard link | Lobby / restaurant | 1 | 5.9 |  | 2248.2 | 2248.2 | 2169.4 |
| B | Green tower (E residential tower) | Residential | 22 | 68.9 | 68.9 | 1165.9 | 23243.9 | 20263.8 |
| B2 | Terraced block (E) | Residential | 8 | 26.9 | 26.9 | 1035.9 | 7482.0 | 6359.3 |
| B3 | Podium north (E) | Residential | 5 | 19.2 | 19.2 | 463.8 | 2319.2 | 1916.7 |
| C1 | Front slab — west head (T5) | Hotel / office | 10 | 31.05 | 31.05 | 434.0 | 4340.4 | 3511.6 |
| C2 | Front slab — wing (T5) | Hotel / office | 10 | 31.05 | 31.05 | 942.5 | 9222.2 | 7787.0 |
| D | Butterfly office (T1 bow-tie) | Office | 8 | 32.3 | 32.3 | 1061.6 | 10456.2 | 9055.9 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 29.2 | 29.2 | 768.1 | 6912.6 | 5807.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 8597.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 83.8 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 22 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 92021.3 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 9 | ❌ FAIL | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 3.64 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | -241 | ❌ FAIL | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — zone 02 (verified 2026-11-11: gs-pub.praha.eu dop/psp_zony_parkovani/MapServer layer 0 (Zóny parkování města (PSP), HMP-IPR), plot polygon intersects only OBJECTID 23, ZONA 02 — raw/psp_parking_zones_plot.geojson; bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
