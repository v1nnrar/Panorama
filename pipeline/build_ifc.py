"""Build an IFC4 BIM model from a normalised design dict (see params.py)."""
from __future__ import annotations

import math

import numpy as np
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
from shapely.geometry import Polygon

API = ifcopenshell.api


def _extrusion(f, ctx, pts2d, depth, z0=0.0):
    pts = [f.createIfcCartesianPoint((float(x), float(y))) for x, y in pts2d]
    profile = f.createIfcArbitraryClosedProfileDef("AREA", None, f.createIfcPolyline(pts + [pts[0]]))
    pos = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, float(z0))), None, None)
    solid = f.createIfcExtrudedAreaSolid(profile, pos, f.createIfcDirection((0.0, 0.0, 1.0)), float(depth))
    return f.createIfcShapeRepresentation(ctx, "Body", "SweptSolid", [solid])


def _place(f, product, z):
    m = np.eye(4)
    m[2, 3] = z
    API.geometry.edit_object_placement(f, product=product, matrix=m)


def _element(f, ctx, cls, name, pts, depth, z, z0=0.0, container=None, predefined=None):
    el = API.root.create_entity(f, ifc_class=cls, name=name, predefined_type=predefined)
    API.geometry.assign_representation(f, product=el, representation=_extrusion(f, ctx, pts, depth, z0))
    _place(f, el, z)
    if container is not None:
        API.spatial.assign_container(f, products=[el], relating_structure=container)
    return el


def inset_ring(pts, t):
    """Inner ring of a CCW polygon offset inward by t, vertex-for-vertex (mitred corners)."""
    n, out = len(pts), []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        lines = []
        for a, b in ((p0, p1), (p1, p2)):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
            lines.append(((a[0] + nx * t, a[1] + ny * t), ((b[0] - a[0]) / L, (b[1] - a[1]) / L)))
        (q1, d1), (q2, d2) = lines
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            out.append(q2)
        else:
            k = ((q2[0] - q1[0]) * d2[1] - (q2[1] - q1[1]) * d2[0]) / den
            out.append((q1[0] + d1[0] * k, q1[1] + d1[1] * k))
    return out


def _wall_rect(a, b, t):
    """Rectangle for a wall whose outer face runs a->b, thickness inward (left of a->b for CCW)."""
    (x1, y1), (x2, y2) = a, b
    L = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L  # inward normal for CCW polygon
    return [(x1, y1), (x2, y2), (x2 + nx * t, y2 + ny * t), (x1 + nx * t, y1 + ny * t)], L, (nx, ny)


def _window_positions(L, w):
    spacing, margin = w["spacing"], w["edge_margin"]
    n = int((L - 2 * margin - w["width"]) // spacing) + 1 if L - 2 * margin >= w["width"] else 0
    if n <= 0:
        return []
    span = (n - 1) * spacing
    start = (L - span) / 2
    return [start + i * spacing for i in range(n)]


def build(design: dict) -> ifcopenshell.file:
    f = API.project.create_file(version="IFC4")
    project = API.root.create_entity(f, ifc_class="IfcProject", name=design["name"])
    units = [API.unit.add_si_unit(f, unit_type=t) for t in ("LENGTHUNIT", "AREAUNIT", "VOLUMEUNIT")]
    API.unit.assign_unit(f, units=units)
    model = API.context.add_context(f, context_type="Model")
    body = API.context.add_context(f, context_type="Model", context_identifier="Body",
                                   target_view="MODEL_VIEW", parent=model)

    site = API.root.create_entity(f, ifc_class="IfcSite", name="Site")
    building = API.root.create_entity(f, ifc_class="IfcBuilding", name=design["name"])
    API.aggregate.assign_object(f, products=[site], relating_object=project)
    API.aggregate.assign_object(f, products=[building], relating_object=site)
    if design["site"]["boundary"]:
        API.geometry.assign_representation(
            f, product=site, representation=_extrusion(f, body, design["site"]["boundary"], 0.05, -0.05))
        _place(f, site, 0.0)

    t, slab = design["exterior_wall"], design["slab_thickness"]
    storey_entities = []
    for s in design["storeys"]:
        st = API.root.create_entity(f, ifc_class="IfcBuildingStorey", name=s["name"])
        _place(f, st, s["elevation"])
        st.Elevation = s["elevation"]
        API.aggregate.assign_object(f, products=[st], relating_object=building)
        API.pset.edit_pset(f, pset=API.pset.add_pset(f, product=st, name="Panorama_Storey"),
                           properties={"Use": s["use"], "Height": s["height"]})
        storey_entities.append(st)
        z, fp = s["elevation"], s["footprint"]

        _element(f, body, "IfcSlab", f"{s['name']} slab", fp, slab, z, container=st, predefined="FLOOR")

        inner = Polygon(fp).buffer(-t, join_style="mitre")
        sp = _element(f, body, "IfcSpace", f"{s['name']} floor area", list(inner.exterior.coords)[:-1],
                      s["height"] - slab, z, z0=slab, predefined="INTERNAL")
        API.aggregate.assign_object(f, products=[sp], relating_object=st)
        API.pset.edit_pset(f, pset=API.pset.add_pset(f, product=sp, name="Qto_SpaceBaseQuantities"),
                           properties={"NetFloorArea": round(inner.area, 2)})

        wall_h = s["height"] - slab
        ring = inset_ring(fp, t)
        for i, a in enumerate(fp):
            j = (i + 1) % len(fp)
            b = fp[j]
            _, L, (nx, ny) = _wall_rect(a, b, t)
            rect = [a, b, ring[j], ring[i]]
            wall = _element(f, body, "IfcWall", f"{s['name']} ext wall {i + 1}", rect, wall_h, z, z0=slab,
                            container=st, predefined="SOLIDWALL")
            w = s["windows"]
            if not w:
                continue
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            for k, d in enumerate(_window_positions(L, w)):
                c0, c1 = d - w["width"] / 2, d + w["width"] / 2
                p = lambda dd, off: (a[0] + ux * dd + nx * off, a[1] + uy * dd + ny * off)
                o_pts = [p(c0, -0.05), p(c1, -0.05), p(c1, t + 0.05), p(c0, t + 0.05)]
                opening = _element(f, body, "IfcOpeningElement", f"{wall.Name} opening {k + 1}", o_pts,
                                   w["height"], z, z0=slab + w["sill"])
                API.feature.add_feature(f, feature=opening, element=wall)
                g_pts = [p(c0, t * 0.4), p(c1, t * 0.4), p(c1, t * 0.6), p(c0, t * 0.6)]
                win = _element(f, body, "IfcWindow", f"{wall.Name} window {k + 1}", g_pts, w["height"], z,
                               z0=slab + w["sill"], container=st, predefined="WINDOW")
                API.feature.add_filling(f, opening=opening, element=win)

    # Roof slab + parapet on top of the last storey
    top = design["storeys"][-1]
    roof_st = API.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Roof")
    _place(f, roof_st, design["top_of_slab"])
    roof_st.Elevation = design["top_of_slab"]
    API.aggregate.assign_object(f, products=[roof_st], relating_object=building)
    _element(f, body, "IfcRoof", "Roof slab", top["footprint"], slab, design["top_of_slab"], container=roof_st,
             predefined="FLAT_ROOF")
    par = design["roof"].get("parapet", 0)
    if par:
        fp = top["footprint"]
        ring = inset_ring(fp, 0.25)
        for i, a in enumerate(fp):
            j = (i + 1) % len(fp)
            rect = [a, fp[j], ring[j], ring[i]]
            _element(f, body, "IfcWall", f"Parapet {i + 1}", rect, par, design["top_of_slab"], z0=slab,
                     container=roof_st, predefined="PARAPET")
    return f
