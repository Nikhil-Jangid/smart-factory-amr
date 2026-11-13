#!/usr/bin/env python3
"""TEST-M4-09 checker: each injected calibration error must make its target criterion FAIL, with the measured error
within ± 25 % of the CALC-M4-05 prediction (M4 plan §3.3b; REQ-M4-08; DEC-043, DEC-044). Written before its run.

Usage: python3 -I docs/evidence/M4/TEST-M4-09_check.py [TAG] [product-state line]
Reads the four case logs written by TEST-M4-09_procedure.sh. Only valid attempts count (harness exit 0 or 1);
invalid attempts (exit 2) are skipped, as in every M4 procedure. Exit 0 = PASS, 1 = FAIL.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
K_L, B = 1.005, 0.400
LEG_RATE = -2 * (K_L - 1) / (B * (K_L + 1))   # rad per metre of true straight travel (odometry - truth)
TURN_FRAC = (K_L - 1) / (K_L + 1)             # of the true in-place turn
LEG_M = 0.98                                   # measured leg length of a 5 s, 0.2 m/s leg (TEST-M2-05)
TOL = 0.25
fails = 0


def check(ok, text):
    global fails
    print(f'{"PASS" if ok else "FAIL"}  {text}')
    fails += 0 if ok else 1


def runs(path):
    """Valid attempts of a procedure log: list of the harness output text per attempt."""
    txt = open(path).read()
    parts = re.split(r'^## attempt \d+.*$', txt, flags=re.M)[1:]
    return [p for p in parts if re.search(r'^# harness exit [01];', p, re.M)]


def near(meas, pred):
    return abs(meas - pred) <= TOL * abs(pred)


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else ''
    product = sys.argv[2] if len(sys.argv) > 2 else ''
    log = lambda case, mode: os.path.join(HERE, f'TEST-M4-09{tag}_{case}_{mode}_review.log')
    print(f'# TEST-M4-09 check, tag "{tag}"; tolerance ± {TOL * 100:.0f} % of each prediction (CALC-M4-05)')

    rr = runs(log('R', 'straight'))
    check(len(rr) >= 3, f'R (radii x 1.01, straight): {len(rr)} valid runs (>= 3)')
    for i, r in enumerate(rr, 1):
        for leg in ('forward', 'reverse'):
            m = re.search(rf'^(PASS|FAIL)  {leg}: distance error [+-][\d.]+ mm = ([+-][\d.]+) %', r, re.M)
            if not m:
                check(False, f'R run {i} {leg}: distance-error line missing'); continue
            v = float(m.group(2))
            check(m.group(1) == 'FAIL' and near(v, 1.00),
                  f'R run {i} {leg}: distance criterion {m.group(1)} (expected FAIL), error {v:+.4f} %, '
                  f'prediction +1.00 % ± 25 %')

    rb = runs(log('B', 'rotate'))
    check(len(rb) >= 3, f'B (separation x 1.02, rotate): {len(rb)} valid runs (>= 3)')
    for i, r in enumerate(rb, 1):
        for sgn in ('+', '-'):
            g = re.search(rf'^INFO  rotate {re.escape(sgn)}360: ground truth .*?dpsi ([+-][\d.]+) deg', r, re.M)
            m = re.search(rf'^(PASS|FAIL)  rotate {re.escape(sgn)}360: yaw error ([+-][\d.]+) deg', r, re.M)
            if not (g and m):
                check(False, f'B run {i} {sgn}360: lines missing'); continue
            pred = (1 / 1.02 - 1) * float(g.group(1))
            v = float(m.group(2))
            check(m.group(1) == 'FAIL' and near(v, pred),
                  f'B run {i} {sgn}360: yaw criterion {m.group(1)} (expected FAIL), error {v:+.3f} deg, '
                  f'prediction {pred:+.3f} deg ± 25 % (true turn {float(g.group(1)):+.2f} deg)')

    for mode, name in (('square_ccw', 'CCW'), ('square_cw', 'CW')):
        rl = runs(log('L', mode))
        check(len(rl) >= 3, f'L (left radius x 1.005, square {name}): {len(rl)} valid runs (>= 3)')
        for i, r in enumerate(rl, 1):
            g = re.search(rf'^INFO  square {name}: ground truth .*?dpsi ([+-][\d.]+) deg', r, re.M)
            m = re.search(rf'^(PASS|FAIL)  square {name}: yaw error ([+-][\d.]+) deg', r, re.M)
            if not (g and m):
                check(False, f'L {name} run {i}: lines missing'); continue
            length = 4 * LEG_M
            legs_true = -LEG_RATE * length
            turns_true = math.radians(float(g.group(1))) - legs_true
            pred = math.degrees(LEG_RATE * length + TURN_FRAC * turns_true)
            v = float(m.group(2))
            check(m.group(1) == 'FAIL' and near(v, pred),
                  f'L {name} run {i}: yaw criterion {m.group(1)} (expected FAIL), error {v:+.3f} deg, '
                  f'prediction {pred:+.3f} deg ± 25 %')

    check(product.endswith('yes'), f'product configuration untouched: {product or "state not given"}')
    print(f'# overall: {"ALL CHECKS PASSED" if fails == 0 else f"{fails} CHECK(S) FAILED"}')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
