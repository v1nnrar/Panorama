#!/usr/bin/env python
"""Panorama build pipeline: parameters YAML -> IFC -> Blender (.blend/.glb/renders) -> drawings & reports.

Usage:
    .venv/bin/python build.py params/test_block.yaml                      # model, drawings, reports
    .venv/bin/python build.py params/test_block.yaml --render             # + Cycles renders
    .venv/bin/python build.py params/test_block.yaml --render --engine WORKBENCH   # fast clay renders
    .venv/bin/python build.py params/test_block.yaml --rules 02_regulations/rules.yaml
"""
import argparse
import json
from pathlib import Path

from pipeline import analysis, params
from pipeline.build_ifc import build


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("params")
    ap.add_argument("--rules", default=None, help="rules YAML (default: 'rules' key in params, if any)")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--engine", default="CYCLES", choices=["CYCLES", "WORKBENCH"])
    ap.add_argument("--no-blender", action="store_true", help="skip the Blender stage")
    ap.add_argument("--only", nargs="*", help="render only these camera names")
    a = ap.parse_args()

    design = params.load(a.params)
    out = Path(design["output_dir"])
    out.mkdir(parents=True, exist_ok=True)

    ifc_path = out / "model.ifc"
    build(design).write(str(ifc_path))
    print(f"IFC        -> {ifc_path}")

    m = analysis.metrics(design)
    rules = a.rules or _rules_from_params(a.params)
    results = analysis.check(m, rules)
    analysis.report(design, m, results, out)
    analysis.schedule(design, out)
    dwgs = analysis.drawings(design, out)
    print(f"Reports    -> {out / 'report.md'}, {out / 'area_schedule.xlsx'}")
    print(f"Drawings   -> {len(dwgs)} plan(s) in {out / 'drawings'}")

    if not a.no_blender:
        from pipeline.blender_scene import build_scene
        res = build_scene(str(ifc_path), out, design, do_render=a.render, engine=a.engine, only=a.only)
        print(f"Blender    -> {res['blend']}, {res['glb']}")
        for r in res["renders"]:
            print(f"Render     -> {r}")

    fails = [r for r in results if r["status"] == "FAIL"]
    print(json.dumps(m, indent=2))
    print(f"Compliance: {len(results) - len(fails)}/{len(results)} pass" if results else "Compliance: no rules")
    for r in fails:
        print(f"  FAIL {r['label']}: {r['value']} (limit {r['limit']})")


def _rules_from_params(p):
    import yaml
    raw = yaml.safe_load(Path(p).read_text())
    return str((Path(p).parent / raw["rules"]).resolve()) if raw.get("rules") else None


if __name__ == "__main__":
    main()
