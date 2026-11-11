#!/usr/bin/env python
"""Heights from the ČÚZK elevation models, in the local survey frame (z = 0 at the site's ground floor).

Sources (00_site/survey/dsm/, fetched from ags.cuzk.gov.cz/arcgis2 ImageServer exportImage, 1 m grid, S-JTSK):
  dmp1g.tif — DMP 1G digital SURFACE model (roofs, ±0.4 m on buildings per ČÚZK)
  dmr5g.tif — DMR 5G digital TERRAIN model (bare ground, ±0.18 m open terrain / ±0.3 m built-up per ČÚZK)

Site ground floor (z = 0) = median terrain inside the official plot, outside building footprints.

Usage: .venv/bin/python tools/survey_heights.py        # prints the reference heights of context buildings
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
DSM_DIR = ROOT / "00_site" / "survey" / "dsm"
LOCAL = "+proj=aeqd +lat_0=50.04919 +lon_0=14.43819 +datum=WGS84 +units=m"
_TR = Transformer.from_crs(LOCAL, "EPSG:5514", always_xy=True)


@lru_cache(None)
def _raster(name):
    meta = json.loads((DSM_DIR / "meta.json").read_text())[name]
    a = np.array(Image.open(DSM_DIR / f"{name}.tif"), dtype=np.float64)
    return a, meta["bbox_sjtsk"], meta["res_m"]


def sample(name, x, y):
    """Bilinear sample of raster `name` ('dmp1g' or 'dmr5g') at local coordinates (arrays allowed)."""
    a, (x0, y0, x1, y1), res = _raster(name)
    X, Y = _TR.transform(np.asarray(x, float), np.asarray(y, float))
    c = (X - x0) / res - 0.5
    r = (y1 - Y) / res - 0.5
    c0, r0 = np.floor(c).astype(int), np.floor(r).astype(int)
    fc, fr = c - c0, r - r0
    c0, r0 = np.clip(c0, 0, a.shape[1] - 2), np.clip(r0, 0, a.shape[0] - 2)
    return (a[r0, c0] * (1 - fc) * (1 - fr) + a[r0, c0 + 1] * fc * (1 - fr)
            + a[r0 + 1, c0] * (1 - fc) * fr + a[r0 + 1, c0 + 1] * fc * fr)


def grid_in(poly, step=1.0):
    x0, y0, x1, y1 = poly.bounds
    xs, ys = np.meshgrid(np.arange(x0 + step / 2, x1, step), np.arange(y0 + step / 2, y1, step))
    from shapely import contains_xy
    m = contains_xy(poly, xs, ys)
    return xs[m], ys[m]


@lru_cache(None)
def site_ground():
    """Absolute elevation (m a.s.l.) of z = 0: median terrain on the plot outside today's buildings."""
    sys.path.insert(0, str(ROOT))
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    from pipeline.params import load
    d = load(ROOT / "03_existing" / "params.yaml")
    plot = unary_union([Polygon(p["ring"]) for p in d["site"]["parcels"]])
    xs, ys = grid_in(plot, 2.0)
    dsm, dtm = sample("dmp1g", xs, ys), sample("dmr5g", xs, ys)
    open_ground = (dsm - dtm) < 1.0                       # not under today's buildings / trees
    return float(np.median(dtm[open_ground]))


def roof_and_base(poly, roof_pct=90, inset=1.5):
    """(base z, roof z) of an existing building polygon relative to the site GF: terrain just outside the walls,
    a high percentile of the surface model inside (inset to avoid edges)."""
    inner = poly.buffer(-inset)
    if inner.is_empty:
        inner = poly
    xs, ys = grid_in(inner, 1.0)
    ring = poly.buffer(4.0).difference(poly.buffer(1.0))
    bx, by = grid_in(ring, 1.0)
    g0 = site_ground()
    base = float(np.median(sample("dmr5g", bx, by))) - g0 if len(bx) else 0.0
    roof = float(np.percentile(sample("dmp1g", xs, ys), roof_pct)) - g0 if len(xs) else float("nan")
    return round(base, 2), round(roof, 2)


if __name__ == "__main__":
    from shapely.geometry import Polygon
    ctx = json.loads((ROOT / "00_site" / "context.json").read_text())["buildings"]
    print(f"site GF = {site_ground():.2f} m a.s.l.")
    print("centroid        OSM h | DSM base  DSM roof  roof−base")
    for c in ctx:
        P = Polygon(c["poly"]).buffer(0)
        q = P.centroid
        if abs(q.x - 30) > 260 or abs(q.y + 20) > 260 or P.area < 80:
            continue
        b, r = roof_and_base(P)
        if abs((r - b) - c["h"]) > 3 or c["h"] > 30:
            print(f"({q.x:6.1f},{q.y:6.1f})  {c['h']:6.1f} | {b:7.2f}  {r:8.2f}  {r - b:8.2f}")
