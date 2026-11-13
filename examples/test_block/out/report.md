# Test Block (pipeline check) — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 1 |
| storeys_above_ground | 6 |
| gfa_below_ground_m2 | 0 |
| height_top_of_parapet_m | 21.9 |
| footprint_area_m2 | 1124.0 |
| gfa_m2 | 6744.0 |
| net_floor_area_m2 | 6394.1 |
| rooms | 140 |
| site_area_m2 | 3500.0 |
| built_up_ratio | 0.321 |
| plot_ratio_far | 1.927 |
| unbuilt_ratio | 0.679 |
| footprint_outside_plot_m2 | 0.0 |
| min_setback_m | 8.0 |
| parking_zone | 02 |
| parking_required_min | 47 |
| parking_required_max | 60 |
| parking_capacity_est | 0 |
| parking_margin | -47 |
| gfa_by_use_m2 | {'restaurant': 1124.0, 'hotel': 5620.0} |
| flats_est | 0 |
| hotel_keys_est | 0 |
| hotel_programme | None |
| psp22_min_boundary_distance_m | None |
| psp21_windows_checked | 0 |
| psp21_windows_failing | 0 |
| psp21_fail_ratio | 0.0 |
| psp21_failing_neighbours | [] |
| daylight_proxy_windows | 28 |
| daylight_proxy_fail_ratio | 0.0 |
| vsc_mean | 0.397 |
| daylight_method | VSC < 15 % (CIE overcast) |
| courtyard_sun_hours_mean_mar21 | 0.0 |
| courtyard_area_2h_sun_ratio | 0.0 |
| open_ground_m2 | 0.0 |

## Buildings

| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |
|---|---|---|---|---|---|---|---|---|
| B |  |  | 6 | 21.9 |  | 1124.0 | 6744.0 | 6394.1 |

## Compliance

| Rule | Limit | Value | Status | Source |
|---|---|---|---|---|
| Max building height (parapet) | ≤ 22 | 21.9 | ✅ PASS | placeholder |
| Max storeys above ground | ≤ 6 | 6 | ✅ PASS | placeholder |
| Max built-up ratio | ≤ 0.4 | 0.321 | ✅ PASS | placeholder |
| Max plot ratio (FAR) | ≤ 2.0 | 1.927 | ✅ PASS | placeholder |
| Min setback from site boundary | ≥ 5 | 8.0 | ✅ PASS | placeholder |
| Min green area ratio | ≥ 0.35 | None | ⚪ N/A | placeholder |
