#!/usr/bin/env python
"""Compile every local regulation that applies to the Panorama Pankrác plot into ONE plain-text file.

Writes 02_regulations/regulations_panorama.txt:
  Part A  English summary of the regulations that apply to the plot (no assessment of any scheme)
  Part B  Locality sheet 058 / Horní Pankrác (MPP příloha 4, krycí list) — full Czech text
  Part C  MPP příloha 2 table rows for locality 058 (transformation areas, metro)
  Part D  Metropolitan Plan (MPP) text — the articles that govern this plot, verbatim Czech
  Part E  Prague building regulations (PSP + national VPV, consolidated text 2025/01) — full Czech text

Building-height regulation is left out on purpose (client instruction 2026-11-16: the height can be raised with a
permit): MPP čl. 18 and 97–103, the "Výšková regulace" block of the cover sheet and the tower-level table row.

Usage: .venv/bin/python tools/compile_regulations.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "02_regulations"
RAW = REG / "raw"
OUT = REG / "regulations_panorama.txt"

# MPP articles that govern a building on this plot (TOC in raw/MPP_textova_cast.txt)
MPP_ARTICLES = [
    (3, 5, "Terms and definitions (RNP, regulated height, block, …)"),
    (12, 12, "Localities and their character"),
    (17, 17, "Mass and structure of the city"),
    (35, 40, "Locality code, target character, cover sheets, buildability, structure"),
    (43, 43, "(03) Hybrid structure — this locality"),
    (61, 61, "Use of locality"),
    (63, 63, "Buildable residential locality — this locality"),
    (68, 70, "Stability; stabilised areas [S] — this plot"),
    (73, 74, "Measure of land use; stabilised areas"),
    (79, 82, "Public spaces, streets, street hierarchy"),
    (87, 89, "Public-space coefficients, pedestrian permeability, building blocks"),
    (92, 92, "Courtyards"),
    (95, 96, "Building coverage coefficients, regulated gross floor area"),
    (104, 105, "Panoramas and protected vistas"),
    (117, 117, "Transport infrastructure — common provisions"),
    (121, 123, "Public transport, metro, tram (metro D corridor next to the plot)"),
    (127, 128, "Cycling and walking"),
    (150, 152, "Public-benefit constructions (metro D VPS 910-621/-/1, -/3)"),
]


def clean(text):
    lines = [ln.rstrip().replace("\f", "") for ln in text.splitlines()]
    out, blank = [], 0
    for ln in lines:
        blank = blank + 1 if not ln.strip() or set(ln.strip()) <= {"!", " "} else 0
        if blank <= 1:
            out.append("" if blank else ln)
    return "\n".join(out).strip() + "\n"


def mpp_articles(text):
    lines = text.splitlines()
    heads = {}
    for i, ln in enumerate(lines):
        m = re.fullmatch(r"\s*Článek (\d+)\s*", ln)
        if m and i > 1000:          # skip the table of contents
            heads.setdefault(int(m.group(1)), i)
    starts = sorted(heads.values())
    def body(n):
        s = heads[n]
        nxt = next((x for x in starts if x > s), len(lines))
        return "\n".join(lines[s:nxt])
    parts = []
    for a, b, label in MPP_ARTICLES:
        parts.append(f"--- čl. {a}{'–' + str(b) if b != a else ''}: {label} ---\n")
        parts += [clean(body(n)) for n in range(a, b + 1) if n in heads]
    return "\n".join(parts)


def drop_height_block(text):
    """Cover sheet without the 'Výšková regulace' block (tower level XIV. Pankrác); panorama references stay."""
    return re.sub(r"\n[ \t]*Výšková regulace\n.*?-> Hladina věží, čl\. 100\n", "\n", text, flags=re.S)


def tab_rows(text):
    keep = [ln.rstrip() for ln in text.splitlines()
            if re.search(r"/058/|\b058\b +Horní Pankrác", ln)]
    return "\n".join(re.sub(r" {3,}", "   ", ln.strip()) for ln in keep) + "\n"


def digest():
    return """\
PART A — SUMMARY (English): regulations that apply to the Panorama Pankrác plot
==============================================================================

1. GOVERNING DOCUMENTS
  - Metropolitan Plan of Prague (Územní plán hl. m. Prahy — Metropolitní plán, MPP), OOP 001/2026,
    issued by the Prague City Assembly 28 May 2026, in force since 1 Sep 2026. Replaced the 1999 zoning plan.
    Court review pending (MS Praha 11 A 24/2026). Part D below.
  - MPP příloha 4, locality cover sheet 058 / Horní Pankrác. Part B below.
  - MPP příloha 2, tables (transformation areas, infrastructure). Part C below.
  - Prague Building Regulations (Pražské stavební předpisy, PSP, nařízení 12/2024 Sb. hl. m. Prahy),
    consolidated with the national construction requirements (VPV) — "Souhrnné znění požadavků na výstavbu
    v Praze", normative text 2025/01. Part E below.

2. CLASSIFICATION OF THE PLOT (16,487 m², 11 ČÚZK parcels)
  - Locality .............. 058 / Horní Pankrác (Praha 4; k.ú. Krč, Michle, Nusle; 40 ha)
  - Buildability .......... Z — buildable (zastavitelná stavební)
  - Structure ............. (03) hybrid structure (čl. 43): compact/loose blocks and solitaires forming
                            sub-centres
  - Use ................... O — residential (obytná, čl. 63); admin and commercial buildings are part of the locality
  - Stability ............. [S] stabilised (čl. 69, 70): changes take the existing character into account
  - Transformation areas .. none on the plot (T 411/058/2235 and 411/058/2336 lie east of the metro D corridor)

3. KEY PROVISIONS
  MPP
  - Regulated floor area (HPPreg) and max coverage (Zmax) are set only for [T]/[R] areas (čl. 95, 96);
    the plot is [S]. Neighbouring T areas: 411/058/2235 Zmax 70 %, Zz 35 %, Vz 8.0;
    411/058/2336 Zmax 100 %, Zz 60 %, Vz 8.0 (HPPreg = area x Zz x Vz, čl. 96).
  - MPP gross floor area also counts underground floors except garages and service spaces (čl. 96 odst. 1).
  - Panoramas and protected vistas (čl. 104, 105; KLZ 058/200).
  - Streets: 5. května metropolitan level; náměstí Arkády, Budějovická, Na Pankráci district level (čl. 82).
  - Metro D (621/-/1, 621/-/3, stations and vestibules Pankrác D) and its public-benefit constructions
    (VPS 910-621/-/1, 910-621/-/3) border the east of the plot; tram Pankrác–Budějovická (622/-/9);
    cycle routes 650/-/127, 650/-/222.
  PSP (Prague building regulations)
  - §20  daylight, sunlight and shading per ČSN 73 0580 / EN 17037
  - §21  distance from neighbouring buildings: no new building above 45° within a ≥45° horizontal sector in
         front of habitable-room windows of existing neighbours (příloha 1, bod II)
  - §22  building at the plot boundary: at least 2 m from boundaries with neighbouring plots (not public space)
  - §23  fencing
  - §24  connection to roads
  - §25  parking capacity: min/max from gross floor area per space (příloha 2: hotel 100 m², housing 85,
         office 50, retail 70, restaurant 40) x zone %; the plot is in parking zone 02 (příloha 3):
         bound spaces 80 %, visitor 15–55 %
  - §26  form and character of parking; §27 bicycle parking
  - §28–30  water supply, waste water, other utility connections
  - §49  residential buildings and flats; §50 accommodation (hotel) buildings; §58–62 garages
"""


def main():
    parts = [
        "PANORAMA PANKRÁC — LOCAL REGULATIONS\n"
        "Compiled by tools/compile_regulations.py from the sources in 02_regulations/raw/. Parts B–E are the\n"
        "official Czech texts (extracted from the PDFs; layout simplified). Part A is an English summary.\nBuilding-height regulation (MPP čl. 18, 97–103; tower level XIV. Pankrác) is not included.\n",
        digest(),
        "PART B — LOCALITY COVER SHEET 058 / HORNÍ PANKRÁC (MPP příloha 4), full text\n" + "=" * 75 + "\n\n"
        + clean(drop_height_block((RAW / "KLZ_058.txt").read_text())),
        "PART C — MPP PŘÍLOHA 2, table rows for locality 058\n" + "=" * 51 + "\n"
        "(columns: code, type, structure, use, Zmax %, Zz %, Vz, area m² — or name and status)\n\n"
        + tab_rows((RAW / "tab.txt").read_text()),
        "PART D — METROPOLITAN PLAN (MPP), text part — articles governing this plot\n" + "=" * 74 + "\n\n"
        + mpp_articles((RAW / "MPP_textova_cast.txt").read_text()),
        "PART E — PRAGUE BUILDING REGULATIONS (PSP + VPV, consolidated text 2025/01), full text\n" + "=" * 84
        + "\n\n" + clean((RAW / "PSP.txt").read_text()),
    ]
    OUT.write_text("\n\n".join(parts), encoding="utf-8")
    print(OUT, f"{OUT.stat().st_size / 1e3:.0f} kB, {OUT.read_text().count(chr(10))} lines")


if __name__ == "__main__":
    main()
