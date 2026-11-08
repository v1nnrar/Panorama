# Panorama Hotel — Architectural Plan

Working repository for the Panorama Hotel project: documenting the client's current
scheme, then developing and modelling our new design.

## Workflow

1. **Brief & parameters** — site, programme, room mix, areas, budget → `01_brief/`
2. **Regulations** — zoning, height, setbacks, plot ratio, fire, accessibility, parking → `02_regulations/`
3. **Existing scheme** — client's current renders and a reconstructed model matching them → `03_existing/`
4. **Proposed design** — our new building, design intent and model → `04_proposed/`
5. **Drawings** — plans, sections, elevations, site plan → `05_drawings/`
6. **Reports** — area schedules, compliance checks, comparisons → `06_reports/`

## Setup & build

```bash
./setup.sh                                                    # Blender (bpy) + IfcOpenShell venv
.venv/bin/python build.py examples/test_block/params.yaml --render
```

Each scheme is one parameters YAML → IFC (BIM) → Blender `.blend` / `.glb` / renders → DXF plans,
area schedule (XLSX) and compliance report. See `CLAUDE.md` for the full stack, conventions and the
8 project agents in `.claude/agents/`.

## Status

- [x] Toolchain set up and tested (`examples/test_block`)
- [ ] Project parameters received
- [ ] Regulations received
- [ ] Current renders received
- [ ] Existing scheme modelled
- [ ] Proposed design modelled
