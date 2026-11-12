"""3D blocking of the pink podium wing (design sketch, not the pipeline model).

Blocks out the client's preferred concept image, 04_proposed/design/pink_podium/08_park_B.png, in Blender
and renders a fixed camera set (same distance for every view) to use as structure references for images.

    .venv/bin/python 04_proposed/design/pink_podium/blocking/build_blocking.py [--views view0,view4] [--samples 24]

All dimensions ASSUMED: plan and heights were read off 08_park_B.png (people in the image as scale), then
the plan was scaled x1.13 so the length (~70 m) fits the existing front-slab slot (C1+C2 = 71 x 24 m,
03_existing/params.yaml). Units: metres. x = right in the reference view, y = away from the camera.
"""
import argparse
import math
import os
import random

import bpy
import bmesh
import mathutils
import numpy as np
from shapely import delaunay_triangles
from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "renders")

# ------------------------------------------------------------------ design parameters (ASSUMED, see docstring)
K = 1.13                                                    # plan scale to the 71 m slot
# centre line from the high head (s=0) to the cafe tip (s=1)
CENTRE = [(-21, 8), (-13, 3.5), (-4, 1), (5, 1.5), (13, 1.5), (20, -0.5), (25, -3)]
WIDTH = [(0.0, 21.0), (0.2, 18.5), (0.42, 15.0), (0.62, 15.5), (0.82, 17.5), (1.0, 13.0)]   # s -> plan width
H_TOP = 16.5          # 4 storeys: GF 5.0 + 3 x 3.8 m, roof park level
FLOORS = [5.0, 8.8, 12.6]
H_LAWN = 3.6          # roof level of the low picnic lawn before it runs out into the ground
H_CAFE = 5.8          # crown of the cafe lattice arch
S_CAFE = 0.70         # the "pinch": front edge touches the ground here, cafe arch starts
INSET = 1.5           # glazing line behind the fin line
ROOF_T = 0.8
FIN_SPACING = 1.9
PORTAL = (0.44, 0.56)  # big arched opening in the front fin screen

CENTRE = [(x * K, y * K) for x, y in CENTRE]
WIDTH = [(s, w * K) for s, w in WIDTH]


def ss(t):
    t = min(1.0, max(0.0, t))
    return 3 * t * t - 2 * t ** 3


def lerp_table(tab, s):
    s = min(1.0, max(0.0, s))
    for (s0, v0), (s1, v1) in zip(tab, tab[1:]):
        if s <= s1:
            return v0 + (v1 - v0) * (s - s0) / (s1 - s0)
    return tab[-1][1]


def catmull(points, n=400):
    p = np.array(points, float)
    p = np.vstack([p[0] * 2 - p[1], p, p[-1] * 2 - p[-2]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for t in np.linspace(0, 1, n // (len(p) - 3), endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-2])
    return np.array(out)


CL_LINE = LineString(catmull(CENTRE))
L = CL_LINE.length
S_END = 1.0 + lerp_table(WIDTH, 1.0) / 2 / L          # s at the very tip (end cap)


def frame(s):
    """Point, tangent and left (= back) normal of the centre line at s in 0..1."""
    s = min(1.0, max(0.0, s))
    p = np.array(CL_LINE.interpolate(s * L).coords[0])
    q = np.array(CL_LINE.interpolate(min(1, s + 0.002) * L).coords[0])
    r = np.array(CL_LINE.interpolate(max(0, s - 0.002) * L).coords[0])
    t = q - r
    t /= np.linalg.norm(t)
    return p, t, np.array([-t[1], t[0]])


def st(x, y):
    """(s, t): s along the centre line (runs past 1 in the tip cap), t across: -1 front edge .. +1 back edge."""
    s = CL_LINE.project(Point(x, y)) / L
    p, tg, nrm = frame(s)
    d = np.array((x, y)) - p
    t = float(np.dot(d, nrm)) / (lerp_table(WIDTH, s) / 2)
    if s >= 0.999:
        s += max(0.0, float(np.dot(d, tg))) / L
    return s, t


def in_cafe(s, t, margin=0.0):
    """Front part of the tail: covered by the lattice arch instead of the green roof."""
    return s > S_CAFE - margin and t < -0.3 + margin * 3


def h_roof(s, t):
    """Green roof level: flat head, continuous descent, low lawn that falls to the ground toward the
    back and the tip; in front of the pinch the roof edge comes down to the ground."""
    h = H_TOP if s <= 0.14 else H_LAWN + (H_TOP - H_LAWN) * (1 - ss((s - 0.14) / 0.52))
    h *= 1 - ss((s - 0.52) / 0.26) * min(1.0, max(0.0, (t + 0.25) / 1.2)) ** 1.3      # falls to the back
    h *= 1 - ss((s - 0.90) / (S_END - 0.90))                                           # falls to the tip
    h *= 1 - ss((s - 0.56) / 0.12) * ss((-t - 0.45) / 0.5)                             # front apron to ground
    return h


def h_cafe(s, t):
    u = min(1.0, max(0.0, (s - S_CAFE) / (S_END - S_CAFE)))
    return H_CAFE * math.sin(math.pi * u) ** 0.75


def H(x, y):
    """Top surface (roof park or cafe arch) at a plan point."""
    s, t = st(x, y)
    return max(h_roof(s, t), h_cafe(s, t)) if in_cafe(s, t) else h_roof(s, t)


OUTLINE = unary_union([Point(*CL_LINE.interpolate(s * L).coords[0]).buffer(lerp_table(WIDTH, s) / 2, 32)
                       for s in np.linspace(0, 1, 160)]).simplify(0.05)
GLASS = OUTLINE.buffer(-INSET)


# ------------------------------------------------------------------ blender helpers
def mat(name, rgb, rough=0.6, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit[0], 1)
        b.inputs["Emission Strength"].default_value = emit[1]
    return m


def add_obj(name, verts, faces, mats, face_mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    for m in mats:
        me.materials.append(m)
    if face_mat is not None:
        for poly, mi in zip(me.polygons, face_mat):
            poly.material_index = mi
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def tri_mesh(poly, spacing):
    pts = [c for ring in [poly.exterior, *poly.interiors] for c in ring.segmentize(spacing * 0.6).coords[:-1]]
    minx, miny, maxx, maxy = poly.bounds
    inner = poly.buffer(-spacing * 0.4)
    for x in np.arange(minx, maxx, spacing):
        for y in np.arange(miny, maxy, spacing):
            if inner.contains(Point(x, y)):
                pts.append((x, y))
    big = poly.buffer(0.01)
    return [list(t.exterior.coords)[:3] for t in delaunay_triangles(MultiPoint(pts)).geoms
            if big.contains(t) and t.area > 1e-4]


_TRIS = {}


def heightfield_solid(name, poly, top, bottom, mats, keep=lambda x, y: True, spacing=1.3, side_mat=1):
    """Closed solid between bottom(x,y) and top(x,y) over the kept triangles of poly (mat 0 top/bottom, side_mat walls)."""
    key = (id(poly), spacing)
    if key not in _TRIS:
        _TRIS[key] = tri_mesh(poly, spacing)
    tris = [t for t in _TRIS[key] if all(keep(x, y) for x, y in t)]
    idx, verts = {}, []

    def v(x, y, which):
        k = (round(x, 3), round(y, 3), which)
        if k not in idx:
            idx[k] = len(verts)
            verts.append((x, y, top(x, y) if which == "t" else bottom(x, y)))
        return idx[k]

    faces, fm, edges = [], [], {}
    for t in tris:
        if not Polygon(t).exterior.is_ccw:
            t = t[::-1]
        faces.append([v(*p, "t") for p in t]); fm.append(0)
        faces.append([v(*p, "b") for p in t[::-1]]); fm.append(0)
        for i in range(3):
            e = (tuple(np.round(t[i], 3)), tuple(np.round(t[(i + 1) % 3], 3)))
            edges.setdefault(tuple(sorted(e)), []).append(e)
    for es in edges.values():
        if len(es) == 1:
            (x0, y0), (x1, y1) = es[0]
            faces.append([v(x0, y0, "b"), v(x1, y1, "b"), v(x1, y1, "t"), v(x0, y0, "t")])
            fm.append(side_mat)
    return add_obj(name, verts, faces, mats, fm)


def cylinder(x, y, z0, z1, r0, r1, seg=10):
    verts, faces = [], []
    for z, r in ((z0, r0), (z1, r1)):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            verts.append((x + r * math.cos(a), y + r * math.sin(a), z))
    for i in range(seg):
        j = (i + 1) % seg
        faces.append([i, j, seg + j, seg + i])
    faces.append(list(range(seg))[::-1])
    faces.append(list(range(seg, 2 * seg)))
    return verts, faces


class Batch:
    def __init__(self, name, m):
        self.name, self.m, self.v, self.f = name, m, [], []

    def add(self, verts, faces):
        o = len(self.v)
        self.v += verts
        self.f += [[i + o for i in fc] for fc in faces]

    def sphere(self, x, y, z, r, sz=1.0):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        self.add([(x + p.co.x, y + p.co.y, z + p.co.z * sz) for p in bm.verts],
                 [[p.index for p in f.verts] for f in bm.faces])
        bm.free()

    def done(self):
        if self.v:
            ob = add_obj(self.name, self.v, self.f, [self.m])
            for p in ob.data.polygons:
                p.use_smooth = True


# ------------------------------------------------------------------ scene
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    M = dict(
        white=mat("white structure", (0.90, 0.88, 0.84), 0.45),
        glass=mat("glass warm", (0.10, 0.10, 0.10), 0.05, emit=((1.0, 0.62, 0.32), 0.5)),
        slab=mat("slab", (0.75, 0.74, 0.72), 0.6),
        green=mat("roof green", (0.20, 0.36, 0.11), 0.9),
        lawn=mat("lawn", (0.30, 0.50, 0.14), 0.9),
        path=mat("path", (0.80, 0.72, 0.58), 0.8),
        wood=mat("wood deck", (0.50, 0.33, 0.18), 0.7),
        water=mat("water", (0.12, 0.30, 0.38), 0.05),
        crown=mat("tree", (0.20, 0.40, 0.10), 0.9),
        bloom=mat("tree flowering", (0.86, 0.58, 0.68), 0.9),
        birch=mat("tree birch", (0.42, 0.55, 0.20), 0.9),
        trunk=mat("trunk", (0.30, 0.22, 0.15), 0.9),
        umb=mat("umbrella", (0.95, 0.94, 0.90), 0.6),
        person=mat("people", (0.18, 0.18, 0.20), 0.8),
        ground=mat("ground paving", (0.80, 0.77, 0.72), 0.85),
    )
    add_obj("ground", [(-400, -400, 0), (400, -400, 0), (400, 400, 0), (-400, 400, 0)], [[0, 1, 2, 3]], [M["ground"]])

    def roof_zone(x, y):                      # green roof everywhere except under the cafe arch
        s, t = st(x, y)
        return not in_cafe(s, t, -0.01)

    def cafe_zone(x, y):
        s, t = st(x, y)
        return in_cafe(s, t, 0.012)

    def HR(x, y):
        return h_roof(*st(x, y))

    def HC(x, y):
        return h_cafe(*st(x, y))

    # main glazed volume, floor slabs, green roof plate
    heightfield_solid("glazing", GLASS, lambda x, y: max(HR(x, y) - ROOF_T, 0.01), lambda x, y: 0.0,
                      [M["glass"], M["glass"]], keep=lambda x, y: HR(x, y) > 3.2 and roof_zone(x, y))
    slab_poly = OUTLINE.buffer(-INSET + 0.6)
    for z in FLOORS:
        heightfield_solid(f"slab {z}", slab_poly, lambda x, y, z=z: z + 0.35, lambda x, y, z=z: z,
                          [M["slab"], M["slab"]], keep=lambda x, y, z=z: HR(x, y) > z + 1.6 and roof_zone(x, y))
    heightfield_solid("roof", OUTLINE, lambda x, y: HR(x, y) + 0.02, lambda x, y: max(HR(x, y) - ROOF_T, 0.0),
                      [M["green"], M["white"]], keep=roof_zone, spacing=1.1)
    # cafe: lattice arch shell + glazed cafe set back under it (front stays open for the terrace)
    heightfield_solid("cafe arch", OUTLINE, lambda x, y: max(HC(x, y), HR(x, y)) + 0.02,
                      lambda x, y: max(max(HC(x, y), HR(x, y)) - 0.5, 0.0), [M["white"], M["white"]], keep=cafe_zone, spacing=1.1)

    def cafe_glass(x, y):
        s, t = st(x, y)
        return s > S_CAFE and -0.72 < t < -0.28 and h_cafe(s, t) > 3.0
    heightfield_solid("cafe glazing", OUTLINE, lambda x, y: HC(x, y) - 0.5, lambda x, y: 0.0,
                      [M["glass"], M["glass"]], keep=cafe_glass, spacing=1.1)

    # lattice edge band along the whole roof edge; taller and flared at the head (the "crown")
    cs = list(OUTLINE.exterior.segmentize(0.6).coords)[:-1]
    inner = OUTLINE.buffer(-0.5).exterior
    pv, pf = [], []
    for x, y in cs:
        ix, iy = inner.interpolate(inner.project(Point(x, y))).coords[0]
        s, _ = st(x, y)
        hz = H(x, y)
        crown = 1 - ss(s / 0.30)
        top = hz + (1.1 + 1.7 * crown) * min(1.0, hz / 2.0)
        n = np.array((x - ix, y - iy)); n /= np.linalg.norm(n)
        ox, oy = np.array((x, y)) + n * 1.3 * crown
        pv += [(x, y, max(hz - ROOF_T, 0)), (ox, oy, top), (ix, iy, top - 0.3 * crown), (ix, iy, max(hz - ROOF_T, 0))]
    n = len(cs)
    for i in range(n):
        a, b = 4 * i, 4 * ((i + 1) % n)
        for k in range(4):
            pf.append([a + k, b + k, b + (k + 1) % 4, a + (k + 1) % 4])
    add_obj("lattice edge", pv, pf, [M["white"]])

    # fins with flared heads (read as branching columns); open portal in the front; wide bays at the cafe
    fins = Batch("fins", M["white"])
    ring = OUTLINE.buffer(-0.25).exterior
    for i, d in enumerate(np.arange(0, ring.length, FIN_SPACING)):
        x, y = ring.interpolate(d).coords[0]
        s, t = st(x, y)
        hz = H(x, y) - (0.5 if in_cafe(s, t) else ROOF_T)
        if hz < 2.4 or (t < 0 and PORTAL[0] < s < PORTAL[1]) or (in_cafe(s, t) and i % 3):
            continue
        flare = min(2.4, hz * 0.3)
        fins.add(*cylinder(x, y, 0, hz - flare, 0.16, 0.22))
        fins.add(*cylinder(x, y, hz - flare, hz + 0.05, 0.22, 0.95))
    fins.done()

    # ---------------- roof park (layout of 08_park_B)
    def on_roof(s, off, dz=0.0):
        p, tg, nrm = frame(s)
        x, y = p + nrm * off
        return x, y, H(x, y) + dz

    def hw(s):
        return lerp_table(WIDTH, s) / 2 - 2.2

    def ribbon(name, m, s0, s1, offset, width, dz, step=0.004, hf=None):
        hf = hf or H
        vs, fs = [], []
        ss_ = np.arange(s0, s1, step)
        for s in ss_:
            p, tg, nrm = frame(s)
            if s > 1:                               # continue straight through the tip cap
                p = p + tg * (s - 1) * L
            c = p + nrm * offset(s)
            for side in (-1, 1):
                x, y = c + nrm * side * width / 2
                vs.append((x, y, hf(x, y) + dz))
        for i in range(len(ss_) - 1):
            fs.append([2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2])
        add_obj(name, vs, fs, [m])

    def path_h(x, y):       # the main path rides over the cafe arch ("the hill")
        s, t = st(x, y)
        return max(h_roof(s, t), h_cafe(s, t)) if s > S_CAFE and t < 0.1 else h_roof(s, t)

    def main_path(s):       # ONE continuous serpentine: lookout deck -> down the roof -> up over the cafe arch -> ground at the tip
        w2 = ss((s - 0.56) / 0.14)
        cap = math.sqrt(max(0.0, 1 - (max(0.0, s - 1) * L / (lerp_table(WIDTH, 1.0) / 2)) ** 2))
        return (1 - w2) * 0.55 * hw(s) * math.sin(2 * math.pi * 2.3 * s + 0.6) - w2 * 0.62 * lerp_table(WIDTH, s) / 2 * cap
    ribbon("path main", M["path"], 0.12, S_END + 0.03, main_path, 2.2, 0.12, hf=path_h)
    ribbon("path loop", M["path"], 0.20, 0.47, lambda s: -main_path(s) * 0.9, 1.6, 0.10)
    ribbon("stream", M["water"], 0.34, 0.60, lambda s: 0.30 * hw(s) * math.cos(2 * math.pi * 2.3 * s + 0.6) + 1.0, 1.5, 0.07)
    ribbon("picnic lawn", M["lawn"], 0.63, 0.86, lambda s: 2.5, 5.5, 0.05)

    deck = Batch("decks", M["wood"])
    for s, off, r in ((0.04, 0.5, 7.6), (0.40, -3.6, 2.3)):       # lookout deck at the head, small deck mid
        x, y, z = on_roof(s, off)
        deck.add(*cylinder(x, y, z, z + 0.35, r, r, seg=28))
    deck.done()

    tree_b = {k: Batch(f"trees {k}", M[k]) for k in ("crown", "bloom", "birch")}
    trunks = Batch("trunks", M["trunk"])
    spots = [(0.00, 9.4, 4.6, "crown"), (0.03, -9.3, 1.8, "bloom"), (0.20, 5.5, 2.6, "birch"), (0.27, 5.0, 2.8, "birch"),
             (0.33, 4.5, 2.4, "birch"), (0.24, -5.0, 2.0, "crown"), (0.47, 5.2, 3.0, "crown"), (0.56, 0.5, 2.6, "bloom"),
             (0.62, 5.6, 3.6, "crown"), (0.72, 5.8, 2.2, "bloom"), (0.80, 6.0, 2.4, "crown"), (0.88, 5.0, 1.8, "birch")]
    for s, off, r, kind in spots:
        x, y, z = on_roof(s, off)
        trunks.add(*cylinder(x, y, z, z + r * 1.1, 0.25, 0.18))
        tree_b[kind].sphere(x, y, z + r * 1.6, r, 0.85 if kind != "birch" else 1.35)
    for b in (*tree_b.values(), trunks):
        b.done()

    # cafe terrace in front of the arch
    umb = Batch("umbrellas", M["umb"])
    for s, d in ((0.80, 3.0), (0.88, 2.5), (0.96, 3.0), (0.84, 7.0), (0.92, 6.5), (1.0, 6.5)):
        p, tg, nrm = frame(s)
        x, y = p - nrm * (lerp_table(WIDTH, s) / 2 + d)
        umb.add(*cylinder(x, y, 0, 2.5, 0.04, 0.04, 6))
        umb.add(*cylinder(x, y, 2.3, 2.75, 1.6, 0.05, 16))
        umb.add(*cylinder(x, y, 0.72, 0.76, 0.5, 0.5, 12))
    umb.done()

    rnd = random.Random(7)
    ppl = Batch("people", M["person"])
    for _ in range(60):
        s = rnd.uniform(0, 1)
        p, tg, nrm = frame(s)
        x, y = p + nrm * rnd.choice([-1, 1]) * rnd.uniform(12, 26)
        if not OUTLINE.buffer(1.0).contains(Point(x, y)):
            ppl.add(*cylinder(x, y, 0, 1.75, 0.22, 0.18, 6))
    for _ in range(24):
        s = rnd.uniform(0.02, 0.9)
        x, y, z = on_roof(s, rnd.uniform(-0.1, 0.8) * hw(s) if s > 0.65 else rnd.uniform(-0.8, 0.8) * hw(s), 0.1)
        ppl.add(*cylinder(x, y, z, z + 1.75, 0.22, 0.18, 6))
    ppl.done()

    # light: warm low sun from the front-left, as in the reference
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sc.collection.objects.link(sun)
    sun.data.energy = 4.0
    sun.data.color = (1.0, 0.86, 0.70)
    sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(58), 0, math.radians(-50))
    world = bpy.data.worlds.new("world")
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.93, 0.88, 0.83, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    return sc


# ------------------------------------------------------------------ cameras: one orbit, SAME distance for every view
VIEWS = [  # name, azimuth offset from the reference front view (deg), elevation (deg)
    ("view0_front", 0, 35), ("view1_front_left_45", -45, 35), ("view2_high_end_90", -90, 35),
    ("view3_back_left_135", -135, 35), ("view4_back_180", 180, 35), ("view5_back_right_225", 135, 35),
    ("view6_cafe_end_270", 90, 35), ("view7_front_right_315", 45, 35),
    ("view8_top", 0, 89.9), ("view9_low_front", 0, 10),
    ("viewA_low_cafe_side", 60, 12), ("viewB_low_back", 180, 12),
]
FRONT_AZ = 280.0      # reference camera: in front, slightly from the cafe side, as in 08_park_B.png
LENS = 40.0
DIST = 130.0          # camera distance from the building centre, all views


def add_cameras(sc):
    cx, cy, cz = OUTLINE.centroid.x, OUTLINE.centroid.y, 5.0
    cams = []
    for name, az, el in VIEWS:
        a, e = math.radians(FRONT_AZ + az), math.radians(el)
        loc = (cx + DIST * math.cos(e) * math.cos(a), cy + DIST * math.cos(e) * math.sin(a), cz + DIST * math.sin(e))
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        cam.data.lens = LENS
        cam.data.clip_end = 2000
        sc.collection.objects.link(cam)
        cam.location = loc
        d = mathutils.Vector((cx, cy, cz)) - mathutils.Vector(loc)
        cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        cams.append(cam)
    return cams


def render(sc, cams, which, samples):
    os.makedirs(OUT, exist_ok=True)
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1344, 756
    sc.view_settings.view_transform = "AgX"
    for cam in cams:
        if which and cam.name.split("_")[0] not in which:
            continue
        sc.camera = cam
        sc.render.filepath = os.path.join(OUT, cam.name + ".png")
        bpy.ops.render.render(write_still=True)
        print("rendered", sc.render.filepath, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--views", default="", help="comma list like view0,view4 (default all)")
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    sc = build()
    cams = add_cameras(sc)
    b = OUTLINE.bounds
    print(f"plan {b[2] - b[0]:.1f} x {b[3] - b[1]:.1f} m, centre line {L:.1f} m, footprint {OUTLINE.area:.0f} m2, camera distance {DIST:.0f} m")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "pink_podium_blocking.blend"))
    if not a.no_render:
        render(sc, cams, [v for v in a.views.split(",") if v], a.samples)
