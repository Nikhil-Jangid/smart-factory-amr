#!/usr/bin/env python3
"""M7 goal set (CALC-M7-05, DEC-074) and its clearance check against the world file and the map. M7 Task B.

One source of truth for the goals: the navigation harness (TEST-M7_nav_run.py) sends these poses and the offline checker
(TEST-M7_nav_check.py) judges arrival against them. The obstacles are read from the world file through the M5 parser
(docs/evidence/M5/TEST-M5_route.py, world_boxes); the footprint is read from amr_bringup/config/nav2.yaml (DEC-069,
CALC-M7-01); the map from amr_bringup/maps/mapping_arena.yaml (/map, DEC-055). Nothing geometric is typed twice.

Usage: python3 TEST-M7_goals.py   prints the goals and the checks; exit 0 if every check passes.

Checks (M7 plan §3.5 and §3.4, DEC-073, DEC-074 as amended by DEC-076):
  - placement (DEC-076): each goal centre (base_footprint) is >= the costmap inflation radius (read from nav2.yaml)
    from every obstacle, so the goal has zero inflation cost; and the footprint at the goal pose keeps >= 1.5 m from
    L1 (the low box the LiDAR cannot see). The plan's first rule, footprint >= 0.8 m from every obstacle, failed for
    G2 (0.683 m) and G4 (0.515 m) and cannot hold in the alcove west of W1 at all; DEC-076 replaced it. The footprint
    gap to the nearest other obstacle is still printed (INFO);
  - turn at the goal (DEC-073 clearance): the robot may turn in place at a goal, so the circle swept by the footprint
    (radius = its circumscribed radius, centred on base_footprint) keeps >= 0.10 m from every obstacle, L1 included;
  - map: every map cell under the footprint at each goal is free in /map (Nav2 plans on the map, not the world file);
  - invalid goals: 'inside_P1' lies inside the footprint of pillar P1; 'outside_map' lies outside the map extent;
  - the sequence of TEST-M7-03 ends at the start; the route of TEST-M7-04 uses goals of the set and ends >= 1.0 m from
    the start (DEC-078: a NavigateThroughPoses path that ends where the robot stands is 'reached' at once, TS-054);
    the cancel goal is in the set.
INFO: straight-line distance and heading change of each leg (the nominal time bound itself uses the planned path length
and is computed by the checker from the recorded plan, DEC-073).
"""
import importlib.util
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('route5', os.path.join(HERE, '..', 'M5', 'TEST-M5_route.py'))
route5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(route5)

BRINGUP = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'amr_ws', 'src', 'amr_bringup'))
WORLD = route5.WORLD
NAV2_YAML = os.path.join(BRINGUP, 'config', 'nav2.yaml')
MAP_YAML = os.path.join(BRINGUP, 'maps', 'mapping_arena.yaml')

PLACEMENT_L1 = 1.5       # m, footprint to L1 at a goal (plan §3.5, kept by DEC-076)
CLEARANCE = 0.10         # m, DEC-073 clearance bound
L1 = 'low_box_l1'
P1 = 'pillar_p1'

# Start and goals: (x, y, yaw in degrees) in the map frame (= world frame; spawn at the origin, DEC-058).
START = (0.0, 0.0, 0.0)
GOALS = {
    'G1': (6.5, -2.6, -90.0),
    'G2': (6.5, 1.3, 0.0),
    'G3': (4.1, 2.7, 90.0),
    'G4': (2.5, -2.8, 180.0),
    'G5': (-0.6, 2.6, 90.0),
    'G6': (0.0, 0.0, 0.0),
}
SEQUENCE = ['G1', 'G2', 'G3', 'G4', 'G5', 'G6']      # TEST-M7-03, NavigateToPose one after another
ROUTE = ['G1', 'G3', 'G5']                             # TEST-M7-04, one NavigateThroughPoses goal (DEC-078)
INVALID = {'inside_P1': (2.0, 2.0, 0.0), 'outside_map': (12.0, 0.0, 0.0)}   # TEST-M7-05
ROUTE_END_MIN = 1.0      # m: the route must not end where it starts (DEC-078, TS-054)
CANCEL_GOAL = 'G1'                                     # TEST-M7-06: cancel after >= 1.0 m of travel
CANCEL_AFTER = 1.0                                     # m


def read_footprints(path=NAV2_YAML):
    """All `footprint:` polygons in nav2.yaml (local and global costmap) as lists of (x, y)."""
    out = []
    with open(path) as f:
        for line in f:
            m = re.match(r'\s*footprint:\s*"(.*)"', line)
            if m:
                out.append([tuple(float(v) for v in p.split(','))
                            for p in re.findall(r'\[\s*([-\d.]+\s*,\s*[-\d.]+)\s*\]', m.group(1))])
    return out


def footprint():
    fps = read_footprints()
    if len(fps) != 2 or fps[0] != fps[1]:
        raise ValueError(f'{NAV2_YAML}: expected two identical footprints, found {len(fps)}')
    return fps[0]


def inflation_radius(path=NAV2_YAML):
    """The costmaps' inflation_radius in nav2.yaml (local and global must agree)."""
    with open(path) as f:
        vals = {float(m.group(1)) for m in re.finditer(r'^\s*inflation_radius:\s*([\d.]+)', f.read(), re.M)}
    if len(vals) != 1:
        raise ValueError(f'{NAV2_YAML}: expected one inflation_radius value, found {sorted(vals)}')
    return vals.pop()


def place(poly, x, y, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return [(x + c * px - s * py, y + s * px + c * py) for px, py in poly]


def box_poly(b):
    return [(b[0], b[2]), (b[1], b[2]), (b[1], b[3]), (b[0], b[3])]


def _seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay)))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def _inside(p, poly):
    """Point in convex polygon (either winding)."""
    sign = 0
    for a, b in zip(poly, poly[1:] + poly[:1]):
        cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        if abs(cr) < 1e-12:
            continue
        if sign == 0:
            sign = 1 if cr > 0 else -1
        elif (cr > 0) != (sign > 0):
            return False
    return True


def poly_dist(p, q):
    """Distance between two convex polygons; 0 if they touch or overlap."""
    if any(_inside(v, q) for v in p) or any(_inside(v, p) for v in q):
        return 0.0
    d = math.inf
    for P, Q in ((p, q), (q, p)):
        for v in P:
            for a, b in zip(Q, Q[1:] + Q[:1]):
                d = min(d, _seg_dist(v, a, b))
    return d


def read_map(path=MAP_YAML):
    """(resolution, origin x, origin y, width, height, rows top-down of occupancy: 'free'/'occ'/'unk')."""
    meta = {}
    with open(path) as f:
        for line in f:
            if ':' in line and not line.lstrip().startswith('#'):
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
    res = float(meta['resolution'])
    ox, oy = (float(v) for v in meta['origin'].strip('[]').split(',')[:2])
    occ_t, free_t, negate = float(meta['occupied_thresh']), float(meta['free_thresh']), int(meta['negate'])
    with open(os.path.join(os.path.dirname(path), meta['image']), 'rb') as f:
        data = f.read()
    tokens, pos = [], 0
    while len(tokens) < 4:                       # P5 header: magic, width, height, maxval (comments skipped)
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b'#':
            pos = data.index(b'\n', pos) + 1
            continue
        end = pos
        while not data[end:end + 1].isspace():
            end += 1
        tokens.append(data[pos:end])
        pos = end
    if tokens[0] != b'P5':
        raise ValueError(f'{meta["image"]}: not a binary PGM')
    w, h, maxval = int(tokens[1]), int(tokens[2]), int(tokens[3])
    pix = data[pos + 1:pos + 1 + w * h]

    def cls(v):
        p = v / maxval if negate else (maxval - v) / maxval
        return 'occ' if p > occ_t else 'free' if p < free_t else 'unk'
    rows = [[cls(pix[r * w + c]) for c in range(w)] for r in range(h)]
    return res, ox, oy, w, h, rows


def cells_under(poly, res, ox, oy, w, h):
    """(col, row-from-bottom) of every map cell whose centre lies inside the polygon, or None if outside the map."""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    out = []
    for c in range(int((min(xs) - ox) / res) - 1, int((max(xs) - ox) / res) + 2):
        for r in range(int((min(ys) - oy) / res) - 1, int((max(ys) - oy) / res) + 2):
            if _inside((ox + (c + 0.5) * res, oy + (r + 0.5) * res), poly):
                if not (0 <= c < w and 0 <= r < h):
                    return None
                out.append((c, r))
    return out


def main():
    boxes = route5.world_boxes(WORLD)
    fp = footprint()
    r_circ = max(math.hypot(x, y) for x, y in fp)
    r_infl = inflation_radius()
    res, ox, oy, w, h, rows = read_map()
    ok = True

    def check(cond, text):
        nonlocal ok
        print(f'{"PASS" if cond else "FAIL"}  {text}')
        ok &= bool(cond)

    print(f'# M7 goal set (CALC-M7-05), world {os.path.basename(WORLD)} ({len(boxes)} obstacles), footprint from '
          f'nav2.yaml ({len(fp)} vertices, circumscribed radius {r_circ:.3f} m), map {os.path.basename(MAP_YAML)} '
          f'({w} x {h} cells at {res} m, x {ox:.3f} to {ox + w * res:.3f}, y {oy:.3f} to {oy + h * res:.3f})')
    for name, (x, y, yd) in GOALS.items():
        poly = place(fp, x, y, math.radians(yd))
        gaps = {b: poly_dist(poly, box_poly(bb)) for b, bb in boxes.items()}
        centre = {b: route5.dist_point_box(x, y, bb) for b, bb in boxes.items()}
        cb = min(centre, key=centre.get)
        check(centre[cb] >= r_infl - 1e-9 and gaps[L1] >= PLACEMENT_L1 - 1e-9,
              f'{name} ({x:5.2f}, {y:5.2f}, {yd:6.1f} deg) placement: centre {centre[cb]:.3f} m from {cb} '
              f'(>= inflation radius {r_infl}), footprint {gaps[L1]:.3f} m from L1 (>= {PLACEMENT_L1})')
        others = {b: g for b, g in gaps.items() if b != L1}
        nb = min(others, key=others.get)
        print(f'INFO  {name} footprint gap to the nearest obstacle other than L1: {others[nb]:.3f} m ({nb})')
        swept = {b: d - r_circ for b, d in centre.items()}
        sb = min(swept, key=swept.get)
        check(swept[sb] >= CLEARANCE - 1e-9,
              f'{name} turn in place: swept-circle gap {swept[sb]:.3f} m to {sb} (>= {CLEARANCE}, DEC-073)')
        cells = cells_under(poly, res, ox, oy, w, h)
        bad = None if cells is None else [cr for cr in cells if rows[h - 1 - cr[1]][cr[0]] != 'free']
        check(cells is not None and not bad,
              f'{name} map: {len(cells or [])} cells under the footprint, '
              f'{"outside the map" if cells is None else f"{len(bad)} not free"}')
    p1 = boxes[P1]
    x, y, _ = INVALID['inside_P1']
    check(p1[0] < x < p1[1] and p1[2] < y < p1[3], f'invalid goal inside_P1 ({x}, {y}) lies inside P1 '
          f'(x {p1[0]:.2f}-{p1[1]:.2f}, y {p1[2]:.2f}-{p1[3]:.2f})')
    x, y, _ = INVALID['outside_map']
    check(not (ox <= x <= ox + w * res and oy <= y <= oy + h * res), f'invalid goal outside_map ({x}, {y}) lies '
          f'outside the map extent')
    rend = math.hypot(GOALS[ROUTE[-1]][0] - START[0], GOALS[ROUTE[-1]][1] - START[1])
    check(all(g in GOALS for g in SEQUENCE + ROUTE) and GOALS[SEQUENCE[-1]] == START and rend >= ROUTE_END_MIN,
          f'sequence {"-".join(SEQUENCE)} ends at the start; route {"-".join(ROUTE)} uses the goal set and ends '
          f'{rend:.2f} m from the start (>= {ROUTE_END_MIN} m, DEC-078)')
    check(CANCEL_GOAL in GOALS and math.hypot(*GOALS[CANCEL_GOAL][:2]) > 2 * CANCEL_AFTER,
          f'cancel goal {CANCEL_GOAL} is {math.hypot(*GOALS[CANCEL_GOAL][:2]):.2f} m away (> 2 x {CANCEL_AFTER} m)')
    for label, seq in (('sequence', SEQUENCE), ('route', ROUTE)):
        prev, tot = START, 0.0
        for g in seq:
            gx, gy, gyaw = GOALS[g]
            d = math.hypot(gx - prev[0], gy - prev[1])
            dyaw = abs((gyaw - prev[2] + 180) % 360 - 180)
            tot += d
            print(f'INFO  {label}: -> {g}: straight line {d:5.2f} m, goal heading change {dyaw:5.1f} deg')
            prev = GOALS[g]
        print(f'INFO  {label}: straight-line total {tot:.2f} m (the planned path is longer: it goes around obstacles)')
    print(f'# result: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
