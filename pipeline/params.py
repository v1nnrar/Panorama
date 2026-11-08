"""Load and expand a scheme parameter file (YAML) into a normalised design dict.

All dimensions are in metres, coordinates in a local site grid (x east, y north).

A scheme has either one `building:` or a list of `buildings:`. Each building has a footprint and a list of
storey groups. Optional `height` on a building scales the typical (repeated) storeys so that the top of the
parapet hits that height exactly.
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


def _building(b: dict, scheme_defaults: dict) -> dict:
    d = _merge(scheme_defaults, {k: b[k] for k in DEFAULTS if k in b})
    groups = b["storeys"]
    if b.get("height"):  # fit repeated storeys to the target parapet height
        fixed = sum(float(g["height"]) * int(g.get("count", 1)) for g in groups if int(g.get("count", 1)) == 1)
        n_rep = sum(int(g["count"]) for g in groups if int(g.get("count", 1)) > 1)
        rest = float(b["height"]) - fixed - d["slab_thickness"] - d["roof"].get("parapet", 0)
        if n_rep:
            typ = rest / n_rep
            groups = [{**g, "height": round(typ, 4)} if int(g.get("count", 1)) > 1 else g for g in groups]

    storeys, z = [], float(b.get("ground_elevation", 0.0))
    prefix = b.get("id", "")
    for s in groups:
        n = int(s.get("count", 1))
        for i in range(n):
            label = s["name"] if n == 1 else f"{s['name']}{i + s.get('start', 1)}"
            storeys.append({
                "name": f"{prefix}-{label}" if prefix else label,
                "elevation": round(z, 4),
                "height": float(s["height"]),
                "use": s.get("use", b.get("use", "")),
                "footprint": ccw(s.get("footprint", b["footprint"])),
                "windows": None if s.get("windows", b.get("windows")) is False
                else _merge(d["windows"], s.get("windows") if isinstance(s.get("windows"), dict) else None),
                "rooms": s.get("rooms"),
            })
            z += float(s["height"])
    return {
        "id": prefix or b.get("name", "B"),
        "name": b.get("name", prefix),
        "use": b.get("use", ""),
        "slab_thickness": d["slab_thickness"],
        "exterior_wall": d["exterior_wall"],
        "roof": d["roof"],
        "storeys": storeys,
        "top_of_slab": round(z, 4),
        "target_height": b.get("height"),
        "notes": b.get("notes", ""),
    }


def load_site(site: dict, base: Path) -> dict:
    cbase = base
    if "file" in site:
        f = base / site["file"]
        cbase = f.parent
        site = {**yaml.safe_load(f.read_text()), **{k: v for k, v in site.items() if k != "file"}}
    parcels = [{"no": p.get("no"), "ring": ccw(p["ring"])} for p in site.get("parcels", [])]
    boundary = ccw(site["boundary"]) if "boundary" in site else None
    context = site.get("context")
    if context:
        context = str((cbase / context).resolve())
    return {"boundary": boundary, "parcels": parcels, "setback": site.get("setback"), "context": context,
            "origin": site.get("origin")}


def load(path: str | Path) -> dict:
    path = Path(path)
    raw = yaml.safe_load(path.read_text())
    scheme_defaults = _merge(DEFAULTS, {k: raw[k] for k in DEFAULTS if k in raw})
    blist = raw.get("buildings") or [raw["building"]]
    buildings = [_building(b, scheme_defaults) for b in blist]
    site = load_site(raw.get("site", {}), path.parent)
    return {
        "name": raw.get("name", path.stem),
        "source": str(path),
        "output_dir": str((path.parent / raw.get("output_dir", f"../out/{path.stem}")).resolve()),
        "site": site,
        "buildings": buildings,
        "materials": raw.get("materials", {}),
        "render": raw.get("render", {}),
    }
