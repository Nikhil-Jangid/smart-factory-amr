#!/usr/bin/env python3
"""TEST-M5-06 drift check (REQ-M5-07; M5 Task D). No ROS needed.

Usage: python3 -I TEST-M5-06_drift_check.py <mapping review log>
Exit 0 = every valid attempt passes, 1 = otherwise.

The mapping procedure (TEST-M5_procedure.sh, run by TEST-M5-06_procedure.sh with the TEST-M4-09 odometry overrides)
already checks, per attempt, the map (TEST-M5_map_check.py, DEC-047 bounds) and the SLAM pose at every rest point
(TEST-M5_map_run.py, 0.05 m and 1.0 deg). This script checks the other half of the TEST-M5-06 criterion, on the last
rest point (the end of the route) of each valid attempt, from its CSV (<log name>_a<N>_rest.csv; odom_err_m in m,
odom_yaw_err in rad, odometry minus ground truth):
  1. the odometry drift is real: position error > 3 x 0.05 m = 0.15 m and |yaw error| > 3 x 1.0 deg = 3.0 deg;
  2. it agrees with the CALC-M5-04 prediction (TEST-M5_route.predict_odometry, separation x 1.02, both radii x 1.01)
     within +/- 25 % in position error and in yaw error (same sign).
Valid attempts are those the log does not declare INVALID.
"""
import csv
import importlib.util
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('route', os.path.join(HERE, 'TEST-M5_route.py'))
route = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(route)

SEP, RADIUS = 1.02, 1.01          # TEST-M4-09 overrides (DEC-043), as in TEST-M5-06_procedure.sh
POS_BOUND, YAW_BOUND = 0.05, 1.0  # TEST-M5-04 pose bound (DEC-047)
FACTOR, AGREE = 3.0, 0.25


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    log = sys.argv[1]
    text = open(log).read()
    attempts = [int(n) for n in re.findall(r'^## attempt (\d+)', text, re.M)]
    invalid = {int(n) for n in re.findall(r'^# attempt (\d+) INVALID', text, re.M)}
    base = log[:-len('_review.log')] if log.endswith('_review.log') else os.path.splitext(log)[0]
    px, py, pyaw = route.predict_odometry(sep=SEP, radius=RADIUS)
    net = sum(t for *_, t in route.legs())
    p_pos = math.hypot(px, py)
    p_yaw = math.degrees(math.atan2(math.sin(pyaw - net), math.cos(pyaw - net)))
    print(f'# TEST-M5-06 drift check on {os.path.basename(log)}: attempts {attempts}, invalid {sorted(invalid)}')
    print(f'# CALC-M5-04 prediction (separation x {SEP}, radii x {RADIUS}): position error {p_pos:.4f} m, '
          f'yaw error {p_yaw:+.3f} deg; bounds: > {FACTOR * POS_BOUND:.2f} m and > {FACTOR * YAW_BOUND:.1f} deg, '
          f'within {AGREE:.0%} of the prediction')
    ok, n = True, 0

    def check(cond, text):
        nonlocal ok
        print(f'{"PASS" if cond else "FAIL"}  {text}')
        ok &= bool(cond)

    for a in attempts:
        if a in invalid:
            continue
        path = f'{base}_a{a}_rest.csv'
        if not os.path.exists(path):
            check(False, f'attempt {a}: {os.path.basename(path)} missing')
            continue
        rows = list(csv.DictReader(open(path)))
        last = rows[-1]
        pos = float(last['odom_err_m'])
        yaw = math.degrees(float(last['odom_yaw_err']))
        n += 1
        check(pos > FACTOR * POS_BOUND and abs(yaw) > FACTOR * YAW_BOUND,
              f'attempt {a} (rest point {last["rest_point"]}): odometry drift {pos:.4f} m, {yaw:+.3f} deg exceeds '
              f'3 x the pose bound')
        check(abs(pos - p_pos) <= AGREE * p_pos and yaw * p_yaw > 0 and abs(yaw - p_yaw) <= AGREE * abs(p_yaw),
              f'attempt {a}: agrees with the prediction: position {100 * (pos / p_pos - 1):+.1f} %, yaw '
              f'{100 * (yaw / p_yaw - 1):+.1f} % (each within +/- {AGREE:.0%})')
    check(n >= 1, f'{n} valid attempts checked')
    print(f'# result: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
