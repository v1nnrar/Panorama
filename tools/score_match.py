#!/usr/bin/env python
"""Score how well our renders match the client's renders (higher = better, max 1.0).

For every camera named `*like_render00N` in <scheme>/params.yaml, compares <scheme>/model/render_<cam>.png with
<scheme>/renders/render-00N.jpg: both are resized to the client image's aspect at 480 px wide, converted to
blurred edge maps, and compared with normalised cross-correlation. Edges ignore colour and lighting, so the
score mostly measures silhouettes, storey lines and camera alignment.

Usage: .venv/bin/python tools/score_match.py 03_existing [--json out.json]
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import gaussian_filter

W = 480


def edges(im):
    g = np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(1.5)), float)
    gx, gy = np.zeros_like(g), np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1] = g[2:] - g[:-2]
    e = gaussian_filter(np.hypot(gx, gy), 3)
    return (e - e.mean()) / (e.std() + 1e-9)


def score_pair(ref_path, ours_path):
    ref = Image.open(ref_path).convert("RGB")
    h = round(W * ref.height / ref.width)
    a = edges(ref.resize((W, h), Image.LANCZOS))
    b = edges(Image.open(ours_path).convert("RGB").resize((W, h), Image.LANCZOS))
    return float((a * b).mean())


def main(scheme, out=None):
    d = Path(scheme)
    import yaml
    cams = yaml.safe_load((d / "params.yaml").read_text())["render"]["cameras"]
    scores = {}
    for c in cams:
        m = re.search(r"like_render-?(\d{3})", c["name"])
        if not m:
            continue
        ref, ours = d / "renders" / f"render-{m.group(1)}.jpg", d / "model" / f"render_{c['name']}.png"
        if ref.exists() and ours.exists():
            scores[c["name"]] = round(score_pair(ref, ours), 4)
    mean = round(sum(scores.values()) / len(scores), 4) if scores else None
    res = {"mean": mean, "per_camera": scores}
    print(json.dumps(res, indent=1))
    if out:
        Path(out).write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    args = sys.argv[1:]
    out = args[args.index("--json") + 1] if "--json" in args else None
    main(args[0] if args else "03_existing", out)
