"""Load and expand a scheme parameter file (YAML) into a normalised design dict.

All dimensions are in metres, coordinates in a local site grid (x east, y north).
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

DEFAULTS = {
    "slab_thickness": 0.30,
    "exterior_wall": 0.35,
    "windows": {"width": 1.6, "height": 1.8, "sill": 0.9, "spacing": 3.6, "edge_margin": 1.2},
    "roof": {"parapet": 1.1},
}


def _merge(base: dict, over: dict | None) -> dict:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def ccw(points) -> list[tuple[float, float]]:
    poly = orient(Polygon(points), sign=1.0)
    return [tuple(map(float, p)) for p in list(poly.exterior.coords)[:-1]]


def load(path: str | Path) -> dict:
    path = Path(path)
    raw = yaml.safe_load(path.read_text())
    b = raw["building"]
    defaults = _merge(DEFAULTS, {k: b[k] for k in DEFAULTS if k in b})

    storeys, z = [], float(b.get("ground_elevation", 0.0))
    for s in b["storeys"]:
        for i in range(int(s.get("count", 1))):
            name = s["name"] if s.get("count", 1) == 1 else f"{s['name']}{i + s.get('start', 1)}"
            storeys.append({
                "name": name,
                "elevation": z,
                "height": float(s["height"]),
                "use": s.get("use", ""),
                "footprint": ccw(s.get("footprint", b["footprint"])),
                "windows": None if s.get("windows") is False else _merge(defaults["windows"], s.get("windows")),
                "rooms": s.get("rooms"),
            })
            z += float(s["height"])

    site = raw.get("site", {})
    design = {
        "name": raw.get("name", path.stem),
        "source": str(path),
        "output_dir": str((path.parent / raw.get("output_dir", f"../out/{path.stem}")).resolve()),
        "site": {
            "boundary": ccw(site["boundary"]) if "boundary" in site else None,
            "setback": site.get("setback"),
        },
        "slab_thickness": defaults["slab_thickness"],
        "exterior_wall": defaults["exterior_wall"],
        "roof": defaults["roof"],
        "storeys": storeys,
        "top_of_slab": z,
        "materials": raw.get("materials", {}),
        "render": raw.get("render", {}),
    }
    return design
