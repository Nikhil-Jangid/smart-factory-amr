#!/usr/bin/env python3
"""M6 test routes and the unmapped-box world checks (DEC-060; M6 Task B).

The routes are the M5 route (CALC-M5-02, docs/evidence/M5/TEST-M5_route.py: the one source of truth for its
waypoints and checks), driven forward and in reverse (the same waypoints in the opposite order, back to the start).
A 180-degree turn is made to the left in both directions (as the M5 harness does).

The unmapped-box world TEST-M6_unmapped_arena.sdf (beside this file, test-only) is the M5 arena plus boxes whose model
names start with `unmapped_`; they are not in the reference map. Their positions are read from the world file.

Usage: python3 TEST-M6_route.py   prints both routes, the checks and the odometry predictions; exit 0 if every check
       passes.
Checks (M5 plan §3.2 rules, applied again here):
  - both routes: closed loops from and to (0, 0), every waypoint of the other direction, 28.8 m;
  - every obstacle of the M5 arena and every unmapped box keeps >= 0.8 m between the robot footprint and the box:
    robot centre >= 1.185 m (swept radius 0.385 m, CALC-M1-13) from each box footprint, along both routes (the same
    path, so the same distances; checked on both anyway);
  - each unmapped box is visible to the LiDAR: its top above the scan plane (0.230 m), and the route passes it at
    1.0-3.0 m (the M5 feature rule);
  - the unmapped boxes overlap no M5 obstacle and keep >= 0.15 m from every one (they are separate objects in the scan);
  - the world file is the M5 arena file plus the unmapped models only (text of every other model identical).
INFO: CALC-M5-04 odometry predictions for each direction (TEST-M6-05 compares the end-of-route drift with them).
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('route5', os.path.join(HERE, '..', 'M5', 'TEST-M5_route.py'))
route5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(route5)

FORWARD = list(route5.WAYPOINTS)
REVERSE = list(reversed(route5.WAYPOINTS))
ROUTES = {'forward': FORWARD, 'reverse': REVERSE}
UNMAPPED_WORLD = os.path.join(HERE, 'TEST-M6_unmapped_arena.sdf')
M5_WORLD = route5.WORLD
SEPARATION = 0.15        # m, minimum gap between an unmapped box and an M5 obstacle


def legs(name):
    return route5.legs(ROUTES[name])


def predict(name, sep=1.02, radius=1.01):
    """CALC-M5-04 replay for a route: (end position error m, end yaw error rad, net signed rotation rad)."""
    wps = ROUTES[name]
    x, y, yaw = route5.predict_odometry(wps, sep=sep, radius=radius)
    net = sum(t for *_, t in route5.legs(wps))
    return math.hypot(x - wps[-1][0], y - wps[-1][1]), math.atan2(math.sin(yaw - net), math.cos(yaw - net)), net


def gap_box_box(a, b):
    dx = max(a[0] - b[1], 0.0, b[0] - a[1])
    dy = max(a[2] - b[3], 0.0, b[2] - a[3])
    return math.hypot(dx, dy)


def model_blocks(path):
    """Model name -> the model's text block, from a world file (repository files only)."""
    text, out = open(path).read(), {}
    pos = 0
    while True:
        i = text.find('<model name="', pos)
        if i < 0:
            return out
        j = text.index('</model>', i) + len('</model>')
        out[text[i + 13:text.index('"', i + 13)]] = text[i:j]
        pos = j


def main():
    ok = True

    def check(cond, text):
        nonlocal ok
        print(f'{"PASS" if cond else "FAIL"}  {text}')
        ok &= bool(cond)

    boxes = route5.world_boxes(UNMAPPED_WORLD)
    unmapped = {k: v for k, v in boxes.items() if k.startswith('unmapped_')}
    mapped = {k: v for k, v in boxes.items() if not k.startswith('unmapped_')}
    need = route5.SWEPT_R + route5.CLEARANCE
    for name, wps in ROUTES.items():
        lg = route5.legs(wps)
        print(f'# {name} route: {len(wps) - 1} legs, {sum(L for L, _, _ in lg):.2f} m, turns '
              + ', '.join(f'{math.degrees(t):+.0f}' for *_, t in lg) + ' deg')
        check(wps[0] == (0.0, 0.0) and wps[-1] == (0.0, 0.0), f'{name}: closed loop from and to the start (0, 0)')
        pts = route5.samples(wps)
        for bname, b in sorted(boxes.items()):
            d = min(route5.dist_point_box(px, py, b) for px, py in pts)
            check(d >= need - 1e-9, f'{name}: {bname} closest approach of the robot centre {d:.3f} m >= {need:.3f} m')
        for bname, b in sorted(unmapped.items()):
            d = min(route5.dist_point_box(px, py, b) for px, py in pts)
            check(1.0 <= d <= 3.0 and b[4] > route5.SCAN_Z,
                  f'{name}: unmapped {bname} (top {b[4]:.2f} m > scan plane {route5.SCAN_Z} m) passed at {d:.2f} m '
                  f'(1.0-3.0 m)')
    check(set(FORWARD) == set(REVERSE) and REVERSE == FORWARD[::-1], 'reverse route = forward waypoints in reverse order')
    check(len(unmapped) == 3, f'unmapped boxes in the test world: {sorted(unmapped)} (DEC-060: three)')
    for uname, u in sorted(unmapped.items()):
        g = min(gap_box_box(u, m) for m in mapped.values())
        near = min(mapped, key=lambda k: gap_box_box(u, mapped[k]))
        print(f'INFO  {uname}: footprint x {u[0]:.2f}-{u[1]:.2f}, y {u[2]:.2f}-{u[3]:.2f}, top {u[4]:.2f} m')
        check(g >= SEPARATION, f'{uname}: gap to the nearest M5 obstacle ({near}) {g:.2f} m >= {SEPARATION} m')
    a, b = model_blocks(M5_WORLD), model_blocks(UNMAPPED_WORLD)
    same = sorted(k for k in a if b.get(k) == a[k])
    extra = sorted(set(b) - set(a))
    check(same == sorted(a) and all(k.startswith('unmapped_') for k in extra),
          f'test world = M5 arena ({len(same)} of {len(a)} models identical) + {extra}')
    for name in ROUTES:
        for label, sep, r in (('separation x 1.02', 1.02, 1.0), ('separation x 1.02, radii x 1.01', 1.02, 1.01)):
            pe, ye, net = predict(name, sep, r)
            print(f'# CALC-M5-04 prediction, {name}, {label}: end position error {pe:.3f} m, yaw error '
                  f'{math.degrees(ye):+.2f} deg (net signed rotation {math.degrees(net):+.0f} deg)')
    print(f'# result: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
