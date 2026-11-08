# Existing scheme — render observations (Panorama Pankrác)

Source: `renders/Panorama-Pankrac-Official-Renders.pdf` (7 pages, images extracted as `render-000…006.jpg`)
and `renders/site_top_view_photo.png` (photo of a printed top-view board).
Status: **v0 model built** (`params.yaml` → `model/`). Plot and footprints come from the PSG website
data (`00_site/`): the plot = all coloured area = 11 cadastral parcels, 16,463 m² (union; cadastre sum 16,474 m²,
to verify at ČÚZK). Footprints = PSG v3 fit to these renders. Storey counts = counted below.

## Render inventory

| File | View | Shows |
|---|---|---|
| render-000.jpg (= render-001.jpg, duplicate page) | Aerial, from the south over the front street | Whole scheme in context |
| render-002.jpg | Aerial, from the south-east street corner | Front slab end, green tower, terraced block, L-shaped corner office |
| render-003.jpg | Eye level from the park (north) | Butterfly office, park facade |
| render-004.jpg | Eye level, street | Green tower + terraced lower block |
| render-005.jpg | Eye level, front street (SW) | Front slab block, diagrid + green tower behind |
| render-006.jpg | Eye level, dusk | Diagrid tower + glazed podium |
| site_top_view_photo.png | Top view (north ≈ up, front street along the bottom) | Footprints and roofs of the whole block |

Orientation: the aerial (render-000) and the top view share an orientation — the front street runs
along the bottom; the four curved "drum" buildings (neighbour, existing) are on the left/west edge.
**North arrow not confirmed** — please confirm.

## Buildings in the scheme

IDs used throughout the project:

| ID | Name (working) | Plan form (top view) | Storeys (counted) | Facade / features | Seen in |
|---|---|---|---|---|---|
| **A** | Diagrid tower | Square, centre of block | ~25 tower floors + 2-level glazed podium ≈ **27** | White steel diagrid over full-height balconies; roof: PV + central green square, 3 plant boxes | 000, 002, 005, 006, top |
| **B** | Green tower | Square, SE part of block | ~17 tower floors (white slab bands every 2 floors) on ~6-storey base ≈ **23** | Planted balconies, white vertical fins; roof PV | 000, 002, 004, top |
| **B2** | Terraced block (base of B) | Wraps B on the south/east | ~8 storeys + GF, stepped terraces | Brown/timber fins, planted terrace edges, PV roof | 000, 002, 004 |
| **C** | Front slab | Long bar along the front street, angled west end | ~10 floors + double-height glazed GF ≈ **11** (aerial suggests fewer — to verify) | Light grey, vertical fins + horizontal bands; green roof with stepped terraces and rooftop structure | 000, 002, 005, top |
| **D** | Butterfly office | Two wings meeting at a recessed joint, north of A | ~9 + GF ≈ **10** | White horizontal bands, ribbon glazing, sawtooth PV roof, green balconies at the joint | 000, 003, top |
| **E** | L-shaped corner office | L along the east street, NE of B | ~9–10 | Dark glass, white frame, bronze crown, rooftop plant | 002, top |

Shared: landscaped courtyard between A, C and B with a low green-roofed link/pavilion; underground
parking implied (ramp/cars in the top view between A and C).

### Context (existing neighbours — not part of the scheme unless told otherwise)
- Four curved drum office buildings with green roofs (west).
- Large white building with three arched roof structures (north-east, rendered in white "massing" style).
- Tall glass tower behind, shopping centre with long roof (north-west), panel housing blocks south of the street.

## v1 model (03_existing/params.yaml) — full detail

| ID | Building | Storeys | Parapet (m) | Modelled |
|---|---|---|---|---|
| A | Diagrid tower | 26 (2 podium + 24) | 88.2 | curtain wall, 1.7 m balconies, white steel diagrid (5 bays/face, 3-storey modules), PV + central green box + plant boxes |
| A0 | Podium + courtyard link | 1 | ≈5.9 | dark glazing, green roof, timber fascia |
| B | Green tower | 22 | 68.9 | storeys 1–6 timber-fin base widened 4 m west; 7–22 planted balconies, white bands every 2 floors, white fins; PV |
| B2 | Terraced block | 8 | 26.9 | steps back 1 m/floor to S + E, planters + glass railings on terraces, timber fins, green roof + PV |
| B3 | Podium north | 5 | 19.2 | timber fins, green roof |
| C1 | Front block head | 10 | 33.9 | glazed GF, punched windows, light fins + bands, green roof, core + rooftop units |
| C2 | Front block wing | 10 | 33.9 | as C1; top floor set back 4 m north with planted terrace; **PSG had 25.1 m** |
| D | Butterfly office | 10 | 34.0 | curtain wall + spandrels, deep white bands, sawtooth PV roof |
| E | Existing corner office (1133/12) | 9 | 32.0 | dark glass, white frame fins, bronze crown — existing, kept |
| U | Underground parking | 2 below | — | **ASSUMED** 2 levels under 1051/3, 1090/2, 1051/16 |

Landscape: courtyard lawn with paths and trees, on-site park (PSG `sitePark`), street trees (PSG/OSM).
Context: PSG website surroundings model (`00_site/context.glb`): streets, paths, parks, neighbours, towers.

Still to verify / not modelled: exact camera match (overlays), interior layouts, the green balconies at
D's joint, B tower's exact overhang over its base, parking ramp position, real floor heights.

## Open questions for the client / user
1. ~~Which buildings are the client's scheme~~ → all coloured = hotel property (user, 8 Nov 2026). Which block(s) will be the **hotel** use?
2. ~~Site boundary~~ → from PSG data. Still useful: any real dimensions (tower plan size, floor-to-floor heights, total heights).
3. ~~North / location~~ → Milevská 7, Praha 4; north = up in the top view.
4. Is the white arched building (NE) existing, approved, or part of the scheme?
5. Uses per building (hotel / residential / office / retail) and number of underground levels.
