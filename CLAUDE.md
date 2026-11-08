# Panorama Hotel — project instructions

Architectural plan for the Panorama Hotel: first a faithful model of the client's **existing scheme**
(rebuilt from their renders), then our **proposed** new building.

## Stack
- **Blender 5.2 (`bpy`)** for scene, materials, renders (Cycles CPU / Workbench), `.blend` and `.glb`
- **IfcOpenShell 0.9** for the BIM model (IFC4); opens in Blender with the **Bonsai** add-on on desktop
- **Shapely** for site geometry, **ezdxf** for DXF drawings, **pandas** for XLSX schedules
- Environment: `./setup.sh` (creates `.venv`). Always run Python as `.venv/bin/python`.

## Single source of truth
Each scheme is ONE parameters YAML. Every output is generated from it — never hand-edit generated files.

```
params YAML ──► pipeline/build_ifc.py ──► model.ifc
                                    └──► pipeline/blender_scene.py ──► model.blend, model.glb, render_*.png
            └──► pipeline/analysis.py ──► report.md, metrics.json, area_schedule.xlsx, drawings/*.dxf|png
```

Build: `.venv/bin/python build.py <params.yaml> [--render] [--engine WORKBENCH] [--rules <rules.yaml>]`
Use `--engine WORKBENCH` for fast clay checks (seconds); Cycles (~30 s/camera) for presentation.

## Folders
| Folder | Content |
|---|---|
| `01_brief/` | client brief, `programme.yaml` (room mix, area targets) |
| `02_regulations/` | source documents + `rules.yaml` (machine-checkable limits, each with a source) |
| `03_existing/` | `renders/` (client images), `params.yaml`, `model/` outputs, `overlays/` |
| `04_proposed/` | `design/` (intent, sketches), `params.yaml`, `model/` outputs |
| `05_drawings/` | issued drawing sets |
| `06_reports/` | compliance, comparison existing vs proposed |
| `examples/test_block/` | pipeline test with PLACEHOLDER numbers — not project data |

## Conventions
- Units: metres. Local site grid: x = east, y = north, z = 0 at ground floor finished level.
- Footprints are polygons; the pipeline makes them CCW. Footprint = outer face of the exterior wall.
- Every number taken from a document records its source (file + page/article) in a YAML comment.
  Every **assumed** number is marked `# ASSUMED: <reason>` so it can be replaced later.
- Rules in `rules.yaml` use metrics from `pipeline/analysis.py::metrics` (`height_top_of_parapet_m`,
  `storeys_above_ground`, `built_up_ratio`, `plot_ratio_far`, `min_setback_m`, `gfa_m2`, …).
  If a rule needs a new metric, add it to `metrics()` first.

## Agents (`.claude/agents/`)
| Agent | Writes | Never |
|---|---|---|
| regulations-analyst | `02_regulations/rules.yaml`, summaries | touches geometry |
| brief-analyst | `01_brief/programme.yaml` | touches geometry |
| render-reconstructor | `03_existing/params.yaml`, overlays | edits the pipeline code |
| bim-modeler | `params.yaml` files, `pipeline/*.py` | judges compliance |
| drawings-producer | `05_drawings/` | changes the model |
| compliance-checker | `06_reports/compliance_*.md` | changes the model or rules |
| visualizer | renders, web viewer, presentation images | changes geometry |
| design-reviewer | `06_reports/review_*.md` | changes files outside reports |

Only **bim-modeler** changes geometry. Run **compliance-checker** after every model change.
