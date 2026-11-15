#!/usr/bin/env python3
"""M5 offline map checker (CALC-M5-03, DEC-047; M5 Task B). No ROS needed (runs in CI).

Usage: python3 -I TEST-M5_map_check.py <map.yaml> [--world <world.sdf>] [--json <out.json>]
Exit 0 = every measure PASS, 1 = a measure FAIL, 2 = the map cannot be read.

Inputs:
  - a saved map in the Nav2 map_saver format (<map>.yaml + its .pgm image, P5; trinary: 0 occupied, 254 free,
    205 unknown; a cell is occupied when (255 - pixel)/255 > occupied_thresh, negate 0);
  - the true geometry, read from the world file (one source of truth; default: the source tree mapping_arena.sdf):
    every box whose top is above the scan plane (0.230 m) is a mapped surface; the low box L1 must be absent;
  - the Selected route (TEST-M5_route.py) for the visibility of surfaces (completeness).
The map frame is the world frame (the robot spawns at the origin, yaw 0, and SLAM starts its map there; checked in
the Task A gate), so no alignment is applied. A best-fit alignment is printed as INFO only.

Measures and bounds (DEC-047):
  1. wall accuracy: the distance from each occupied cell centre to the nearest true surface; P95 <= 0.10 m;
  2. ghosts: the share of occupied cells farther than 0.25 m from every true surface; <= 0.5 %;
  3. completeness: surface points every 0.05 m on the faces visible from the route (line of sight within the 12 m
     range, not inside another box); the share with an occupied cell centre within 0.10 m; >= 90 %;
  4. dimensions: straight lines fitted (least squares) to the occupied cells within 0.15 m of each inner wall face
     (cells within 0.20 m of another feature, e.g. W1 where it joins the south wall, excluded);
     interior length (east - west at y = 0) 10.0 m and width (north - south at x = 3) 8.0 m, each +/- 0.10 m; each
     wall within 1.0 deg of its true direction; opposite walls parallel and adjacent walls perpendicular within 1.0 deg;
  5. L1 absent: zero occupied cell centres inside the L1 footprint.
"""
import importlib.util
import json
import math
import os
import sys

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('route', os.path.join(HERE, 'TEST-M5_route.py'))
route = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(route)

P95_MAX, GHOST_D, GHOST_MAX, COMPLETE_D, COMPLETE_MIN = 0.10, 0.25, 0.005, 0.10, 0.90
DIM_TOL, ANGLE_TOL, RANGE = 0.10, 1.0, 12.0
INTERIOR = {'west': -2.0, 'east': 8.0, 'south': -4.0, 'north': 4.0}


def read_pgm(path):
    with open(path, 'rb') as f:
        data = f.read()
    tokens, pos = [], 0
    while len(tokens) < 4:
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
    if tokens[0] != b'P5' or int(tokens[3]) > 255:
        raise ValueError(f'{path}: not an 8-bit binary PGM')
    w, h = int(tokens[1]), int(tokens[2])
    pos += 1
    return np.frombuffer(data[pos:pos + w * h], dtype=np.uint8).reshape(h, w)


def load_map(yaml_path):
    meta = yaml.safe_load(open(yaml_path))
    img = read_pgm(os.path.join(os.path.dirname(os.path.abspath(yaml_path)), meta['image']))
    if meta.get('negate', 0) or abs(meta['origin'][2]) > 1e-9:
        raise ValueError('negate or a rotated origin is not supported')
    occ = (255.0 - img) / 255.0 > meta['occupied_thresh']
    res, ox, oy = meta['resolution'], meta['origin'][0], meta['origin'][1]
    rows, cols = np.nonzero(occ)
    h = img.shape[0]
    xs = ox + (cols + 0.5) * res
    ys = oy + (h - rows - 0.5) * res
    return meta, img, np.column_stack([xs, ys])


def surface_distance(pts, boxes):
    """Distance from each point to the nearest box boundary (inside or outside the box)."""
    best = np.full(len(pts), np.inf)
    for x0, x1, y0, y1, _ in boxes:
        dx = np.maximum.reduce([x0 - pts[:, 0], np.zeros(len(pts)), pts[:, 0] - x1])
        dy = np.maximum.reduce([y0 - pts[:, 1], np.zeros(len(pts)), pts[:, 1] - y1])
        out = np.hypot(dx, dy)
        inside = (dx == 0) & (dy == 0)
        depth = np.minimum.reduce([pts[:, 0] - x0, x1 - pts[:, 0], pts[:, 1] - y0, y1 - pts[:, 1]])
        best = np.minimum(best, np.where(inside, depth, out))
    return best


def segment_hits_box(p, q, b, eps=1e-9):
    """True if the open segment p-q passes through the interior of box b (Liang-Barsky)."""
    x0, x1, y0, y1 = b[:4]
    t0, t1 = 0.0, 1.0
    dx, dy = q[0] - p[0], q[1] - p[1]
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pk) < eps:
            if qk <= eps:
                return False
        else:
            t = qk / pk
            if pk < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return t1 - t0 > eps


def visible_surface_points(boxes, route_pts, step=0.05, off=0.01):
    pts = []
    for i, b in enumerate(boxes):
        x0, x1, y0, y1 = b[:4]
        faces = [((x0, y0), (x1, y0), (0, -1)), ((x1, y0), (x1, y1), (1, 0)),
                 ((x1, y1), (x0, y1), (0, 1)), ((x0, y1), (x0, y0), (-1, 0))]
        for (ax, ay), (bx, by), (nx, ny) in faces:
            n = max(1, int(round(math.hypot(bx - ax, by - ay) / step)))
            for k in range(n + 1):
                sx, sy = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
                tx, ty = sx + nx * off, sy + ny * off
                if any(o[0] < tx < o[1] and o[2] < ty < o[3] for j, o in enumerate(boxes) if j != i):
                    continue
                for rx, ry in route_pts:
                    if math.hypot(tx - rx, ty - ry) > RANGE:
                        continue
                    if (tx - rx) * nx + (ty - ry) * ny >= 0:   # the face points away from this route point
                        continue
                    if not any(segment_hits_box((rx, ry), (tx, ty), o) for o in boxes):
                        pts.append((sx, sy))
                        break
    return np.array(pts)


def fit_line(pts, vertical):
    """Least-squares line: x = a + b*y (vertical) or y = a + b*x; returns (a, b)."""
    u, v = (pts[:, 1], pts[:, 0]) if vertical else (pts[:, 0], pts[:, 1])
    b, a = np.polyfit(u, v, 1)
    return a, b


def best_fit(occ, boxes):
    """INFO: rigid offset (dx, dy, dtheta about the origin) that minimises the mean clipped surface distance."""
    best = (np.inf, 0, 0, 0)
    for th in np.radians(np.arange(-1.0, 1.01, 0.25)):
        c, s = math.cos(th), math.sin(th)
        rot = occ @ np.array([[c, s], [-s, c]])
        for dx in np.arange(-0.10, 0.101, 0.025):
            for dy in np.arange(-0.10, 0.101, 0.025):
                d = np.minimum(surface_distance(rot + [dx, dy], boxes), GHOST_D).mean()
                if d < best[0]:
                    best = (d, dx, dy, th)
    return best


def check(yaml_path, world=route.WORLD):
    res = {'map': os.path.basename(yaml_path), 'measures': {}}
    out = []

    def m(key, ok, text):
        res['measures'][key] = bool(ok)
        out.append(f'{"PASS" if ok else "FAIL"}  {text}')

    meta, img, occ = load_map(yaml_path)
    allb = route.world_boxes(world)
    boxes = [b for n, b in sorted(allb.items()) if b[4] > route.SCAN_Z]
    low = {n: b for n, b in allb.items() if b[4] <= route.SCAN_Z}
    out.append(f'# map {os.path.basename(yaml_path)}: {img.shape[1]} x {img.shape[0]} cells, {meta["resolution"]} m, '
               f'origin {meta["origin"][:2]}; occupied cells {len(occ)}; true surfaces: {len(boxes)} boxes above the '
               f'scan plane, below it: {sorted(low)}')
    if len(occ) == 0:
        m('wall_accuracy', False, 'no occupied cells')
        res['pass'] = False
        return res, out
    d = surface_distance(occ, boxes)
    p95 = float(np.percentile(d, 95))
    res['wall_p95_m'] = p95
    m('wall_accuracy', p95 <= P95_MAX, f'wall accuracy: P95 distance to the true surface {p95:.4f} m (<= {P95_MAX} m); '
      f'median {np.median(d):.4f} m, max {d.max():.3f} m')
    ghost = float((d > GHOST_D).mean())
    res['ghost_share'] = ghost
    m('ghosts', ghost <= GHOST_MAX, f'ghosts: {int((d > GHOST_D).sum())} of {len(d)} occupied cells farther than '
      f'{GHOST_D} m from any surface = {100 * ghost:.3f} % (<= {100 * GHOST_MAX:.1f} %)')
    rp = route.samples(step=0.25)
    vis = visible_surface_points(boxes, rp)
    near = np.array([np.min(np.hypot(occ[:, 0] - x, occ[:, 1] - y)) <= COMPLETE_D for x, y in vis])
    comp = float(near.mean()) if len(vis) else 0.0
    res['completeness'] = comp
    m('completeness', comp >= COMPLETE_MIN, f'completeness: {int(near.sum())} of {len(vis)} visible surface points '
      f'have an occupied cell within {COMPLETE_D} m = {100 * comp:.2f} % (>= {100 * COMPLETE_MIN:.0f} %)')
    lines, ok_dim, txt = {}, True, []
    features = [b for n, b in allb.items() if not n.startswith('wall_') and b[4] > route.SCAN_Z]
    clear = surface_distance(occ, features) > 0.20 if features else np.ones(len(occ), bool)   # not W1's faces etc.
    for name, val in INTERIOR.items():
        vert = name in ('west', 'east')
        coord = occ[:, 0] if vert else occ[:, 1]
        sel = occ[(np.abs(coord - val) <= 0.15) & clear]
        if len(sel) < 10:
            ok_dim = False
            txt.append(f'{name}: only {len(sel)} cells')
            continue
        lines[name] = fit_line(sel, vert)
    if len(lines) == 4:
        length = (lines['east'][0] + lines['east'][1] * 0.0) - (lines['west'][0] + lines['west'][1] * 0.0)
        width = (lines['north'][0] + lines['north'][1] * 3.0) - (lines['south'][0] + lines['south'][1] * 3.0)
        dev = {n: math.degrees(math.atan(b)) for n, (a, b) in lines.items()}
        rot = {'west': -dev['west'], 'east': -dev['east'], 'south': dev['south'], 'north': dev['north']}
        par = max(abs(rot['west'] - rot['east']), abs(rot['south'] - rot['north']))
        perp = max(abs(rot['west'] - rot['south']), abs(rot['east'] - rot['north']),
                   abs(rot['west'] - rot['north']), abs(rot['east'] - rot['south']))
        worst = max(abs(v) for v in rot.values())
        res.update(length_m=length, width_m=width, wall_rotation_deg=rot)
        ok_dim = (abs(length - 10.0) <= DIM_TOL and abs(width - 8.0) <= DIM_TOL and worst <= ANGLE_TOL
                  and par <= ANGLE_TOL and perp <= ANGLE_TOL)
        txt.append(f'interior {length:.3f} x {width:.3f} m (10.0 x 8.0 +/- {DIM_TOL}); wall rotation vs the world '
                   f'(deg) west {rot["west"]:+.2f}, east {rot["east"]:+.2f}, south {rot["south"]:+.2f}, north '
                   f'{rot["north"]:+.2f} (each <= {ANGLE_TOL}); parallel {par:.2f}, perpendicular {perp:.2f} deg '
                   f'(<= {ANGLE_TOL})')
    m('dimensions', ok_dim, 'dimensions: ' + '; '.join(txt))
    for name, b in sorted(low.items()):
        inside = int(((occ[:, 0] > b[0]) & (occ[:, 0] < b[1]) & (occ[:, 1] > b[2]) & (occ[:, 1] < b[3])).sum())
        res[f'{name}_occupied_cells'] = inside
        m('l1_absent', inside == 0, f'{name} (top {b[4]:.2f} m, below the scan plane) absent: {inside} occupied cells '
          f'in its footprint (0)')
    fit = best_fit(occ, boxes)
    out.append(f'INFO  best-fit offset (not applied): dx {fit[1]:+.3f} m, dy {fit[2]:+.3f} m, rotation '
               f'{math.degrees(fit[3]):+.2f} deg (mean clipped distance {fit[0]:.4f} m)')
    res['pass'] = all(res['measures'].values())
    return res, out


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        print(__doc__)
        return 2
    world = args[args.index('--world') + 1] if '--world' in args else route.WORLD
    try:
        res, out = check(args[0], world)
    except (OSError, ValueError, KeyError) as exc:
        print(f'# cannot read the map: {type(exc).__name__}: {exc}')
        return 2
    print('\n'.join(out))
    print(f'# result: {"PASS" if res["pass"] else "FAIL"}')
    if '--json' in args:
        json.dump(res, open(args[args.index('--json') + 1], 'w'), indent=1)
    return 0 if res['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
