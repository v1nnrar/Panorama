# Proposed design — intent (v0)

Decisions by the user, 11 Nov 2026. Every later design step starts from this file.

## Brief for the redesign
- **Blank canvas.** The existing Panorama hotel tower (≈ 79 m) is **demolished** (user decision, an idea-stage
  ASSUMPTION, not yet confirmed by the client). Everything on the plot is designed from scratch.
  The context model (`00_site/context.json`, `context.glb`) already has no building on the plot.
- **The client's scheme (`03_existing/`) is an orientation reference, not a template.** It shows the order of
  magnitude the client expects: about 91,000 m² above ground (FAR ≈ 5.5), a ≈ 84 m tower, a ≈ 69 m tower,
  mid-rise blocks of 8–11 storeys, a landscaped courtyard and underground parking. Do **not** copy its buildings.
- **The client's scheme is not itself permittable** (it fails PSP §21 at 10 neighbour windows and §25 parking).
  The binding envelope is `02_regulations/rules.yaml`, not the renders:
  - height ≤ 100 m, ≤ 27 storeys above ground (MPP čl. 98/3, range 27)
  - no regulated floor-area cap in the stabilised area [S] (MPP čl. 96/2)
  - PSP §21 45°/45° distance angle to neighbour windows, §22 ≥ 2 m from private plot edges,
    §25 parking ≥ the minimum for zone 02
  - quality floors used in the capacity study: daylight proxy, ≥ 2 h courtyard sun on 21 March, built-up ≤ 0.45
- **Goal:** similar programme and scale, but a far stronger and more aesthetic architecture than the client's
  renders, presented with photoreal stills and video (Higgsfield skills, see `CLAUDE.md` → Visual skills).
- **Starting data:** the capacity study (`06_reports/capacity_study.md`, options A–E) shows what fits legally:
  e.g. option E ≈ 79,900 m² and option A ≈ 79,000 m², both passing every hard rule.

## Still open (ASSUMED until answered)
- Office E (existing, parcel 1133/12): keep or include in the redesign? The capacity study keeps it.
- Programme: hotel category and keys (ASSUMED 4*, 300–450 keys), share of flats / offices, F&B, conference, spa.
- Design direction and references (materials, character, landmark ambition).
