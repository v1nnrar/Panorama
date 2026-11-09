"""Metrics, compliance checks, area schedule and 2D drawings from a design dict."""
from __future__ import annotations

import json
from pathlib import Path

import ezdxf
import pandas as pd
import yaml
from ezdxf.addons.drawing import matplotlib as ezmpl
from shapely.geometry import Polygon
from shapely.ops import unary_union

from .build_ifc import _window_positions


def site_polygon(design):
    sd = design["site"]
    if sd["parcels"]:
        return unary_union([Polygon(p["ring"]) for p in sd["parcels"]])
    return Polygon(sd["boundary"]) if sd["boundary"] else None


def _nfa(fp, t):
    return Polygon(fp).buffer(-t, join_style="mitre").area


def building_metrics(b: dict) -> dict:
    above = [s for s in b["storeys"] if s["elevation"] >= 0]
    return {
        "id": b["id"], "name": b["name"], "use": b["use"],
        "storeys": len(above),
        "height_parapet_m": round(b["top_of_slab"] + b["slab_thickness"] + b["roof"].get("parapet", 0), 2),
        "target_height_m": b["target_height"],
        "footprint_m2": round(Polygon(b["storeys"][0]["footprint"]).area, 1),
        "gfa_m2": round(sum(Polygon(s["footprint"]).area for s in above), 1),
        "nfa_m2": round(sum(_nfa(s["footprint"], b["exterior_wall"]) for s in above), 1),
        "rooms": sum(int(s.get("rooms") or 0) for s in b["storeys"]),
    }


def metrics(design: dict) -> dict:
    per = [building_metrics(b) for b in design["buildings"]]
    ground = unary_union([Polygon(b["storeys"][0]["footprint"]) for b in design["buildings"]
                          if not b.get("below_ground")])
    m = {
        "buildings": len(per),
        "storeys_above_ground": max(p["storeys"] for p in per),
        "gfa_below_ground_m2": round(sum(Polygon(s["footprint"]).area for b in design["buildings"]
                                         for s in b["storeys"] if s["elevation"] < 0), 1),
        "height_top_of_parapet_m": max(p["height_parapet_m"] for p in per),
        "footprint_area_m2": round(ground.area, 1),
        "gfa_m2": round(sum(p["gfa_m2"] for p in per), 1),
        "net_floor_area_m2": round(sum(p["nfa_m2"] for p in per), 1),
        "rooms": sum(p["rooms"] for p in per),
    }
    sp = site_polygon(design)
    if sp is not None:
        m.update({
            "site_area_m2": round(sp.area, 1),
            "built_up_ratio": round(ground.area / sp.area, 3),
            "plot_ratio_far": round(m["gfa_m2"] / sp.area, 3),
            "unbuilt_ratio": round(1 - ground.intersection(sp).area / sp.area, 3),
            "footprint_outside_plot_m2": round(ground.difference(sp).area, 1),
        })
        if sp.geom_type == "Polygon":
            m["min_setback_m"] = round(min(sp.exterior.distance(Polygon(b["storeys"][0]["footprint"]))
                                           for b in design["buildings"]), 2)
    try:
        from . import psp
        m.update({k: v for k, v in psp.run_all(design, design.get("parking_zone", "02")).items()})
    except Exception as e:  # checks must never break a build
        m["psp_error"] = repr(e)
    m["per_building"] = per
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
             "## Site & totals", "", "| Metric | Value |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in m.items() if k != "per_building"]
    lines += ["", "## Buildings", "",
              "| ID | Name | Use | Storeys | Height (m) | Target (m) | Footprint (m²) | GFA (m²) | NFA (m²) |",
              "|---|---|---|---|---|---|---|---|---|"]
    lines += [f"| {p['id']} | {p['name']} | {p['use']} | {p['storeys']} | {p['height_parapet_m']} | "
              f"{p['target_height_m'] or ''} | {p['footprint_m2']} | {p['gfa_m2']} | {p['nfa_m2']} |"
              for p in m["per_building"]]
    if results:
        lines += ["", "## Compliance", "", "| Rule | Limit | Value | Status | Source |", "|---|---|---|---|---|"]
        icon = {"PASS": "✅ PASS", "FAIL": "❌ FAIL", "N/A": "⚪ N/A", "INFO": "ℹ️"}
        lines += [f"| {r['label']} | {r['limit']} | {r['value']} | {icon[r['status']]} | {r.get('source', '')} |"
                  for r in results]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n")
    (out_dir / "metrics.json").write_text(json.dumps({"metrics": m, "compliance": results}, indent=2,
                                                     ensure_ascii=False))


def _windows_on(fp, w):
    n = 0
    for i, a in enumerate(fp):
        b = fp[(i + 1) % len(fp)]
        n += len(_window_positions(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5, w))
    return n


def schedule(design, out_dir: Path):
    rows = []
    for b in design["buildings"]:
        for s in b["storeys"]:
            p = Polygon(s["footprint"])
            rows.append({"Building": b["id"], "Storey": s["name"], "Use": s["use"], "Elevation (m)": s["elevation"],
                         "Height (m)": round(s["height"], 3), "GFA (m²)": round(p.area, 1),
                         "Net floor area (m²)": round(_nfa(s["footprint"], b["exterior_wall"]), 1),
                         "Rooms": s.get("rooms") or 0,
                         "Windows": _windows_on(s["footprint"], s["windows"]) if s["windows"] else 0})
    df = pd.DataFrame(rows)
    summary = df.groupby("Building", sort=False).agg({"Storey": "count", "GFA (m²)": "sum",
                                                      "Net floor area (m²)": "sum", "Rooms": "sum"}).reset_index()
    summary.loc[len(summary)] = ["TOTAL", summary["Storey"].sum(), summary["GFA (m²)"].sum(),
                                 summary["Net floor area (m²)"].sum(), summary["Rooms"].sum()]
    with pd.ExcelWriter(out_dir / "area_schedule.xlsx") as xw:
        summary.rename(columns={"Storey": "Storeys"}).to_excel(xw, sheet_name="Summary", index=False)
        df.to_excel(xw, sheet_name="Storeys", index=False)
    return df


def _new_doc():
    doc = ezdxf.new("R2018", setup=True)
    doc.units = ezdxf.units.M
    for name, col in (("PARCEL", 6), ("SITE", 3), ("SETBACK", 1), ("WALL", 7), ("WINDOW", 5), ("TEXT", 250),
                      ("CONTEXT", 8), ("BUILDING", 5)):
        doc.layers.add(name, color=col)
    return doc


def _text(msp, s, xy, h=1.0):
    msp.add_text(s, height=h, dxfattribs={"layer": "TEXT"}).set_placement(
        xy, align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)


def _save(doc, stem):
    doc.saveas(f"{stem}.dxf")
    ezmpl.qsave(doc.modelspace(), f"{stem}.png", bg="#FFFFFF", dpi=200)
    return f"{stem}.dxf"


def _site_layers(msp, design):
    sd = design["site"]
    for p in sd["parcels"]:
        msp.add_lwpolyline(p["ring"], close=True, dxfattribs={"layer": "PARCEL"})
        if p["no"]:
            c = Polygon(p["ring"]).representative_point()
            _text(msp, p["no"], (c.x, c.y), 1.2)
    if sd["boundary"]:
        msp.add_lwpolyline(sd["boundary"], close=True, dxfattribs={"layer": "SITE"})
        if sd.get("setback"):
            inset = Polygon(sd["boundary"]).buffer(-sd["setback"], join_style="mitre")
            msp.add_lwpolyline(list(inset.exterior.coords), close=True,
                               dxfattribs={"layer": "SETBACK", "linetype": "DASHED"})


def _survey_grid(doc, msp, bounds, minor=10, major=50, margin=30):
    """Survey grid of the local frame (see 00_site/survey): 10 m lines, 50 m axes lettered W→E, numbered N→S.
    Axis labels match tools/site_survey.py (columns from x = -150, rows from y = +200)."""
    import string
    for n, c in (("GRID_MINOR", 9), ("GRID_MAJOR", 2), ("GRID_TEXT", 2)):
        if n not in doc.layers:
            doc.layers.add(n, color=c)
    x0, y0, x1, y1 = bounds
    x0, y0 = (int(x0 - margin) // minor) * minor, (int(y0 - margin) // minor) * minor
    x1, y1 = (int(x1 + margin) // minor + 1) * minor, (int(y1 + margin) // minor + 1) * minor
    for x in range(x0, x1 + 1, minor):
        msp.add_line((x, y0), (x, y1), dxfattribs={"layer": "GRID_MAJOR" if x % major == 0 else "GRID_MINOR"})
        if x % major == 0:
            lab = string.ascii_uppercase[(x + 150) // major]
            for yy in (y0 - 6, y1 + 2):
                _text(msp, lab, (x, yy + 2), 3.0)
            _text(msp, f"x={x:+d}", (x + 6, y1 - 3), 1.2)
    for y in range(y0, y1 + 1, minor):
        msp.add_line((x0, y), (x1, y), dxfattribs={"layer": "GRID_MAJOR" if y % major == 0 else "GRID_MINOR"})
        if y % major == 0:
            lab = str((200 - y) // major + 1)
            for xx in (x0 - 5, x1 + 5):
                _text(msp, lab, (xx, y), 3.0)
            _text(msp, f"y={y:+d}", (x0 + 6, y + 1.5), 1.2)


def drawings(design, out_dir: Path):
    d_dir = out_dir / "drawings"
    d_dir.mkdir(parents=True, exist_ok=True)
    files = []

    # Site plan: parcels, context footprints, building footprints with labels
    doc = _new_doc()
    msp = doc.modelspace()
    sp = site_polygon(design)
    if design["site"].get("context") and sp is not None:
        for c in json.loads(Path(design["site"]["context"]).read_text())["buildings"]:
            if Polygon(c["poly"]).distance(sp) < 120:
                msp.add_lwpolyline(c["poly"], close=True, dxfattribs={"layer": "CONTEXT"})
    _site_layers(msp, design)
    if sp is not None:
        _survey_grid(doc, msp, sp.bounds)
    for b in design["buildings"]:
        if b.get("below_ground"):
            continue
        fp = b["storeys"][0]["footprint"]
        msp.add_lwpolyline(fp, close=True, dxfattribs={"layer": "BUILDING", "lineweight": 50})
        c = Polygon(fp).representative_point()
        bm = building_metrics(b)
        _text(msp, f"{b['id']}  {bm['storeys']} fl / {bm['height_parapet_m']:.1f} m", (c.x, c.y), 1.6)
    files.append(_save(doc, d_dir / "site_plan"))

    # Floor plans: one per distinct storey type per building
    seen = set()
    for b in design["buildings"]:
        t = b["exterior_wall"]
        for s in b["storeys"]:
            key = (b["id"], tuple(s["footprint"]), json.dumps(s["windows"], sort_keys=True), s["use"])
            if key in seen:
                continue
            seen.add(key)
            doc = _new_doc()
            msp = doc.modelspace()
            fp = s["footprint"]
            inner = Polygon(fp).buffer(-t, join_style="mitre")
            msp.add_lwpolyline(fp, close=True, dxfattribs={"layer": "WALL", "lineweight": 50})
            msp.add_lwpolyline(list(inner.exterior.coords), close=True, dxfattribs={"layer": "WALL"})
            w = s["windows"]
            if w:
                for i, a in enumerate(fp):
                    bb = fp[(i + 1) % len(fp)]
                    L = ((bb[0] - a[0]) ** 2 + (bb[1] - a[1]) ** 2) ** 0.5
                    ux, uy = (bb[0] - a[0]) / L, (bb[1] - a[1]) / L
                    nx, ny = -uy, ux
                    for dd in _window_positions(L, w):
                        for c in (dd - w["width"] / 2, dd + w["width"] / 2):
                            p0 = (a[0] + ux * c, a[1] + uy * c)
                            msp.add_line(p0, (p0[0] + nx * t, p0[1] + ny * t), dxfattribs={"layer": "WINDOW"})
                        q0 = (a[0] + ux * (dd - w["width"] / 2) + nx * t / 2,
                              a[1] + uy * (dd - w["width"] / 2) + ny * t / 2)
                        msp.add_line(q0, (q0[0] + ux * w["width"], q0[1] + uy * w["width"]),
                                     dxfattribs={"layer": "WINDOW"})
            c = inner.representative_point()
            _text(msp, f"{s['name']} - {s['use']}  NFA {inner.area:.0f} m2", (c.x, c.y), 1.0)
            files.append(_save(doc, d_dir / f"plan_{s['name']}"))
    return files
