#!/usr/bin/env python
"""Site survey: georeferenced grid cross-referenced with ČÚZK orthophoto + cadastral map.

Frame (same as psg-website): azimuthal equidistant tangent plane at Milevská 7
(50.04919 N, 14.43819 E), metres, x = east, y = true north. Verified against 254 official parcels:
mean 0.34 m, max 0.84 m (00_site/survey/frame_check.json).

Steps:
  1. fetch  — ČÚZK WMS orthophoto + cadastral map (EPSG:5514), warped onto the local north-up grid (0.2 m/px)
  2. parcels — official parcel polygons (INSPIRE CP WFS) → local frame; plot = parcels listed in site.yaml
  3. sheets — grid sheets (10 m minor / 50 m major, lettered columns + numbered rows) over ortho / cadastre,
              control-point table (local, S-JTSK, WGS84), DXF with grid + parcels + footprints

Usage: .venv/bin/python tools/site_survey.py [fetch|parcels|sheets|all]
"""
from __future__ import annotations

import io
import json
import re
import string
import sys
import urllib.request
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFont
from pyproj import CRS, Transformer
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
SURVEY = ROOT / "00_site" / "survey"
RAW = SURVEY / "raw"
LOCAL = CRS.from_proj4("+proj=aeqd +lat_0=50.04919 +lon_0=14.43819 +datum=WGS84 +units=m +no_defs")
L2J = Transformer.from_crs(LOCAL, 5514, always_xy=True)
J2L = Transformer.from_crs(5514, LOCAL, always_xy=True)
L2W = Transformer.from_crs(LOCAL, 4326, always_xy=True)

# survey window in the local frame (metres) and resolution
X0, X1, Y0, Y1, RES = -150.0, 210.0, -160.0, 200.0, 0.2
GRID_MINOR, GRID_MAJOR = 10, 50
UA = {"User-Agent": "panorama-site-survey/1.0"}

WMS = {
    "ortho": ("https://ags.cuzk.gov.cz/arcgis1/services/ORTOFOTO/MapServer/WMSServer", "0", "image/jpeg", "1.3.0"),
    "cadastre": ("https://services.cuzk.gov.cz/wms/local-km-wms.asp", "KN", "image/png", "1.3.0"),
}


def _get(url, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _jtsk_bbox(pad=20):
    xs, ys = np.meshgrid([X0 - pad, X1 + pad], [Y0 - pad, Y1 + pad])
    jx, jy = L2J.transform(xs.ravel(), ys.ravel())
    return min(jx), min(jy), max(jx), max(jy)


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    bx0, by0, bx1, by1 = _jtsk_bbox()
    w, h = int((bx1 - bx0) / RES), int((by1 - by0) / RES)
    for key, (url, layer, fmt, ver) in WMS.items():
        tiles, ts = [], 1000          # fetch in tiles (servers cap image size)
        img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        for ty in range(0, h, ts):
            for tx in range(0, w, ts):
                tw, th = min(ts, w - tx), min(ts, h - ty)
                ax0, ax1 = bx0 + tx * RES, bx0 + (tx + tw) * RES
                ay1, ay0 = by1 - ty * RES, by1 - (ty + th) * RES
                # WMS 1.3.0 + EPSG:5514 axis order is easting, northing for these services
                q = (f"{url}?service=WMS&version={ver}&request=GetMap&layers={layer}&styles=&crs=EPSG:5514"
                     f"&bbox={ax0},{ay0},{ax1},{ay1}&width={tw}&height={th}&format={fmt}&transparent=true")
                data = _get(q)
                try:
                    tile = Image.open(io.BytesIO(data)).convert("RGBA")
                except Exception:
                    raise RuntimeError(f"{key}: not an image: {data[:300]!r}")
                img.paste(tile, (tx, ty))
        img.save(RAW / f"{key}_jtsk.png")
        json.dump({"bbox": [bx0, by0, bx1, by1], "res": RES, "size": [w, h]}, open(RAW / f"{key}_jtsk.json", "w"))
        warp(key)
        print("fetched", key, w, h)


def warp(key):
    """Resample the EPSG:5514 raster onto the local north-up grid."""
    meta = json.load(open(RAW / f"{key}_jtsk.json"))
    src = np.asarray(Image.open(RAW / f"{key}_jtsk.png").convert("RGBA"))
    bx0, by0, bx1, by1 = meta["bbox"]
    W, H = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
    xs = X0 + (np.arange(W) + 0.5) * RES
    ys = Y1 - (np.arange(H) + 0.5) * RES
    gx, gy = np.meshgrid(xs, ys)
    jx, jy = L2J.transform(gx.ravel(), gy.ravel())
    col = ((np.asarray(jx) - bx0) / meta["res"]).astype(int).clip(0, src.shape[1] - 1)
    row = ((by1 - np.asarray(jy)) / meta["res"]).astype(int).clip(0, src.shape[0] - 1)
    out = src[row, col].reshape(H, W, 4)
    Image.fromarray(out).save(SURVEY / f"{key}_local.png")


def to_px(x, y):
    return ((x - X0) / RES, (Y1 - y) / RES)


# ----------------------------------------------------------------------------------------------- parcels
def parcels():
    feats = json.load(open(RAW / "parcels_cuzk.json"))
    site = yaml.safe_load(open(ROOT / "00_site" / "site.yaml"))
    old = {p["no"]: p for p in site["parcels"]}
    psg_union = unary_union([Polygon(p["ring"]) for p in site["parcels"]])

    def loc(ring):
        x, y = J2L.transform([p[0] for p in ring], [p[1] for p in ring])
        return [[round(a, 3), round(b, 3)] for a, b in zip(x, y)]

    chosen = []
    for f in feats:
        P = Polygon(loc(f["ring"]))
        if not P.is_valid:
            P = P.buffer(0)
        inter = P.intersection(psg_union).area
        if inter > 0.5 * P.area:          # official parcel lies inside the PSG plot
            ring = list(orient(P, 1.0).exterior.coords)[:-1]
            chosen.append({"no": f["label"], "cadastral_area": f["zoning"], "ref": f["ref"],
                           "area_official_m2": f["area"], "area_geometry_m2": round(P.area, 1),
                           "ring": [[round(a, 3), round(b, 3)] for a, b in ring]})
    union = unary_union([Polygon(p["ring"]) for p in chosen])
    site["parcels"] = chosen
    site["source"] = ("ČÚZK INSPIRE cadastral parcels WFS (services.cuzk.gov.cz), fetched "
                      "for this project; geometry converted from S-JTSK (EPSG:5514) to the local frame")
    site["frame"] = {"proj4": LOCAL.to_proj4(), "check": "254 parcels vs PSG data: mean 0.34 m, max 0.84 m"}
    site["cadastral_area_total_m2"] = round(sum(p["area_official_m2"] for p in chosen), 1)
    site["union_area_m2"] = round(union.area, 1)
    (ROOT / "00_site" / "site.yaml").write_text(
        yaml.safe_dump(site, sort_keys=False, allow_unicode=True, default_flow_style=None, width=200))
    print(f"{len(chosen)} official parcels, cadastre total {site['cadastral_area_total_m2']} m², "
          f"union {site['union_area_m2']} m² (PSG union was {psg_union.area:.1f} m²)")
    for p in chosen:
        print(f"  {p['no']:>8} {p['cadastral_area']:<6} {p['area_official_m2']:>7.0f} m²")


# ----------------------------------------------------------------------------------------------- sheets
def _col_label(i):
    return string.ascii_uppercase[i] if i < 26 else string.ascii_uppercase[i // 26 - 1] + string.ascii_uppercase[i % 26]


def grid_axes():
    """Major grid axes: columns lettered west→east, rows numbered north→south."""
    cols = list(range(int(np.ceil(X0 / GRID_MAJOR)) * GRID_MAJOR, int(X1) + 1, GRID_MAJOR))
    rows = list(range(int(np.floor(Y1 / GRID_MAJOR)) * GRID_MAJOR, int(Y0) - 1, -GRID_MAJOR))
    return {(_col_label(i)): x for i, x in enumerate(cols)}, {str(i + 1): y for i, y in enumerate(rows)}


def _font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def sheet(base_key, footprints, out_name, title):
    base = Image.open(SURVEY / f"{base_key}_local.png").convert("RGBA")
    if base_key == "cadastre":
        bg = Image.new("RGBA", base.size, (255, 255, 255, 255))
        base = Image.alpha_composite(bg, base)
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    f_s, f_m = _font(22), _font(34)
    W, H = base.size
    # minor + major grid
    for x in range(int(np.ceil(X0 / GRID_MINOR)) * GRID_MINOR, int(X1) + 1, GRID_MINOR):
        px, _ = to_px(x, 0)
        major = x % GRID_MAJOR == 0
        d.line([(px, 0), (px, H)], fill=(255, 255, 0, 200) if major else (255, 255, 255, 90), width=3 if major else 1)
    for y in range(int(np.ceil(Y0 / GRID_MINOR)) * GRID_MINOR, int(Y1) + 1, GRID_MINOR):
        _, py = to_px(0, y)
        major = y % GRID_MAJOR == 0
        d.line([(0, py), (W, py)], fill=(255, 255, 0, 200) if major else (255, 255, 255, 90), width=3 if major else 1)
    cols, rows = grid_axes()
    for lab, x in cols.items():
        px, _ = to_px(x, 0)
        for yy in (8, H - 52):
            d.rectangle([px - 34, yy, px + 34, yy + 44], fill=(20, 20, 20, 220))
            d.text((px, yy + 22), lab, font=f_m, fill="yellow", anchor="mm")
        d.text((px + 6, 60), f"x={x:+d}", font=f_s, fill="yellow")
    for lab, y in rows.items():
        _, py = to_px(0, y)
        for xx in (8, W - 52):
            d.rectangle([xx, py - 22, xx + 44, py + 22], fill=(20, 20, 20, 220))
            d.text((xx + 22, py), lab, font=f_m, fill="yellow", anchor="mm")
        d.text((60, py + 6), f"y={y:+d}", font=f_s, fill="yellow")
    # official parcels (plot)
    site = yaml.safe_load(open(ROOT / "00_site" / "site.yaml"))
    for p in site["parcels"]:
        pts = [to_px(*q) for q in p["ring"]]
        d.polygon(pts, outline=(255, 0, 200, 255), fill=(255, 0, 200, 35), width=4)
        c = Polygon(p["ring"]).representative_point()
        d.text(to_px(c.x, c.y), p["no"], font=f_s, fill=(255, 0, 200, 255), anchor="mm")
    # footprints
    for name, ring in footprints:
        pts = [to_px(*q) for q in ring]
        d.polygon(pts, outline=(40, 120, 255, 255), width=4)
        c = Polygon(ring).representative_point()
        d.text(to_px(c.x, c.y), name, font=f_m, fill=(40, 120, 255, 255), anchor="mm", stroke_width=3,
               stroke_fill="white")
    # origin + north arrow + scale bar
    ox, oy = to_px(0, 0)
    d.ellipse([ox - 10, oy - 10, ox + 10, oy + 10], outline="red", width=4)
    d.text((ox + 14, oy + 14), "0,0 Milevská 7", font=f_s, fill="red")
    d.polygon([(W - 120, 120), (W - 100, 190), (W - 140, 190)], fill="white")
    d.text((W - 120, 210), "N", font=f_m, fill="white", anchor="mm")
    sx, sy = 120, H - 110
    d.rectangle([sx, sy, sx + 50 / RES, sy + 14], fill="white")
    d.text((sx, sy - 34), "50 m", font=f_m, fill="white")
    d.text((120, 100), title, font=f_m, fill="white", stroke_width=3, stroke_fill="black")
    out = Image.alpha_composite(base, ov).convert("RGB")
    out.save(SURVEY / f"{out_name}.jpg", quality=90)
    out.resize((W // 2, H // 2)).save(SURVEY / f"{out_name}_preview.jpg", quality=85)
    return SURVEY / f"{out_name}.jpg"


def control_points():
    site = yaml.safe_load(open(ROOT / "00_site" / "site.yaml"))
    union = unary_union([Polygon(p["ring"]) for p in site["parcels"]])
    hull = union.convex_hull.simplify(1.0)
    rows = []
    pts = [("O", (0.0, 0.0), "origin, Milevská 7 address point")]
    pts += [(f"S{i + 1}", c, "plot hull corner") for i, c in enumerate(list(hull.exterior.coords)[:-1])]
    cols, rws = grid_axes()
    for cl, x in cols.items():
        for rl, y in rws.items():
            if union.buffer(60).contains(Polygon([(x - .1, y - .1), (x + .1, y - .1), (x + .1, y + .1)])):
                pts.append((f"{cl}{rl}", (float(x), float(y)), "grid intersection"))
    for name, (x, y), note in pts:
        jx, jy = L2J.transform(x, y)
        lon, lat = L2W.transform(x, y)
        rows.append({"point": name, "x_local": round(x, 3), "y_local": round(y, 3), "Y_jtsk": round(jx, 3),
                     "X_jtsk": round(jy, 3), "lat": round(lat, 7), "lon": round(lon, 7), "note": note})
    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(SURVEY / "control_points.csv", index=False)
    md = ["| Point | x local | y local | S-JTSK E (Y) | S-JTSK N (X) | lat | lon | note |", "|---|---|---|---|---|---|---|---|"]
    md += [f"| {r['point']} | {r['x_local']} | {r['y_local']} | {r['Y_jtsk']} | {r['X_jtsk']} | {r['lat']} | {r['lon']} | {r['note']} |"
           for r in rows]
    return "\n".join(md)


def dxf(footprints):
    import ezdxf
    site = yaml.safe_load(open(ROOT / "00_site" / "site.yaml"))
    doc = ezdxf.new("R2018", setup=True)
    doc.units = ezdxf.units.M
    for n, c in (("GRID_MINOR", 8), ("GRID_MAJOR", 2), ("GRID_TEXT", 2), ("PARCEL_OFFICIAL", 6), ("PARCEL_TEXT", 6),
                 ("FOOTPRINT", 5), ("ORIGIN", 1)):
        doc.layers.add(n, color=c)
    msp = doc.modelspace()
    for x in range(int(np.ceil(X0 / GRID_MINOR)) * GRID_MINOR, int(X1) + 1, GRID_MINOR):
        msp.add_line((x, Y0), (x, Y1), dxfattribs={"layer": "GRID_MAJOR" if x % GRID_MAJOR == 0 else "GRID_MINOR"})
    for y in range(int(np.ceil(Y0 / GRID_MINOR)) * GRID_MINOR, int(Y1) + 1, GRID_MINOR):
        msp.add_line((X0, y), (X1, y), dxfattribs={"layer": "GRID_MAJOR" if y % GRID_MAJOR == 0 else "GRID_MINOR"})
    cols, rows = grid_axes()
    for lab, x in cols.items():
        msp.add_text(lab, height=4, dxfattribs={"layer": "GRID_TEXT"}).set_placement((x, Y1 + 4))
    for lab, y in rows.items():
        msp.add_text(lab, height=4, dxfattribs={"layer": "GRID_TEXT"}).set_placement((X0 - 8, y))
    for p in site["parcels"]:
        msp.add_lwpolyline(p["ring"], close=True, dxfattribs={"layer": "PARCEL_OFFICIAL"})
        c = Polygon(p["ring"]).representative_point()
        msp.add_text(p["no"], height=1.5, dxfattribs={"layer": "PARCEL_TEXT"}).set_placement((c.x, c.y))
    for name, ring in footprints:
        msp.add_lwpolyline(ring, close=True, dxfattribs={"layer": "FOOTPRINT"})
    msp.add_circle((0, 0), 1.0, dxfattribs={"layer": "ORIGIN"})
    doc.saveas(SURVEY / "site_survey_grid.dxf")


def existing_footprints():
    from pipeline import params
    d = params.load(ROOT / "03_existing" / "params.yaml")
    return [(b["id"], b["storeys"][0]["footprint"]) for b in d["buildings"] if not b.get("below_ground")]


def sheets():
    fps = existing_footprints()
    a = sheet("ortho", fps, "grid_ortho", "Survey grid on ČÚZK orthophoto — existing scheme footprints (blue), official parcels (magenta)")
    b = sheet("cadastre", fps, "grid_cadastre", "Survey grid on ČÚZK cadastral map")
    dxf(fps)
    md = control_points()
    (SURVEY / "control_points.md").write_text(md + "\n")
    print("sheets:", a, b)


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("fetch", "all"):
        fetch()
    if step in ("parcels", "all"):
        parcels()
    if step in ("sheets", "all"):
        sheets()
