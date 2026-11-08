#!/usr/bin/env bash
# One-time environment setup: Python venv with Blender (bpy), IfcOpenShell and helpers.
set -euo pipefail
cd "$(dirname "$0")"
# Mesa EGL so Blender Workbench (fast clay renders) runs headless
if ! ldconfig -p | grep -q libEGL.so.1; then (apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq libegl1 libgl1-mesa-dri libgbm1) || echo "EGL install skipped"; fi
command -v uv >/dev/null || pip install -q uv
[ -d .venv ] || uv venv .venv --python 3.13
uv pip install -q --python .venv/bin/python -r requirements.txt
.venv/bin/python -c "import bpy, ifcopenshell; print('Blender', bpy.app.version_string, '| IfcOpenShell', ifcopenshell.version)"
