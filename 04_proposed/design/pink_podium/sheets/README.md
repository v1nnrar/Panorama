# Pink podium: hyper-realistic 4-view sheets from the blocking (iteration 2 of the blocking)

Blocking changes (`../blocking/build_blocking.py`): gathering deck at the head enlarged (radius 5.6 → 7.6 m);
ONE continuous main path that runs down the roof, climbs over the café arch and reaches the ground only at the tip
(the earlier path exit at the back of the tail is removed; the lawn itself still meets the ground there).
Two extra cameras (viewA low café side, viewB low back), so 12 views = 3 clay sheets of 4 (`../blocking/renders/clay_sheet1–3.png`).

Each sheet is one Higgsfield gpt_image_2_5 image (0.25 credits) with a clay sheet as the only reference. 20 sheets = 5 credits.

| Sheets | Clay sheet | Cells |
|---|---|---|
| 01–07 | clay_sheet1 | A front (reference view), B front-left 45°, C high end, D back-left 135° |
| 08–14 | clay_sheet2 | A back, B back-right 225°, C café end, D front-right 315° |
| 15–20 | clay_sheet3 | A from above, B low front, C low café side, D low back |

Each cell is only about 670 px wide; pick cells, then render the picks as full-size single images.
