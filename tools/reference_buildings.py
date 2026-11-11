#!/usr/bin/env python
"""Reference buildings for camera calibration at ~1 m (accuracy step 1).

Footprints: RÚIAN building polygons (ČÚZK, ags.cuzk.gov.cz/arcgis/rest/services/RUIAN/MapServer/3 "StavebniObjekt",
cadastral accuracy). Heights: ČÚZK DMP 1G surface − DMR 5G terrain (tools/survey_heights.py), relative to the site GF.
Only buildings whose surveyed roof is ≥ 6 m and whose surface model is flat enough (roof spread ≤ 3 m) are marked
`usable` — newer buildings (absent from the surface model) are kept but flagged.

Writes 00_site/survey/reference_buildings.json. Usage: .venv/bin/python tools/reference_buildings.py
"""
import json
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import survey_heights as sh  # noqa: E402

URL = "https://ags.cuzk.gov.cz/arcgis/rest/services/RUIAN/MapServer/3/query"
TO_LOCAL = Transformer.from_crs("EPSG:5514", sh.LOCAL, always_xy=True)
TO_SJTSK = Transformer.from_crs(sh.LOCAL, "EPSG:5514", always_xy=True)


def fetch(radius=320.0):
    xs, ys = zip(*[TO_SJTSK.transform(x, y) for x in (-radius + 30, radius + 30) for y in (-radius - 20, radius - 20)])
    env = {"xmin": min(xs), "ymin": min(ys), "xmax": max(xs), "ymax": max(ys), "spatialReference": {"wkid": 5514}}
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    feats, offset = [], 0
    while True:
        q = urllib.parse.urlencode({"geometry": json.dumps(env), "geometryType": "esriGeometryEnvelope", "inSR": 5514,
                                    "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "true",
                                    "outSR": 5514, "f": "json", "resultOffset": offset, "resultRecordCount": 1000})
        r = json.load(urllib.request.urlopen(urllib.request.Request(URL, data=q.encode()), context=ctx, timeout=120))
        feats += r.get("features", [])
        if not r.get("exceededTransferLimit"):
            return feats
        offset += len(r["features"])


def main():
    out = []
    for f in fetch():
        rings = f["geometry"].get("rings") or []
        if not rings:
            continue
        ring = [list(map(lambda v: round(v, 2), TO_LOCAL.transform(x, y))) for x, y in rings[0]]
        P = Polygon(ring).buffer(0)
        if P.area < 60:
            continue
        inner = P.buffer(-1.5)
        xs, ys = sh.grid_in(inner if not inner.is_empty else P, 1.0)
        if len(xs) < 5:
            continue
        dsm = sh.sample("dmp1g", xs, ys) - sh.site_ground()
        base, roof = sh.roof_and_base(P)
        spread = float(np.percentile(dsm, 90) - np.percentile(dsm, 50))
        attrs = {k: v for k, v in f["attributes"].items() if k.lower() in ("kod", "zpusobvyuzitikod", "pocetpodlazi", "id")}
        out.append({"ruian": attrs, "poly": [p for p in list(P.exterior.coords)[:-1]], "area_m2": round(P.area, 1),
                    "base_z": base, "roof_z": roof, "roof_spread_m": round(spread, 2),
                    "usable": bool(roof - base >= 6 and spread <= 3.0)})
    p = ROOT / "00_site" / "survey" / "reference_buildings.json"
    p.write_text(json.dumps({"source": "RÚIAN StavebniObjekt (ČÚZK) + DMP1G/DMR5G heights; site GF "
                             f"{sh.site_ground():.2f} m a.s.l.", "buildings": out}, indent=0, ensure_ascii=False))
    n = sum(b["usable"] for b in out)
    print(f"{len(out)} RÚIAN buildings, {n} usable as height references -> {p}")


if __name__ == "__main__":
    main()
