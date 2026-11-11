# Pink podium wing — isolated extraction

Starting point for redesigning the low curved podium wing (outlined pink in the client's
annotated aerial view, `00_source_annotated.png`).

| File | Content |
|---|---|
| `00_source_annotated.png` | client aerial render with hand annotations (pink = this wing) |
| `01_extract_A.png`, `01_extract_B.png` | the wing alone, same aerial angle, zoomed in, on a neutral base |

Generated with Higgsfield `gpt_image_2_6` using the source as reference (job ids
e359b6b3-2960-4b47-9011-45adcb89a7ce, fd833417-b0cf-4b68-bcfd-c0a4b70c2c34), 1344×752 px.

Note: the wing is only ~150 px tall in the source. The fine detail in the extracts (fin shapes,
glazing, roof planting) was filled in by the model. They show design intent; they are not survey
data. Use them as the base for design iterations, not for dimensions.

## Iteration 2 — wider back-left, park at true scale, ramp to ground

Edited from `01_extract_A.png` (Higgsfield `gpt_image_2_6`, jobs ce7b8cd6-fb14-44e3-93b4-a6557f62b176,
5e14d063-5be4-40da-828a-55bad861e7d6).

- Back-left end widened: no thin neck, a broad rounded wing with roof garden.
- Roof park drawn for a building of about 250 m × 50–60 m (ASSUMED: scale intent given to the model,
  not measured), 4–5 storeys of ~4 m: human figures for scale, 3–5 m paths, lawns, 8–12 m trees,
  pavilion, seating steps.
- Right end no longer stops at an end wall: the roof slopes down to street level as a landscaped
  ramp, so the park can be reached on foot from the ground.

| File | Notes |
|---|---|
| `02_wide_ramp_A.png` | bigger, bulbous back-left wing with amphitheatre; ramp side has an open edge |
| `02_wide_ramp_B.png` | more even width along the whole crescent; central lawn + pavilion; continuous lattice edge |

## Iteration 3 — real Panorama scale, slim back-left, straight descent

Iteration 2 was drawn about 3× too large. The wing sits where the existing front slab (C1 + C2) is:
71 × 24 m footprint, 1,348 m² (03_existing/params.yaml, PSG v3 fit); the whole plot is about 190 × 150 m (00_site/site.yaml).
Scale given to the model (ASSUMED: design intent, not yet modelled): about 90 m long incl. the descent, 20–24 m deep,
4 storeys (5 m GF + 3 × 3.7 m ≈ 17 m), linear roof garden about 18 m wide with one 3 m path, small 5–7 m trees.
References: the pink wing cropped from the client image at its own perspective + `01_extract_A.png`.
Jobs b5b7f9e2-5dd7-4787-801b-706cb29050a4, be642092-cc3d-4985-87b4-c8926c72729b, 50ba8cc0-2ad0-4249-9d18-81336286c001.

| File | Notes |
|---|---|
| `03_to_scale_A.png` | slim even width, simple rounded back-left end, garden stairs straight down at the right end |
| `03_to_scale_B.png` | same, sharper tip at back-left, wider stair flight |
| `03_in_context.png` | attempt at placing the wing in the client image; edit is weak (wing too small, descent not readable) |

Note: 17 m of height over ~35 m of length is about 1:2. That is a stair garden, not a step-free ramp.
A step-free 1:12 ramp would need about 200 m, so step-free access to the roof needs lifts.

## Iteration 4: original design, refined (current base)

Back to the wing as the client image shows it (shape, curve, ends, storeys unchanged), only cleaned up:
regular fin rhythm, a consistent lattice, clear floor slabs, an ordered roof garden, people for scale.
Reference: the pink wing cropped from the client image only. Jobs 5b45ef2e-ad54-49e4-95ee-c2c74ce4cf66,
8c0cbd5c-8de5-4733-b932-517a31c90fa7.

| File | Notes |
|---|---|
| `04_original_refined_A.png` | denser fin rhythm, more lattice openings, planted pavement edge |
| `04_original_refined_B.png` | calmer: fewer, more slender fins, smoother lattice, clearer roof path with benches |

## Iteration 5: B lowers to the right and melts into the ground

Edited from `04_original_refined_B.png` (jobs b837d03b-43bf-4f93-85b5-0281c72b6c02, 80bc1096-a387-401e-8c5f-2f19cbddb876).
From about mid-length the roof drops steadily (4 → 3 → 2 → 1 storeys) and the right end merges into the
ground on all sides (front, back, end) as a landscaped hill: no end wall, no stairs, one continuous walkable surface.

| File | Notes |
|---|---|
| `05_melt_A.png` | wider landscaped tail, several winding paths, more trees on the slope |
| `05_melt_B.png` | slimmer tail, the lattice edge runs further down, one main path along the street side |

Check when this is modelled: about 17 m of descent over about half the length is steep for a step-free walk.
The winding paths make the walking route longer; a real gradient (≤ 1:12 step-free, ≤ 1:8 with landings)
needs to be checked against the actual length.

## Iteration 6: one promenade, open edges, a purpose for the end

Edits of `05_melt_B.png` (amphitheatre) and `05_melt_A.png` (café) (jobs 2e037374-d026-441e-93ad-c33985e3e6fb,
6df0c72a-07d5-4f32-9d7f-c17e5357e203). Both have one continuous ~4 m stone promenade from the high end down to the ground.

| File | End use | Notes |
|---|---|---|
| `06_amphitheatre.png` | open-air amphitheatre: curved grass and timber seating terraces down to a round stage plaza at ground level | tail meets the ground with no edge on the front, back and tip, so it can be entered from any direction. **Preferred.** |
| `06_cafe_plaza.png` | glazed café pavilion under the lattice, opening onto a round café plaza | promenade reads well, but the lattice lifts back up over the café, so the tip does not merge with the ground as fully |

## Iteration 7: café end (idea B), serpentine park paths, coherent on all sides

Edited from `06_cafe_plaza.png` (jobs 7b13d1aa-957c-4369-9ec8-9ab17fdd4574, 006057fa-e263-4bd5-a779-e4145a1b2229).
The single promenade is replaced by a network of ~2–2.5 m serpentine paths: one main path winds from the high end down
to the ground, with loops and side paths that branch off and rejoin it. Between the paths: lawns, picnic and seating
areas, benches/loungers, tree groups, meadow beds. The lattice edge runs along front and back; the tail and the café
plaza meet the ground with no edge.

| File | Notes |
|---|---|
| `07_park_A.png` | calmer: one clear main serpentine with a few loops, larger lawns |
| `07_park_B.png` | freer: more interwoven loops, more seating niches, the back of the tail slopes into the ground behind the café |

## Iteration 8: varied roof park, back edge per client markup, park on top only

Edit of `07_park_A.png`, with the client's markup (`07_client_markup.png`: blue = repetitive tree islands to remove,
yellow = required back roof edge) as a second reference. Job 1cc46d78-61a5-463b-b867-dc1aef4e1b7a
(the second variant, 0157dd7c-…, was discarded: the lattice broke off and floated in the air).

`08_varied_park_A.png`:
- Back edge: one smooth line that sweeps down from the high end, runs calmly along the back and descends to the ground behind the café.
- Planting stays on the roof inside the lattice edge; the facades are clean.
- Distinct zones from high to low: viewpoint terrace with seating, hammock grove, picnic/sunbathing lawn,
  reflecting pool with stepping stones, wisteria pergola walk, timber play area, sun deck with loungers, wildflower meadow.
- One serpentine main path with secondary branches; nothing runs over the café roof.
