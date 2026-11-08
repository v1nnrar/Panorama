"""Metrics, compliance checks, area schedule and 2D drawings from a design dict."""
from __future__ import annotations

import json
from pathlib import Path

import ezdxf
import pandas as pd
import yaml
from ezdxf.addons.drawing import matplotlib as ezmpl
from shapely.geometry import Polygon

from .build_ifc import _window_positions


def metrics(design: dict) -> dict:
    t = design["exterior_wall"]
    st = design["storeys"]
    above = [s for s in st if s["elevation"] >= 0]
    footprint = Polygon(st[0]["footprint"])
    gfa = sum(Polygon(s["footprint"]).area for s in above)
    nfa = sum(Polygon(s["footprint"]).buffer(-t, join_style="mitre").area for s in above)
    m = {
        "storeys_above_ground": len(above),
        "height_top_of_roof_m": round(design["top_of_slab"] + design["slab_thickness"], 2),
        "height_top_of_parapet_m": round(design["top_of_slab"] + design["slab_thickness"]
                                         + design["roof"].get("parapet", 0), 2),
        "footprint_area_m2": round(footprint.area, 1),
        "gfa_m2": round(gfa, 1),
        "net_floor_area_m2": round(nfa, 1),
        "rooms": sum(int(s.get("rooms") or 0) for s in st),
    }
    site = design["site"]["boundary"]
    if site:
        sp = Polygon(site)
        m.update({
            "site_area_m2": round(sp.area, 1),
            "built_up_ratio": round(footprint.area / sp.area, 3),
            "plot_ratio_far": round(gfa / sp.area, 3),
            "green_ratio_max": round(1 - footprint.area / sp.area, 3),
            "min_setback_m": round(min(sp.exterior.distance(Polygon(s["footprint"])) for s in st), 2),
        })
    return m


def check(m: dict, rules_path: str | Path | None) -> list[dict]:
    if not rules_path or not Path(rules_path).exists():
        return []
    rules = yaml.safe_load(Path(rules_path).read_text()).get("rules", [])
    results = []
    for r in rules:
        val = m.get(r["metric"])
        if val is None:
            status = "N/A"
        elif "max" in r:
            status = "PASS" if val <= r["max"] else "FAIL"
        elif "min" in r:
            status = "PASS" if val >= r["min"] else "FAIL"
        else:
            status = "INFO"
        limit = f"≤ {r['max']}" if "max" in r else f"≥ {r['min']}" if "min" in r else ""
        results.append({**r, "value": val, "limit": limit, "status": status})
    return results


def report(design, m, results, out_dir: Path):
    lines = [f"# {design['name']} — metrics & compliance", "", f"Source: `{Path(design['source']).name}`", "",
             "## Metrics", "", "| Metric | Value |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in m.items()]
    if results:
        lines += ["", "## Compliance", "", "| Rule | Limit | Value | Status | Source |", "|---|---|---|---|---|"]
        icon = {"PASS": "✅ PASS", "FAIL": "❌ FAIL", "N/A": "⚪ N/A", "INFO": "ℹ️"}
        lines += [f"| {r['label']} | {r['limit']} | {r['value']} | {icon[r['status']]} | {r.get('source', '')} |"
                  for r in results]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n")
    (out_dir / "metrics.json").write_text(json.dumps({"metrics": m, "compliance": results}, indent=2,
                                                     ensure_ascii=False))


def schedule(design, out_dir: Path):
    t = design["exterior_wall"]
    rows = []
    for s in design["storeys"]:
        p = Polygon(s["footprint"])
        wins = 0
        if s["windows"]:
            fp = s["footprint"]
            for i, a in enumerate(fp):
                L = Polygon([a, fp[(i + 1) % len(fp)], a]).length / 2
                wins += len(_window_positions(L, s["windows"]))
        rows.append({"Storey": s["name"], "Use": s["use"], "Elevation (m)": s["elevation"],
                     "Height (m)": s["height"], "GFA (m²)": round(p.area, 1),
                     "Net floor area (m²)": round(p.buffer(-t, join_style="mitre").area, 1),
                     "Rooms": s.get("rooms") or 0, "Windows": wins})
    df = pd.DataFrame(rows)
    df.loc[len(df)] = {"Storey": "TOTAL", "GFA (m²)": df["GFA (m²)"].sum(),
                       "Net floor area (m²)": df["Net floor area (m²)"].sum(),
                       "Rooms": df["Rooms"].sum(), "Windows": df["Windows"].sum()}
    df.to_excel(out_dir / "area_schedule.xlsx", index=False)
    return df


def drawings(design, out_dir: Path):
    d_dir = out_dir / "drawings"
    d_dir.mkdir(parents=True, exist_ok=True)
    t = design["exterior_wall"]
    site, setback = design["site"]["boundary"], design["site"].get("setback")
    seen, files = set(), []
    for s in design["storeys"]:
        key = (tuple(s["footprint"]), json.dumps(s["windows"], sort_keys=True), s["use"])
        if key in seen:  # typical floors: draw once
            continue
        seen.add(key)
        doc = ezdxf.new("R2018", setup=True)
        doc.units = ezdxf.units.M
        for name, col in (("SITE", 3), ("SETBACK", 1), ("WALL", 7), ("WINDOW", 5), ("TEXT", 250)):
            doc.layers.add(name, color=col)
        msp = doc.modelspace()
        if site:
            msp.add_lwpolyline(site, close=True, dxfattribs={"layer": "SITE"})
            if setback:
                inset = Polygon(site).buffer(-setback, join_style="mitre")
                msp.add_lwpolyline(list(inset.exterior.coords), close=True,
                                   dxfattribs={"layer": "SETBACK", "linetype": "DASHED"})
        outer = Polygon(s["footprint"])
        inner = outer.buffer(-t, join_style="mitre")
        msp.add_lwpolyline(s["footprint"], close=True, dxfattribs={"layer": "WALL", "lineweight": 50})
        msp.add_lwpolyline(list(inner.exterior.coords), close=True, dxfattribs={"layer": "WALL"})
        if s["windows"]:
            fp = s["footprint"]
            for i, a in enumerate(fp):
                b = fp[(i + 1) % len(fp)]
                L = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
                ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                nx, ny = -uy, ux
                for dd in _window_positions(L, s["windows"]):
                    for c in (dd - s["windows"]["width"] / 2, dd + s["windows"]["width"] / 2):
                        p0 = (a[0] + ux * c, a[1] + uy * c)
                        msp.add_line(p0, (p0[0] + nx * t, p0[1] + ny * t), dxfattribs={"layer": "WINDOW"})
                    q0 = (a[0] + ux * (dd - s["windows"]["width"] / 2) + nx * t / 2,
                          a[1] + uy * (dd - s["windows"]["width"] / 2) + ny * t / 2)
                    msp.add_line(q0, (q0[0] + ux * s["windows"]["width"], q0[1] + uy * s["windows"]["width"]),
                                 dxfattribs={"layer": "WINDOW"})
        c = inner.centroid
        msp.add_text(f"{s['name']} - {s['use']}  NFA {inner.area:.0f} m2", height=1.0,
                     dxfattribs={"layer": "TEXT"}).set_placement((c.x, c.y),
                                                                  align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        stem = d_dir / f"plan_{s['name']}"
        doc.saveas(f"{stem}.dxf")
        ezmpl.qsave(msp, f"{stem}.png", bg="#FFFFFF", dpi=200)
        files.append(f"{stem}.dxf")
    return files
