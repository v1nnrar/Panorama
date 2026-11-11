#!/usr/bin/env python
"""Calibrate a client-render camera on surveyed reference buildings (accuracy step 2).

Projects the roof outlines of RÚIAN reference buildings at their DMP 1G roof height
(00_site/survey/reference_buildings.json, tools/reference_buildings.py) into the client image and minimises a robust
distance to the image's edges (Sobel magnitude → distance transform). Free parameters: camera position, yaw, pitch,
roll, focal length. Buildings on the plot are excluded (the client replaced them with the scheme render).

Point mode (--points, P1 of the ±1 m precision task): instead of the global edge fit, each reference roof outline is
matched to the image edges on its own (best 2-D shift within ±R px, chamfer distance), its shifted corners become
observed image points, and the camera is solved by least squares on those corners (outlier rejection at 3 px, repeated
with shrinking R). Correspondences are written next to --out (`*_points.json`) so they can be checked or hand-edited
and fed back with --manual <json> ([{"id": i, "vertex": k, "px": [u, v]}], these override automatic matches).

Usage: .venv/bin/python tools/calibrate_camera.py 03_existing aerial_S_like_render000 [--points] [--out cam.json] [--draw out.jpg]
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
sys.path.insert(0, str(ROOT / "tools"))
from survey_heights import roof_edge_z  # noqa: E402


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


def roof_refs(refs, plot, exclude=()):
    out = []
    for i, b in enumerate(refs):                       # id = index in reference_buildings.json (as drawn by refdraw)
        P = Polygon(b["poly"])
        if b["usable"] and P.distance(plot) >= 8.0 and i not in exclude and b["ruian"]["kod"] not in exclude:
            out.append((dict(b, id=i, roof_z=roof_edge_z(P)), P.simplify(0.3)))   # main roof plane, not p90
    return out


def grad_field(img):
    g = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(0.8)), float)
    return sobel(g, 1), sobel(g, 0)                       # d/du, d/dv


def refine_corner(G, c, d1, d2, R=12, L=14, ang=4):
    """Sub-pixel image corner near c: maximise the edge response (|gradient · normal|) along two half-edges leaving the
    corner in directions d1, d2 (projected roof edges, each rotated by up to ±ang°). Returns (uv, response, contrast)."""
    gu, gv = G
    t = np.linspace(1.5, L, 2 * L)

    def resp(cu, cv, e):
        n = np.array([-e[1], e[0]])
        q = np.array([cu, cv]) + t[:, None] * e
        g = map_coordinates(gu, [q[:, 1], q[:, 0]], order=1) * n[0] + map_coordinates(gv, [q[:, 1], q[:, 0]], order=1) * n[1]
        return np.abs(g.mean())                               # a straight edge has one sign of contrast along its length

    def rotd(e, a_):
        c_, s_ = math.cos(a_), math.sin(a_)
        return np.array([c_ * e[0] - s_ * e[1], s_ * e[0] + c_ * e[1]])

    best, allv = None, []
    angs = np.radians(np.arange(-ang, ang + 0.1, 2.0))
    E1, E2 = [rotd(d1, a_) for a_ in angs], [rotd(d2, a_) for a_ in angs]
    for du in np.arange(-R, R + 0.1, 1.0):
        for dv in np.arange(-R, R + 0.1, 1.0):
            cu, cv = c[0] + du, c[1] + dv
            r = max(resp(cu, cv, e) for e in E1) + max(resp(cu, cv, e) for e in E2)
            r = min(max(resp(cu, cv, e) for e in E1), max(resp(cu, cv, e) for e in E2)) * 2 if r else 0
            allv.append(r)
            if best is None or r > best[1]:
                best = ((cu, cv), r)
    (cu, cv), r0 = best
    for step in (0.5, 0.25):                                  # sub-pixel refinement
        for _ in range(4):
            cands = [(cu + du, cv + dv) for du in (-step, 0, step) for dv in (-step, 0, step)]
            sc = [min(max(resp(x, y, e) for e in E1), max(resp(x, y, e) for e in E2)) * 2 for x, y in cands]
            cu, cv = cands[int(np.argmax(sc))]
            r0 = max(sc)
    return np.array([cu, cv]), float(r0), float(r0 / (np.median(allv) + 1e-6))


FIX_ROLL = False                                              # --fix-roll: renders with level verticals (CG)


def solve_points(p0, X, uv_obs, W, H):
    def full(q):
        return np.array([*q[:5], 0.0, q[5]]) if FIX_ROLL else q

    def res(p):
        return (project(p, X, W, H)[0] - uv_obs).ravel()
    keep = np.ones(len(X), bool)
    q0 = np.delete(np.asarray(p0, float), 5) if FIX_ROLL else np.asarray(p0, float)
    for _ in range(3):
        sol = least_squares(lambda q: res(full(q)).reshape(-1, 2)[keep].ravel(), q0, loss="soft_l1", f_scale=2.0,
                            x_scale="jac")
        e = np.linalg.norm(res(full(sol.x)).reshape(-1, 2), axis=1)
        keep = e < max(3.0, 2.5 * np.median(e))
        q0 = sol.x
    return full(sol.x), e, keep


def point_mode(a, cam, img, D, W, H, plot, refs, p0):
    rr = roof_refs(refs, plot, exclude={int(x) for x in a.exclude.split(",") if x})
    allv = [np.array(Polygon(r["poly"]).exterior.coords) for r in refs]
    manual = json.loads(Path(a.manual).read_text()) if a.manual else []
    G = grad_field(img)
    p = np.array(p0, float)
    for R, it in (((12, 0), (5, 1)) if not a.only_manual else ((0, 0),)):
        X, obs, tags = [], [], []
        for b, P in ([] if a.only_manual else rr):
            cs = list(P.exterior.coords)[:-1]
            X3 = np.array([(*c, b["roof_z"]) for c in cs])
            uv, zc = project(p, X3, W, H)
            for k in range(len(cs)):
                q = uv[k]
                if zc[k] <= 1 or not (R + 20 < q[0] < W - R - 20 and R + 20 < q[1] < H - R - 20):
                    continue
                shared = any(np.min(np.hypot(*(v[:, :2] - cs[k]).T)) < 1.5 for j, v in enumerate(allv) if j != b["id"])
                if shared:
                    continue
                e1, e2 = uv[k - 1] - q, uv[(k + 1) % len(cs)] - q
                if min(np.linalg.norm(e1), np.linalg.norm(e2)) < 8:
                    continue
                d1, d2 = e1 / np.linalg.norm(e1), e2 / np.linalg.norm(e2)
                if abs(d1 @ d2) > 0.94:                       # nearly straight: no corner to see
                    continue
                L = int(min(16, 0.6 * min(np.linalg.norm(e1), np.linalg.norm(e2))))
                o, r, con = refine_corner(G, q, d1, d2, R=R, L=L)
                if r < a.min_resp or con < 2.0:
                    continue
                X.append(X3[k]); obs.append(o); tags.append((b["id"], k, round(r, 1)))
        for mp in manual:
            b = next(b for b, _ in rr if b["id"] == mp["id"])
            c = list(Polygon(b["poly"]).simplify(0.3).exterior.coords)[mp["vertex"]]   # b["roof_z"] = main roof plane
            X.append((*c, b["roof_z"])); obs.append(np.array(mp["px"], float)); tags.append((b["id"], mp["vertex"], "manual"))
        X, obs = np.array(X), np.array(obs)
        p, e, keep = solve_points(p, X, obs, W, H)
        nb = len({t[0] for t in tags})
        print(f"pass {it} (search ±{R} px): {nb} buildings, {len(X)} corners, kept {keep.sum()}, "
              f"RMS {np.sqrt(np.mean(e[keep] ** 2)):.2f} px (all {np.sqrt(np.mean(e ** 2)):.2f})")
    return p, X, obs, e, keep, tags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scheme")
    ap.add_argument("camera")
    ap.add_argument("--out")
    ap.add_argument("--draw")
    ap.add_argument("--points", action="store_true", help="per-building corner matching + point least squares")
    ap.add_argument("--manual", help="JSON list of hand-picked correspondences")
    ap.add_argument("--only-manual", dest="only_manual", action="store_true", help="solve on the --manual points only")
    ap.add_argument("--min-resp", dest="min_resp", type=float, default=40.0, help="minimum corner edge response")
    ap.add_argument("--fix-roll", dest="fix_roll", action="store_true", help="keep roll = 0 (level camera)")
    ap.add_argument("--init", help="JSON [x, y, z, yaw, pitch, roll, lens] start pose (camera not yet in params.yaml)")
    ap.add_argument("--image", help="client image (default: renders/render-NNN.jpg from the camera name)")
    ap.add_argument("--exclude", default="", help="comma list of RÚIAN ids to skip (changed since the survey)")
    a = ap.parse_args()
    global FIX_ROLL
    FIX_ROLL = a.fix_roll
    d = Path(a.scheme)
    cams = yaml.safe_load((d / "params.yaml").read_text())["render"]["cameras"]
    cam = next((c for c in cams if c["name"] == a.camera), None)
    ref_img = Path(a.image) if a.image else d / "renders" / f"render-{re.search(r'like_render-?(\d{3})', a.camera).group(1)}.jpg"
    img = Image.open(ref_img).convert("RGB")
    W, H = img.size
    D = edge_distance(img)
    from pipeline.params import load
    des = load(d / "params.yaml")
    plot = unary_union([Polygon(p["ring"]) for p in des["site"]["parcels"]])
    refs = json.loads((ROOT / "00_site/survey/reference_buildings.json").read_text())["buildings"]
    P = sample_outlines(refs, plot)
    if a.init:
        p0 = list(json.loads(Path(a.init).read_text()))
    else:
        loc, tgt = np.array(cam["location"], float), np.array(cam["target"], float)
        v = tgt - loc
        p0 = [*loc, math.atan2(v[1], v[0]), math.atan2(v[2], math.hypot(v[0], v[1])), 0.0, cam.get("lens", 35)]

    if a.points:
        p, X, obs, e, keep, tags = point_mode(a, cam, img, D, W, H, plot, refs, p0)
        x, y, z, yaw, pitch, roll, lens = p
        fw, _, _ = rot(yaw, pitch, roll)
        dist = float(np.linalg.norm(np.array([30, -20, 20]) - p[:3]))
        gsd = dist / (lens / 36.0 * max(W, H))
        rms = float(np.sqrt(np.mean(e[keep] ** 2)))
        print(f"camera ({x:.2f}, {y:.2f}, {z:.2f}) yaw {math.degrees(yaw):.3f}° pitch {math.degrees(pitch):.3f}° "
              f"roll {math.degrees(roll):.3f}° lens {lens:.3f} mm; site at {dist:.0f} m → {gsd:.3f} m/px; "
              f"RMS {rms:.2f} px ≈ {rms * gsd:.2f} m")
        res = {"location": [round(x, 2), round(y, 2), round(z, 2)], "target": [round(v, 2) for v in (p[:3] + fw * 100)],
               "lens": round(lens, 3), "roll_deg": round(math.degrees(roll), 3), "rms_px": round(rms, 2),
               "gsd_m_per_px": round(gsd, 3), "corners": int(keep.sum()), "buildings": len({t[0] for t in tags})}
        if a.out:
            Path(a.out).write_text(json.dumps(res, indent=1))
            Path(a.out).with_name(Path(a.out).stem + "_points.json").write_text(json.dumps(
                [{"id": t[0], "vertex": t[1], "match": t[2], "xyz": [round(v, 2) for v in X[i]],
                  "px": [round(v, 1) for v in obs[i]], "err_px": round(float(e[i]), 2), "kept": bool(keep[i])}
                 for i, t in enumerate(tags)], indent=0))
        if a.draw:
            uv, _ = project(p, X, W, H)
            dr = ImageDraw.Draw(img)
            for q, o, k in zip(uv, obs, keep):
                col = (0, 255, 0) if k else (255, 0, 0)
                dr.ellipse((o[0] - 3, o[1] - 3, o[0] + 3, o[1] + 3), outline=col)
                dr.line((o[0], o[1], q[0], q[1]), fill=(255, 255, 0))
            for b, P in roof_refs(refs, plot):
                cs = np.array([(*c, b["roof_z"]) for c in P.exterior.coords])
                dr.line([tuple(q) for q in project(p, cs, W, H)[0]], fill=(0, 200, 255))
            img.save(a.draw, quality=92)
        print(json.dumps(res))
        return

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
