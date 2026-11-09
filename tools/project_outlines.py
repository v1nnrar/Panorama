#!/usr/bin/env python
"""Draw every building's model outline (roof edge, base, corner verticals) through each matched camera onto the
client render, so heights, positions and plan shapes can be checked building by building.

Camera model = Blender's: sensor 36 mm on the larger image side (sensor_fit AUTO), shift in units of the larger
side, camera aimed at `target` with no roll. Writes <scheme>/overlays/outline_<camera>.jpg.

Usage: .venv/bin/python tools/project_outlines.py 03_existing [--on-model]   (--on-model: draw on our render instead)
"""
import re
import sys
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline.params import load  # noqa: E402

COLORS = {"A": (255, 40, 40), "A0": (255, 160, 0), "B": (40, 120, 255), "B2": (0, 200, 255), "B3": (150, 90, 255),
          "C1": (255, 0, 200), "C2": (255, 120, 220), "D": (0, 220, 60), "E": (255, 255, 0)}


class Cam:
    def __init__(self, c, W, H):
        self.W, self.H = W, H
        self.loc = np.array(c["location"], float)
        fw = np.array(c["target"], float) - self.loc
        self.fw = fw / np.linalg.norm(fw)
        r = np.cross(self.fw, [0, 0, 1.0])
        self.r = r / np.linalg.norm(r)
        self.u = np.cross(self.r, self.fw)
        self.S = max(W, H)
        self.f = c.get("lens", 35) / 36.0 * self.S
        self.sx, self.sy = c.get("shift_x", 0.0), c.get("shift_y", 0.0)

    def __call__(self, p):
        d = np.asarray(p, float) - self.loc
        z = d @ self.fw
        if z <= 0.5:
            return None
        return (self.W / 2 + self.f * (d @ self.r) / z - self.sx * self.S,
                self.H / 2 - self.f * (d @ self.u) / z + self.sy * self.S)


def outlines(design):
    out = []
    for b in design["buildings"]:
        if not b["storeys"] or b["id"] == "U":
            continue
        st = b["storeys"]
        top = st[-1]
        z_roof = b["top_of_slab"] + b["slab_thickness"] + b["roof"].get("parapet", 0)
        out.append((b["id"], st[0]["footprint"], max(st[0]["elevation"], 0.0), top["footprint"], z_roof))
    return out


def context_blocks(design, radius=330.0):
    """Surrounding buildings (OSM/archiMap footprints + heights) near the site, minus excluded ones."""
    import json
    from shapely.geometry import Polygon
    ctx = design["site"].get("context")
    if not ctx:
        return []
    ex = [Polygon(r) for r in design["site"].get("context_exclude", [])]
    out = []
    for b in json.loads(Path(ctx).read_text())["buildings"]:
        P = Polygon(b["poly"])
        c = P.centroid
        if abs(c.x - 30) > radius or abs(c.y + 20) > radius or any(P.intersects(e) for e in ex):
            continue
        out.append((b["poly"], b.get("z0", 0.0), b.get("z0", 0.0) + b["h"]))
    return out


def draw(scheme, on_model=False, with_context=True):
    d = Path(scheme)
    design = load(d / "params.yaml")
    ctx = context_blocks(design) if with_context else []
    cams = yaml.safe_load((d / "params.yaml").read_text())["render"]["cameras"]
    for c in cams:
        m = re.search(r"like_render-?(\d{3})", c["name"])
        if not m:
            continue
        ref = d / "renders" / f"render-{m.group(1)}.jpg"
        img = Image.open(d / "model" / f"render_{c['name']}.png" if on_model else ref).convert("RGB")
        res = c.get("resolution", [1600, 1000])
        img = img.resize((res[0], res[1]))
        cam = Cam(c, *res)
        dr = ImageDraw.Draw(img)
        lw = max(2, res[0] // 500)
        for poly, z0, z1 in ctx:  # context: thin white roof + base outline
            for z in (z0, z1):
                ring = [cam((x, y, z)) for x, y in poly]
                for i in range(len(ring)):
                    a, b_ = ring[i], ring[(i + 1) % len(ring)]
                    if a and b_ and max(abs(a[0]), abs(a[1]), abs(b_[0]), abs(b_[1])) < 1e5:
                        dr.line([a, b_], fill=(255, 255, 255), width=1)
        for bid, base, z0, roof, zr in outlines(design):
            col = COLORS.get(bid, (255, 255, 255))
            ring_r = [cam((x, y, zr)) for x, y in roof]
            ring_b = [cam((x, y, z0)) for x, y in base]
            for ring in (ring_r, ring_b):
                for i in range(len(ring)):
                    a, b_ = ring[i], ring[(i + 1) % len(ring)]
                    if a and b_:
                        dr.line([a, b_], fill=col, width=lw)
            for x, y in roof:  # verticals at roof corners down to base level
                a, b_ = cam((x, y, zr)), cam((x, y, z0))
                if a and b_:
                    dr.line([a, b_], fill=col, width=max(1, lw // 2))
            pts = [p for p in ring_r if p and 0 <= p[0] < res[0] and 0 <= p[1] < res[1]]
            if pts:
                p = min(pts, key=lambda q: q[1])
                dr.text((p[0] + 4, p[1] - 14), bid, fill=col)
        out = d / "overlays" / f"outline_{c['name']}{'_model' if on_model else ''}.jpg"
        img.save(out, quality=88)
        print("wrote", out)


if __name__ == "__main__":
    draw(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "03_existing",
         "--on-model" in sys.argv)
