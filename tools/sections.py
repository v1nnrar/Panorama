#!/usr/bin/env python
"""Elevations and sections of a scheme, generated from its params YAML (LOOP.md B3).

Elevations (S, E, N, W): every storey is a vertical prism; seen along a compass axis its outline is the interval of its
projected footprint × [floor, floor + height]. Prisms are drawn from far to near with an opaque fill, so nearer
blocks hide farther ones; storey lines, roof parapets and the ground line are added. Sections: a vertical cut along a
line; storeys cut by the line are drawn solid (poché), buildings beyond the cut as light outlines.

Output: <out>/elevation_<S|E|N|W>.dxf|png, section_<name>.dxf|png, index.md.
Usage: .venv/bin/python tools/sections.py 03_existing [--out 05_drawings/existing/2026-11-13]
       [--section AA:x=-60,140:y=5]  (name:axis=from,to:position ...)
"""
import argparse
import math
import sys
from datetime import date
from pathlib import Path

import ezdxf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MplPoly  # noqa: E402
from shapely.geometry import LineString, Polygon  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline.params import load  # noqa: E402

DEFAULT_SECTIONS = ["AA:x=-60,140:y=5",     # W–E through tower A, podium A0, B3 and office E
                    "BB:y=-75,70:x=5"]      # S–N through block C2, tower A and building D
VIEWS = {  # view name: (unit vector of the image's horizontal axis, unit vector pointing AWAY from the viewer)
    "S": ((1, 0), (0, 1)),      # seen from the south: east to the right, looking north
    "N": ((-1, 0), (0, -1)),
    "E": ((0, 1), (-1, 0)),     # seen from the east: north to the right, looking west
    "W": ((0, -1), (1, 0)),
}


def prisms(design):
    """(building id, storey name, footprint polygon, z0, z1, parapet) for every storey above or below ground."""
    out = []
    for b in design["buildings"]:
        par = float((b.get("roof") or {}).get("parapet", 0) or 0)
        st = b["storeys"]
        for k, s in enumerate(st):
            top = s["elevation"] + s["height"] + (b["slab_thickness"] + par if k == len(st) - 1 else 0.0)
            out.append((b["id"], s["name"], Polygon(s["footprint"]), s["elevation"], top, b.get("below_ground", False)))
    return out


def _new_doc():
    doc = ezdxf.new("R2018", setup=True)
    doc.units = ezdxf.units.M
    for n, c in (("OUTLINE", 7), ("FLOOR", 8), ("CUT", 1), ("BEYOND", 9), ("GROUND", 3), ("TEXT", 250)):
        doc.layers.add(n, color=c)
    return doc


def elevation(design, view, out):
    ux, dv = VIEWS[view]
    items = []
    for bid, name, P, z0, z1, below in prisms(design):
        if below:
            continue
        xs = [x * ux[0] + y * ux[1] for x, y in P.exterior.coords]
        depth = min(x * dv[0] + y * dv[1] for x, y in P.exterior.coords)
        items.append((depth, bid, min(xs), max(xs), z0, z1))
    items.sort(key=lambda t: -t[0])                      # far first
    doc = _new_doc()
    msp = doc.modelspace()
    fig, ax = plt.subplots(figsize=(16, 6))
    tops = {}
    for depth, bid, a, b, z0, z1 in items:
        ax.add_patch(MplPoly([(a, z0), (b, z0), (b, z1), (a, z1)], closed=True, fc="white", ec="black", lw=0.6))
        ax.plot([a, b], [z0, z0], color="0.6", lw=0.3)
        msp.add_lwpolyline([(a, z0), (b, z0), (b, z1), (a, z1)], close=True, dxfattribs={"layer": "OUTLINE"})
        if z1 > tops.get(bid, (0, 0, -1e9))[2]:
            tops[bid] = ((a + b) / 2, depth, z1)
    xmin = min(t[2] for t in items) - 10
    xmax = max(t[3] for t in items) + 10
    ax.plot([xmin, xmax], [0, 0], color="green", lw=1.2)
    msp.add_line((xmin, 0), (xmax, 0), dxfattribs={"layer": "GROUND"})
    for bid, (xc, _, z1) in tops.items():
        ax.text(xc, z1 + 1.5, f"{bid}  +{z1:.1f}", ha="center", fontsize=7)
        msp.add_text(f"{bid} +{z1:.1f}", height=1.2, dxfattribs={"layer": "TEXT"}).set_placement((xc, z1 + 1.5))
    _finish(ax, fig, f"Elevation {view} (seen from the {dict(S='south', N='north', E='east', W='west')[view]})",
            out / f"elevation_{view}", doc)


def section(design, name, axis, a, b, pos, out):
    """Cut along x (axis 'x': line y = pos from x=a..b) or along y (axis 'y': line x = pos from y=a..b)."""
    line = LineString([(a, pos), (b, pos)] if axis == "x" else [(pos, a), (pos, b)])
    doc = _new_doc()
    msp = doc.modelspace()
    fig, ax = plt.subplots(figsize=(16, 6))
    k = 0 if axis == "x" else 1
    beyond = []
    for bid, sname, P, z0, z1, below in prisms(design):
        cut = P.intersection(line)
        if cut.is_empty:
            # beyond the cut, on the far side (north for an x-cut seen from the south, east for a y-cut seen from the west)
            c = P.centroid
            if (axis == "x" and c.y > pos) or (axis == "y" and c.x > pos):
                xs = [p[k] for p in P.exterior.coords]
                if max(xs) > min(a, b) and min(xs) < max(a, b):
                    beyond.append((min(xs), max(xs), z0, z1))
            continue
        for g in getattr(cut, "geoms", [cut]):
            if g.length < 0.05:
                continue
            s0, s1 = sorted(p[k] for p in g.coords)
            ax.add_patch(MplPoly([(s0, z0), (s1, z0), (s1, z1), (s0, z1)], closed=True, fc="0.85", ec="black", lw=0.6))
            ax.add_patch(MplPoly([(s0, z0), (s1, z0), (s1, z0 + 0.3), (s0, z0 + 0.3)], closed=True, fc="black", lw=0))
            msp.add_lwpolyline([(s0, z0), (s1, z0), (s1, z1), (s0, z1)], close=True, dxfattribs={"layer": "CUT"})
    for s0, s1, z0, z1 in beyond:
        ax.add_patch(MplPoly([(s0, z0), (s1, z0), (s1, z1), (s0, z1)], closed=True, fill=False, ec="0.65", lw=0.4))
        msp.add_lwpolyline([(s0, z0), (s1, z0), (s1, z1), (s0, z1)], close=True, dxfattribs={"layer": "BEYOND"})
    ax.plot([min(a, b), max(a, b)], [0, 0], color="green", lw=1.2)
    msp.add_line((min(a, b), 0), (max(a, b), 0), dxfattribs={"layer": "GROUND"})
    where = f"y = {pos:g}, x {a:g} → {b:g}" if axis == "x" else f"x = {pos:g}, y {a:g} → {b:g}"
    _finish(ax, fig, f"Section {name} ({where}); grey = cut, light = beyond", out / f"section_{name}", doc)


def _finish(ax, fig, title, stem, doc):
    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("m (local survey frame)")
    ax.set_ylabel("m above site GF (267.70 m a.s.l.)")
    ax.grid(color="0.92", lw=0.4)
    fig.tight_layout()
    fig.savefig(stem.with_suffix(".png"), dpi=150)
    plt.close(fig)
    doc.saveas(stem.with_suffix(".dxf"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scheme")
    ap.add_argument("--out")
    ap.add_argument("--section", action="append", default=None,
                    help="name:axis=from,to:position — axis x = cut along x at y=position (repeatable)")
    a = ap.parse_args()
    d = Path(a.scheme)
    design = load(d / "params.yaml")
    out = Path(a.out) if a.out else ROOT / "05_drawings" / d.name / str(date.today())
    out.mkdir(parents=True, exist_ok=True)
    for v in VIEWS:
        elevation(design, v, out)
    secs = a.section or DEFAULT_SECTIONS
    for spec in secs:
        name, rng, pos = spec.split(":")
        axis, ab = rng.split("=")
        s0, s1 = map(float, ab.split(","))
        section(design, name, axis, s0, s1, float(pos.split("=")[1]), out)
    files = sorted(p.name for p in out.iterdir() if p.suffix == ".png")
    (out / "index.md").write_text(
        f"# {d.name} — elevations and sections ({out.name})\n\nGenerated by `tools/sections.py {a.scheme}` from "
        f"`{d.name}/params.yaml` — do not edit; rebuild instead. DXF (metres, local survey frame) next to each PNG.\n\n"
        + "\n".join(f"- [{f}]({f})" for f in files) + "\n")
    print(f"wrote {len(files)} drawings to {out}")


if __name__ == "__main__":
    main()
