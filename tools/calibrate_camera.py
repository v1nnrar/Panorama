#!/usr/bin/env python
"""Calibrate a client-render camera on surveyed reference buildings (accuracy step 2).

Projects the roof outlines of RÚIAN reference buildings at their DMP 1G roof height
(00_site/survey/reference_buildings.json, tools/reference_buildings.py) into the client image and minimises a robust
distance to the image's edges (Sobel magnitude → distance transform). Free parameters: camera position, yaw, pitch,
roll, focal length. Buildings on the plot are excluded (the client replaced them with the scheme render).

Usage: .venv/bin/python tools/calibrate_camera.py 03_existing aerial_S_like_render000 [--out cam.json] [--draw out.jpg]
Prints the residual in pixels and the ground sampling distance, i.e. the metres one pixel represents at the site.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import distance_transform_edt, map_coordinates, sobel
from scipy.optimize import least_squares
from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def rot(yaw, pitch, roll):
    fw = np.array([math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)])
    r = np.cross(fw, [0, 0, 1.0]); r /= np.linalg.norm(r)
    u = np.cross(r, fw)
    c, s = math.cos(roll), math.sin(roll)
    return fw, c * r + s * u, -s * r + c * u


def project(p, P, W, H):
    x, y, z, yaw, pitch, roll, lens = p
    fw, r, u = rot(yaw, pitch, roll)
    f = lens / 36.0 * max(W, H)
    d = P - np.array([x, y, z])
    zc = d @ fw
    return np.stack([W / 2 + f * (d @ r) / zc, H / 2 - f * (d @ u) / zc], 1), zc


def edge_distance(img):
    g = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(1.0)), float)
    mag = np.hypot(sobel(g, 0), sobel(g, 1))
    edges = mag > np.percentile(mag, 88)
    return distance_transform_edt(~edges)


def sample_outlines(refs, plot, step=1.0):
    pts = []
    for b in refs:
        P = Polygon(b["poly"])
        if not b["usable"] or P.distance(plot) < 8.0:
            continue
        ring = P.simplify(0.3).exterior
        n = max(4, int(ring.length / step))
        for k in range(n):
            q = ring.interpolate(k * ring.length / n)
            pts.append((q.x, q.y, b["roof_z"]))
    return np.array(pts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scheme")
    ap.add_argument("camera")
    ap.add_argument("--out")
    ap.add_argument("--draw")
    a = ap.parse_args()
    d = Path(a.scheme)
    cam = next(c for c in yaml.safe_load((d / "params.yaml").read_text())["render"]["cameras"] if c["name"] == a.camera)
    ref_img = d / "renders" / f"render-{re.search(r'like_render-?(\d{3})', a.camera).group(1)}.jpg"
    img = Image.open(ref_img).convert("RGB")
    W, H = img.size
    D = edge_distance(img)
    from pipeline.params import load
    des = load(d / "params.yaml")
    plot = unary_union([Polygon(p["ring"]) for p in des["site"]["parcels"]])
    refs = json.loads((ROOT / "00_site/survey/reference_buildings.json").read_text())["buildings"]
    P = sample_outlines(refs, plot)
    loc, tgt = np.array(cam["location"], float), np.array(cam["target"], float)
    v = tgt - loc
    p0 = [*loc, math.atan2(v[1], v[0]), math.atan2(v[2], math.hypot(v[0], v[1])), 0.0, cam.get("lens", 35)]

    uv0, zc0 = project(p0, P, W, H)
    keep = (zc0 > 1) & (uv0[:, 0] > 20) & (uv0[:, 0] < W - 20) & (uv0[:, 1] > 20) & (uv0[:, 1] < H - 20)
    P = P[keep]

    def resid(p):
        uv, zc = project(p, P, W, H)
        ok = (zc > 1) & (uv[:, 0] > 2) & (uv[:, 0] < W - 3) & (uv[:, 1] > 2) & (uv[:, 1] < H - 3)
        r = np.full(len(P), 15.0)          # off-image points get a constant (no gradient)
        r[ok] = map_coordinates(D, [uv[ok, 1], uv[ok, 0]], order=1)
        return r

    r0 = resid(p0)
    sol = least_squares(resid, p0, loss="soft_l1", f_scale=3.0, diff_step=1e-4, max_nfev=400)
    r1 = resid(sol.x)
    inl = r1 < 6
    x, y, z, yaw, pitch, roll, lens = sol.x
    fw, _, _ = rot(yaw, pitch, roll)
    dist = float(np.linalg.norm(np.array([30, -20, 20]) - sol.x[:3]))
    gsd = dist / (lens / 36.0 * max(W, H))
    print(f"points {len(P)}; median edge distance {np.median(r0):.2f} px → {np.median(r1):.2f} px "
          f"(inliers <6 px: {inl.mean():.0%}, inlier RMS {np.sqrt(np.mean(r1[inl] ** 2)):.2f} px)")
    print(f"camera ({x:.1f}, {y:.1f}, {z:.1f}) yaw {math.degrees(yaw):.2f}° pitch {math.degrees(pitch):.2f}° "
          f"roll {math.degrees(roll):.2f}° lens {lens:.2f} mm; site at {dist:.0f} m → {gsd:.2f} m per pixel")
    res = {"location": [round(x, 2), round(y, 2), round(z, 2)],
           "target": [round(v, 2) for v in (sol.x[:3] + fw * 100)], "lens": round(lens, 3), "roll_deg": round(math.degrees(roll), 3),
           "median_px": round(float(np.median(r1)), 2), "gsd_m_per_px": round(gsd, 3), "points": int(len(P))}
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=1))
    if a.draw:
        uv, zc = project(sol.x, P, W, H)
        dr = ImageDraw.Draw(img)
        for (u, v_), ok in zip(uv, r1 < 6):
            dr.point((u, v_), fill=(0, 255, 0) if ok else (255, 0, 0))
        img.save(a.draw, quality=90)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
