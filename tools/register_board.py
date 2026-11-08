#!/usr/bin/env python
"""Register the client's top-view board photo onto the survey grid (similarity transform, least squares).

Control points: features visible on the board and on the ČÚZK orthophoto (00_site/survey/grid_ortho.jpg).
Result (8 roof-level points): scale ≈0.403 m/px, rotation ≈8.0°, RMS ≈2.4 m.

Limits: the board is a phone photo of a printed perspective render, so tall roofs lean outward
(roofs read ~1.2–1.3× too large) and the photo adds keystone. Use it for SIZES of the scheme buildings
(after scaling roofs by (H-h)/H, H≈420 m) and as a visual check — not for absolute positions of tall buildings.

Usage: .venv/bin/python tools/register_board.py   → 00_site/survey/board_fit.json + board_overlay.jpg
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "03_existing/renders/site_top_view_photo.png"
OUT = ROOT / "00_site/survey"
CONTROL = [  # board px, local plan xy (orthophoto / OSM), name
    ((316, 240), (57, 20), "3-wing building, W wing S end"),
    ((386, 240), (84, 26), "3-wing building, M wing S end"),
    ((456, 240), (113, 31), "3-wing building, E wing S end"),
    ((394, 263), (93, 16), "E office NW corner"),
    ((400, 420), (100, -48), "E office S tip"),
    ((28, 80), (-68, 66), "drum N roof garden centre"),
    ((12, 190), (-67, 27), "drum NE roof garden centre"),
    ((25, 290), (-54, -14), "drum SE roof garden centre"),
]


def fit():
    A = np.array([c[0] for c in CONTROL], float)
    A[:, 1] *= -1
    B = np.array([c[1] for c in CONTROL], float)
    ma, mb = A.mean(0), B.mean(0)
    A0, B0 = A - ma, B - mb
    U, S, Vt = np.linalg.svd(B0.T @ A0 / len(A))
    D = np.eye(2)
    if np.linalg.det(U @ Vt) < 0:
        D[1, 1] = -1
    R = U @ D @ Vt
    s = np.trace(np.diag(S) @ D) / ((A0 ** 2).sum() / len(A))
    t = mb - s * R @ ma
    res = np.linalg.norm((s * (R @ A.T)).T + t - B, axis=1)
    return s, R, t, res


def to_local(s, R, t, u, v):
    return s * R @ np.array([u, -v]) + t


if __name__ == "__main__":
    s, R, t, res = fit()
    rot = float(np.degrees(np.arctan2(R[1, 0], R[0, 0])))
    out = {"scale_m_per_px": float(s), "rotation_deg": rot, "R": R.tolist(), "t": t.tolist(),
           "rms_m": float(np.sqrt((res ** 2).mean())),
           "control_points": [{"name": c[2], "px": c[0], "local": c[1], "residual_m": round(float(e), 2)}
                              for c, e in zip(CONTROL, res)]}
    (OUT / "board_fit.json").write_text(json.dumps(out, indent=1))
    print(f"scale {s:.4f} m/px, rotation {rot:.2f}°, RMS {out['rms_m']:.2f} m")
    X0, X1, Y0, Y1, RES = -150.0, 210.0, -160.0, 200.0, 0.5
    W, H = int((X1 - X0) / RES), int((Y1 - Y0) / RES)
    gx, gy = np.meshgrid(X0 + (np.arange(W) + .5) * RES, Y1 - (np.arange(H) + .5) * RES)
    Q = (R.T @ np.stack([gx.ravel() - t[0], gy.ravel() - t[1]])) / s
    u, v = Q[0], -Q[1]
    b = np.asarray(Image.open(BOARD).convert("RGB"))
    ok = (u >= 0) & (u < b.shape[1] - 1) & (v >= 0) & (v < b.shape[0] - 1)
    img = np.zeros((H * W, 4), np.uint8)
    img[ok, :3] = b[v[ok].astype(int), u[ok].astype(int)]
    img[ok, 3] = 140
    o = Image.open(OUT / "ortho_local.png").convert("RGBA").resize((W, H))
    Image.alpha_composite(o, Image.fromarray(img.reshape(H, W, 4))).convert("RGB").save(OUT / "board_overlay.jpg", quality=88)
