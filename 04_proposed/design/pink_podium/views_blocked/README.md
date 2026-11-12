# Pink podium: 10 hyperrealistic views from the 3D blocking

Replaces the earlier `views/` set, which was deleted because the image model redrew the building differently for each view.

How it works:
1. `../blocking/build_blocking.py` builds the massing in Blender: the L-shaped curved plan, a 4-storey high arm,
   a continuous descent, the back of the roof sloping into the ground at the saddle, a café arch at the tip,
   fins, the lattice band, glazing, slabs, roof park elements and people. All dimensions ASSUMED (design intent).
2. 10 cameras on a fixed orbit: every view is the same distance (189 m) from the building centre with the same 40 mm lens.
   Views 0–7: every 45° at 35° elevation; 8: overhead; 9: 10° elevation from the front.
   Clay renders: `../blocking/renders/`.
3. Each clay render was turned into a photoreal image with Higgsfield gpt_image_2_6, using the clay render as the
   only image reference; the materials are described in the prompt.

| # | File | Clay | Job |
|---|---|---|---|
| 0 | view0_front.png | view0_front | ff122b45-5048-4d2e-ad8a-0a46ed9d0649 |
| 1 | view1_front_left_45.png | view1 | 9769fadf-70ef-4e85-8806-e97411b955eb |
| 2 | view2_high_end_90.png | view2 | c3fb1d14-3881-404d-b6f9-3bcf5ce4de84 |
| 3 | view3_back_left_135.png | view3 | c2291892-9418-4ceb-a953-e5727a606e58 |
| 4 | view4_back_180.png | view4 | b7cf539e-81ca-4388-874c-5fb0bc2e80ad |
| 5 | view5_back_right_225.png | view5 | e6a40a5d-083f-4f4c-8a55-29cc4625d7a4 |
| 6 | view6_cafe_end_270.png | view6 | 5f7f38b0-3734-427a-afdd-ac41dd8ba69f |
| 7 | view7_front_right_315.png | view7 | 696d2e02-af1c-441a-8ccb-a6478d6febbe |
| 8 | view8_top.png | view8 | 74f186a1-c44c-41a6-bd6c-141ee82ac42a |
| 9 | view9_low_front.png | view9 | 90e0c831-1407-444f-9c2a-b02154a3f0f8 |

Note: views 5 and 6 came from a first pass that also used `../08_park_B.png` as a style reference;
in that pass views 0–3 and 7–9 copied that image's camera, so they were redone with the clay render alone.

Re-run the blocking:  `.venv/bin/python 04_proposed/design/pink_podium/blocking/build_blocking.py [--views view0,view4] [--samples 24]`
