#!/usr/bin/env python
"""Compile every local regulation that applies to the Panorama Pankrác plot into ONE plain-text file.

Writes 02_regulations/regulations_panorama.txt:
  Part A  English digest — what applies to the plot, the limits, and how the existing scheme scores
          (limits from 02_regulations/rules.yaml + summary.md, scores from 03_existing/model/metrics.json)
  Part B  Locality sheet 058 / Horní Pankrác (MPP příloha 4, krycí list) — full Czech text
  Part C  MPP příloha 2 table rows for locality 058 (transformation areas, tower level, metro)
  Part D  Metropolitan Plan (MPP) text — the articles that govern this plot, verbatim Czech
  Part E  Prague building regulations (PSP + national VPV, consolidated text 2025/01) — full Czech text

Usage: .venv/bin/python tools/compile_regulations.py
"""
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "02_regulations"
RAW = REG / "raw"
OUT = REG / "regulations_panorama.txt"

# MPP articles that govern a building on this plot (TOC in raw/MPP_textova_cast.txt)
MPP_ARTICLES = [
    (3, 5, "Terms and definitions (RNP, regulated height, block, …)"),
    (12, 12, "Localities and their character"),
    (17, 18, "Mass and structure of the city; height regulation concept"),
    (35, 40, "Locality code, target character, cover sheets, buildability, structure"),
    (43, 43, "(03) Hybrid structure — this locality"),
    (61, 61, "Use of locality"),
    (63, 63, "Buildable residential locality — this locality"),
    (68, 70, "Stability; stabilised areas [S] — this plot"),
    (73, 74, "Measure of land use; stabilised areas"),
    (79, 82, "Public spaces, streets, street hierarchy"),
    (87, 89, "Public-space coefficients, pedestrian permeability, building blocks"),
    (92, 92, "Courtyards"),
    (95, 105, "Building coverage, regulated floor area, height regulation, towers, dominants, panoramas"),
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


def tab_rows(text):
    keep = [ln.rstrip() for ln in text.splitlines()
            if re.search(r"/058/|\b058\b +Horní Pankrác|058 / Horní Pankrác|XIV\. Pankrác", ln)]
    return "\n".join(re.sub(r" {3,}", "   ", ln.strip()) for ln in keep) + "\n"


def digest():
    rules = yaml.safe_load((REG / "rules.yaml").read_text())["rules"]
    metrics = json.loads((ROOT / "03_existing/model/metrics.json").read_text())
    m = metrics.get("metrics", metrics)
    def val(key):
        v = m.get(key, metrics.get(key))
        return "—" if v is None else v
    rows = []
    for r in rules:
        lim = f"<= {r['max']}" if "max" in r else f">= {r['min']}" if "min" in r else "no numeric limit"
        v = val(r["metric"])
        ok = ("PASS" if (("max" in r and v <= r["max"]) or ("min" in r and v >= r["min"])) else "FAIL") \
            if isinstance(v, (int, float)) and ("max" in r or "min" in r) else "info"
        rows.append(f"  - {r['label']}\n      limit: {lim}   existing scheme: {v}   -> {ok}\n      source: {r['source']}")
    return f"""\
PART A — DIGEST (English): what applies to the Panorama Pankrác plot
====================================================================

1. GOVERNING DOCUMENTS
  - Metropolitan Plan of Prague (Územní plán hl. m. Prahy — Metropolitní plán, MPP), OOP 001/2026,
    issued by the Prague City Assembly 28 May 2026, in force since 1 Sep 2026. Replaced the 1999 zoning plan.
    Court review pending (MS Praha 11 A 24/2026).  Text: raw/MPP_textova_cast.pdf; Part D below.
  - MPP příloha 4, locality cover sheet 058 / Horní Pankrác. Part B below.
  - MPP příloha 2, tables (transformation areas, tower levels, infrastructure). Part C below.
  - Prague Building Regulations (Pražské stavební předpisy, PSP, nařízení 12/2024 Sb. hl. m. Prahy),
    consolidated with the national construction requirements (VPV) — "Souhrnné znění požadavků na výstavbu
    v Praze", normative text 2025/01. Text: raw/PSP_souhrnne_zneni.pdf; Part E below.

2. CLASSIFICATION OF THE PLOT (16,487 m², 11 ČÚZK parcels; origin Milevská 7)
  - Locality .............. 058 / Horní Pankrác (Praha 4; k.ú. Krč, Michle, Nusle; 40 ha)
  - Buildability .......... Z — buildable (zastavitelná stavební)
  - Structure ............. (03) hybrid structure (čl. 43): compact/loose blocks and solitaires forming
                            sub-centres, varied heights
  - Use ................... O — residential (obytná, čl. 63); admin and commercial buildings are part of the locality
  - Stability ............. [S] stabilised (čl. 69, 70): target character derived from the existing character
  - Transformation areas .. none on the plot (T 411/058/2235 and 411/058/2336 lie east of the metro D corridor)
  - Height squares (Z 02) . storey range 27 over the whole plot (black = above height-stable development)

3. LIMITS
  - Max regulated building height: 100 m (range 27, čl. 98 odst. 3)
  - Max storeys above ground (RNP): range 27 = more than 21 RNP — read as max 27 (INTERPRETATION, čl. 98/3)
  - Height in a stabilised area: must take the surrounding heights and any territorial study into account
    (čl. 98 odst. 2a; čl. 70). Neighbours: City Tower 109 m, V Tower 105 m, City Empiria 104 m.
  - One set-back storey / attic / roof structure allowed above the main cornice (čl. 98 odst. 6).
  - Regulated floor area (HPPreg) and max coverage (Zmax): NOT set in [S] areas (čl. 95, 96 apply to [T]/[R]).
    Benchmark only: neighbouring T areas use Zz 35 %/Vz 8.0 (HPPreg 2.8 x plot) and Zz 60 %/Vz 8.0 (4.8 x plot).
  - Tower level XIV. Pankrác (towers max 70 m, max 75 % of built area, čl. 100) applies only to the marked
    squares by the metro D, NOT to this plot.
  - Metro D corridor (VPS 910-621/-/1, 910-621/-/3) borders the east wedge of the plot.
  - PSP §20  daylight per ČSN 73 0580 / EN 17037 (direct sunlight requirement for flats does not apply in Prague)
  - PSP §21  distance from neighbouring buildings: no new building above 45° within a ≥45° horizontal sector
             in front of habitable-room windows of existing neighbours (příloha 1, bod II)
  - PSP §22  at least 2 m from boundaries with neighbouring plots (not public space)
  - PSP §25  parking: min/max from HPP per space (hotel 100 m², housing 85, office 50, retail 70,
             restaurant 40) x zone %; plot is in parking zone 02 (IPR layer, verified 2026-11-11):
             bound spaces 80 %, visitor 15–55 %
  - PSP §26  form of parking; §27 bicycle parking; §28–30 utility connections; Part E has the rest.

4. CHECK OF THE EXISTING (CLIENT) SCHEME — generated from the model
{chr(10).join(rows)}

5. OPEN POINTS
  - Confirm with IPR / the building authority that the whole plot is [S] (read from the binding KLZ 058 map, ±5 m).
  - §22 assumes the S (Milevská) and E (street/metro) plot edges face public space — to confirm.
  - Any existing permit or territorial decision for the client scheme under the old plan would take precedence.

Machine-checkable rules: 02_regulations/rules.yaml.  Notes: 02_regulations/summary.md.
"""


def main():
    parts = [
        "PANORAMA PANKRÁC — LOCAL REGULATIONS\n"
        "Compiled by tools/compile_regulations.py from the sources in 02_regulations/raw/. Parts B–E are the\n"
        "official Czech texts (extracted from the PDFs; layout simplified). Part A is our English digest.\n",
        digest(),
        "PART B — LOCALITY COVER SHEET 058 / HORNÍ PANKRÁC (MPP příloha 4), full text\n" + "=" * 75 + "\n\n"
        + clean((RAW / "KLZ_058.txt").read_text()),
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
