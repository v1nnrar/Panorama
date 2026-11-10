# Option D — client scheme, made compliant — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 10 |
| storeys_above_ground | 22 |
| gfa_below_ground_m2 | 25791.0 |
| height_top_of_parapet_m | 83.8 |
| footprint_area_m2 | 8051.9 |
| gfa_m2 | 85928.0 |
| net_floor_area_m2 | 81775.9 |
| rooms | 0 |
| site_area_m2 | 16491.7 |
| built_up_ratio | 0.488 |
| plot_ratio_far | 5.21 |
| unbuilt_ratio | 0.512 |
| footprint_outside_plot_m2 | 9.1 |
| min_setback_m | 0.0 |
| parking_zone | 02 |
| parking_required_min | 668 |
| parking_required_max | 763 |
| parking_capacity_est | 730 |
| parking_margin | 62 |
| gfa_by_use_m2 | {'retail': 7006.6, 'residential': 52238.5, 'restaurant': 2704.6, 'hotel': 11067.9, 'office': 6737.2} |
| hotel_keys_est | 201 |
| flats_est | 626 |
| psp22_min_boundary_distance_m | 6.77 |
| psp21_windows_checked | 699 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 363 |
| daylight_proxy_fail_ratio | 0.262 |
| vsc_mean | 0.246 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 3.38 |
| courtyard_area_2h_sun_ratio | 0.722 |
| open_ground_m2 | 7567.4 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| A | Diagrid tower (T2) | Residential / hotel tower | 22 | 83.8 | 83.8 | 1172.6 | 25796.6 | 24752.3 |
| A0 | Diagrid tower podium + courtyard link | Lobby / restaurant | 1 | 5.9 |  | 2704.6 | 2704.6 | 2616.5 |
| B | Green tower (E residential tower) | Residential | 22 | 68.9 | 68.9 | 1165.9 | 23243.9 | 22243.8 |
| B2 | Terraced block (E) | Residential | 8 | 26.9 | 26.9 | 847.8 | 6165.3 | 5726.5 |
| B3 | Podium north (E) | Residential | 4 | 15.83 |  | 463.8 | 1855.4 | 1725.4 |
| C1 | Front slab — west head (T5) | Hotel / office | 6 | 19.8 |  | 369.1 | 2214.9 | 2054.4 |
| C2 | Front slab — wing (T5) | Hotel / office | 11 | 33.9 | 33.9 | 942.5 | 10164.8 | 9641.7 |
| D | Butterfly office (T1 bow-tie) | Office | 7 | 28.89 |  | 872.3 | 7609.4 | 7195.1 |
| E | Existing corner office (parcel 1133/12) | Office (existing, kept) | 9 | 32.0 | 32.0 | 685.9 | 6173.1 | 5820.2 |
| U | Underground parking | Parking / technical | 0 | 0.3 |  | 8597.0 | 0 | 0 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max regulated building height (storey range 27) | ≤ 100 | 83.8 | ✅ PASS | MPP text čl. 98 odst. 3 (range 27: >21 RNP, max 100 m); Z 02 / KLZ 058 map — squares over the plot read 27 |
| Max regulated above-ground storeys (range 27) | ≤ 27 | 22 | ✅ PASS | MPP čl. 98 odst. 3 — INTERPRETATION: range label 27 = maximum RNP (ranges 21 = 13–21, 15 = 10–15 …) |
| Regulated floor area (HPPreg) — not set in stabilised areas |  | 85928.0 | ℹ️ | MPP čl. 96 odst. 2: HPPreg/Zmax apply only to [T] and [R] areas; plot is [S] (KLZ 058 map, no T hatch) |
| PSP §21: neighbour windows failing the 45°/45° distance angle | ≤ 0 | 0 | ✅ PASS | PSP §21 odst. 1 + příloha 1 bod II (sampled windows on neighbour façades facing the plot; pipeline/psp.py) |
| PSP §22: min distance to private neighbouring plots (m) | ≥ 2.0 | 6.77 | ✅ PASS | PSP §22 odst. 2 — ASSUMED: plot edges facing S (Milevská) and E (street/metro) are public space |
| PSP §25: parking capacity minus required minimum (spaces) | ≥ 0 | 62 | ✅ PASS | PSP §25 + příloha 2 (HPP per space by use) + příloha 3 — ASSUMED zone 02 (bound 80 %, visitor 15–55 %), 30 m²/space at 85 % basement efficiency |
