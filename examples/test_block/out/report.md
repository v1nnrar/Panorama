# Test Block (pipeline check) — metrics & compliance

Source: `params.yaml`

## Site & totals

| Metric | Value |
|---|---|
| buildings | 1 |
| storeys_above_ground | 6 |
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
