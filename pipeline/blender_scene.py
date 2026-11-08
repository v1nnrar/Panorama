"""Turn an IFC model into a Blender scene: meshes, materials, ground, sun, camera.

Outputs a .blend (open in desktop Blender), a .glb (web viewer) and optional renders.
"""
from __future__ import annotations

import math
from pathlib import Path

import bpy
import ifcopenshell
import ifcopenshell.geom
from mathutils import Vector

DEFAULT_MATERIALS = {  # RGBA base colour, roughness, (transmission)
    "IfcWall": ((0.86, 0.84, 0.80, 1), 0.8, 0.0),
    "IfcSlab": ((0.55, 0.55, 0.56, 1), 0.7, 0.0),
    "IfcRoof": ((0.35, 0.35, 0.37, 1), 0.8, 0.0),
    "IfcWindow": ((0.30, 0.42, 0.50, 1), 0.05, 0.85),
    "IfcSite": ((0.36, 0.50, 0.30, 1), 0.9, 0.0),
    "IfcSpace": ((0.9, 0.7, 0.3, 0.15), 0.5, 0.0),
}
SKIP = {"IfcOpeningElement"}


def _reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _material(name, rgba, rough, trans):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = rough
    if trans:
        bsdf.inputs["Transmission Weight"].default_value = trans
    m.diffuse_color = rgba
    return m


def import_ifc(ifc_path: str, overrides: dict | None = None):
    f = ifcopenshell.open(ifc_path)
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    specs = {**DEFAULT_MATERIALS, **{k: tuple(v) for k, v in (overrides or {}).items()}}
    mats = {cls: _material(cls.removeprefix("Ifc"), *spec) for cls, spec in specs.items()}
    collections = {}
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
            mat = mats.get(cls)
            if mat:
                obj.data.materials.append(mat)
            col = collections.get(cls)
            if col is None:
                col = collections[cls] = bpy.data.collections.new(cls)
                bpy.context.scene.collection.children.link(col)
            col.objects.link(obj)
        if not it.next():
            break
    if "IfcSpace" in collections:  # spaces are analytical, hide from renders
        collections["IfcSpace"].hide_render = True
        bpy.context.view_layer.layer_collection.children["IfcSpace"].hide_viewport = True
    return collections


def add_context(path: str | None, centre_xy=(0, 0), radius=350.0):
    """Neighbouring buildings as plain grey extrusions (not part of the IFC)."""
    if not path:
        return
    import json
    data = json.loads(Path(path).read_text())
    col = bpy.data.collections.new("Context")
    bpy.context.scene.collection.children.link(col)
    mat = _material("Context", (0.80, 0.80, 0.79, 1), 0.9, 0.0)
    for i, c in enumerate(data["buildings"]):
        poly = c["poly"][:-1] if c["poly"][0] == c["poly"][-1] else c["poly"]
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        if math.hypot(cx - centre_xy[0], cy - centre_xy[1]) > radius:
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


def _bbox():
    pts = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == "MESH" and not o.get("context")
           and o.get("ifc_class") not in ("IfcSite", "IfcSpace", None) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def stage(render_cfg: dict | None = None):
    cfg = render_cfg or {}
    scene = bpy.context.scene
    lo, hi = _bbox()
    centre, size = (lo + hi) / 2, (hi - lo).length

    bpy.ops.mesh.primitive_plane_add(size=max(size * 8, 900), location=(centre.x, centre.y, -0.06))
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground.data.materials.append(_material("Ground", (0.42, 0.44, 0.40, 1), 0.95, 0.0))

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = cfg.get("sun_strength", 4.0)
    sun.data.angle = math.radians(1.5)
    az, alt = math.radians(cfg.get("sun_azimuth", 210)), math.radians(cfg.get("sun_altitude", 40))
    sun.rotation_euler = (math.pi / 2 - alt, 0, az)
    scene.collection.objects.link(sun)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.62, 0.74, 0.88, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    world.color = (0.62, 0.74, 0.88)  # Workbench background
    scene.world = world

    cams = cfg.get("cameras") or [{"name": "aerial_SW", "dir": [-1.0, -1.3, 0.8]},
                                  {"name": "street_SE", "dir": [1.2, -1.0, 0.12]}]
    for c in cams:
        cam = bpy.data.objects.new(c["name"], bpy.data.cameras.new(c["name"]))
        cam.data.lens = c.get("lens", 35)
        cam.data.clip_end = 5000
        if "location" in c:
            cam.location = Vector(c["location"])
        else:
            d = Vector(c["dir"]).normalized()
            cam.location = centre + d * size * c.get("distance", 1.6)
        target = Vector(c["target"]) if "target" in c else centre
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        scene.collection.objects.link(cam)
    scene.camera = bpy.data.objects[cams[0]["name"]]
    return [c["name"] for c in cams]


def render(out_dir: Path, cameras, engine="CYCLES", samples=48, res=(1600, 1000)):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH" if engine == "WORKBENCH" else "CYCLES"
    if scene.render.engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
    else:
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.background_type = "WORLD"
    scene.view_settings.view_transform = "AgX"
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.image_settings.file_format = "PNG"
    paths = []
    for name in cameras:
        scene.camera = bpy.data.objects[name]
        scene.render.filepath = str(out_dir / f"render_{name}.png")
        bpy.ops.render.render(write_still=True)
        paths.append(scene.render.filepath)
    return paths


def build_scene(ifc_path: str, out_dir: Path, design: dict, do_render=False, engine="CYCLES"):
    _reset()
    import_ifc(ifc_path, design.get("materials"))
    add_context(design["site"].get("context"))
    cams = stage(design.get("render"))
    out_dir.mkdir(parents=True, exist_ok=True)
    blend = out_dir / "model.blend"
    glb = out_dir / "model.glb"
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", use_visible=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    renders = render(out_dir, cams, engine=engine, samples=design.get("render", {}).get("samples", 48)) \
        if do_render else []
    return {"blend": str(blend), "glb": str(glb), "renders": renders}
