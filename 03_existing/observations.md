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

## v0 model (03_existing/params.yaml)

| ID | PSG block | Storeys | Parapet height (m) | Note |
|---|---|---|---|---|
| A | P_T2_diagrid_tower | 26 (2 podium + 24) | 88.2 | PSG height |
| B | P_E_residential_tower | 22 | 68.9 | PSG height; tower-on-base stepping not yet modelled |
| B2 | P_E_terraced_block | 8 | 26.9 | terraces not yet modelled |
| B3 | P_E_podium_north | 5 | 19.2 | |
| C1 | P_T5_office_head | 10 | 33.9 | |
| C2 | P_T5_office_wing | 10 | 33.9 | **PSG had 25.1 m**; renders show one continuous cornice with C1 |
| D | P_T1_bowtie_office | 10 | 34.0 | sawtooth PV roof not modelled |
| E | — (OSM context) | 9 | 32.0 | existing corner office on parcel 1133/12, kept in the scheme |

Next refinements: camera match to render-000/-004/-005 with 50 % overlays; tower-on-base for B; terrace steps
for B2 and C roof setbacks; diagrid and balcony expression for A.

## Open questions for the client / user
1. ~~Which buildings are the client's scheme~~ → all coloured = hotel property (user, 8 Nov 2026). Which block(s) will be the **hotel** use?
2. ~~Site boundary~~ → from PSG data. Still useful: any real dimensions (tower plan size, floor-to-floor heights, total heights).
3. ~~North / location~~ → Milevská 7, Praha 4; north = up in the top view.
4. Is the white arched building (NE) existing, approved, or part of the scheme?
5. Uses per building (hotel / residential / office / retail) and number of underground levels.
