#!/usr/bin/env python
"""Generate the params YAML of the proposed design concept "Dancers" (04_proposed/concept_dancers/params.yaml).

Design (user picks, 04_proposed/design/round5_blocks_open_roofs.md): two hourglass towers joined by ONE sky bridge,
standing roughly where the client's towers A and B stand; separate low blocks on the rough outlines of the client's
blocks (front block on Milevská, north block, terraced block by the east tower, west pavilion) plus a spa pavilion in
the east wedge — every block a different shape, with gaps of >= 6 m between buildings.

Footprints are generated here (circles, buffered arcs, ellipses) so the YAML stays the single source of truth for the
pipeline. Run:  .venv/bin/python tools/make_concept.py  then  build.py 04_proposed/concept_dancers/params.yaml
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon

OUT = Path(__file__).resolve().parents[1] / "04_proposed" / "concept_dancers" / "params.yaml"

# --- storey heights (ASSUMED: typical 4* hotel / residential values until the brief arrives) -----------------
GF, L1, TYP = 6.0, 4.5, 3.3          # lobby, first floor (restaurants / meeting), typical room floor


def ring(poly: Polygon, nd=2) -> list[list[float]]:
    return [[round(x, nd), round(y, nd)] for x, y in list(poly.exterior.coords)[:-1]]


def circle(cx, cy, r, n=36) -> Polygon:
    return Polygon([(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)])


def arc_bar(pts, half_width) -> Polygon:
    """A curved bar: a smoothed polyline buffered with round ends."""
    line = LineString(pts)
    return line.buffer(half_width, quad_segs=8).simplify(0.15)


def ellipse(cx, cy, rx, ry, rot=0.0) -> Polygon:
    e = affinity.rotate(affinity.scale(circle(0, 0, 1, 40), rx, ry, origin=(0, 0)), rot, origin=(0, 0))
    return affinity.translate(e, cx, cy)


def hourglass_tower(tid, name, cx, cy, n_storeys, r_base, r_waist, waist_at=0.55, use="Hotel"):
    """One storey group per floor; the radius follows a smooth hourglass profile (waist at `waist_at` of height)."""
    groups = []
    for i in range(n_storeys):
        t = i / max(n_storeys - 1, 1)
        # cosine blend: r_base at bottom and top, r_waist at waist_at
        u = t / waist_at if t <= waist_at else (1 - t) / (1 - waist_at)
        r = r_waist + (r_base - r_waist) * (1 - math.cos(math.pi * (1 - u))) / 2
        h = GF if i == 0 else L1 if i == 1 else TYP
        groups.append({"name": "GF" if i == 0 else f"L{i:02d}", "height": h, "count": 1,
                       "use": "Hotel lobby" if i == 0 else use, "footprint": ring(circle(cx, cy, r))})
    return {
        "id": tid, "name": name, "use": use, "material": "Steel white",
        "footprint": groups[0]["footprint"], "storeys": groups,
        "facade": [{"type": "curtain", "glass": "Glass dark", "mullion": 1.5, "spandrel": 0.6},
                   {"type": "band", "depth": 0.9, "thickness": 0.35, "every": 1}],
        "roof": {"parapet": 1.4, "slab": True, "green": True},   # open crown with sky garden (detailed later)
    }


def storey_z(k):
    """Bottom elevation of storey k (1-based) in a tower: GF 6.0, L1 4.5, then 3.3 m."""
    return 0 if k == 1 else GF if k == 2 else GF + L1 + TYP * (k - 3)


def main():
    # ---- towers: roughly at the client's A (4, 10) and B (72, -33), pulled together for a ~25 m bridge -----
    T1c, T2c = (24.0, 2.0), (63.0, -27.0)
    T1 = hourglass_tower("T1", "Tower 1 — hotel (27 storeys)", *T1c, 27, 16.0, 12.5)   # MPP range 27: max 27
    T2 = hourglass_tower("T2", "Tower 2 — hotel / serviced apartments (23 storeys)", *T2c, 23, 15.0, 11.5,
                         use="Serviced apartments")

    # ---- ONE sky bridge: T2 storeys 18-19 (two-storey sky lounge), between the facing tower surfaces ---------
    k0 = 18
    z0 = storey_z(k0)
    axis = LineString([T1c, T2c])
    bridge = axis.buffer(6.0, cap_style=2)                       # 12 m wide
    bridge = bridge.difference(circle(*T1c, 12.0)).difference(circle(*T2c, 11.0))
    bridge = max(getattr(bridge, "geoms", [bridge]), key=lambda g: g.area)
    BR = {"id": "BR", "name": "Sky bridge — lounge + bar", "use": "Restaurant", "material": "Steel white",
          "ground_elevation": round(z0, 2), "footprint": ring(bridge),
          "storeys": [{"name": "SB1", "height": 4.5, "use": "Restaurant"}, {"name": "SB2", "height": 3.3, "use": "Restaurant"}],
          "facade": [{"type": "curtain", "glass": "Glass dark", "mullion": 1.8, "spandrel": 0.5}],
          "roof": {"parapet": 1.1, "slab": True, "green": True}}

    # ---- low blocks: client outlines, each a different form -------------------------------------------------
    C1 = arc_bar([(-26, -46), (-19, -43), (-13, -45)], 7.5)                                  # rounded head (client C1)
    C2 = arc_bar([(8, -53), (25, -48), (43, -55)], 8.0)                                       # bowed bar (client C2)
    D = arc_bar([(-36, 31), (-14, 41), (2, 41), (13, 36)], 8.0)                              # crescent (client D)
    B2 = arc_bar([(93, -45), (95, -37), (93, -27)], 8.0)                                      # terraced lens (client B2)
    W = ellipse(-31, 2, 10.0, 15.0, 8)                                                       # west pavilion (client A0)
    S = ellipse(110, -2, 13.0, 8.0, 25)                                                      # spa pavilion (east wedge)

    def low(bid, name, poly, n, use, material, facade, setbacks=None, gf=4.5, typ=3.3):
        st = [{"name": "GF", "height": gf, "use": use}]
        if n > 1:
            st.append({"name": "L", "height": typ, "count": n - 1, "use": use})
        b = {"id": bid, "name": name, "use": use, "material": material, "footprint": ring(poly), "storeys": st,
             "facade": facade, "roof": {"parapet": 1.1, "slab": True, "green": True}}
        if setbacks:   # terraces stepping back to the S/E: explicit footprint per floor (curved outlines)
            step = setbacks[0]["per_storey"]
            st = []
            for i in range(n):
                k = max(0, i - (setbacks[0]["from"] - 2))
                fp = poly.intersection(affinity.translate(poly, -step * k, step * k * 0.6)) if k else poly
                st.append({"name": "GF" if i == 0 else f"L{i}", "height": gf if i == 0 else typ, "use": use,
                           "footprint": ring(fp.simplify(0.1))})
            b["storeys"] = st
        return b

    blocks = [
        low("C1", "Front head — hotel restaurants + ballroom", C1, 5, "Hotel", "Concrete white",
            [{"type": "fins", "spacing": 1.2, "width": 0.12, "depth": 0.45, "material": "Aluminium white"}]),
        low("C2", "Front bar — serviced apartments", C2, 7, "Residential", "Render white",
            [{"type": "balcony", "depth": 1.6, "planter": True, "railing": True}]),
        low("D", "North crescent — conference + offices", D, 7, "Office", "Aluminium white",
            [{"type": "curtain", "glass": "Glass", "mullion": 1.5, "spandrel": 0.9},
             {"type": "band", "depth": 0.6, "thickness": 0.4, "every": 1}]),
        low("B2", "East terraces — apartments", B2, 8, "Residential", "Render white",
            [{"type": "fins", "spacing": 1.5, "width": 0.1, "depth": 0.4, "material": "Timber"}],
            setbacks=[{"facing": ["S", "SE", "E"], "per_storey": 1.4, "from": 3}]),
        low("W", "West pavilion — all-day dining", W, 2, "Restaurant", "Steel white",
            [{"type": "curtain", "glass": "Glass", "mullion": 2.0, "spandrel": 0.4}], gf=5.0, typ=4.0),
        low("S", "Spa pavilion", S, 3, "Hotel", "Concrete white",
            [{"type": "fins", "spacing": 0.9, "width": 0.1, "depth": 0.5, "material": "Bronze"}], gf=5.0, typ=4.0),
    ]

    # ---- basement parking (client U footprint as a start; levels set after the PSP §25 check) ---------------
    U = {"id": "U", "name": "Underground parking", "use": "Parking", "ground_elevation": -10.5,
         "footprint": [[-38.0, -54.0], [52.0, -66.0], [80.0, -66.0], [80.0, -8.0], [38.0, 0.0], [30.0, 22.0],
                       [-36.0, 22.0]],
         "storeys": [{"name": "B", "height": 3.5, "count": 3, "use": "Parking", "windows": False}]}

    design = {
        "name": "Panorama Pankrác — proposed concept 'Dancers' (v0 massing)",
        "output_dir": "model",
        "site": {"file": "../../00_site/site.yaml"},
        "rules": "../../02_regulations/rules.yaml",
        "exterior_wall": 0.35, "slab_thickness": 0.30, "roof": {"parapet": 1.1},
        "buildings": [T1, T2, BR, *blocks, U],
        "landscape": {"edge_paving": 1.5, "building_paving": 3.0, "context_tree_radius": 450},
        "render": {
            "samples": 32, "sun_azimuth": 200, "sun_altitude": 42,
            "cameras": [
                {"name": "aerial_S_like_render000", "location": [-93.67, -255.78, 218.91], "target": [14.88, -5.5, 20],
                 "lens": 36.86, "resolution": [1280, 905]},
                {"name": "aerial_SE", "location": [289, -262, 230], "target": [29, -12, 20], "lens": 36,
                 "resolution": [1600, 900]},
                {"name": "aerial_N", "location": [-60, 330, 260], "target": [29, -12, 20], "lens": 36,
                 "resolution": [1600, 900]},
                {"name": "top_view", "location": [40, -10, 600], "target": [40, -9.99, 0], "lens": 35},
            ],
        },
    }
    header = ("# PROPOSED CONCEPT 'Dancers' — v0 massing. GENERATED by tools/make_concept.py — edit the tool, not this file.\n"
              "# Storey heights ASSUMED (GF 6.0 / L1 4.5 / typical 3.3 m in towers; 4.5 / 3.3 m in low blocks) until the brief.\n"
              "# Positions: towers ~ client A/B, low blocks on the client's outlines (03_existing/params.yaml), reshaped.\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(header + yaml.safe_dump(design, sort_keys=False, width=140))

    # quick report: gaps between buildings and plot fit
    from shapely.ops import unary_union  # noqa: F401
    shapes = {"T1": Polygon(T1["footprint"]), "T2": Polygon(T2["footprint"]), "C1": C1, "C2": C2, "D": D,
              "B2": B2, "W": W, "S": S}
    names = list(shapes)
    gaps = sorted((round(shapes[a].distance(shapes[b]), 1), a, b) for i, a in enumerate(names) for b in names[i + 1:])
    print("closest gaps (m):", gaps[:6])
    print("T1 height", round(sum(g["height"] for g in T1["storeys"]), 1), "T2 height",
          round(sum(g["height"] for g in T2["storeys"]), 1), "bridge z", round(z0, 1))
    print("wrote", OUT)
    return shapes


if __name__ == "__main__":
    main()
