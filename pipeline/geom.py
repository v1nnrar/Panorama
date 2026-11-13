"""2D/3D geometry helpers shared by params, IFC builder and drawings (metres, x east, y north)."""
from __future__ import annotations

import math

COMPASS = {"N": (0, 1), "NE": (0.7071, 0.7071), "E": (1, 0), "SE": (0.7071, -0.7071),
           "S": (0, -1), "SW": (-0.7071, -0.7071), "W": (-1, 0), "NW": (-0.7071, 0.7071)}


def edges(pts):
    n = len(pts)
    return [(pts[i], pts[(i + 1) % n]) for i in range(n)]


def outward_normal(a, b):
    """Outward unit normal of edge a->b of a CCW polygon."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return (dy / L, -dx / L)


def facing_edges(pts, facing) -> list[int]:
    """Indices of edges whose outward normal points within ±50° of any compass direction in `facing`."""
    if facing in (None, "all", "ALL"):
        return list(range(len(pts)))
    dirs = [COMPASS[f] for f in ([facing] if isinstance(facing, str) else facing)]
    out = []
    for i, (a, b) in enumerate(edges(pts)):
        n = outward_normal(a, b)
        if any(n[0] * d[0] + n[1] * d[1] >= 0.64 for d in dirs):
            out.append(i)
    return out


def rule_edges(pts, rule) -> list[int]:
    """Edges a facade rule applies to: `near: [[x, y], ...]` picks, for each point, the edge whose midpoint is
    closest (for single edges such as a recess); otherwise compass `facing` (see facing_edges)."""
    near = rule.get("near")
    if not near:
        return facing_edges(pts, rule.get("facing"))
    if isinstance(near[0], (int, float)):
        near = [near]
    out = []
    for q in near:
        d = [math.hypot((a[0] + b[0]) / 2 - q[0], (a[1] + b[1]) / 2 - q[1]) for a, b in edges(pts)]
        i = min(range(len(d)), key=d.__getitem__)
        if i not in out:
            out.append(i)
    return sorted(out)


def offset_edges(pts, dist):
    """Move each edge i of a CCW polygon inward by dist[i] (negative = outward); vertices re-intersected."""
    n = len(pts)
    lines = []
    for i, (a, b) in enumerate(edges(pts)):
        nx, ny = outward_normal(a, b)
        d = dist[i]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        lines.append(((a[0] - nx * d, a[1] - ny * d), ((b[0] - a[0]) / L, (b[1] - a[1]) / L)))
    out = []
    for i in range(n):
        (q1, d1), (q2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 1e-9:
            out.append(q2)
        else:
            k = ((q2[0] - q1[0]) * d2[1] - (q2[1] - q1[1]) * d2[0]) / den
            out.append((q1[0] + d1[0] * k, q1[1] + d1[1] * k))
    return [(round(x, 4), round(y, 4)) for x, y in out]


def inset(pts, t):
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient
    out = offset_edges(pts, [t] * len(pts))
    P, Q = Polygon(pts), Polygon(out)
    expect = P.buffer(-t, join_style="mitre")
    if Q.is_valid and not expect.is_empty and abs(Q.area - expect.area) < 0.02 * max(expect.area, 1):
        return out
    g = max(getattr(expect, "geoms", [expect]), key=lambda p: p.area)
    return [tuple(c) for c in list(orient(g, 1.0).exterior.coords)[:-1]]


def local_frame(pts):
    """Origin = centroid, x axis = direction of the longest edge."""
    from shapely.geometry import Polygon
    c = Polygon(pts).centroid
    a, b = max(edges(pts), key=lambda e: math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    return (c.x, c.y), (ux, uy), (-uy, ux)


def to_world(frame, dx, dy):
    (ox, oy), (ux, uy), (vx, vy) = frame
    return (ox + ux * dx + vx * dy, oy + uy * dx + vy * dy)


def rect_world(frame, dx, dy, w, d):
    return [to_world(frame, dx + sx * w / 2, dy + sy * d / 2) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def in_range(n, rule, n_max):
    lo = rule.get("from", 1)
    hi = rule.get("to", n_max)
    hi = n_max + hi + 1 if hi < 0 else hi
    return lo <= n <= hi


def core_rects(b):
    """Cores of a building: (rectangle in world xy, from, to, definition) per `cores:` entry. dx, dy, w, d are in the
    local frame of the ground-floor footprint (centroid + longest edge), so cores stay put through setbacks."""
    st = b["storeys"]
    frame = local_frame(st[0]["footprint"])
    out = []
    for c in b.get("cores", []) or []:
        lo, hi = c.get("from", 1), c.get("to", len(st))
        hi = len(st) + hi + 1 if hi < 0 else hi
        out.append((rect_world(frame, c.get("dx", 0), c.get("dy", 0), c["w"], c["d"]), lo, hi, c))
    return out
