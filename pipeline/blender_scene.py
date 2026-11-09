"""Turn an IFC model into a Blender scene: meshes with materials, site context, landscape, sun, cameras.

Outputs a .blend (open in desktop Blender), a .glb of the scheme only (web viewer) and optional renders.
Materials come from the IFC material name (see PALETTE); context comes from 00_site/context.glb (PSG website).
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import bpy  # noqa: I001  (bpy must load before bmesh)
import bmesh
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import shapely
from mathutils import Vector
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

# name: (RGBA, roughness, transmission, metallic)
PALETTE = {
    "Render white": ((0.87, 0.86, 0.83, 1), 0.85, 0, 0),
    "Render grey": ((0.55, 0.55, 0.55, 1), 0.85, 0, 0),
    "Render light grey": ((0.74, 0.74, 0.73, 1), 0.8, 0, 0),
    "Concrete white": ((0.90, 0.89, 0.86, 1), 0.7, 0, 0),
    "Concrete grey": ((0.52, 0.52, 0.52, 1), 0.8, 0, 0),
    "Glass": ((0.10, 0.14, 0.17, 1), 0.04, 0, 0.35),
    "Glass dark": ((0.03, 0.04, 0.05, 1), 0.04, 0, 0.5),
    "Glass railing": ((0.70, 0.80, 0.84, 1), 0.02, 0.92, 0),
    "Aluminium": ((0.70, 0.71, 0.72, 1), 0.35, 0, 0.7),
    "Aluminium white": ((0.93, 0.93, 0.91, 1), 0.4, 0, 0.1),
    "Steel white": ((0.96, 0.96, 0.94, 1), 0.35, 0, 0.1),
    "Timber": ((0.42, 0.25, 0.14, 1), 0.7, 0, 0),
    "Bronze": ((0.42, 0.27, 0.12, 1), 0.35, 0, 0.85),
    "Planting": ((0.13, 0.27, 0.08, 1), 1.0, 0, 0),
    "PV": ((0.03, 0.05, 0.11, 1), 0.15, 0, 0.3),
    "Roof metal": ((0.80, 0.80, 0.80, 1), 0.4, 0, 0.6),
    "Paving": ((0.60, 0.58, 0.54, 1), 0.9, 0, 0),
    "Lawn": ((0.22, 0.38, 0.12, 1), 1.0, 0, 0),
    "Bark": ((0.22, 0.15, 0.09, 1), 0.9, 0, 0),
    "Foliage": ((0.15, 0.30, 0.09, 1), 0.95, 0, 0),
    "Ground": ((0.42, 0.44, 0.40, 1), 0.95, 0, 0),
}
CLASS_DEFAULT = {"IfcWindow": "Glass", "IfcSite": "Paving", "IfcSpace": "Render white"}
SKIP = {"IfcOpeningElement"}


def _reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _material(name, spec=None):
    m = bpy.data.materials.get(name)
    if m:
        return m
    rgba, rough, trans, metal = spec or PALETTE.get(name, ((0.8, 0.8, 0.8, 1), 0.8, 0, 0))
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if trans:
        bsdf.inputs["Transmission Weight"].default_value = trans
    m.diffuse_color = rgba if not trans else (*rgba[:3], 0.35)
    return m


def _collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col


def import_ifc(ifc_path: str, overrides: dict | None = None):
    for k, v in (overrides or {}).items():
        PALETTE[k] = (tuple(v[0]), v[1], v[2] if len(v) > 2 else 0, v[3] if len(v) > 3 else 0)
    f = ifcopenshell.open(ifc_path)
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    root = _collection("Scheme")
    it = ifcopenshell.geom.iterator(settings, f, 4)
    if not it.initialize():
        raise RuntimeError("IFC geometry iterator found nothing to process")
    while True:
        shape = it.get()
        el = f.by_id(shape.id)
        cls = el.is_a()
        if cls not in SKIP:
            v, fc = shape.geometry.verts, shape.geometry.faces
            verts = [tuple(v[i:i + 3]) for i in range(0, len(v), 3)]
            faces = [tuple(fc[i:i + 3]) for i in range(0, len(fc), 3)]
            mesh = bpy.data.meshes.new(el.Name or cls)
            mesh.from_pydata(verts, [], faces)
            mesh.validate()
            obj = bpy.data.objects.new(el.Name or cls, mesh)
            obj["ifc_class"], obj["ifc_guid"] = cls, el.GlobalId
            mat = ifcopenshell.util.element.get_material(el)
            mname = getattr(mat, "Name", None) or CLASS_DEFAULT.get(cls, "Render white")
            obj.data.materials.append(_material(mname))
            _collection(cls, root).objects.link(obj)
        if not it.next():
            break
    if bpy.data.collections.get("IfcSpace"):
        bpy.data.collections["IfcSpace"].hide_render = True
        bpy.data.collections["IfcSpace"].hide_viewport = True


# ----------------------------------------------------------------------------------------------- context
def add_context_glb(path, exclude_polys, drop=0.12):
    """Import the PSG surroundings model; remove geometry inside `exclude_polys` (buildings we model)."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    col = _collection("Context")
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
        o["context"] = True
    for o in new:
        if o.type != "MESH":
            continue
        group = o.parent.name if o.parent else ""
        o["context_group"] = group
        for m in o.data.materials:
            if m and m.node_tree:
                b = m.node_tree.nodes.get("Principled BSDF")
                if b:
                    m.diffuse_color = b.inputs["Base Color"].default_value
        if exclude_polys and group in ("neighbours", "roofkit", "plant", "towers"):
            bm = bmesh.new()
            bm.from_mesh(o.data)
            mw = o.matrix_world
            kill = [fa for fa in bm.faces
                    if any(p.contains(Point((mw @ fa.calc_center_median()).x, (mw @ fa.calc_center_median()).y))
                           for p in exclude_polys)]
            bmesh.ops.delete(bm, geom=kill, context="FACES")
            bm.to_mesh(o.data)
            bm.free()
    layer_drop = {"ground": 0.40, "parks": 0.32, "streets_minor": 0.26, "streets_major": 0.22, "paths": 0.18}
    for o in new:
        if o.parent is None:
            o.location.z -= layer_drop.get(o.name, drop)
    return col


def add_context_json(path, radius=350.0):
    """Fallback: neighbouring buildings as plain grey extrusions."""
    data = json.loads(Path(path).read_text())
    col = _collection("Context")
    mat = _material("Context", ((0.80, 0.80, 0.79, 1), 0.9, 0, 0))
    for i, c in enumerate(data["buildings"]):
        poly = c["poly"][:-1] if c["poly"][0] == c["poly"][-1] else c["poly"]
        cx, cy = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
        if math.hypot(cx, cy) > radius or c.get("name", "").startswith("E_existing"):
            continue
        z0, z1, n = c.get("z0", 0.0), c["h"], len(poly)
        verts = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
        faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        faces += [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        mesh = bpy.data.meshes.new(f"ctx_{i}")
        mesh.from_pydata(verts, [], faces)
        mesh.validate()
        obj = bpy.data.objects.new(c.get("name") or f"ctx_{i}", mesh)
        obj["context"] = True
        obj.data.materials.append(mat)
        col.objects.link(obj)


# ----------------------------------------------------------------------------------------------- landscape
def _poly_mesh(name, geom, z, mat, col):
    polys = [geom] if geom.geom_type == "Polygon" else [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]
    verts, faces = [], []
    for p in polys:
        tris = shapely.constrained_delaunay_triangles(p)
        for t in tris.geoms:
            cs = list(t.exterior.coords)[:3]
            base = len(verts)
            verts += [(x, y, z) for x, y in cs]
            faces.append((base, base + 1, base + 2))
    if not faces:
        return None
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    for fa in mesh.polygons:
        if fa.normal.z < 0:
            fa.flip()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(_material(mat))
    col.objects.link(obj)
    return obj


def add_landscape(design):
    land = design.get("landscape") or {}
    sd = design["site"]
    col = _collection("Landscape")
    site = unary_union([Polygon(p["ring"]) for p in sd["parcels"]]) if sd["parcels"] else None
    footprints = unary_union([Polygon(b["storeys"][0]["footprint"]) for b in design["buildings"]
                              if not b.get("below_ground")])
    if site is not None and land.get("lawn", True):
        lawn = site.buffer(-land.get("edge_paving", 2.0)).difference(footprints.buffer(land.get("building_paving", 3.0)))
        for p in land.get("paths", []):
            lawn = lawn.difference(Polygon(p))
        _poly_mesh("Courtyard lawn", lawn, 0.03, "Lawn", col)
    for k, p in enumerate(land.get("lawns", [])):
        _poly_mesh(f"Lawn {k + 1}", Polygon(p), 0.03, "Lawn", col)

    trees = list(land.get("trees", []))
    if land.get("courtyard_trees") and site is not None:
        cfg = land["courtyard_trees"]
        rng = random.Random(cfg.get("seed", 7))
        zone = site.buffer(-3).difference(footprints.buffer(cfg.get("clear", 6)))
        for p in land.get("paths", []):
            zone = zone.difference(Polygon(p).buffer(1.5))
        x0, y0, x1, y1 = zone.bounds
        step = cfg.get("spacing", 9.0)
        y = y0
        while y < y1:
            x = x0 + (rng.random() * step)
            while x < x1:
                px, py = x + rng.uniform(-2, 2), y + rng.uniform(-2, 2)
                if zone.contains(Point(px, py)):
                    trees.append([px, py, rng.uniform(*cfg.get("height", [6, 11]))])
                x += step
            y += step * 0.87
    if sd.get("trees"):
        data = json.loads(Path(sd["trees"]).read_text())
        r = land.get("context_tree_radius", 450)
        trees += [t for t in data if math.hypot(t[0], t[1]) < r and (site is None or not site.contains(Point(t[0], t[1])))]
    _trees(trees, col)


def _trees(trees, col):
    if not trees:
        return
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1, depth=1)
    trunk = bpy.context.active_object
    trunk_mesh = trunk.data
    trunk_mesh.materials.append(_material("Bark"))
    bpy.data.objects.remove(trunk)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
    crown = bpy.context.active_object
    crown_mesh = crown.data
    crown_mesh.materials.append(_material("Foliage"))
    bpy.data.objects.remove(crown)
    for i, (x, y, h) in enumerate(trees):
        h = max(float(h), 3.0)
        t = bpy.data.objects.new(f"tree_trunk_{i}", trunk_mesh)
        t.location = (x, y, h * 0.2)
        t.scale = (0.18, 0.18, h * 0.4)
        c = bpy.data.objects.new(f"tree_crown_{i}", crown_mesh)
        c.location = (x, y, h * 0.62)
        c.scale = (h * 0.27, h * 0.27, h * 0.36)
        col.objects.link(t)
        col.objects.link(c)


# ----------------------------------------------------------------------------------------------- stage & render
def _bbox():
    pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == "MESH" and not o.get("context")
           and o.get("ifc_class") not in ("IfcSite", "IfcSpace", None) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def stage(render_cfg: dict | None = None, ground=True):
    cfg = render_cfg or {}
    scene = bpy.context.scene
    lo, hi = _bbox()
    centre, size = (lo + hi) / 2, (hi - lo).length

    if ground:
        bpy.ops.mesh.primitive_plane_add(size=max(size * 8, 900), location=(centre.x, centre.y, -0.2))
        g = bpy.context.active_object
        g.name = "Ground"
        g.data.materials.append(_material("Ground"))

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = cfg.get("sun_strength", 4.0)
    sun.data.angle = math.radians(1.5)
    az, alt = math.radians(cfg.get("sun_azimuth", 210)), math.radians(cfg.get("sun_altitude", 40))
    # Blender sun shines along its local -Z; point it from the given azimuth (0 = N, clockwise) and altitude
    d = Vector((math.sin(az) * math.cos(alt), math.cos(az) * math.cos(alt), math.sin(alt)))
    sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.62, 0.74, 0.88, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = cfg.get("sky_strength", 0.9)
    world.color = (0.62, 0.74, 0.88)
    scene.world = world

    cams = cfg.get("cameras") or [{"name": "aerial_SW", "dir": [-1.0, -1.3, 0.8]}]
    for c in cams:
        cam = bpy.data.objects.new(c["name"], bpy.data.cameras.new(c["name"]))
        cam.data.lens = c.get("lens", 35)
        cam.data.clip_end = 5000
        if "location" in c:
            cam.location = Vector(c["location"])
        else:
            dd = Vector(c["dir"]).normalized()
            cam.location = centre + dd * size * c.get("distance", 1.6)
        target = Vector(c["target"]) if "target" in c else centre
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        if c.get("shift_y"):
            cam.data.shift_y = c["shift_y"]
        scene.collection.objects.link(cam)
    scene.camera = bpy.data.objects[cams[0]["name"]]
    return cams


def hide_buildings(ids):
    """Hide the objects of the given building ids for one camera (a client render that omits a building).
    Objects are named after their storey ('C1-L3 ...') or building ('C1 roof slab')."""
    out = []
    for o in bpy.data.objects:
        if not o.hide_render and any(o.name.startswith(i + "-") or o.name.startswith(i + " ") for i in ids):
            o.hide_render = True
            out.append(o)
    return out


def render(out_dir: Path, cams, engine="CYCLES", samples=48, only=None):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH" if engine == "WORKBENCH" else "CYCLES"
    if scene.render.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
    else:
        sh = scene.display.shading
        sh.light, sh.color_type = "STUDIO", "MATERIAL"
        sh.show_shadows = sh.show_cavity = True
        sh.background_type = "WORLD"
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.file_format = "PNG"
    paths = []
    for c in cams:
        if only and c["name"] not in only:
            continue
        scene.render.resolution_x, scene.render.resolution_y = c.get("resolution", [1600, 1000])
        scene.camera = bpy.data.objects[c["name"]]
        scene.render.filepath = str(out_dir / f"render_{c['name']}.png")
        hidden = hide_buildings(c.get("hide", []))
        bpy.ops.render.render(write_still=True)
        for o in hidden:
            o.hide_render = False
        paths.append(scene.render.filepath)
    return paths


def build_scene(ifc_path: str, out_dir: Path, design: dict, do_render=False, engine="CYCLES", only=None):
    _reset()
    import_ifc(ifc_path, design.get("materials"))
    sd = design["site"]
    scheme_objs = [o for o in bpy.data.objects if o.get("ifc_class")]
    excl = [Polygon(p).buffer(1.0) for p in sd.get("context_exclude", [])]
    if sd.get("context_glb"):
        excl += [Polygon(b["storeys"][0]["footprint"]).buffer(0.5) for b in design["buildings"]]
        add_context_glb(sd["context_glb"], excl)
    elif sd.get("context"):
        add_context_json(sd["context"])
    add_landscape(design)
    cams = stage(design.get("render"), ground=not sd.get("context_glb"))
    out_dir.mkdir(parents=True, exist_ok=True)
    blend, glb = out_dir / "model.blend", out_dir / "model.glb"
    bpy.ops.object.select_all(action="DESELECT")
    for o in scheme_objs:
        if o.visible_get():
            o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_selection=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    renders = render(out_dir, cams, engine=engine, samples=design.get("render", {}).get("samples", 48),
                     only=only) if do_render else []
    return {"blend": str(blend), "glb": str(glb), "renders": renders}
