#!/usr/bin/env python
"""Export a scheme's building model for Snaptrude (or any other BIM/massing tool).

Reads the generated <model>/model.blend (never edit it by hand — rebuild with build.py first) and writes
<model>/snaptrude/ with the scheme buildings only: no context city, landscape, trees, site plate or IfcSpace
volumes. One object per building and element type (e.g. "A CurtainWall", "C2 Window").
Units: metres. Origin: Milevská 7 (00_site/survey/README.md), x = east, y = north, z = 0 at GF.

  scheme.glb        glTF binary, materials as colours (Y-up as glTF requires)
  scheme.fbx        FBX 7.4 — the file for Snaptrude. Geometry written in cm with unit scale 1, so it lands at true
                    size whether the importer reads the FBX unit header or assumes cm; Y-up FBX convention
  scheme.obj/.mtl   Wavefront OBJ, Y-up (the OBJ convention)
  scheme.ifc        copy of model.ifc (IFC4) — full BIM elements: walls, slabs, curtain walls, windows, spaces

Usage: .venv/bin/python tools/export_snaptrude.py 03_existing/model
"""
import re
import shutil
import sys
from pathlib import Path

import bpy
import bmesh  # noqa: E402 — only importable once bpy is loaded

SKIP = {"IfcSpace", "IfcSite"}   # room volumes and the site plate: Snaptrude makes its own


def main(model_dir):
    model_dir = Path(model_dir).resolve()
    out = model_dir / "snaptrude"
    out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(model_dir / "model.blend"))
    scheme = bpy.data.collections["Scheme"]
    groups = {}   # (building id, IFC class) -> objects; one merged object each keeps the import light
    for c in scheme.children:
        if c.name in SKIP:
            continue
        for o in c.all_objects:
            if o.type == "MESH" and o.visible_get():
                groups.setdefault((re.split(r"[- ]", o.name)[0], c.name), []).append(o)
    dg = bpy.context.evaluated_depsgraph_get()
    objs = []
    for (bid, ifc), members in sorted(groups.items()):
        merged = bpy.data.meshes.new(f"{bid} {ifc}")
        bm = bmesh.new()
        mats = []
        for o in members:
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
            me.transform(o.matrix_world)
            for p in me.polygons:   # remap material slots into the merged mesh
                m = me.materials[p.material_index] if me.materials else None
                if m not in mats:
                    mats.append(m)
                p.material_index = mats.index(m)
            bm.from_mesh(me)
            bpy.data.meshes.remove(me)
        bm.to_mesh(merged)
        bm.free()
        for m in mats:
            merged.materials.append(m)
        ob = bpy.data.objects.new(f"{bid} {ifc.removeprefix('Ifc')}", merged)
        bpy.context.scene.collection.objects.link(ob)
        objs.append(ob)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    print(f"{len(objs)} objects, {sum(len(o.data.polygons) for o in objs)} faces")

    bpy.ops.export_scene.gltf(filepath=str(out / "scheme.glb"), export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)
    bpy.ops.export_scene.fbx(filepath=str(out / "scheme.fbx"), use_selection=True, apply_unit_scale=True,
                             global_scale=1.0, apply_scale_options="FBX_SCALE_NONE", use_mesh_modifiers=True,
                             object_types={"MESH"},
                             axis_forward="-Z", axis_up="Y", path_mode="COPY")
    bpy.ops.wm.obj_export(filepath=str(out / "scheme.obj"), export_selected_objects=True, apply_modifiers=True,
                          export_materials=True, forward_axis="NEGATIVE_Z", up_axis="Y", export_uv=False)
    shutil.copyfile(model_dir / "model.ifc", out / "scheme.ifc")
    for f in sorted(out.iterdir()):
        print(f"{f.name:14s} {f.stat().st_size / 1e6:6.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "03_existing/model")
