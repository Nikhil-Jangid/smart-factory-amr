#!/usr/bin/env python3
"""M5 test route (CALC-M5-02) and its checks; the robustness prediction for it (CALC-M5-04). M5 Task B.

One source of truth for the route: the harness (TEST-M5_map_run.py) drives these waypoints and the map checker
(TEST-M5_map_check.py) uses them for the visibility of surfaces. The obstacles are read from the world file
(amr_bringup/worlds/mapping_arena.sdf), not typed here.

Usage: python3 TEST-M5_route.py [<world.sdf>]   prints the route, the checks and the prediction; exit 0 if every check
       passes. Default world: the source tree file.

Criteria (M5 plan §3.2, finalized 2026-11-15):
  - one closed loop that returns to the start (0, 0), about 25-30 m;
  - it visits the alcove behind W1 (the region east of W1 and south of its tip: x 3.6-8.0, y -4.0 to -1.5);
  - it passes every feature at 1.0-3.0 m (shortest distance from the robot centre path to the feature's footprint);
  - it keeps >= 0.8 m between the robot footprint and any obstacle: the footprint's swept radius is 0.385 m
    (CALC-M1-13), so the robot centre stays >= 1.185 m from every obstacle footprint, the low box L1 included
    (it is below the scan plane but the robot would hit it).
Motion (plan §3.2): stop and turn; straight legs at 0.25 m/s, turns in place at 0.5 rad/s, a 1 s settle at each
waypoint (a rest point). Simulated duration estimate printed.
CALC-M5-04 robustness prediction (plan §3.4; CALC-M4-02): with wheel_separation_multiplier 1.02 the odometry yaw error
is -1/1.02 + 1 = -1.96 % of the turned angle (the controller turns the true robot by the commanded angle, odometry
reports it divided by 1.02); the predicted odometry pose at the end of the route is computed by replaying the route
with every turn scaled by 1/1.02 (wheel radii x 1.01 on both wheels scale distance and rotation by 1.01 in odometry
and are included as a distance and rotation factor of 1.01, as in TEST-M4-09). The yaw error follows the net signed
rotation (left turns positive), not the total turned angle: right and left turns cancel. 180-degree turns are made
to the left, by the harness as well, so the prediction matches what is driven.
"""
import math
import os
import sys
import xml.etree.ElementTree as ET  # parses only the repository's own world file (trusted input)

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'amr_ws', 'src', 'amr_bringup', 'worlds',
                                      'mapping_arena.sdf'))
SCAN_Z = 0.230          # scan plane height above ground, m (amr.sensors.xacro, DEC-030)
SWEPT_R = 0.385         # robot footprint swept radius, m (CALC-M1-13)
CLEARANCE = 0.8         # required gap between footprint and obstacle, m (plan §3.2)
V, W, SETTLE = 0.25, 0.5, 1.0

# Waypoints (x, y) in the world frame = the map frame (spawn at the origin, yaw 0). Selected in Task B (2026-11-15).
# Legs: east along y = 0 past P1, W1's tip and P2; south into the alcove east of P2; north to below B1; west to the
# gap between P1 and B1 and north into it; back south and west along y = 0.6 below P1; north-west spur; home.
WAYPOINTS = [(0.0, 0.0), (6.5, 0.0), (6.5, -2.6), (6.5, 0.9), (4.1, 0.9), (4.1, 2.7), (4.1, 0.6),
             (-0.6, 0.6), (-0.6, 2.6), (-0.6, 0.0), (0.0, 0.0)]
ALCOVE = (3.6, 8.0, -4.0, -1.5)   # x0, x1, y0, y1


def world_boxes(path=WORLD):
    """Static box obstacles of the world: name -> (x0, x1, y0, y1, top_z). Pose: x y z r p yaw with yaw 0 or 90°."""
    boxes = {}
    for model in ET.parse(path).getroot().iter('model'):
        pose = [float(v) for v in (model.findtext('pose') or '0 0 0 0 0 0').split()]
        for link in model.iter('link'):
            col = link.find('collision')
            size = col.find('geometry/box/size') if col is not None else None
            if size is None:
                continue
            sx, sy, sz = (float(v) for v in size.text.split())
            lp = [float(v) for v in (link.findtext('pose') or '0 0 0 0 0 0').split()]
            yaw = pose[5] + lp[5]
            if abs(math.sin(yaw)) > 0.5:
                sx, sy = sy, sx
            if abs(math.sin(2 * yaw)) > 1e-6:
                raise ValueError(f'{model.get("name")}: yaw not a multiple of 90 deg')
            cx, cy, cz = pose[0] + lp[0], pose[1] + lp[1], pose[2] + lp[2]
            boxes[model.get('name')] = (cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2, cz + sz / 2)
    return boxes


def dist_point_box(px, py, b):
    dx = max(b[0] - px, 0.0, px - b[1])
    dy = max(b[2] - py, 0.0, py - b[3])
    return math.hypot(dx, dy)


def samples(waypoints=WAYPOINTS, step=0.05):
    """Points along the path every `step` m (centre positions of the robot)."""
    pts = []
    for (x0, y0), (x1, y1) in zip(waypoints, waypoints[1:]):
        n = max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0) / step)))
        pts += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
    return pts + [waypoints[-1]]


def legs(waypoints=WAYPOINTS):
    """(length, heading) of each leg and the signed in-place turn before it (the first from yaw 0)."""
    out, yaw = [], 0.0
    for (x0, y0), (x1, y1) in zip(waypoints, waypoints[1:]):
        h = math.atan2(y1 - y0, x1 - x0)
        turn = (h - yaw + math.pi) % (2 * math.pi) - math.pi
        if abs(abs(turn) - math.pi) < 1e-9:
            turn = math.pi    # a 180° turn is made to the left
        out.append((math.hypot(x1 - x0, y1 - y0), h, turn))
        yaw = h
    return out


def predict_odometry(waypoints=WAYPOINTS, sep=1.02, radius=1.0):
    """Odometry pose at the end of the route when the true robot drives it exactly (CALC-M5-04)."""
    x = y = yaw = 0.0
    for length, _h, turn in legs(waypoints):
        yaw += turn * radius / sep
        x += length * radius * math.cos(yaw)
        y += length * radius * math.sin(yaw)
    return x, y, yaw


def main():
    world = sys.argv[1] if len(sys.argv) > 1 else WORLD
    boxes = world_boxes(world)
    ok = True

    def check(cond, text):
        nonlocal ok
        print(f'{"PASS" if cond else "FAIL"}  {text}')
        ok &= bool(cond)

    lg = legs()
    length = sum(L for L, _, _ in lg)
    turned = sum(abs(t) for _, _, t in lg)
    print(f'# M5 route (CALC-M5-02), world {os.path.basename(world)}: {len(WAYPOINTS) - 1} legs')
    for i, ((x, y), (L, h, t)) in enumerate(zip(WAYPOINTS[1:], lg), 1):
        print(f'  W{i:<2} ({x:5.2f}, {y:5.2f})  leg {L:4.2f} m, heading {math.degrees(h):7.1f} deg, turn before '
              f'{math.degrees(t):7.1f} deg')
    check(WAYPOINTS[0] == (0.0, 0.0) and WAYPOINTS[-1] == WAYPOINTS[0], 'closed loop from and to the start (0, 0)')
    check(25.0 <= length <= 30.0, f'length {length:.2f} m (25-30 m)')
    pts = samples()
    a = ALCOVE
    inside = [p for p in pts if a[0] < p[0] < a[1] and a[2] < p[1] < a[3]]
    check(bool(inside), f'enters the alcove east of W1 (x {a[0]}-{a[1]}, y {a[2]} to {a[3]}): {len(inside)} path samples')
    need = SWEPT_R + CLEARANCE
    for name, b in sorted(boxes.items()):
        d = min(dist_point_box(px, py, b) for px, py in pts)
        check(d >= need - 1e-9, f'{name}: closest approach of the robot centre {d:.3f} m >= {need:.3f} m '
              f'(footprint gap {d - SWEPT_R:.3f} m >= {CLEARANCE} m)')
    for name, b in sorted(boxes.items()):
        if name.startswith('wall_'):
            continue
        d = min(dist_point_box(px, py, b) for px, py in pts)
        check(1.0 <= d <= 3.0, f'feature {name} (top {b[4]:.2f} m{", below the scan plane" if b[4] < SCAN_Z else ""}) '
              f'passed at {d:.2f} m (1.0-3.0 m)')
    t_drive = length / V
    t_turn = turned / W
    print(f'INFO  turning in place {math.degrees(turned):.0f} deg in {sum(1 for *_, t in lg if abs(t) > 1e-9)} turns; '
          f'estimated simulated time {t_drive:.0f} s driving + {t_turn:.0f} s turning + {len(lg)} s settling = '
          f'{t_drive + t_turn + len(lg):.0f} s')
    print(f'INFO  scan nodes (one per 0.5 m or 0.5 rad): about {length / 0.5 + turned / 0.5:.0f}')
    net = sum(t for *_, t in lg)
    for label, r in (('separation x 1.02', 1.0), ('separation x 1.02 and both radii x 1.01', 1.01)):
        x, y, yaw = predict_odometry(radius=r)
        err = math.atan2(math.sin(yaw - net), math.cos(yaw - net))
        print(f'# CALC-M5-04 prediction, {label}: odometry at the end ({x:+.3f}, {y:+.3f}) m (truth (0, 0)): '
              f'position error {math.hypot(x, y):.3f} m; yaw error {math.degrees(err):+.2f} deg '
              f'(net signed rotation {math.degrees(net):+.0f} deg x ({r:g}/1.02 - 1) = '
              f'{math.degrees(net) * (r / 1.02 - 1):+.2f} deg)')
    print(f'# result: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
