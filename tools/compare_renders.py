#!/usr/bin/env python
"""Side-by-side and 50 % overlay images: client render vs our render from the matched camera.

Usage: .venv/bin/python tools/compare_renders.py 03_existing
Pairs are read from <scheme>/params.yaml cameras whose name contains `like_render00N`.
"""
import re
import sys
from pathlib import Path

import yaml
from PIL import Image, ImageDraw


def main(scheme_dir):
    d = Path(scheme_dir)
    cams = yaml.safe_load((d / "params.yaml").read_text())["render"]["cameras"]
    out = d / "overlays"
    out.mkdir(exist_ok=True)
    for c in cams:
        m = re.search(r"like_(render-?\d{3})", c["name"])
        if not m:
            continue
        ref = d / "renders" / (m.group(1).replace("render", "render-").replace("--", "-") + ".jpg")
        ours = d / "model" / f"render_{c['name']}.png"
        if not ref.exists() or not ours.exists():
            print("skip", c["name"])
            continue
        a = Image.open(ref).convert("RGB")
        b = Image.open(ours).convert("RGB")
        h = 700
        a = a.resize((round(a.width * h / a.height), h))
        b = b.resize((round(b.width * h / b.height), h))
        W = Image.new("RGB", (a.width + b.width + 20, h + 30), "white")
        W.paste(a, (0, 30))
        W.paste(b, (a.width + 20, 30))
        dr = ImageDraw.Draw(W)
        dr.text((8, 8), f"CLIENT {ref.name}", fill="black")
        dr.text((a.width + 28, 8), f"OUR MODEL — camera {c['name']}", fill="black")
        W.save(out / f"compare_{c['name']}.jpg", quality=88)
        blend = Image.blend(a.resize(b.size), b, 0.5)
        blend.save(out / f"overlay_{c['name']}.jpg", quality=85)
        print("wrote", out / f"compare_{c['name']}.jpg")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "03_existing")
