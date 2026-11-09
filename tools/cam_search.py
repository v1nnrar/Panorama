#!/usr/bin/env python
"""Tune one matched camera by coordinate descent on the match score (tools/score_match.py).

Opens <scheme>/model/model.blend (build it first), renders the camera with Workbench at 50 % for each candidate
and keeps the best. Prints the best camera as a params.yaml line; does NOT edit params.yaml.
Each render takes ~8-10 s, one sweep = 2 renders per free parameter.

Usage: .venv/bin/python tools/cam_search.py 03_existing <camera_name> [--sweeps 3] [--fix z,shift_y]
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from score_match import score_pair  # noqa: E402

# parameter name -> (initial step, minimum step)
STEPS = {"x": (8.0, 1.0), "y": (8.0, 1.0), "z": (0.5, 0.25), "tx": (6.0, 0.75), "ty": (6.0, 0.75),
         "tz": (6.0, 0.75), "lens": (2.0, 0.5), "shift_y": (0.05, 0.01)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scheme")
    ap.add_argument("camera")
    ap.add_argument("--sweeps", type=int, default=3)
    ap.add_argument("--fix", default="z", help="comma list of parameters to keep fixed")
    a = ap.parse_args()

    import bpy
    from mathutils import Vector

    d = Path(a.scheme)
    cams = yaml.safe_load((d / "params.yaml").read_text())["render"]["cameras"]
    c = next(c for c in cams if c["name"] == a.camera)
    ref = d / "renders" / f"render-{re.search(r'like_render-?(\d{3})', a.camera).group(1)}.jpg"
    bpy.ops.wm.open_mainfile(filepath=str(d / "model" / "model.blend"))
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type = "STUDIO", "MATERIAL"
    sh.show_shadows = sh.show_cavity = True
    sh.background_type = "WORLD"
    sc.view_settings.view_transform = "AgX"
    for o in bpy.data.objects:  # buildings this client render omits (camera `hide:` list)
        if any(o.name.startswith(i + "-") or o.name.startswith(i + " ") for i in c.get("hide", [])):
            o.hide_render = True
    cam = bpy.data.objects[a.camera]
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = c.get("resolution", [1600, 1000])
    sc.render.resolution_percentage = 50
    out = str(Path(tempfile.mkdtemp()) / "cs.png")

    p = {"x": c["location"][0], "y": c["location"][1], "z": c["location"][2], "tx": c["target"][0],
         "ty": c["target"][1], "tz": c["target"][2], "lens": c.get("lens", 35), "shift_y": c.get("shift_y", 0.0)}
    fixed = set(filter(None, a.fix.split(",")))
    cache = {}

    def score(q):
        key = tuple(round(q[k], 4) for k in STEPS)
        if key not in cache:
            cam.location = Vector((q["x"], q["y"], q["z"]))
            cam.data.lens, cam.data.shift_y = q["lens"], q["shift_y"]
            cam.rotation_euler = (Vector((q["tx"], q["ty"], q["tz"])) - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = out
            bpy.ops.render.render(write_still=True)
            cache[key] = score_pair(ref, out)
        return cache[key]

    best = score(p)
    print(f"start {best:.4f}", flush=True)
    step = {k: v[0] for k, v in STEPS.items()}
    for sweep in range(a.sweeps):
        for k in STEPS:
            if k in fixed:
                continue
            improved = True
            while improved:
                improved = False
                for sgn in (1, -1):
                    q = dict(p, **{k: p[k] + sgn * step[k]})
                    s = score(q)
                    if s > best + 1e-4:
                        p, best, improved = q, s, True
                        print(f"sweep {sweep} {k}={q[k]:.3f} -> {s:.4f}", flush=True)
                        break
            step[k] = max(STEPS[k][1], step[k] / 2)
    r = lambda v: round(v, 2)  # noqa: E731
    line = {"name": a.camera, "location": [r(p["x"]), r(p["y"]), r(p["z"])],
            "target": [r(p["tx"]), r(p["ty"]), r(p["tz"])], "lens": r(p["lens"])}
    if abs(p["shift_y"]) > 1e-6:
        line["shift_y"] = round(p["shift_y"], 3)
    line["resolution"] = c.get("resolution", [1600, 1000])
    if c.get("hide"):
        line["hide"] = c["hide"]
    print(f"BEST {best:.4f} renders={len(cache)}")
    print("RESULT " + json.dumps(line))


if __name__ == "__main__":
    main()
