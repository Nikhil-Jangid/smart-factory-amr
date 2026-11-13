#!/usr/bin/env python3
"""TEST-M4-03: independent recomputation of the wheel odometry (REQ-M4-01; test_plan.md §9; DEC-044).

Usage: python3 -I docs/evidence/M4/TEST-M4-03_recompute.py [csv]   (default: TEST-M4-03_record.csv here)
No ROS needed: runs in CI (REQ-M4-11).

Input: a recording made by `TEST-M4_procedure.sh record` (rows `js,t,theta_L,theta_R` at 100 Hz and
`odom,t,x,y,psi` at 50 Hz from /diff_drive_controller/odom). r and b are read from the owner,
amr_properties.xacro (wheel_radius, wheel_track), not from the controller configuration, so the check is
independent of the controller's own parameters.

Pairing (TS-035, measured in the 2026-11-13 dry run): each odometry message is paired with the joint_states
sample of the same control cycle, i.e. the first joint_states stamp in [t_odom, t_odom + 1.5 ms]. In most cycles the
two stamps are equal; in about 7 % of the cycles the odometry stamp is exactly 1 ms earlier than the joint_states
stamp of the same cycle, and the pose computed from that cycle's positions matches it exactly.
Method (CALC-M4-01, M4 plan §3.1; the rule read from diff_drive_controller 4.42.1 odometry.cpp): starting from
the first paired odometry message, integrate every later joint_states step:
    ds = r (dθ_L + dθ_R)/2,  dψ = r (dθ_R − dθ_L)/b,
    |dψ| < 1e-6: RK2 (x += ds cos(ψ + dψ/2), y += ds sin(ψ + dψ/2)); otherwise exact arc (R = ds/dψ).
At every later paired odometry message, compare the pose with the published one.
Criteria: position within 1 mm and yaw within 0.01° at every compared stamp; at least 95 % of the odometry
messages compared. Exit 0 = PASS, 1 = FAIL.
"""
import bisect
import csv
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
XACRO = os.path.join(HERE, '..', '..', '..', 'amr_ws', 'src', 'amr_description', 'urdf', 'amr_properties.xacro')
fails = 0


def check(ok, text):
    global fails
    print(f'{"PASS" if ok else "FAIL"}  {text}')
    fails += 0 if ok else 1


def prop(txt, name):
    return float(re.search(rf'<xacro:property name="{name}" value="([0-9.eE+-]+)"', txt).group(1))


def integrate(x, y, psi, ds, dpsi):
    if abs(dpsi) < 1e-6:
        d = psi + dpsi * 0.5
        return x + ds * math.cos(d), y + ds * math.sin(d), psi + dpsi
    rr = ds / dpsi
    p1 = psi + dpsi
    return x + rr * (math.sin(p1) - math.sin(psi)), y - rr * (math.cos(p1) - math.cos(psi)), p1


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'TEST-M4-03_record.csv')
    txt = open(XACRO).read()
    r, b = prop(txt, 'wheel_radius'), prop(txt, 'wheel_track')
    print(f'# TEST-M4-03 recomputation: {os.path.basename(path)}; r = {r} m, b = {b} m (amr_properties.xacro)')
    js, od = [], []
    with open(path) as f:
        for row in csv.DictReader(f):
            t = round(float(row['t']), 6)
            if row['kind'] == 'js':
                js.append((t, float(row['a']), float(row['b'])))
            else:
                od.append((t, float(row['a']), float(row['b']), float(row['c'])))
    jt = [j[0] for j in js]

    def cycle(t):
        """Index of the joint_states sample of the same control cycle (TS-035), or None."""
        i = bisect.bisect_left(jt, t - 1e-6)
        return i if i < len(jt) and jt[i] <= t + 0.0015 else None

    pair = [(o, cycle(o[0])) for o in od]
    pair = [(o, i) for o, i in pair if i is not None]
    shifted = sum(1 for o, i in pair if abs(jt[i] - o[0]) > 1e-6)
    check(bool(pair), 'odometry messages paired with their control cycle (start point)')
    if not pair:
        return 1
    start, i0 = pair[0]
    print(f'INFO  {shifted} of {len(pair)} paired odometry stamps are earlier than their joint_states stamp '
          f'(max {max((jt[i] - o[0] for o, i in pair), default=0) * 1000:.3f} ms; TS-035)')
    x, y, psi = start[1], start[2], start[3]
    pose_at = {}
    for k in range(i0 + 1, len(js)):
        a, c = js[k - 1], js[k]
        dl, dr = r * (c[1] - a[1]), r * (c[2] - a[2])
        x, y, psi = integrate(x, y, psi, (dl + dr) / 2, (dr - dl) / b)
        pose_at[k] = (x, y, psi)
    later = [o for o in od if o[0] > start[0]]
    comp = [(o, pose_at[i]) for o, i in pair if o[0] > start[0] and i in pose_at]
    perr = [math.hypot(o[1] - p[0], o[2] - p[1]) for o, p in comp]
    yerr = [abs(math.degrees(math.atan2(math.sin(o[3] - p[2]), math.cos(o[3] - p[2])))) for o, p in comp]
    travel = sum(math.hypot(q[1] - p[1], q[2] - p[2]) for p, q in zip(od, od[1:]))
    turn = sum(abs(math.atan2(math.sin(q[3] - p[3]), math.cos(q[3] - p[3]))) for p, q in zip(od, od[1:]))
    print(f'INFO  {len(js)} joint_states, {len(od)} odometry messages; odometry path {travel:.3f} m, '
          f'turned {math.degrees(turn):.1f} deg in total')
    check(len(comp) >= 0.95 * len(later), f'{len(comp)} of {len(later)} odometry messages compared (>= 95 %)')
    if comp:
        check(max(perr) <= 0.001, f'max position difference {max(perr) * 1000:.6f} mm <= 1 mm')
        check(max(yerr) <= 0.01, f'max yaw difference {max(yerr):.8f} deg <= 0.01 deg')
    print(f'# overall: {"ALL CHECKS PASSED" if fails == 0 else f"{fails} CHECK(S) FAILED"}')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
