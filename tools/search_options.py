#!/usr/bin/env python
"""Parametric search for a "max yield" capacity-study option (LOOP.md D5).

Layout family: a street bar along Milevská (S), an east bar (R), a north wing (O) and 1–3 towers (first = hotel,
others residential), all axis-aligned in the plot frame (see tools/make_options.py). A random local search mutates
one or two parameters at a time, sometimes adds or removes a tower, and keeps a layout if its score improves.

Every candidate is checked with the pipeline's own functions (pipeline/psp.py): §21 distance angle, §22 boundary
distance, §25 parking, own-façade daylight proxy, courtyard sun, plus height/storey limits (≤ 27 storeys). Hard
failures are rejected; the score mirrors tools/score_options.py: GFA (k m², estimated as footprint × storeys) minus
10 % per missed quality floor. Rules are never relaxed. The best layout is written to
04_proposed/options/<key>/spec.json; tools/make_options.py turns that into params.yaml.

Usage: .venv/bin/python tools/search_options.py --seconds 480 [--seed 1] [--key E] [--start A]
"""
import argparse
import copy
import json
import random
import shutil
import sys
import time
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import make_options as mo  # noqa: E402
from pipeline import psp  # noqa: E402
from pipeline.params import load  # noqa: E402

TMP_KEY = "_search_tmp"
MAX_STOREYS = 27
FLOORS = {"daylight": 0.15, "sun": 2.0, "built": 0.45}

# layout = {"S": [u0, u1, n], "R": [v1, n], "O": [u0, u1, v0, v1, n], "T": [[u, v, w, d, n], ...]}
START = {"A": {"S": [-20, 86, 10], "R": [4, 12], "O": [-52, 22, 12, 34, 7], "T": [[30, -41, 30, 36, 27]]}}
LIMITS = {"S": [(-30, 0), (40, 104), (6, 12)], "R": [(-30, 6), (6, 12)],
          "O": [(-56, -20), (0, 40), (8, 24), (24, 40), (4, 12)],
          "T": [(-30, 80), (-42, 10), (22, 36), (22, 36), (12, MAX_STOREYS)]}   # tower sides ≤ 36 m (realistic hotel/residential floorplates)
STEP = {"S": [2, 2, 1], "R": [2, 1], "O": [2, 2, 2, 2, 1], "T": [2, 2, 2, 2, 1]}


def spec_of(lay, name="Option E — max yield (search)"):
    blocks = []
    for i, (u, v, w, d, n) in enumerate(lay["T"]):
        if i == 0:
            blocks.append({"id": "H", "name": "Hotel tower", "use": "Hotel", "preset": "hotel_tower", "key_cap": 450,
                           "poly": mo.rect(u, v, u + w, v + d),
                           "storeys": mo.storeys(n, 6.0, 3.3, "Hotel lobby / restaurant", "Hotel rooms", 5.0, "Conference / spa")})
        else:
            blocks.append({"id": f"T{i}", "name": f"Residential tower {i}", "use": "Residential", "preset": "resi_tower",
                           "poly": mo.rect(u, v, u + w, v + d), "storeys": mo.storeys(n, 4.5, 3.2, "Retail", "Apartments")})
    su0, su1, sn = lay["S"]
    rv1, rn = lay["R"]
    ou0, ou1, ov0, ov1, on = lay["O"]
    blocks += [
        {"id": "S", "name": "Street bar (Milevská)", "use": "Residential", "preset": "resi", "poly": mo.rect(su0, -61, su1, -45),
         "storeys": mo.storeys(sn, 4.5, 3.1, "Retail", "Apartments")},
        {"id": "R", "name": "East bar", "use": "Residential", "preset": "resi", "poly": mo.rect(88, -59, 104, rv1),
         "storeys": mo.storeys(rn, 4.5, 3.1, "Retail", "Apartments")},
        {"id": "O", "name": "North office wing", "use": "Office", "preset": "office", "poly": mo.rect(ou0, ov0, ou1, ov1),
         "storeys": mo.storeys(on, 4.5, 3.6, "Office lobby", "Offices")},
    ]
    n_t = len(lay["T"])
    return {"name": name, "intent": f"Max-yield layout from tools/search_options.py: {n_t} tower(s), street bar, east bar "
                                     "and north wing, every PSP / MPP check passing.", "basement_levels": 3, "blocks": blocks}


class Evaluator:
    def __init__(self):
        d0 = load(mo.build_option(TMP_KEY, spec_of(START["A"])))
        self.ctx = psp.load_context(d0)
        self.plot = unary_union([Polygon(q["ring"]) for q in d0["site"]["parcels"]])
        self.E = Polygon(mo.E_EXISTING).buffer(1.0)

    def __call__(self, lay):
        spec = spec_of(lay)
        polys = [Polygon(mo.to_survey(b["poly"])) for b in spec["blocks"]]
        for P in polys:
            if not P.is_valid or P.difference(self.plot).area > 3.0 or P.intersects(self.E):
                return None
        for i in range(len(polys)):
            for j in range(i + 1, len(polys)):
                if polys[i].buffer(1.0).intersects(polys[j]):
                    return None
        d = load(mo.build_option(TMP_KEY, spec))
        if (psp.boundary_distance(d)["psp22_min_boundary_distance_m"] or 0) < 2.0:
            return None
        if psp.parking(d)["parking_margin"] < 0:
            return None
        if psp.distance_angle_neighbours(d, self.ctx)["psp21_windows_failing"] > 0:
            return None
        new = [b for b in d["buildings"] if not b.get("existing") and not b.get("below_ground")]
        gfa = sum(Polygon(s["footprint"]).area for b in new for s in b["storeys"])
        sun = psp.courtyard_sun(d, self.ctx)["courtyard_sun_hours_mean_mar21"]
        dl = psp.daylight_proxy_own(d, self.ctx)["daylight_proxy_fail_ratio"]
        built = sum(Polygon(b["storeys"][0]["footprint"]).area for b in d["buildings"] if not b.get("below_ground")) / self.plot.area
        miss = (sun < FLOORS["sun"]) + (dl > FLOORS["daylight"]) + (built > FLOORS["built"])
        return {"score": gfa / 1000 * (1 - 0.1 * miss), "gfa": gfa, "sun": sun, "daylight": dl, "built": built}


def clamp(v, lim):
    return min(lim[1], max(lim[0], v))


def mutate(lay, rng):
    x = copy.deepcopy(lay)
    r = rng.random()
    if r < 0.08 and len(x["T"]) < 3:                     # add a tower
        lo = LIMITS["T"]
        x["T"].append([rng.randrange(lo[0][0], lo[0][1], 2), rng.randrange(lo[1][0], lo[1][1], 2),
                       rng.choice([24, 28, 30]), rng.choice([24, 28, 30]), rng.randint(12, MAX_STOREYS)])
        return x
    if r < 0.12 and len(x["T"]) > 1:                     # remove a residential tower
        x["T"].pop(rng.randrange(1, len(x["T"])))
        return x
    for _ in range(rng.choice([1, 1, 2])):
        key = rng.choice(["S", "R", "O", "T", "T"])
        vec = x[key][rng.randrange(len(x[key]))] if key == "T" else x[key]
        k = rng.randrange(len(vec))
        vec[k] = clamp(vec[k] + rng.choice([-1, 1]) * STEP[key][k] * rng.choice([1, 1, 2, 4]), LIMITS[key][k])
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=480)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--key", default="E")
    ap.add_argument("--start", default=None, help="JSON layout file to start from (default: option A layout)")
    a = ap.parse_args()
    rng = random.Random(a.seed)
    ev = Evaluator()
    best = json.loads(Path(a.start).read_text())["layout"] if a.start else copy.deepcopy(START["A"])
    best_r = ev(best)
    print("start", best_r, flush=True)
    t0, n = time.time(), 0
    try:
        while time.time() - t0 < a.seconds:
            cand = mutate(best, rng)
            r = ev(cand)
            n += 1
            if r and (best_r is None or r["score"] > best_r["score"]):
                best, best_r = cand, r
                print(f"{time.time() - t0:5.0f}s score {r['score']:.2f} towers {len(best['T'])} {json.dumps(best)}", flush=True)
    finally:
        shutil.rmtree(mo.OUT / TMP_KEY, ignore_errors=True)
    out = mo.OUT / a.key
    out.mkdir(parents=True, exist_ok=True)
    (out / "spec.json").write_text(json.dumps({"layout": best, "estimate": best_r, "samples": n, "seed": a.seed,
                                               "seconds": a.seconds, "spec": spec_of(best)}, indent=1))
    print(f"samples {n}; best {best_r}; wrote {out / 'spec.json'}")


if __name__ == "__main__":
    main()
