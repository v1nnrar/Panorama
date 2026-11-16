#!/usr/bin/env python
"""Export a scheme's building model for Snaptrude (or any other BIM/massing tool).

Reads the generated <model>/model.blend (never edit it by hand — rebuild with build.py first) and writes
<model>/snaptrude/ with the scheme buildings only: no context city, landscape, trees, site plate or IfcSpace
volumes. Units: metres. Origin: Milevská 7 (00_site/survey/README.md), x = east, y = north, z = 0 at GF.

  scheme.glb        glTF binary, materials as colours (Y-up as glTF requires)
  scheme.fbx        FBX 7.4, metres (scale 1.0, Z-up converted to the FBX convention)
  scheme.obj/.mtl   Wavefront OBJ, Y-up (the OBJ convention)
  scheme.ifc        copy of model.ifc (IFC4) — full BIM elements: walls, slabs, curtain walls, windows, spaces

Usage: .venv/bin/python tools/export_snaptrude.py 03_existing/model
"""
import shutil
import sys
from pathlib import Path

import bpy

SKIP = {"IfcSpace", "IfcSite"}   # room volumes and the site plate: Snaptrude makes its own


def main(model_dir):
    model_dir = Path(model_dir).resolve()
    out = model_dir / "snaptrude"
    out.mkdir(exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(model_dir / "model.blend"))
    scheme = bpy.data.collections["Scheme"]
    objs = [o for c in scheme.children if c.name not in SKIP for o in c.all_objects
            if o.type == "MESH" and o.visible_get()]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    print(f"{len(objs)} objects, {sum(len(o.data.polygons) for o in objs)} faces")

    bpy.ops.export_scene.gltf(filepath=str(out / "scheme.glb"), export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)
    bpy.ops.export_scene.fbx(filepath=str(out / "scheme.fbx"), use_selection=True, apply_unit_scale=True,
                             global_scale=1.0, use_mesh_modifiers=True, object_types={"MESH"},
                             axis_forward="-Z", axis_up="Y", path_mode="COPY")
    bpy.ops.wm.obj_export(filepath=str(out / "scheme.obj"), export_selected_objects=True, apply_modifiers=True,
                          export_materials=True, forward_axis="NEGATIVE_Z", up_axis="Y", export_uv=False)
    shutil.copyfile(model_dir / "model.ifc", out / "scheme.ifc")
    for f in sorted(out.iterdir()):
        print(f"{f.name:14s} {f.stat().st_size / 1e6:6.1f} MB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "03_existing/model")
