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
    """C-shaped perimeter block (courtyard open to side N, S, W or E — in the plot frame), wing depth `wing`."""
    if open_side == "N":
        return [[u0, v0], [u1, v0], [u1, v1], [u1 - wing, v1], [u1 - wing, v0 + wing], [u0 + wing, v0 + wing],
                [u0 + wing, v1], [u0, v1]]
    if open_side == "S":
        return [[u0, v0], [u0 + wing, v0], [u0 + wing, v1 - wing], [u1 - wing, v1 - wing], [u1 - wing, v0], [u1, v0],
                [u1, v1], [u0, v1]]
    if open_side == "W":
        return [[u0, v0], [u1, v0], [u1, v1], [u0, v1], [u0, v1 - wing], [u1 - wing, v1 - wing], [u1 - wing, v0 + wing],
                [u0, v0 + wing]]
    if open_side == "E":
        return [[u0, v0], [u1, v0], [u1, v0 + wing], [u0 + wing, v0 + wing], [u0 + wing, v1 - wing], [u1, v1 - wing],
                [u1, v1], [u0, v1]]
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
            # D3 (loop 2026-11-10): grown by a local search with the pipeline's own §21/§22/parking/daylight/sun checks:
            # 30 x 40 m hotel floorplate, longer 10-storey street bar, east bar +4 m north, deeper 7-storey north wing.
            {"id": "H", "name": "Hotel tower", "use": "Hotel", "preset": "hotel_tower", "poly": rect(30, -41, 60, -1),
             "storeys": storeys(27, 6.0, 3.3, "Hotel lobby / restaurant", "Hotel rooms", 5.0, "Conference / spa")},
            {"id": "S", "name": "Street bar (Milevská)", "use": "Residential", "preset": "resi", "poly": rect(-20, -61, 86, -45),
             "storeys": storeys(10, 4.5, 3.1, "Retail", "Apartments")},
            {"id": "R", "name": "East bar", "use": "Residential", "preset": "resi", "poly": rect(88, -59, 104, 4),
             "storeys": storeys(12, 4.5, 3.1, "Retail", "Apartments")},
            {"id": "O", "name": "North office wing", "use": "Office", "preset": "office", "poly": rect(-52, 12, 22, 34),
             "storeys": storeys(7, 4.5, 3.6, "Office lobby", "Offices")},
        ],
    },
    "B": {
        "name": "Option B — twin towers on a podium",
        "intent": "Hotel tower and residential tower (27 storeys each, ≈95 m) on a 2-storey retail/conference podium "
                  "along Milevská, placed to keep the 45° distance angle of the neighbours (PSP §21); 6-storey offices "
                  "in the north wing; large central park.",
        "basement_levels": 3,
        "blocks": [
            # D1 (loop 2026-11-09): towers re-positioned by a §21 search (random + local, psp.distance_angle_neighbours):
            # hotel tower 4 m E / 10 m N, residential tower 18 m W / 4 m N, north wing 10 → 6 storeys (three-wing building).
            {"id": "H", "name": "Hotel tower", "use": "Hotel", "preset": "hotel_tower", "poly": rect(-8, -26, 22, 4),
             "storeys": storeys(27, 6.0, 3.3, "Hotel lobby / restaurant", "Hotel rooms", 5.0, "Conference / spa")},
            {"id": "T", "name": "Residential tower", "use": "Residential", "preset": "resi_tower", "poly": rect(44, -34, 72, -6),
             "storeys": storeys(27, 4.5, 3.2, "Retail", "Apartments")},
            {"id": "P", "name": "Podium (retail + conference)", "use": "Retail", "preset": "podium", "poly": rect(-28, -61, 104, -44),
             "storeys": storeys(2, 5.0, 4.5, "Retail", "Conference")},
            {"id": "O", "name": "North office wing", "use": "Office", "preset": "office", "poly": rect(-48, 16, 22, 32),
             "storeys": storeys(6, 4.5, 3.6, "Office lobby", "Offices")},
        ],
    },
    "C": {
        "name": "Option C — mid-rise city blocks (no towers)",
        "intent": "Two courtyard blocks of 10 storeys (≤36 m), the hotel courtyard open to the south (sun) and the "
                  "apartment courtyard open to the east; offices to the north. Lower visual impact, no tower debate.",
        "basement_levels": 3,
        "blocks": [
            # D2 (loop 2026-11-10): search over block extents, open side, wing depth and heights with the pipeline's own
            # §21 / §22 / daylight / courtyard-sun checks. West block opens SOUTH, east block opens EAST, both 10 storeys.
            {"id": "HW", "name": "West block — hotel", "use": "Hotel", "preset": "office",
             "poly": cshape(-14, -61, 36, -6, 16, "S"), "storeys": storeys(10, 5.0, 3.2, "Hotel lobby / restaurant", "Hotel rooms")},
            {"id": "RE", "name": "East block — apartments", "use": "Residential", "preset": "resi",
             "poly": cshape(42, -61, 104, -4, 16, "E"), "storeys": storeys(10, 4.5, 3.1, "Retail", "Apartments")},
            {"id": "O", "name": "North office wing", "use": "Office", "preset": "office", "poly": rect(-48, 16, 22, 32),
             "storeys": storeys(10, 4.5, 3.6, "Office lobby", "Offices")},
        ],
    },
    "D": {
        "name": "Option D — client scheme, made compliant",
        "intent": "The client's own buildings with the smallest changes that pass PSP §21 and parking (D4): tower A "
                  "moved 8 m south at full height, D's east end 10 m shorter and 7 storeys, C1 6 storeys and 4 m "
                  "shorter on the drum side, B3 4 storeys, a third basement level.",
        "from_existing": "03_existing/params.yaml",
        "basement_levels": 3,
        # Found by a search with the pipeline's own §21 check (log 2026-11-10, iterations 14-15). Typical storey
        # heights are frozen at the client model's values where a storey count changes.
        "edits": {
            "A": {"footprint": [[-16.13, 15.74], [16.9, 21.8], [23.19, -12.89], [-9.5, -18.62]]},
            "D": {"footprint": [[-10.78, 46.71], [-10.78, 43.71], [-3.91, 44.99], [-3.91, 47.99], [19.87, 53.8],
                                [19.01, 32.86], [-4.47, 31.91], [-38.05, 19.89], [-42.29, 42.65]],
                  "typical_count": 6, "typical_height": 3.4143},
            "C1": {"footprint": [[-11.26, -35.24], [-12.67, -59.62], [-28.08, -58.73], [-28.57, -56.6], [-28.57, -38.46]],
                   "typical_count": 5, "typical_height": 2.82},
            "B3": {"typical_count": 3, "typical_height": 3.375},
        },
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


def build_from_existing(key, spec):
    """Option derived from an existing scheme's params (client scheme) by per-building edits."""
    raw = yaml.safe_load((ROOT / spec["from_existing"]).read_text())
    for b in raw["buildings"]:
        e = spec.get("edits", {}).get(b["id"], {})
        if "footprint" in e:
            b["footprint"] = e["footprint"]
        if "typical_count" in e:
            rep = [g for g in b["storeys"] if int(g.get("count", 1)) > 1][0]
            rep["count"] = e["typical_count"]
            rep["height"] = e["typical_height"]
            b.pop("height", None)          # storey heights are explicit now (no rescaling to the old total)
        if b["id"] == "U":
            lv = spec.get("basement_levels", 2)
            b["storeys"] = [{"name": "B", "count": lv, "height": 3.5, "use": "Parking"}]
            b["ground_elevation"] = round(-3.5 * lv, 2)
            b["notes"] = f"ASSUMED {lv} basement levels under the client's U footprint"
    raw.update({"name": spec["name"], "output_dir": "model", "site": {"file": "../../../00_site/site.yaml"},
                "rules": "../../../02_regulations/rules.yaml", "parking_zone": "02"})
    raw["render"] = {"samples": 32, "sun_azimuth": 200, "sun_altitude": 42, "cameras": CAMERAS}
    d = OUT / key
    d.mkdir(parents=True, exist_ok=True)
    head = (f"# {spec['name']}\n# Intent: {spec['intent']}\n"
            f"# Generated by tools/make_options.py from {spec['from_existing']} — edit SPECS there, not this file.\n")
    (d / "params.yaml").write_text(head + yaml.safe_dump(raw, sort_keys=False, allow_unicode=True, width=140))
    return d / "params.yaml"


CAMERAS = [
    {"name": "aerial_S", "location": [-93.67, -255.78, 218.91], "target": [14.88, -5.5, 20], "lens": 36.86, "resolution": [1280, 905]},
    {"name": "aerial_SE", "location": [260, -200, 160], "target": [30, -5, 25], "lens": 35, "resolution": [1280, 905]},
    {"name": "top_view", "location": [40, -10, 600], "target": [40, -9.99, 0], "lens": 35, "resolution": [1100, 1100]}]


def build_option(key, spec):
    if "from_existing" in spec:
        return build_from_existing(key, spec)
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
        "render": {"samples": 32, "sun_azimuth": 200, "sun_altitude": 42, "cameras": CAMERAS},
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
