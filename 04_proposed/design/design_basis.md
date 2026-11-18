# Design basis — our proposed scheme for Panorama Pankrác

Everything the repo has established that constrains or informs **our own design**, in one place.
Compiled 2026-11-18 from the files listed under each heading. No renders, only the facts we need.
Where a number is an estimate or assumption it says so; check the source file before relying on it in an issue.

---

## 1. Site

| Item | Value | Source |
|---|---|---|
| Address / origin | Milevská 7, Praha 4 – Pankrác (50.04919 N, 14.43819 E) | `00_site/site.yaml` |
| Plot | **11 ČÚZK parcels, 16,487 m² official** (union polygon 16,492 m²) | `00_site/survey/README.md` |
| Parcels | 1051/3 (5,618) · 1090/2 (2,561) · 1133/1 (2,346) · 2841/1 Nusle (1,681) · 1133/12 (1,514) · 1051/16 (1,020) · 1051/5 (600) · 1133/13 (595) · 1052/244 (250) · 1133/2 (227) · 1133/21 (75) | ČÚZK WFS |
| Model frame | local aeqd at the origin, x = east, y = true north, metres, z = 0 at GF; S-JTSK is rotated −7.8° here | survey README |
| Grid | columns A… from x = −150, rows 1… from y = +200; D5 = origin; 10 m minor / 50 m major | survey README |
| Street edges | **S = Milevská**, **E = street / metro D corridor**; both treated as public space (ASSUMED) | `rules.yaml` psp22 |
| Existing building kept | **Office E** on parcel 1133/12 (east wedge): 9 storeys, 29.2 m (measured), ≈768 m² footprint, ≈6,900 m² GFA | `03_existing/params.yaml` |
| On-site park | polygon (−51, 94)…(27, 58) north of the scheme | `site.yaml: site_park` |
| Neighbours | west: four curved "drum" offices with green roofs; north: three-wing office building; NE: white building with arched roofs (status unknown); towers nearby: City Tower 109 m, V Tower 105 m, City Empiria 104 m, existing hotel 79 m; panel housing south of Milevská | `03_existing/observations.md`, `00_site/context.json` |

Survey accuracy: frame verified against 254 cadastre parcels (mean 0.34 m). The client's scheme positions are only
known to ±5–10 m (from a photo of a printed board); **we have no client DWG/PDF site plan**.

---

## 2. Planning rules — Metropolitan Plan of Prague (MPP)

In force since **1 Sep 2026** (OOP 001/2026); replaced the 1999 plan. Court review MS Praha 11 A 24/2026 pending.
Sources: `02_regulations/summary.md`, `rules.yaml`, `raw/MPP_textova_cast.txt`, `raw/KLZ_058.txt`.

### Classification
| Item | Value | Article |
|---|---|---|
| Locality | **058 Horní Pankrác**, 40 ha | KLZ 058 |
| Buildability / use | buildable, **residential** (admin and commercial buildings are part of the locality; hotel fits) | čl. 63 |
| Stability | **[S] stabilised**: no fundamental change of structure expected; partial changes allowed but must take the **existing character** into account | čl. 70/1 |
| Structure | **(03) hybrid** | čl. 43 |
| Height range | **27** on every grid square over the plot (black = above height-stable development) | Z 02, čl. 98 |

### What the hybrid structure (čl. 43/2) asks of the layout
- Intensive structure of compact and loose blocks or solitaires that form a **sub-centre**; buildings typically **fully surrounded by publicly accessible space**; mixed typologies in one building are normal.
- Street line usually defined by façades, or not defined (open ground flows into the public space).
- Building line closed or open, exceptionally free.
- Unbuilt land between building line and street line is usually **publicly accessible**.
- **Large blocks should be permeable**, with passages or arcades.
- Heights may vary, respecting cultural values (čl. 9/7–8).

### Height
| Rule | Limit | Note |
|---|---|---|
| Max regulated height | **100 m** | čl. 98/3, range 27 |
| Storeys | range 27 = **"> 21 RNP"** (above-ground storeys) | `rules.yaml` caps at **27**: our interpretation. The article text itself gives only "> 21" with the 100 m cap, so 100 m is the binding number. Confirm with IPR. |
| In [S] areas | the actual storey count must **take the surrounding heights into account** (and any territorial study) | čl. 98/2a: authority judgement |
| Roof | **one set-back storey** (or attic / other roof form) is allowed above the main cornice | čl. 98/6 |
| Tower level XIV. Pankrác (70 m, ≤ 75 % of built area) | applies only to the pink squares by metro D, **not this plot** | KLZ 058/200, čl. 100 |
| Protected panoramas / views | KLZ 058 refers to čl. 104–105 and appendix 1; **not yet checked** whether the plot lies in a protected view | open |

### Floor area
- **No HPPreg / Zmax cap** in [S] areas (čl. 96/2 applies only to [T]/[R]).
- Negotiation benchmark if neighbouring transformation-area values were applied (HPPreg = plot × Zz × Vz):
  - T 411/058/2235 (Zz 35 %, Vz 8.0): **46,178 m²** (52,774 m² with the +5 pp bonus, čl. 96/6)
  - T 411/058/2336 (Zz 60 %, Vz 8.0): **79,162 m²** (85,757 m² with the bonus)
- MPP gross floor area also counts **underground floors except garages and service spaces** (čl. 96/1).

### Infrastructure next to the plot (KLZ 058/600, 900)
- **Metro D** (Náměstí Míru – Pankrác – Nové Dvory), proposed, public-benefit construction VPS 910-621/-/1 and /3. Corridor runs past the **east wedge** (1133/12, 1052/244). Pankrác D station and vestibules (621/058/1001, 1020, 1045, 1046) are proposed in the locality.
- Tram line Pankrác – Budějovická (622/-/9, proposed): may remove existing parking spaces.
- Tangential rail reserves 621/-/21, /22: mostly underground, **do not restrict** new buildings.
- Proposed cycle routes 650/-/127 and /222.

---

## 3. Prague building regulations (PSP, nař. 12/2024, consolidated 2025/01)

Checked automatically on every build by `pipeline/psp.py`. Source PDF: `02_regulations/raw/PSP_souhrnne_zneni.pdf`.

| § | Requirement | How it bites |
|---|---|---|
| **§21** + příloha 1/II | No new mass above **45°** inside any contiguous **≥ 45° horizontal sector** (counted from 25° off the façade) in front of habitable-room windows of existing neighbours | Limits height near the **north three-wing building (≈ 54, 48)** and the **west drum building (≈ −58, −26)**: the client scheme fails 9 windows there |
| **§22/2** | ≥ **2 m** from boundaries with neighbouring private plots | S and E edges ASSUMED public (no limit there) |
| **§25** + přílohy 2, 3 | Parking. **Zone 02 verified** on the official IPR layer (whole plot). Base: 1 space per HPP of hotel 100 m², housing 85, office 50, retail 70, restaurant 40; **bound min 80 %**; visitor 15–55 % | Drives the basement: the client scheme needs **728 min / 825 max**, but only ≈488 fit in 2 levels |
| **§20** | Daylight per ČSN 73 0580 / EN 17037; Prague excludes the direct-sunlight requirement for flats | Our proxy: VSC < 15 % (CIE overcast) on sampled own-façade windows; target ≤ 15 % failing (ASSUMED, BRE 209). **Proper daylight study still needed.** |

Quality floors used to score options (ASSUMED, our own): daylight proxy fail ≤ 0.15, courtyard **≥ 2 h sun on
21 March**, built-up ratio ≤ 0.45.

---

## 4. The client's existing scheme — numbers only

Rebuilt from their renders (`03_existing/params.yaml` → `03_existing/model/report.md`). Heights and storeys are
**estimates from renders**, ±3 m on positions.

| ID | Building | Use | Storeys | Height m | Footprint m² | GFA m² |
|---|---|---|---|---|---|---|
| A | Diagrid tower, centre (≈ 33.6 × 35.3 m) | residential / hotel | 22 (5.0 + 3.7 podium, 20 × 3.7) | 83.8 | 1,173 | 25,797 |
| A0 | Glazed podium + courtyard link | lobby / restaurant | 1 | 5.9 | 2,248 | 2,248 |
| B | Green tower, SE (≈ 27.8 × 37.5 m) | residential | 22 (GF 4.5, 21 × 3.0) | 68.9 | 1,166 | 23,244 |
| B2 | Terraced block wrapping B (steps 1 m/floor to S + E) | residential, retail GF | 8 | 26.9 | 1,036 | 7,482 |
| B3 | Podium north of B | residential | 5 | 19.2 | 464 | 2,319 |
| C1 + C2 | Front slab along Milevská, angled west head | hotel / office | 10 (GF 4.4, 9 × 2.85) | 31.05 | 1,377 | 13,563 |
| D | Butterfly office, north (≈ 23.2 × 70.9 m) | office | 8 (GF 6.5, 7 × 3.45) | 32.3 | 1,062 | 10,456 |
| E | Existing corner office, kept | office | 9 | 29.2 | 768 | 6,913 |
| U | Underground parking (ASSUMED 2 levels, −7.0 m) | parking | 2 below | — | 8,597 | 17,194 below ground |

**Totals:** GFA 92,021 m² above ground · FAR 5.58 · built-up ratio 0.49 · tallest 83.8 m · ≈ 645 flats + 236 hotel keys (estimates).
Uses by GFA: residential 53,831 · hotel 12,186 · office 9,395 · retail 7,449 · restaurant 2,248 m².

**Why it is not permittable as drawn**
- §21: 9 neighbour windows fail (north three-wing building, west drum).
- §25: parking capacity 488 vs 728 required (−240).
- Quality: 26 % of windows below VSC 15 %; built-up ratio 0.49 > 0.45.
- Hotel programme weak: 236 keys (< 300 for a 4* city hotel), no meeting, no spa.

Design features worth knowing (from `observations.md`): white steel diagrid over full-height balconies on A;
planted balconies + white fins on B; timber fins and planted terraces on B2; PV roofs throughout; green roofs on
C and A0; landscaped courtyard between A, B and C with a low green-roofed pavilion; parking ramp at the west
end of the forecourt (≈ −36, −29).

---

## 5. What our capacity study already found

`06_reports/capacity_study.md` (generated by `tools/make_options.py` + `tools/score_options.py`; options in
`04_proposed/options/A–E/`). All options keep office E and **pass every hard rule**.

| Option | GFA m² | FAR | Max height / storeys | Hotel keys | Flats | Parking need / capacity | Basements | Note |
|---|---|---|---|---|---|---|---|---|
| **E: max yield (search)** | 80,594 | 4.89 | 95.2 m / 27 | 426 | 402 | 665 / 781 | 2 | 1 hotel tower (34 × 36 m at x 28…62, y −39…−3) + street bar on Milevská + east bar + north wing |
| **A: hotel tower + residential blocks** | 79,770 | 4.84 | 95.2 m / 27 | 441 | 402 | 646 / 781 | 2 | |
| D: client scheme made compliant | 86,585 | 5.25 | 83.8 m / 22 | 177 | 640 | 665 / 726 | **3** | daylight + built-up misses |
| B: twin towers on a podium | 63,590 | 3.86 | 95.2 m / 27 | 435 | 244 | 467 / 781 | 2 | only option meeting every quality floor |
| C: mid-rise blocks, no towers | 62,423 | 3.79 | 38.4 m / 10 | 317 | 257 | 500 / 781 | 2 | |

Takeaways for the design:
- A **legal scheme reaches ≈ 80,000 m² (87–88 % of the client's)** with 2 basement levels, or ≈ 86,600 m² if we accept 3 basement levels and worse daylight.
- One **hotel tower up to ≈ 95 m / 27 storeys** in the south-east quarter works under §21. Height near the north and west neighbours is what §21 limits.
- Parking, not height, is the binding constraint on floor area: every extra 85 m² of housing costs about one space.
- Hotel tower preset used: GF 6.0 m lobby/restaurant, L2 5.0 m conference/spa, 25 × 3.3 m room floors. Hotel assumptions: 70/20/10 standard/superior/suite at 28/34/56 m² net, 62 % room-floor efficiency, 34 m² GFA per key; benchmarks 300–450 keys, lobby + F&B ≥ 2.0, meeting ≥ 1.5, spa ≥ 0.8 m² per key (ALL ASSUMED until the brief arrives).

---

## 6. How to build it in this repo

- Our scheme = **one params YAML** in `04_proposed/` (schema in `CLAUDE.md`), `site: {file: ../00_site/site.yaml}`; mark office E `existing: true`.
- Build and check: `.venv/bin/python build.py 04_proposed/<scheme>/params.yaml --rules 02_regulations/rules.yaml [--render]` → IFC, Blender, GLB, report with every MPP/PSP check, DXF drawings, area schedule.
- Only the **bim-modeler** agent edits geometry; run **compliance-checker** after every change.

---

## 7. Gaps: what we do NOT have

| Missing | Effect | Who |
|---|---|---|
| **Client brief / programme** (`01_brief/` is empty) | Hotel size, star rating, room mix, which other uses (flats? offices?) are all ASSUMED | client |
| Which block is the hotel, and does the client want residential / office at all | Drives the whole massing | client |
| Client drawings (DWG/PDF site plan, plans, levels) | Existing-scheme positions ±5–10 m, heights estimated | client |
| Existing permit / territorial decision under the old plan | Would take precedence over the MPP | client |
| Confirmation the whole plot is [S], and of the storey reading of range 27 | Read from the KLZ map at ±5 m | IPR / building authority |
| Protected panoramas (čl. 104–105, appendix 1) | Could limit tower height | regulations-analyst |
| Metro D corridor geometry / protection zone at the east wedge | May restrict basements and foundations there | regulations-analyst / IPR |
| Real daylight study (ČSN 73 0580), fire, structural grid, terrain levels | Proxies only so far | later stages |
| Status of the white arched building to the NE | Context for §21 and views | client |

Note: `06_reports/compliance_existing.md` (09 Nov) predates the PSP checks and says "nothing fails". The current
status is in `03_existing/model/report.md` and the capacity study (§21 and §25 fail).
