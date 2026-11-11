# HANDOVER — part-by-part refinement of the final design (start here in a new chat)

**How the next chat starts:** the user types `go` plus a correction for the YELLOW building. Read this file, then do
exactly the "Workflow per part" below for YELLOW, using the user's correction. Do not change the other parts.

## The base image (the agreed design)
- **`07657871-9301-4e50-8b4a-f5f4621bbe85`** (Higgsfield job, Nano Banana 2.1, 4k, 4800×3584)
  local copy: `04_proposed/design/refs/final_base_07657871.jpg`
  URL: https://d8j0ntlcm91z4.cloudfront.net/user_3IMqnluwqiYRXlwNed6Rk2YuqlY/hf_20261111_214234_07657871-9301-4e50-8b4a-f5f4621bbe85.png
- Made from the user's chosen design `ea3cf223-abb1-463a-85e6-bc27f11c0c22` + empty plot `afafc2b0…`, as a
  professional realistic render. Camera = the client's render-000 aerial (empty plot render:
  `04_proposed/blank_canvas/model/render_aerial_S_like_render000.png`, Higgsfield media `afafc2b0-ce47-432b-a3ab-7861b20fc8f4`).

## The four parts (user's markings: `04_proposed/design/refs/final_parts_markup.jpg`)
| Colour | Part | Order | Status |
|---|---|---|---|
| **YELLOW** | the long curved L-shaped low building along the front street (Milevská), white lattice fins, green roof | **1st** | waiting for the user's correction |
| RED | the two hourglass towers with lattice crowns, rooftop pools/gardens, the lattice ribbon/bridge between them | later | |
| GREEN | the lattice-roofed block at the back left (next to the drum towers) — wellness/spa roof wanted (one pool, one modern dark-timber sauna with dim warm LED, decks, loungers, calm) | later | |
| CYAN | the round building with a meadow roof at the base of the right tower | later | |
After all parts are approved, compose them into ONE cohesive image (guide composite + one clean render, see Method).

## What the user has said about YELLOW so far (keep unless the correction says otherwise)
- One distinct, freestanding L-shaped building — never merging with the towers, the round building, the drum towers or
  the ground; clear paved walkways/gaps around it; a lower inner courtyard behind it.
- Keep the white organic lattice running down the facade as column-like fins (the user likes this "theme of the outside
  facade going down it and those columns").
- Roof: a walkable park; access from the RIGHT end near the street (the user rejected stairs at the front/left end in
  `338a12c8` and the morphing/landform versions); gently rising, subtle few levels hidden in planting; a glass railing /
  aesthetic lattice edge; a "central park" with a small bar pavilion at the top was liked.
- Not too high; no big pond; no extra water; must stay inside the plot.

## Workflow per part
1. One image only per step (user rule). **All budgets approved** (user, 11 Nov 2026).
2. Model: **Nano Banana 2.1, `resolution: 4k`, aspect 4:3 (3 credits)** — gives the realistic look the user wants.
   (GPT Image 2.5 high 2k = 2.75 credits is the alternative; the "flare" variant looks too CGI.)
3. References: the base image `07657871…` (+ the empty plot `afafc2b0…` when the footprint/position matters).
   Prompt pattern: "Edit Image 1 … keep camera, framing, photographic look and EVERYTHING ELSE exactly; change ONLY the
   <part> …"; end with "real photo / professional render, natural materials, no CGI look, no text, no logos".
4. Download the result (`curl` from d8j0ntlcm91z4.cloudfront.net — allowed host) and CHECK it yourself: full view + crops
   of the part and of every other part (did anything else drift?). Report honestly what worked and what didn't.
5. Show with `show_generation_by_ids`, log in `04_proposed/design/round7_final_polish.md` (or a new `round8_parts.md`),
   commit + push to `claude/charming-albattani-2xtufa`.

## Method that keeps other parts unchanged (use for the final composition, or when a part drifts)
The image models redraw the whole picture. To lock everything outside a part: build a **guide** in Python/PIL — base
image + the new part pasted inside a polygon mask (align by testing small offsets on static background; 4800×3584 vs
1168×880 images need resizing) → commit it under `04_proposed/design/refs/` → `media_import_url` from
`https://raw.githubusercontent.com/v1nnrar/Panorama/claude/charming-albattani-2xtufa/<path>` → one clean render from
[guide + original]. Verify pixel drift outside the part. (Direct Higgsfield upload host is blocked; raw GitHub import works.)

## Lessons from this session (avoid repeating)
- The user identifies images by screenshot — match them to job IDs by pixel comparison against downloaded copies.
- "Mirror" vs "identical copy" caused several wrong rounds — ask or show a guide when wording is ambiguous.
- Edit-of-edit chains make textures look "AI"; go back to a good base instead of stacking edits.
- Do not add water, extra buildings or new access stairs the user didn't ask for.
