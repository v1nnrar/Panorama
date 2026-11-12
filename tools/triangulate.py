#!/usr/bin/env python
"""Measure the client scheme's roof corners in a calibrated client image (precision task P3, single-view form).

For every building of a scheme, the model's roof outline (top storey footprint at top slab + parapet) is projected
through a CALIBRATED camera (tools/calibrate_camera.py --points), each corner is searched in the client image with the
sub-pixel corner detector (calibrate_camera.refine_corner) and back-projected to the roof plane. With one view the
roof height must be known: the error of the plan position is propagated from the pixel error (±1.5 px) and the roof
height uncertainty (default ±0.5 m, storey counts verified on the client images), giving a 1-σ error ellipse.

  detect:  .venv/bin/python tools/triangulate.py 03_existing aerial_S_like_render000 --detect out.json --tiles sheet.png
           (writes candidate corners; check the tiles by eye and set "ok": false on wrong ones)
  solve:   .venv/bin/python tools/triangulate.py 03_existing aerial_S_like_render000 --solve checked.json [--report md]
           (plan position per corner, shift vs. the model, error ellipse; summary per building)

Two calibrated views (P2) would allow true triangulation of height as well; until then the height is an input.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from calibrate_camera import grad_field, project, refine_corner, rot  # noqa: E402
from pipeline.params import load  # noqa: E402

PX_SIGMA = 1.5          # corner pick + calibration (render-000: 1.64 px RMS on the references)


def camera(scheme, name):
    c = next(c for c in yaml.safe_load((Path(scheme) / "params.yaml").read_text())["render"]["cameras"] if c["name"] == name)
    loc, tgt = np.array(c["location"], float), np.array(c["target"], float)
    v = tgt - loc
    return [*loc, math.atan2(v[1], v[0]), math.atan2(v[2], math.hypot(v[0], v[1])), 0.0, c.get("lens", 35)], c


def roofs(design):
    """(id, visible roof outline, its height). A diagrid stands `offset` m outside the facade and rises `above_roof`
    above the top slab, so for diagrid buildings the visible crown is the footprint offset outward (mitred)."""
    from shapely.geometry import Polygon
    for b in design["buildings"]:
        if b.get("below_ground"):
            continue
        s = b["storeys"][-1]
        top = s["elevation"] + s["height"]
        z = top + float((b.get("roof") or {}).get("parapet", 0) or 0)
        poly = [tuple(map(float, q)) for q in s["footprint"]]
        dg = next((r for r in b.get("facade", []) or [] if r.get("type") == "diagrid"), None)
        if dg:
            P = Polygon(poly).buffer(float(dg.get("offset", 0)), join_style=2)
            poly = [tuple(q) for q in P.exterior.coords[:-1]]
            if Polygon(poly).exterior.is_ccw != Polygon(s["footprint"]).exterior.is_ccw:
                poly = poly[::-1]
            z = top + float(dg.get("above_roof", 0))
        yield b["id"], poly, z


def backproject(p, uv, z, W, H):
    """Plan point where the pixel ray of uv meets the horizontal plane at height z."""
    x, y, zc, yaw, pitch, roll, lens = p
    fw, r, u = rot(yaw, pitch, roll)
    f = lens / 36.0 * max(W, H)
    d = fw + r * (uv[0] - W / 2) / f - u * (uv[1] - H / 2) / f
    t = (z - zc) / d[2]
    return np.array([x, y, zc]) + t * d


def plan_cov(p, uv, z, W, H, sz):
    """1-σ plan covariance from ±PX_SIGMA pixel noise and ±sz roof-height uncertainty (numerical Jacobian)."""
    J = np.zeros((2, 3))
    base = backproject(p, uv, z, W, H)[:2]
    for k, (du, dv, dz) in enumerate(((1, 0, 0), (0, 1, 0), (0, 0, 1))):
        J[:, k] = backproject(p, uv + np.array([du, dv]), z + dz, W, H)[:2] - base
    return J @ np.diag([PX_SIGMA ** 2, PX_SIGMA ** 2, sz ** 2]) @ J.T


def detect(a, p, img, design):
    W, H = img.size
    G = grad_field(img)
    out = []
    for bid, poly, z in roofs(design):
        if a.only and bid not in a.only.split(","):
            continue
        X = np.array([(*q, z) for q in poly])
        uv, zc = project(p, X, W, H)
        for k in range(len(poly)):
            q = uv[k]
            if zc[k] <= 1 or not (40 < q[0] < W - 40 and 40 < q[1] < H - 40):
                continue
            e1, e2 = uv[k - 1] - q, uv[(k + 1) % len(poly)] - q
            if min(np.linalg.norm(e1), np.linalg.norm(e2)) < 10:
                continue
            d1, d2 = e1 / np.linalg.norm(e1), e2 / np.linalg.norm(e2)
            if abs(d1 @ d2) > 0.94:
                continue
            L = int(min(16, 0.6 * min(np.linalg.norm(e1), np.linalg.norm(e2))))
            o, r, con = refine_corner(G, q, d1, d2, R=a.radius, L=L)
            out.append({"building": bid, "vertex": k, "model_xy": [round(v, 2) for v in poly[k]], "z": round(z, 2),
                        "model_px": [round(v, 1) for v in q], "px": [round(v, 2) for v in o], "response": round(r, 1),
                        "contrast": round(con, 1), "ok": bool(r > 40 and con > 2.0)})
    return out


def tiles(img, pts, path, h=22, sc=6):
    T = 2 * h * sc
    rows = math.ceil(len(pts) / 5)
    sheet = Image.new("RGB", (5 * (T + 8), rows * (T + 16)), "white")
    ds = ImageDraw.Draw(sheet)
    for j, q in enumerate(pts):
        o, m = q["px"], q["model_px"]
        u0, v0 = int(o[0]) - h, int(o[1]) - h
        t = img.crop((u0, v0, u0 + 2 * h, v0 + 2 * h)).resize((T, T), Image.NEAREST)
        dt = ImageDraw.Draw(t)
        for (x, y), col in ((o, (0, 255, 0)), (m, (255, 0, 0))):
            X, Y = (x - u0) * sc, (y - v0) * sc
            dt.ellipse((X - 6, Y - 6, X + 6, Y + 6), outline=col, width=2)
        X, Y = (j % 5) * (T + 8), (j // 5) * (T + 16)
        sheet.paste(t, (X, Y + 14))
        ds.text((X + 2, Y), f"{j}: {q['building']} v{q['vertex']} r{q['response']:.0f} c{q['contrast']:.1f}", fill="black")
    sheet.save(path)


def solve(a, p, W, H, pts):
    rows, per = [], {}
    for q in pts:
        if not q.get("ok"):
            continue
        z = q["z"] + q.get("dz", 0.0)
        xy = backproject(p, np.array(q["px"], float), z, W, H)[:2]
        C = plan_cov(p, np.array(q["px"], float), z, W, H, a.height_sigma)
        ev, evec = np.linalg.eigh(C)
        sh = xy - np.array(q["model_xy"])
        rows.append((q["building"], q["vertex"], xy, sh, math.sqrt(ev[-1]), math.sqrt(ev[0]),
                     math.degrees(math.atan2(evec[1, -1], evec[0, -1]))))
        per.setdefault(q["building"], []).append(sh)
    lines = ["| Building | vertex | measured x, y | shift vs model (m) | |shift| | 1-σ ellipse (m) |", "|---|---|---|---|---|---|"]
    for b, k, xy, sh, s1, s2, ang in rows:
        lines.append(f"| {b} | {k} | {xy[0]:.2f}, {xy[1]:.2f} | {sh[0]:+.2f}, {sh[1]:+.2f} | {np.hypot(*sh):.2f} | "
                     f"{s1:.2f} × {s2:.2f} @ {ang:.0f}° |")
    summ = ["| Building | corners | mean shift dx, dy (m) | max |shift| (m) | spread (m) |", "|---|---|---|---|---|"]
    for b, S in per.items():
        S = np.array(S)
        m = S.mean(0)
        spread = float(np.sqrt(np.mean(np.sum((S - m) ** 2, 1)))) if len(S) > 1 else float("nan")
        summ.append(f"| {b} | {len(S)} | {m[0]:+.2f}, {m[1]:+.2f} | {np.hypot(S[:, 0], S[:, 1]).max():.2f} | {spread:.2f} |")
    return "\n".join(summ), "\n".join(lines), per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scheme")
    ap.add_argument("camera")
    ap.add_argument("--image")
    ap.add_argument("--detect")
    ap.add_argument("--tiles")
    ap.add_argument("--solve")
    ap.add_argument("--report")
    ap.add_argument("--only", help="comma list of building ids")
    ap.add_argument("--radius", type=int, default=15)
    ap.add_argument("--height-sigma", dest="height_sigma", type=float, default=0.5)
    a = ap.parse_args()
    p, c = camera(a.scheme, a.camera)
    import re
    img_path = Path(a.image) if a.image else Path(a.scheme) / "renders" / f"render-{re.search(r'like_render-?(\d{3})', a.camera).group(1)}.jpg"
    img = Image.open(img_path).convert("RGB")
    design = load(Path(a.scheme) / "params.yaml")
    if a.detect:
        pts = detect(a, p, img, design)
        Path(a.detect).write_text(json.dumps(pts, indent=0))
        print(f"{len(pts)} candidate corners, {sum(q['ok'] for q in pts)} with a clear response → {a.detect}")
        if a.tiles:
            tiles(img, pts, a.tiles)
    if a.solve:
        summ, table, _ = solve(a, p, *img.size, json.loads(Path(a.solve).read_text()))
        print(summ)
        print(table)
        if a.report:
            Path(a.report).write_text(summ + "\n\n" + table + "\n")


if __name__ == "__main__":
    main()
