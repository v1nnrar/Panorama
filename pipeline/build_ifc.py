"""Build an IFC4 BIM model from a normalised design dict (see params.py).

All geometry is written in absolute site coordinates (identity placements), as extruded solids.
Element types: slabs, spaces, walls + windows or curtain walls, balconies + railings/planters, slab-edge bands,
fins, diagrid, terrace edges, roof slab, parapet, green roof, rooftop structures, PV arrays, sawtooth roofs.
Every element gets an IfcMaterial; Blender colours by material name.
"""
from __future__ import annotations

import math

import numpy as np
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
from shapely.geometry import LineString, MultiPolygon, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from .geom import edges, facing_edges, rule_edges, in_range, inset, local_frame, offset_edges, outward_normal, rect_world

API = ifcopenshell.api


# ----------------------------------------------------------------------------------------------- primitives
class Ctx:
    def __init__(self, f, body):
        self.f, self.body, self.mats = f, body, {}

    def material(self, name):
        if name not in self.mats:
            self.mats[name] = API.material.add_material(self.f, name=name)
        return self.mats[name]


def _pt3(f, p):
    return f.createIfcCartesianPoint(tuple(float(v) for v in p))


def _dir(f, v):
    return f.createIfcDirection(tuple(float(c) for c in v))


def _polyline(f, pts):
    ps = [f.createIfcCartesianPoint((float(x), float(y))) for x, y in pts]
    return f.createIfcPolyline(ps + [ps[0]])


def solid(f, origin, xdir, normal, outer, depth, holes=()):
    """Profile `outer` (2D, local X = xdir, local Y = normal × xdir) extruded `depth` along `normal`."""
    if holes:
        prof = f.createIfcArbitraryProfileDefWithVoids("AREA", None, _polyline(f, outer),
                                                       [_polyline(f, h) for h in holes])
    else:
        prof = f.createIfcArbitraryClosedProfileDef("AREA", None, _polyline(f, outer))
    pos = f.createIfcAxis2Placement3D(_pt3(f, origin), _dir(f, normal), _dir(f, xdir))
    return f.createIfcExtrudedAreaSolid(prof, pos, _dir(f, (0, 0, 1)), float(depth))


def plan_solid(f, pts, z0, depth, holes=()):
    return solid(f, (0, 0, z0), (1, 0, 0), (0, 0, 1), pts, depth, holes)


def member_solid(f, p0, p1, w, d, side):
    """Box from p0 to p1 (3D); cross-section d along `side` (made perpendicular), w across."""
    a, b = np.array(p0, float), np.array(p1, float)
    n = b - a
    L = float(np.linalg.norm(n))
    n /= L
    s = np.array(side, float)
    s = s - s.dot(n) * n
    if np.linalg.norm(s) < 1e-6:
        s = np.cross(n, [0, 0, 1]) if abs(n[2]) < 0.99 else np.array([1.0, 0, 0])
    s /= np.linalg.norm(s)
    prof = [(-d / 2, -w / 2), (d / 2, -w / 2), (d / 2, w / 2), (-d / 2, w / 2)]
    return solid(f, a, s, n, prof, L)


def _identity(f, product):
    API.geometry.edit_object_placement(f, product=product, matrix=np.eye(4))


def product(C, cls, name, solids, container=None, predefined=None, object_type=None, material=None):
    if not solids:
        return None
    f = C.f
    el = API.root.create_entity(f, ifc_class=cls, name=name, predefined_type=predefined)
    if object_type:
        el.ObjectType = object_type
    rep = f.createIfcShapeRepresentation(C.body, "Body", "SweptSolid", solids)
    API.geometry.assign_representation(f, product=el, representation=rep)
    _identity(f, el)
    if container is not None:
        API.spatial.assign_container(f, products=[el], relating_structure=container)
    if material:
        API.material.assign_material(f, products=[el], type="IfcMaterial", material=C.material(material))
    return el


def _window_positions(L, w):
    spacing, margin = w["spacing"], w["edge_margin"]
    n = int((L - 2 * margin - w["width"]) // spacing) + 1 if L - 2 * margin >= w["width"] else 0
    if n <= 0:
        return []
    span = (n - 1) * spacing
    start = (L - span) / 2
    return [start + i * spacing for i in range(n)]


def inset_ring(pts, t):  # kept for backwards compatibility
    return inset(pts, t)


def _ring(poly):
    return [tuple(c) for c in list(poly.exterior.coords)[:-1]]


def _polys(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon)]


# ----------------------------------------------------------------------------------------------- facade parts
def _walls_and_windows(C, st, s, t, slab, wall_mat):
    f, z, fp = C.f, s["elevation"], s["footprint"]
    ring = offset_edges(fp, [t] * len(fp))       # vertex-matched with fp
    wall_h = s["height"] - slab
    for i, (a, b) in enumerate(edges(fp)):
        j = (i + 1) % len(fp)
        wall = product(C, "IfcWall", f"{s['name']} ext wall {i + 1}",
                       [plan_solid(f, [a, b, ring[j], ring[i]], z + slab, wall_h)], st, "SOLIDWALL",
                       material=wall_mat)
        w = s["windows"]
        if not w:
            continue
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        on = outward_normal(a, b)
        nx, ny = -on[0], -on[1]
        for k, d in enumerate(_window_positions(L, w)):
            c0, c1 = d - w["width"] / 2, d + w["width"] / 2
            p = lambda dd, off: (a[0] + ux * dd + nx * off, a[1] + uy * dd + ny * off)
            zz = z + slab + w["sill"]
            opening = product(C, "IfcOpeningElement", f"{wall.Name} opening {k + 1}",
                              [plan_solid(f, [p(c0, -0.05), p(c1, -0.05), p(c1, t + 0.05), p(c0, t + 0.05)],
                                          zz, w["height"])])
            API.feature.add_feature(f, feature=opening, element=wall)
            win = product(C, "IfcWindow", f"{wall.Name} window {k + 1}",
                          [plan_solid(f, [p(c0, t * 0.4), p(c1, t * 0.4), p(c1, t * 0.6), p(c0, t * 0.6)],
                                      zz, w["height"])], st, "WINDOW", material=w.get("material", "Glass"))
            API.feature.add_filling(f, opening=opening, element=win)


def _curtain(C, st, s, t, slab, rule):
    f, z, fp = C.f, s["elevation"], s["footprint"]
    line = inset(fp, rule.get("inset", t / 2))
    h = s["height"] - slab
    glass, mull, spandrel = [], [], []
    sp = rule.get("mullion", 1.5)
    for a, b in edges(line):
        n = outward_normal(a, b)
        q = [a, b, (b[0] - n[0] * 0.05, b[1] - n[1] * 0.05), (a[0] - n[0] * 0.05, a[1] - n[1] * 0.05)]
        glass.append(plan_solid(f, q, z + slab, h))
        if rule.get("spandrel"):
            q2 = [(a[0] + n[0] * 0.02, a[1] + n[1] * 0.02), (b[0] + n[0] * 0.02, b[1] + n[1] * 0.02),
                  (b[0] - n[0] * 0.07, b[1] - n[1] * 0.07), (a[0] - n[0] * 0.07, a[1] - n[1] * 0.07)]
            spandrel.append(plan_solid(f, q2, z + slab, rule["spandrel"]))
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        for k in range(0, int(L // sp) + 1):
            px, py = a[0] + (b[0] - a[0]) * k * sp / L, a[1] + (b[1] - a[1]) * k * sp / L
            mull.append(member_solid(f, (px, py, z + slab), (px, py, z + s["height"]), 0.06, 0.14, (n[0], n[1], 0)))
    product(C, "IfcCurtainWall", f"{s['name']} curtain wall", glass, st, material=rule.get("glass", "Glass"))
    product(C, "IfcMember", f"{s['name']} mullions", mull, st, "MULLION", material=rule.get("frame", "Aluminium"))
    product(C, "IfcPlate", f"{s['name']} spandrels", spandrel, st, "USERDEFINED", "SPANDREL",
            material=rule.get("spandrel_material", "Aluminium"))


def _edge_strips(f, fp, idx, depth, z, th):
    out = []
    for i in idx:
        a, b = fp[i], fp[(i + 1) % len(fp)]
        n = outward_normal(a, b)
        out.append(plan_solid(f, [a, b, (b[0] + n[0] * depth, b[1] + n[1] * depth),
                                  (a[0] + n[0] * depth, a[1] + n[1] * depth)], z, th))
    return out


def _band_or_balcony(C, st, s, slab, rule, kind):
    f, z, fp = C.f, s["elevation"], s["footprint"]
    d = rule.get("depth", 1.5)
    th = rule.get("thickness", slab)
    idx = rule_edges(fp, rule)
    if len(idx) == len(fp):
        outer = offset_edges(fp, [-d] * len(fp))
        solids = [plan_solid(f, outer, z, th, holes=[fp])]
        rail_edges = edges(outer)
    else:
        solids = _edge_strips(f, fp, idx, d, z, th)
        rail_edges = []
        for i in idx:
            a, b = fp[i], fp[(i + 1) % len(fp)]
            n = outward_normal(a, b)
            rail_edges.append(((a[0] + n[0] * d, a[1] + n[1] * d), (b[0] + n[0] * d, b[1] + n[1] * d)))
    if kind == "band":
        product(C, "IfcSlab", f"{s['name']} slab edge band", solids, st, "USERDEFINED", "SLAB EDGE",
                material=rule.get("material", "Concrete white"))
        return
    product(C, "IfcSlab", f"{s['name']} balconies", solids, st, "USERDEFINED", "BALCONY",
            material=rule.get("material", "Concrete white"))
    _edge_elements(C, st, s["name"], rail_edges, z + th, rule)


def _edge_elements(C, st, name, segs, z, rule):
    """Railing (glass) and/or planter boxes along segments (outer edge = segment, inward = left side)."""
    f = C.f
    if rule.get("planter"):
        pw, ph = rule.get("planter_width", 0.45), rule.get("planter_height", 0.55)
        solids, green = [], []
        for a, b in segs:
            n = outward_normal(a, b)
            q = [a, b, (b[0] - n[0] * pw, b[1] - n[1] * pw), (a[0] - n[0] * pw, a[1] - n[1] * pw)]
            solids.append(plan_solid(f, q, z, ph))
            green.append(plan_solid(f, inset(q, 0.06) if len(q) == 4 else q, z + ph, rule.get("plant_height", 0.45)))
        product(C, "IfcBuildingElementProxy", f"{name} planters", solids, st, "USERDEFINED", "PLANTER",
                material=rule.get("planter_material", "Concrete white"))
        product(C, "IfcBuildingElementProxy", f"{name} planting", green, st, "USERDEFINED", "PLANTING",
                material="Planting")
    if rule.get("railing", True):
        solids = []
        for a, b in segs:
            n = outward_normal(a, b)
            q = [a, b, (b[0] - n[0] * 0.03, b[1] - n[1] * 0.03), (a[0] - n[0] * 0.03, a[1] - n[1] * 0.03)]
            solids.append(plan_solid(f, q, z, rule.get("railing_height", 1.05)))
        product(C, "IfcRailing", f"{name} railing", solids, st, "BALUSTRADE",
                material=rule.get("railing_material", "Glass railing"))


def _fins(C, st, s, rule):
    f, z, fp = C.f, s["elevation"], s["footprint"]
    sp, w, d, off = rule.get("spacing", 1.2), rule.get("width", 0.1), rule.get("depth", 0.4), rule.get("offset", 0.0)
    h = s["height"]
    solids = []
    for i in rule_edges(fp, rule):
        a, b = fp[i], fp[(i + 1) % len(fp)]
        n = outward_normal(a, b)
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k_n = max(int(L // sp), 1)
        start = (L - (k_n - 1) * sp) / 2
        for k in range(k_n):
            t_ = (start + k * sp) / L
            cx = a[0] + (b[0] - a[0]) * t_ + n[0] * (off + d / 2)
            cy = a[1] + (b[1] - a[1]) * t_ + n[1] * (off + d / 2)
            solids.append(member_solid(f, (cx, cy, z), (cx, cy, z + h), w, d, (n[0], n[1], 0)))
    product(C, "IfcMember", f"{s['name']} fins", solids, st, "USERDEFINED", "FIN",
            material=rule.get("material", "Aluminium white"))


def _terrace_edges(C, st, s, slab_poly, rule):
    """Railings / planters on the part of a floor slab left exposed by a setback."""
    exposed = slab_poly.exterior.difference(Polygon(s["footprint"]).buffer(0.05))
    segs = []
    for g in getattr(exposed, "geoms", [exposed]):
        if isinstance(g, LineString) and g.length > 0.5:
            cs = list(g.coords)
            segs += [(cs[k], cs[k + 1]) for k in range(len(cs) - 1)
                     if math.hypot(cs[k + 1][0] - cs[k][0], cs[k + 1][1] - cs[k][1]) > 0.3]
    if segs:
        _edge_elements(C, st, f"{s['name']} terrace", segs, s["elevation"] + rule.get("slab", 0.3), rule)
    if rule.get("green"):                    # planted terrace surface (terrace_edge: {green: true})
        area = slab_poly.difference(Polygon(s["footprint"]).buffer(0.3, join_style="mitre"))
        parts = [g for g in getattr(area, "geoms", [area]) if isinstance(g, Polygon) and g.area > 2.0]
        solids = [plan_solid(C.f, _ring(orient(g.buffer(-0.5, join_style="mitre"), sign=1.0)),
                             s["elevation"] + rule.get("slab", 0.3), 0.25)
                  for g in parts if not g.buffer(-0.5, join_style="mitre").is_empty
                  and isinstance(g.buffer(-0.5, join_style="mitre"), Polygon)]
        if solids:
            product(C, "IfcCovering", f"{s['name']} terrace green", solids, st, "USERDEFINED", "GREEN ROOF",
                    material="Planting")


def _diagrid(C, b, st_map, rule):
    f, st = C.f, b["storeys"]
    n_max = len(st)
    lo = rule.get("from", 1)
    hi = rule.get("to", n_max)
    s_lo, s_hi = st[lo - 1], st[hi - 1]
    z0 = s_lo["elevation"]
    z1 = b["top_of_slab"] + b["slab_thickness"] + rule.get("above_roof", 0.0) if hi == n_max \
        else s_hi["elevation"] + s_hi["height"]
    plane = offset_edges(s_lo["footprint"], [-rule.get("offset", 2.0)] * len(s_lo["footprint"]))
    M = rule.get("modules") or max(1, round((z1 - z0) / (rule.get("storeys_per_module", 3) * s_hi["height"])))
    Hm = (z1 - z0) / M
    w, d = rule.get("member", [0.45, 0.6])
    container = st_map[s_lo["name"]]
    rings = []
    for i, (a, b_) in enumerate(edges(plane)):
        n = outward_normal(a, b_)
        side = (n[0], n[1], 0)
        L = math.hypot(b_[0] - a[0], b_[1] - a[1])
        K = rule.get("bays") or max(1, round(L / rule.get("bay_width", 7.0)))
        P = lambda u, zz: (a[0] + (b_[0] - a[0]) * u / K, a[1] + (b_[1] - a[1]) * u / K, zz)
        solids = []
        for m in range(M):
            zb, zt = z0 + m * Hm, z0 + (m + 1) * Hm
            for k in range(K):
                if m % 2 == 0:   # bottom nodes on bay lines, top nodes mid-bay
                    solids += [member_solid(f, P(k, zb), P(k + 0.5, zt), w, d, side),
                               member_solid(f, P(k + 1, zb), P(k + 0.5, zt), w, d, side)]
                else:            # bottom nodes mid-bay, top nodes on bay lines
                    solids += [member_solid(f, P(k + 0.5, zb), P(k, zt), w, d, side),
                               member_solid(f, P(k + 0.5, zb), P(k + 1, zt), w, d, side)]
        product(C, "IfcMember", f"{b['id']} diagrid face {i + 1}", solids, container, "USERDEFINED", "DIAGRID",
                material=rule.get("material", "Steel white"))
        for m in range(M + 1):
            zz = z0 + m * Hm
            rings.append(member_solid(f, (a[0], a[1], zz), (b_[0], b_[1], zz), w * 0.8, d, side))
    product(C, "IfcMember", f"{b['id']} diagrid ring beams", rings, container, "USERDEFINED", "DIAGRID RING",
            material=rule.get("material", "Steel white"))


# ----------------------------------------------------------------------------------------------- roof parts
def _intervals(line, region):
    """Parameter intervals (distance along `line`) where the line lies inside `region`."""
    hit = line.intersection(region)
    out = []
    for seg in getattr(hit, "geoms", [hit]):
        if isinstance(seg, LineString) and seg.length > 0:
            a, b = line.project(Point(seg.coords[0])), line.project(Point(seg.coords[-1]))
            out.append((min(a, b), max(a, b)))
    return out


def _rows(f, region, z, azimuth_deg, row, gap, tilt_deg, triangle=False, lift=0.3, th=0.06):
    """Rows of tilted panels (or sawtooth prisms) facing `azimuth_deg` (0 = N, 90 = E, 180 = S) inside region.
    A row is kept only where its full depth fits (intersection of back-edge and front-edge spans)."""
    az = math.radians(azimuth_deg)
    fx, fy = math.sin(az), math.cos(az)            # facing direction (front, low edge)
    ux, uy = fy, -fx                               # along-row direction (= extrusion direction)
    rd = row * math.cos(math.radians(tilt_deg))
    rh = row * math.sin(math.radians(tilt_deg))
    normal = (ux, uy, 0.0)                         # f × up
    coords = [c for p in _polys(region) for c in p.exterior.coords]
    if not coords:
        return []
    proj = [x * fx + y * fy for x, y in coords]
    R = max(abs(x) + abs(y) for x, y in coords) + 200
    prof = [(0, 0), (rd, 0), (0, rh)] if triangle else \
        [(0, lift + rh), (rd, lift), (rd, lift + th), (0, lift + rh + th)]
    out, s = [], min(proj) + 0.05
    while s + rd <= max(proj) - 0.05:
        def line_at(fc):
            p0 = (fc * fx - ux * R, fc * fy - uy * R)
            return LineString([p0, (p0[0] + ux * 2 * R, p0[1] + uy * 2 * R)]), p0
        (lb, p0), (lf, _) = line_at(s + 0.02), line_at(s + rd - 0.02)
        for a0, a1 in _intervals(lb, region):
            for b0, b1 in _intervals(lf, region):
                lo, hi = max(a0, b0), min(a1, b1)
                if hi - lo < 1.2:
                    continue
                origin = (p0[0] + ux * lo, p0[1] + uy * lo, z)
                out.append(solid(f, origin, (fx, fy, 0.0), normal, prof, hi - lo))
        s += rd + gap
    return out


def _azimuth(cfg, fp):
    az = cfg.get("azimuth", 180)
    if az != "building":
        return az
    _, _, (vx, vy) = local_frame(fp)
    if vy > 0:
        vx, vy = -vx, -vy                          # face the southern side of the building
    return math.degrees(math.atan2(vx, vy))


def _roof(C, b, roof_st):
    f = C.f
    top = b["storeys"][-1]
    fp, slab = top["footprint"], b["slab_thickness"]
    roof = b["roof"]
    zr = b["top_of_slab"]
    zt = zr + slab
    if roof.get("slab", True):
        product(C, "IfcRoof", f"{b['id']} roof slab", [plan_solid(f, fp, zr, slab)], roof_st, "FLAT_ROOF",
                material=roof.get("material", "Concrete grey"))
    par = roof.get("parapet", 0)
    if par:
        ring = offset_edges(fp, [0.25] * len(fp))  # vertex-matched with fp
        solids = [plan_solid(f, [a, fp[(i + 1) % len(fp)], ring[(i + 1) % len(fp)], ring[i]], zt, par)
                  for i, a in enumerate(fp)]
        product(C, "IfcWall", f"{b['id']} parapet", solids, roof_st, "PARAPET",
                material=roof.get("parapet_material", b["material"]))
    frame = local_frame(fp)
    usable = Polygon(inset(fp, roof.get("margin", 1.0)))
    blocked = []
    for k, sdef in enumerate(roof.get("structures", [])):
        r = rect_world(frame, sdef.get("dx", 0), sdef.get("dy", 0), sdef["w"], sdef["d"])
        blocked.append(Polygon(r).buffer(sdef.get("clear", 0.8)))
        nm = sdef.get("name", "structure")
        product(C, "IfcBuildingElementProxy", f"{b['id']} roof {nm} {k + 1}", [plan_solid(f, r, zt, sdef["h"])],
                roof_st, "USERDEFINED", nm.upper(), material=sdef.get("material", "Render grey"))
        if sdef.get("green"):
            product(C, "IfcCovering", f"{b['id']} roof {nm} {k + 1} green",
                    [plan_solid(f, inset(r, 0.3), zt + sdef["h"], 0.25)], roof_st, "USERDEFINED", "GREEN ROOF",
                    material="Planting")
    if roof.get("green"):
        g = roof["green"] if isinstance(roof["green"], dict) else {}
        product(C, "IfcCovering", f"{b['id']} green roof", [plan_solid(f, inset(fp, 0.4), zt, g.get("depth", 0.15))],
                roof_st, "USERDEFINED", "GREEN ROOF", material="Planting")
    free = usable.difference(unary_union(blocked)) if blocked else usable
    for key, tri in (("pv", False), ("sawtooth", True)):
        cfg = roof.get(key)
        if not cfg:
            continue
        region = free
        if cfg.get("exclude_center"):
            ex = cfg["exclude_center"]
            region = region.difference(Polygon(rect_world(frame, 0, 0, ex[0], ex[1])).buffer(0.8))
        solids = _rows(f, region, zt + (0.15 if roof.get("green") else 0), _azimuth(cfg, fp),
                       cfg.get("row", 2.0), cfg.get("gap", 1.0), cfg.get("tilt", 12), triangle=tri,
                       lift=cfg.get("lift", 0.3))
        if tri:
            product(C, "IfcRoof", f"{b['id']} sawtooth roof", solids, roof_st, "USERDEFINED", "SAWTOOTH",
                    material=cfg.get("material", "PV"))
        else:
            product(C, "IfcSolarDevice", f"{b['id']} PV array", solids, roof_st, "SOLARPANEL",
                    material=cfg.get("material", "PV"))


# ----------------------------------------------------------------------------------------------- building
def _add_building(C, site, b):
    f = C.f
    building = API.root.create_entity(f, ifc_class="IfcBuilding", name=b["name"])
    building.Description = b.get("use") or None
    API.aggregate.assign_object(f, products=[building], relating_object=site)
    API.pset.edit_pset(f, pset=API.pset.add_pset(f, product=building, name="Panorama_Building"),
                       properties={"Id": b["id"], "Use": b["use"] or "", "Notes": b["notes"] or ""})
    t, slab = b["exterior_wall"], b["slab_thickness"]
    rules = b["facade"]
    n_max = len(b["storeys"])
    st_map, prev = {}, None
    for s in b["storeys"]:
        st = API.root.create_entity(f, ifc_class="IfcBuildingStorey", name=s["name"])
        API.geometry.edit_object_placement(f, product=st, matrix=np.eye(4))
        st.Elevation = s["elevation"]
        API.aggregate.assign_object(f, products=[st], relating_object=building)
        API.pset.edit_pset(f, pset=API.pset.add_pset(f, product=st, name="Panorama_Storey"),
                           properties={"Use": s["use"], "Height": s["height"]})
        st_map[s["name"]] = st
        z, fp, n = s["elevation"], s["footprint"], s["n"]

        slab_poly = Polygon(fp)
        if prev is not None and Polygon(prev).area > slab_poly.area + 0.5:
            u = unary_union([slab_poly, Polygon(prev)])
            slab_poly = orient(max(_polys(u), key=lambda p: p.area), sign=1.0)
        product(C, "IfcSlab", f"{s['name']} slab", [plan_solid(f, _ring(slab_poly), z, slab)], st, "FLOOR",
                material="Concrete grey")
        if slab_poly.area > Polygon(fp).area + 0.5:
            _terrace_edges(C, st, s, slab_poly, {"slab": slab, **b.get("terrace_edge", {"planter": True})})

        inner = Polygon(fp).buffer(-t, join_style="mitre")
        sp = product(C, "IfcSpace", f"{s['name']} floor area",
                     [plan_solid(f, _ring(inner), z + slab, s["height"] - slab)], predefined="INTERNAL")
        API.aggregate.assign_object(f, products=[sp], relating_object=st)
        API.pset.edit_pset(f, pset=API.pset.add_pset(f, product=sp, name="Qto_SpaceBaseQuantities"),
                           properties={"NetFloorArea": round(inner.area, 2)})

        active = [r for r in rules if r.get("type") != "diagrid" and in_range(n, r, n_max)]
        curtain = [r for r in active if r["type"] == "curtain"]
        if curtain:
            _curtain(C, st, s, t, slab, curtain[0])
        else:
            _walls_and_windows(C, st, s, t, slab, b["material"])
        for r in active:
            if r["type"] in ("balcony", "band"):
                if (n - r.get("from", 1)) % r.get("every", 1) == 0:
                    _band_or_balcony(C, st, s, slab, r, r["type"])
            elif r["type"] == "fins":
                _fins(C, st, s, r)
        prev = fp

    for r in rules:
        if r.get("type") == "diagrid":
            _diagrid(C, b, st_map, r)

    roof_st = API.root.create_entity(f, ifc_class="IfcBuildingStorey", name=f"{b['id']}-Roof")
    API.geometry.edit_object_placement(f, product=roof_st, matrix=np.eye(4))
    roof_st.Elevation = b["top_of_slab"]
    API.aggregate.assign_object(f, products=[roof_st], relating_object=building)
    _roof(C, b, roof_st)


def build(design: dict) -> ifcopenshell.file:
    f = API.project.create_file(version="IFC4")
    project = API.root.create_entity(f, ifc_class="IfcProject", name=design["name"])
    units = [API.unit.add_si_unit(f, unit_type=t) for t in ("LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT")]
    API.unit.assign_unit(f, units=units)
    model = API.context.add_context(f, context_type="Model")
    body = API.context.add_context(f, context_type="Model", context_identifier="Body",
                                   target_view="MODEL_VIEW", parent=model)
    C = Ctx(f, body)

    site = API.root.create_entity(f, ifc_class="IfcSite", name="Site")
    API.aggregate.assign_object(f, products=[site], relating_object=project)
    sd = design["site"]
    rings = [p["ring"] for p in sd["parcels"]] or ([sd["boundary"]] if sd["boundary"] else [])
    if rings:
        rep = f.createIfcShapeRepresentation(body, "Body", "SweptSolid",
                                             [plan_solid(f, r, -0.05, 0.05) for r in rings])
        API.geometry.assign_representation(f, product=site, representation=rep)
        _identity(f, site)
    if sd["parcels"]:
        API.pset.edit_pset(f, pset=API.pset.add_pset(f, product=site, name="Panorama_Site"),
                           properties={"Parcels": ", ".join(p["no"] or "?" for p in sd["parcels"])})
    for b in design["buildings"]:
        _add_building(C, site, b)
    return f
