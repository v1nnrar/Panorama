# Pink podium: 10-view set (base: ../08_park_B.png)

Camera plan for full coverage at a fixed distance: an orbit around the building centre at the
reference camera's distance, height and tilt (~35° down) every 45°, plus one top view and one low view
at the same distance from the centre.

| # | File | Camera |
|---|---|---|
| 0 | view0_front.png | reference (= 08_park_B.png) |
| 1 | view1_front_left_45.png | orbit 45° left |
| 2 | view2_left_end_90.png | 90°: high end face-on |
| 3 | view3_back_left_135.png | 135° |
| 4 | view4_back_180.png | 180°: back facade |
| 5 | view5_back_right_225.png | 225° |
| 6 | view6_cafe_end_270.png | 270°: café end face-on |
| 7 | view7_front_right_315.png | 315° |
| 8 | view8_top.png | overhead |
| 9 | view9_low_front.png | front, low (~10° elevation) |

Generated with Higgsfield gpt_image_2_6, each from the reference image alone (jobs 746c44f6…, 5398e2df…, 9e51d7eb…,
a86b18f2…, 42b2d21a…, cec17bdb…, 14579056…, d4e3dc91…, 2de7b558…).

**Limitations: these are not true camera moves.** The model redraws the building for each view:
- The massing drifts. Most views show a shorter, wider block that stays near full height, so the long descent
  to the ground is mostly lost (views 2–6 especially).
- The roof park layout differs between views.
- View 8 is not a true plan view; it is still oblique.
- The building's size in the frame varies, so camera distance is not exactly constant.

For an exact, consistent set, model the building in 3D and render the same 10 cameras from it.
