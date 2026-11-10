"""Prague building regulations (Pražské stavební předpisy, nař. 12/2024) checks + design proxies.

Legal checks (massing level):
  §21 + příloha 1/II  distance angle: from windows of habitable rooms of EXISTING neighbouring buildings, no new
                      building may rise above 45° within some contiguous horizontal sector of ≥45°, counted
                      from 25° off the façade (sectors cannot be summed).
  §22 odst. 2         2 m minimum from boundaries with neighbouring (non-public) plots.
  §25 + přílohy 2, 3  parking: base count from gross floor area per use, scaled by the city-zone percentage.
Design proxies (not legal limits, used to compare options):
  own-façade daylight proxy (same 45°/45° test from our own façades against all buildings),
  courtyard sun hours on 21 March (open ground of the plot), hotel keys / flats estimates.

Window sampling, the parking zone and the per-use ratios are ASSUMPTIONS documented in 02_regulations/summary.md.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

# ----------------------------------------------------------------------------------------------- parking
# HPP m² per base space, bound share, visitor share (PSP příloha 2)
PARKING_USES = {
    "hotel": (100, 0.90, 0.10), "residential": (85, 0.90, 0.10), "office": (50, 0.90, 0.10),
    "retail": (70, 0.10, 0.90), "restaurant": (40, 0.10, 0.90), "congress": (60, 0.10, 0.90),
    "wellness": (40, 0.10, 0.90),
}
# zone (příloha 3): bound %, visitor min %, visitor max %   — values per IPR consolidated text (to verify)
PARKING_ZONES = {"00": (0.50, 0.0, 0.15), "01": (0.70, 0.10, 0.35), "02": (0.80, 0.15, 0.55),
                 "03": (0.90, 0.30, 0.75), "04": (0.90, 0.50, 0.90), "05": (1.00, 0.65, 0.65),
                 "06": (1.00, 0.80, 1.10), "07": (1.20, 0.90, 0.90)}
USE_KEYWORDS = [("hotel", ("hotel", "room", "key", "suite")), ("residential", ("apartment", "residential", "flat", "unit")),
                ("office", ("office",)), ("restaurant", ("restaurant", "bar", "café", "cafe", "dining")),
                ("congress", ("conference", "congress", "ballroom", "event")), ("wellness", ("spa", "wellness", "fitness")),
                ("retail", ("retail", "shop", "lobby", "amenit"))]


def classify_use(text, default="residential"):
    t = (text or "").lower()
    for use, kws in USE_KEYWORDS:
        if any(k in t for k in kws):
            return use
    return default


def gfa_by_use(design):
    out = {}
    for b in design["buildings"]:
        if b.get("below_ground") or b.get("existing"):
            continue
        bdef = classify_use(b.get("use"))
        for s in b["storeys"]:
            if s["elevation"] < 0:
                continue
            u = classify_use(s.get("use"), bdef)
            out[u] = out.get(u, 0.0) + Polygon(s["footprint"]).area
    return out


def parking(design, zone="02", m2_per_space=30.0, basement_efficiency=0.85):
    bound_pct, vis_min, vis_max = PARKING_ZONES[zone]
    uses = gfa_by_use(design)
    req_min = req_max = 0.0
    for u, a in uses.items():
        per, bs, vs = PARKING_USES[u]
        base = a / per
        req_min += base * bs * bound_pct + base * vs * vis_min
        req_max += base * bs * bound_pct + base * vs * vis_max
    below = sum(Polygon(s["footprint"]).area for b in design["buildings"] for s in b["storeys"] if s["elevation"] < 0)
    capacity = below * basement_efficiency / m2_per_space
    return {"parking_zone": zone, "parking_required_min": math.floor(req_min), "parking_required_max": math.ceil(req_max),
            "parking_capacity_est": math.floor(capacity),
            "parking_margin": math.floor(capacity) - math.floor(req_min),
            "gfa_by_use_m2": {k: round(v, 1) for k, v in uses.items()}}


def unit_estimates(design, hotel_eff=0.62, m2_per_key=34.0, resi_eff=0.78, m2_per_flat=65.0):
    uses = gfa_by_use(design)
    return {"hotel_keys_est": int(uses.get("hotel", 0) * hotel_eff / m2_per_key),
            "flats_est": int(uses.get("residential", 0) * resi_eff / m2_per_flat)}


# ----------------------------------------------------------------------------------------------- obstacles
def obstacles(design, include_existing=True, context=None, exclude_ids=()):
    """List of (Polygon, z_bottom, z_top) prisms: every storey of every above-ground building (+ roof parapet)."""
    obs = []
    for b in design["buildings"]:
        if b.get("below_ground") or b["id"] in exclude_ids or (b.get("existing") and not include_existing):
            continue
        cur = None                              # merge consecutive storeys with identical footprints
        for s in b["storeys"]:
            if s["elevation"] < 0:
                continue
            fp = tuple(map(tuple, s["footprint"]))
            if cur and cur[0] == fp:
                cur[2] = s["elevation"] + s["height"]
            else:
                if cur:
                    obs.append((Polygon(cur[0]), cur[1], cur[2], b["id"]))
                cur = [fp, s["elevation"], s["elevation"] + s["height"]]
        if cur:
            obs.append((Polygon(cur[0]), cur[1], cur[2], b["id"]))
        top = b["storeys"][-1]
        obs.append((Polygon(top["footprint"]), b["top_of_slab"],
                    b["top_of_slab"] + b["slab_thickness"] + b["roof"].get("parapet", 0), b["id"]))
    for c in context or []:
        obs.append((c["poly"], 0.0, c["h"], "ctx"))
    return obs


def _ray_blocked(p, d, z, obs, max_len=160.0, tan_limit=1.0):
    """True if some obstacle along horizontal direction d from p rises above the elevation angle atan(tan_limit)."""
    ray = LineString([p, (p[0] + d[0] * max_len, p[1] + d[1] * max_len)])
    for poly, z0, z1, _ in obs:
        if z1 <= z:
            continue
        if not ray.intersects(poly):
            continue
        dist = Point(p).distance(ray.intersection(poly))
        if dist < 0.05:
            continue
        if (z1 - z) > dist * tan_limit:
            return True
    return False


def angle_ok(p, t, n, z, obs, step=2.5):
    """Distance-angle test (PSP příloha 1/II): free contiguous horizontal sector ≥45° within φ ∈ [25°, 155°]."""
    P = Point(p)
    obs = [o for o in obs if (o[2] - z) > P.distance(o[0])]      # only prisms that can rise above 45°
    if not obs:
        return True
    run, best = 0.0, 0.0
    phi = 25.0
    while phi <= 155.0 + 1e-9:
        a = math.radians(phi)
        d = (math.cos(a) * t[0] + math.sin(a) * n[0], math.cos(a) * t[1] + math.sin(a) * n[1])
        if _ray_blocked(p, d, z, obs):
            run = 0.0
        else:
            run += step
            best = max(best, run)
        phi += step
    return best >= 45.0


def _facade_samples(poly, floors, storey_h, spacing=8.0, every=3, toward=None, min_len=4.0):
    """Window sample points on the façades of a CCW polygon (outward normals), optionally only façades facing `toward`."""
    from shapely.geometry.polygon import orient
    poly = orient(poly, 1.0)
    cs = list(poly.exterior.coords)[:-1]
    out = []
    for i, a in enumerate(cs):
        b = cs[(i + 1) % len(cs)]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < min_len:
            continue
        t = ((b[0] - a[0]) / L, (b[1] - a[1]) / L)
        n = (t[1], -t[0])                       # outward for CCW
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if toward is not None:
            v = (toward[0] - mid[0], toward[1] - mid[1])
            if v[0] * n[0] + v[1] * n[1] <= 0:
                continue
        k = max(1, int(L // spacing))
        for j in range(k):
            s = (j + 0.5) * L / k
            p = (a[0] + t[0] * s + n[0] * 0.05, a[1] + t[1] * s + n[1] * 0.05)
            for f in range(0, max(floors, 1), every):
                out.append((p, t, n, f * storey_h + 1.0))
    return out


def load_context(design, radius=120.0):
    path = design["site"].get("context")
    if not path or not Path(path).exists():
        return []
    site = unary_union([Polygon(p["ring"]) for p in design["site"]["parcels"]])
    out = []
    for c in json.loads(Path(path).read_text())["buildings"]:
        P = Polygon(c["poly"]).buffer(0)
        if P.is_empty or P.intersection(site).area > 0.3 * P.area or P.distance(site) > radius:
            continue
        out.append({"poly": P, "h": float(c["h"]), "floors": int(c.get("floors") or max(1, round(c["h"] / 3.2))),
                     "name": c.get("name", "")})
    return out


def distance_angle_neighbours(design, ctx):
    """§21: windows on neighbour façades facing the plot, against all NEW buildings."""
    site = unary_union([Polygon(p["ring"]) for p in design["site"]["parcels"]])
    c = site.centroid
    obs = obstacles(design, include_existing=False)
    if not obs:
        return {"psp21_windows_checked": 0, "psp21_windows_failing": 0, "psp21_fail_ratio": 0.0, "psp21_failing_neighbours": []}
    fails, total, by_n = 0, 0, {}
    for nb in ctx:
        sh = nb["h"] / max(nb["floors"], 1)
        for p, t, n, z in _facade_samples(nb["poly"], nb["floors"], sh, toward=(c.x, c.y)):
            if z > nb["h"]:
                continue
            total += 1
            if not angle_ok(p, t, n, z, obs):
                fails += 1
                key = nb["name"] or f"{nb['poly'].centroid.x:.0f},{nb['poly'].centroid.y:.0f}"
                by_n[key] = by_n.get(key, 0) + 1
    return {"psp21_windows_checked": total, "psp21_windows_failing": fails,
            "psp21_fail_ratio": round(fails / total, 3) if total else 0.0,
            "psp21_failing_neighbours": sorted(by_n.items(), key=lambda kv: -kv[1])[:6]}


VSC_FAIL = 0.15   # ASSUMED: BRE 209 (3rd ed.) — below ~15 % VSC adequate daylight needs very large windows; used as a
                  # design proxy for ČSN 73 0580 / EN 17037 until a real daylight-factor study is made (D7).
_EH = 2 * math.pi * 7 / 18          # unobstructed horizontal illuminance of the CIE overcast sky (Lz = 1)


def _vertical_band(t0):
    """∫_{t0}^{π/2} L(θ) cos²θ dθ for the CIE overcast sky L(θ) = (1 + 2 sinθ)/3 (vertical plane, unit azimuth)."""
    F = lambda t: (t / 2 + math.sin(2 * t) / 4) - 2 * math.cos(t) ** 3 / 3  # noqa: E731
    return (F(math.pi / 2) - F(t0)) / 3


def _obstruction_tan(p, d, z, obs, max_len=200.0):
    """Highest obstruction elevation (as tan) along horizontal direction d from p at height z."""
    ray = LineString([p, (p[0] + d[0] * max_len, p[1] + d[1] * max_len)])
    best = 0.0
    for poly, z0, z1, _ in obs:
        if z1 <= z or not ray.intersects(poly):
            continue
        dist = Point(p).distance(ray.intersection(poly))
        if dist < 0.05:
            continue
        best = max(best, (z1 - z) / dist)
    return best


def vsc(p, t, n, z, obs, step=10.0):
    """Vertical sky component (0..0.396) of a window at p (façade tangent t, outward normal n, height z)."""
    tot = 0.0
    a = -90.0 + step / 2
    while a < 90.0:
        r = math.radians(a)
        d = (math.cos(r) * n[0] + math.sin(r) * t[0], math.cos(r) * n[1] + math.sin(r) * t[1])
        t0 = math.atan(_obstruction_tan(p, d, z, obs))
        tot += _vertical_band(t0) * math.cos(r) * math.radians(step)
        a += step
    return tot / _EH


def daylight_proxy_own(design, ctx):
    """Daylight proxy on our own new façades (D7): vertical sky component per sampled window against all other
    buildings (ours + neighbours); a window fails below VSC_FAIL. Same sampling as before (every 3rd storey, 10 m)."""
    total = fails = 0
    acc = 0.0
    ctx_obs = [{"poly": c["poly"], "h": c["h"]} for c in ctx]
    for b in design["buildings"]:
        if b.get("below_ground") or b.get("existing"):
            continue
        obs = obstacles(design, include_existing=True, context=ctx_obs, exclude_ids=(b["id"],))
        for s in b["storeys"][::3]:
            if s["elevation"] < 0:
                continue
            for p, t, n, _ in _facade_samples(Polygon(s["footprint"]), 1, 0, spacing=10.0):
                z = s["elevation"] + 1.0
                near = [o for o in obs if o[2] > z]
                v = vsc(p, t, n, z, near)
                total += 1
                acc += v
                fails += v < VSC_FAIL
    return {"daylight_proxy_windows": total, "daylight_proxy_fail_ratio": round(fails / total, 3) if total else 0.0,
            "vsc_mean": round(acc / total, 3) if total else 0.0, "daylight_method": "VSC < 15 % (CIE overcast)"}


# ----------------------------------------------------------------------------------------------- sun
def sun_positions(lat=50.049, day_of_year=80, hours=None):
    """(azimuth from north clockwise, altitude) in degrees, local solar time."""
    hours = hours or [8 + 0.5 * i for i in range(17)]
    decl = math.radians(23.44) * math.sin(2 * math.pi * (284 + day_of_year) / 365)
    phi = math.radians(lat)
    out = []
    for h in hours:
        H = math.radians(15 * (h - 12))
        alt = math.asin(math.sin(phi) * math.sin(decl) + math.cos(phi) * math.cos(decl) * math.cos(H))
        if alt <= math.radians(3):
            continue
        az = math.atan2(math.sin(H), math.cos(H) * math.sin(phi) - math.tan(decl) * math.cos(phi))
        out.append(((math.degrees(az) + 180) % 360, math.degrees(alt)))
    return out


def courtyard_sun(design, ctx, grid=6.0, day_of_year=80):
    site = unary_union([Polygon(p["ring"]) for p in design["site"]["parcels"]])
    fps = unary_union([Polygon(b["storeys"][0]["footprint"]) for b in design["buildings"] if not b.get("below_ground")])
    open_ground = site.difference(fps.buffer(1.0))
    obs = obstacles(design, include_existing=True, context=[{"poly": c["poly"], "h": c["h"]} for c in ctx])
    suns = sun_positions(day_of_year=day_of_year)
    x0, y0, x1, y1 = open_ground.bounds
    hrs = []
    y = y0 + grid / 2
    while y < y1:
        x = x0 + grid / 2
        while x < x1:
            if open_ground.contains(Point(x, y)):
                lit = 0
                for az, alt in suns:
                    d = (math.sin(math.radians(az)), math.cos(math.radians(az)))
                    if not _ray_blocked((x, y), d, 0.0, obs, max_len=400, tan_limit=math.tan(math.radians(alt))):
                        lit += 1
                hrs.append(lit * 0.5)
            x += grid
        y += grid
    if not hrs:
        return {"courtyard_sun_hours_mean_mar21": 0.0, "courtyard_area_2h_sun_ratio": 0.0, "open_ground_m2": 0.0}
    return {"courtyard_sun_hours_mean_mar21": round(sum(hrs) / len(hrs), 2),
            "courtyard_area_2h_sun_ratio": round(sum(1 for h in hrs if h >= 2) / len(hrs), 3),
            "open_ground_m2": round(open_ground.area, 1)}


# ----------------------------------------------------------------------------------------------- §22
def boundary_distance(design, public_facing=("S", "E")):
    """§22: min distance of new building footprints to plot boundary segments that are NOT along public space.
    ASSUMED: boundary edges whose outward normal faces `public_facing` (Milevská to the S, street/metro to the E)
    are public space; the rest borders private neighbours."""
    from .geom import COMPASS
    site = unary_union([Polygon(p["ring"]) for p in design["site"]["parcels"]]).buffer(0.3).buffer(-0.3)
    site = max(getattr(site, "geoms", [site]), key=lambda g: g.area)
    from shapely.geometry.polygon import orient
    cs = list(orient(site.simplify(0.5), 1.0).exterior.coords)[:-1]
    priv = []
    dirs = [COMPASS[f] for f in public_facing]
    for i, a in enumerate(cs):
        b = cs[(i + 1) % len(cs)]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 0.5:
            continue
        n = ((b[1] - a[1]) / L, -(b[0] - a[0]) / L)
        if any(n[0] * d[0] + n[1] * d[1] >= 0.64 for d in dirs):
            continue
        priv.append(LineString([a, b]))
    new = [Polygon(b["storeys"][0]["footprint"]) for b in design["buildings"]
           if not b.get("below_ground") and not b.get("existing")]
    if not priv or not new:
        return {"psp22_min_boundary_distance_m": None}
    return {"psp22_min_boundary_distance_m": round(min(p.distance(l) for p in new for l in priv), 2)}


def run_all(design, zone="02"):
    ctx = load_context(design)
    m = {}
    m.update(parking(design, zone))
    m.update(unit_estimates(design))
    m.update(boundary_distance(design))
    m.update(distance_angle_neighbours(design, ctx))
    m.update(daylight_proxy_own(design, ctx))
    m.update(courtyard_sun(design, ctx))
    return m
