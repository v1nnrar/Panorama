#!/usr/bin/env python
"""Generate capacity-study options (04_proposed/options/<id>/params.yaml) from compact specs.

Geometry is written in the PLOT FRAME (u along Milevská, v perpendicular to it, metres), which is the local survey
frame rotated by +7.7°; the generator rotates footprints back into the survey frame. Every option keeps the
existing corner office E (parcel 1133/12) and has a basement for parking. Presets give each use a plausible
facade and roof so the renders read correctly. All numbers are ASSUMED design choices of the capacity study.

Usage: .venv/bin/python tools/make_options.py            # writes all options
       .venv/bin/python tools/make_options.py A          # one option
Edit SPECS (or add new ones) to explore further; the improvement loop does exactly that (LOOP.md section D).
"""
import json
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "04_proposed" / "options"
ROT = math.radians(-7.7)          # plot frame → survey frame

E_EXISTING = [[94.76, 12.3], [125.82, 18.02], [126.85, 12.26], [125.39, 12.02], [125.78, 10.41], [131.87, 11.17],
              [125.83, -4.35], [120.4, -5.47], [120.42, -6.96], [119.35, -7.83], [117.94, -7.24], [117.57, -5.99],
              [110.95, -6.87], [98.27, -6.87]]


def to_survey(pts):
    c, s = math.cos(ROT), math.sin(ROT)
    return [[round(u * c - v * s, 2), round(u * s + v * c, 2)] for u, v in pts]


def rect(u0, v0, u1, v1):
    return [[u0, v0], [u1, v0], [u1, v1], [u0, v1]]


def cshape(u0, v0, u1, v1, wing, open_side="N"):
    """C-shaped perimeter block (courtyard open to one side), wing depth `wing`."""
    if open_side == "N":
        return [[u0, v0], [u1, v0], [u1, v1], [u1 - wing, v1], [u1 - wing, v0 + wing], [u0 + wing, v0 + wing],
                [u0 + wing, v1], [u0, v1]]
    raise ValueError(open_side)


PRESETS = {
    "hotel_tower": {
        "material": "Concrete white",
        "facade": [{"type": "curtain", "glass": "Glass", "mullion": 1.5, "spandrel": 0.9},
                   {"type": "band", "from": 2, "depth": 0.6, "thickness": 0.45, "material": "Aluminium white"},
                   {"type": "fins", "from": 3, "spacing": 3.0, "width": 0.25, "depth": 0.5, "material": "Bronze"}],
        "roof": {"parapet": 1.4, "parapet_material": "Bronze", "pv": {"azimuth": "building", "tilt": 10, "row": 2.0, "gap": 0.8},
                 "structures": [{"name": "core", "dx": 0, "dy": 0, "w": 9, "d": 7, "h": 4.0, "material": "Render grey"}]},
    },
    "resi": {
        "material": "Render white",
        "windows": {"width": 1.8, "height": 2.1, "sill": 0.6, "spacing": 3.6, "edge_margin": 1.2},
        "facade": [{"type": "curtain", "from": 1, "to": 1, "glass": "Glass dark", "mullion": 3.0},
                   {"type": "balcony", "from": 2, "facing": ["S", "W", "E"], "depth": 1.6, "planter": True},
                   {"type": "fins", "from": 2, "spacing": 3.6, "width": 0.2, "depth": 0.3, "material": "Timber"}],
        "roof": {"parapet": 1.0, "parapet_material": "Render white", "green": True,
                 "pv": {"azimuth": "building", "tilt": 12, "row": 2.0, "gap": 0.8}},
    },
    "resi_tower": {
        "material": "Concrete white",
        "facade": [{"type": "curtain", "glass": "Glass", "mullion": 1.5},
                   {"type": "balcony", "from": 2, "depth": 1.8, "planter": True},
                   {"type": "band", "from": 2, "every": 3, "depth": 2.1, "thickness": 0.5, "material": "Concrete white"}],
        "roof": {"parapet": 1.1, "parapet_material": "Concrete white", "pv": {"azimuth": "building", "tilt": 10, "row": 2.0, "gap": 0.8}},
    },
    "office": {
        "material": "Aluminium white",
        "facade": [{"type": "curtain", "glass": "Glass", "mullion": 1.35, "spandrel": 1.0},
                   {"type": "band", "from": 2, "depth": 0.7, "thickness": 0.5, "material": "Aluminium white"}],
        "roof": {"parapet": 1.2, "parapet_material": "Aluminium white", "green": True,
                 "pv": {"azimuth": "building", "tilt": 12, "row": 2.0, "gap": 0.8}},
    },
    "podium": {
        "material": "Concrete white",
        "facade": [{"type": "curtain", "glass": "Glass dark", "mullion": 2.4},
                   {"type": "band", "depth": 0.8, "thickness": 0.6, "material": "Timber"}],
        "roof": {"parapet": 0.9, "parapet_material": "Timber", "green": True},
    },
}


def storeys(n, gf, typ, gf_use, use, gf2=None, gf2_use=None):
    s = [{"name": "GF", "height": gf, "use": gf_use}]
    if gf2:
        s.append({"name": "L2", "height": gf2, "use": gf2_use})
        n -= 1
    s.append({"name": "L", "count": n - 1, "start": len(s) + 1, "height": typ, "use": use})
    return s


SPECS = {
    "A": {
        "name": "Option A — hotel tower + residential blocks",
        "intent": "One slender 27-storey hotel tower as the landmark (≈95 m, under the 100 m cap), residential bars "
                  "holding the Milevská street line and the east edge, low office wing to the north, park kept.",
        "basement_levels": 3,
        "blocks": [
            {"id": "H", "name": "Hotel tower", "use": "Hotel", "preset": "hotel_tower", "poly": rect(30, -39, 58, -11),
             "storeys": storeys(27, 6.0, 3.3, "Hotel lobby / restaurant", "Hotel rooms", 5.0, "Conference / spa")},
            {"id": "S", "name": "Street bar (Milevská)", "use": "Residential", "preset": "resi", "poly": rect(-16, -61, 84, -45),
             "storeys": storeys(9, 4.5, 3.1, "Retail", "Apartments")},
            {"id": "R", "name": "East bar", "use": "Residential", "preset": "resi", "poly": rect(88, -59, 104, 0),
             "storeys": storeys(12, 4.5, 3.1, "Retail", "Apartments")},
            {"id": "O", "name": "North office wing", "use": "Office", "preset": "office", "poly": rect(-48, 16, 22, 32),
             "storeys": storeys(8, 4.5, 3.6, "Office lobby", "Offices")},
        ],
    },
    "B": {
        "name": "Option B — twin towers on a podium",
        "intent": "Hotel tower and residential tower (27 storeys each, ≈95 m) on a 2-storey retail/conference podium "
                  "along Milevská; offices in the north wing; large central park.",
        "basement_levels": 3,
        "blocks": [
            {"id": "H", "name": "Hotel tower", "use": "Hotel", "preset": "hotel_tower", "poly": rect(-12, -36, 18, -6),
             "storeys": storeys(27, 6.0, 3.3, "Hotel lobby / restaurant", "Hotel rooms", 5.0, "Conference / spa")},
            {"id": "T", "name": "Residential tower", "use": "Residential", "preset": "resi_tower", "poly": rect(62, -38, 90, -10),
             "storeys": storeys(27, 4.5, 3.2, "Retail", "Apartments")},
            {"id": "P", "name": "Podium (retail + conference)", "use": "Retail", "preset": "podium", "poly": rect(-28, -61, 104, -44),
             "storeys": storeys(2, 5.0, 4.5, "Retail", "Conference")},
            {"id": "O", "name": "North office wing", "use": "Office", "preset": "office", "poly": rect(-48, 16, 22, 32),
             "storeys": storeys(10, 4.5, 3.6, "Office lobby", "Offices")},
        ],
    },
    "C": {
        "name": "Option C — mid-rise city blocks (no towers)",
        "intent": "Two courtyard blocks of 11 storeys (≤40 m) open to the park; hotel in the west block, apartments in "
                  "the east block, offices to the north. Lower visual impact, no tower debate.",
        "basement_levels": 3,
        "blocks": [
            {"id": "HW", "name": "West block — hotel", "use": "Hotel", "preset": "office",
             "poly": cshape(-28, -61, 38, 2, 16), "storeys": storeys(11, 5.0, 3.2, "Hotel lobby / restaurant", "Hotel rooms")},
            {"id": "RE", "name": "East block — apartments", "use": "Residential", "preset": "resi",
             "poly": cshape(48, -61, 104, -2, 16), "storeys": storeys(11, 4.5, 3.1, "Retail", "Apartments")},
            {"id": "O", "name": "North office wing", "use": "Office", "preset": "office", "poly": rect(-48, 16, 22, 32),
             "storeys": storeys(10, 4.5, 3.6, "Office lobby", "Offices")},
        ],
    },
}


def basement(levels):
    return {"id": "U", "name": "Underground parking", "use": "Parking / technical",
            "footprint": [[-49.78, 14.14], [-50.12, 11.75], [-49.3, 10.76], [-36.74, -55.39], [-37.61, -57.3],
                          [53.85, -69.64], [100.0, -73.0], [118.0, -22.0], [96.0, -8.0], [33.28, 43.14], [-51.67, 24.54]],
            "ground_elevation": round(-3.5 * levels, 2), "windows": False, "material": "Concrete grey",
            "notes": f"ASSUMED {levels} basement levels under the plot (parking + technical)",
            "storeys": [{"name": "B", "count": levels, "height": 3.5, "use": "Parking"}], "roof": {"parapet": 0, "slab": False}}


def existing_E():
    return {"id": "E", "name": "Existing corner office (parcel 1133/12)", "existing": True, "use": "Office (existing, kept)",
            "footprint": E_EXISTING, "height": 32.0,
            "storeys": [{"name": "GF", "height": 4.5, "use": "Lobby"}, {"name": "L", "count": 8, "height": 3.3, "use": "Offices"}],
            "facade": [{"type": "curtain", "glass": "Glass dark", "mullion": 1.5, "spandrel": 0.9},
                       {"type": "band", "from": 2, "depth": 0.35, "thickness": 0.4, "material": "Aluminium white"}],
            "roof": {"parapet": 1.6, "parapet_material": "Bronze"}}


def build_option(key, spec):
    blds = []
    for blk in spec["blocks"]:
        pre = json.loads(json.dumps(PRESETS[blk["preset"]]))
        b = {"id": blk["id"], "name": blk["name"], "use": blk["use"], "footprint": to_survey(blk["poly"]),
             "storeys": blk["storeys"], **pre}
        for k in ("height", "setbacks", "terrace_edge"):
            if k in blk:
                b[k] = blk[k]
        blds.append(b)
    blds += [existing_E(), basement(spec.get("basement_levels", 2))]
    params = {
        "name": spec["name"], "output_dir": "model", "site": {"file": "../../../00_site/site.yaml"},
        "rules": "../../../02_regulations/rules.yaml", "parking_zone": "02",
        "exterior_wall": 0.35, "slab_thickness": 0.30, "roof": {"parapet": 1.1},
        "buildings": blds,
        "landscape": {"edge_paving": 1.5, "building_paving": 3.0, "courtyard_trees": {"spacing": 11, "height": [6, 11], "seed": 3, "clear": 5},
                      "context_tree_radius": 450},
        "render": {"samples": 32, "sun_azimuth": 200, "sun_altitude": 42, "cameras": [
            {"name": "aerial_S", "location": [-93.67, -255.78, 218.91], "target": [14.88, -5.5, 20], "lens": 36.86, "resolution": [1280, 905]},
            {"name": "aerial_SE", "location": [260, -200, 160], "target": [30, -5, 25], "lens": 35, "resolution": [1280, 905]},
            {"name": "top_view", "location": [40, -10, 600], "target": [40, -9.99, 0], "lens": 35, "resolution": [1100, 1100]}]},
    }
    d = OUT / key
    d.mkdir(parents=True, exist_ok=True)
    head = f"# {spec['name']}\n# Intent: {spec['intent']}\n# Generated by tools/make_options.py — edit SPECS there, not this file.\n"
    (d / "params.yaml").write_text(head + yaml.safe_dump(params, sort_keys=False, allow_unicode=True, width=140))
    return d / "params.yaml"


if __name__ == "__main__":
    keys = sys.argv[1:] or list(SPECS)
    for k in keys:
        print(build_option(k, SPECS[k]))
