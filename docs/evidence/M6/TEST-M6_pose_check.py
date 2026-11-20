#!/usr/bin/env python3
"""M6 offline pose checker (DEC-059 bounds; M6 Task B). Standard library only (runs in CI).

Usage: python3 -I TEST-M6_pose_check.py <prefix> [--recovery] [--drift <route> | --fusion <route>] [--json <file>]
Reads <prefix>_rest.csv and <prefix>_track.csv written by TEST-M6_run.py. Errors are estimate minus ground truth:
position = distance, heading = wrapped yaw difference. Exit 0 = every criterion PASS, 1 = a FAIL, 2 = unusable input.

Criteria (DEC-059; test_plan §11):
  rest       every rest point: position <= 0.05 m and heading <= 1.0 deg              (TEST-M6-03, -05, -06, -07)
  moving     the 10 Hz samples while the robot moves: P95 position <= 0.10 m, P95 heading <= 2.0 deg, maximum
             position <= 0.25 m. "Moving": the ground truth moved more than 2 mm or turned more than 0.005 rad
             since the previous sample (0.1 s), i.e. faster than 0.02 m/s or 0.05 rad/s.
  --recovery (TEST-M6-04, wrong start) the wrong start must become visible: a 10 Hz sample outside the rest bounds
             (AMCL publishes the injected pose in map -> odom only at its next filter update, so the first samples
             can still be correct; found in the Task B dry run). Convergence = the first sample after that one with
             position <= 0.05 m and heading <= 1.0 deg; it must come within 6.0 m (DEC-065) of ground-truth travel (counted from
             the start of the route). The rest and moving criteria then apply only after convergence (rest points
             after it; samples after it).
  --drift R  (TEST-M6-05) the odometry end-of-route position error must exceed 3 x 0.05 m and agree with the
             CALC-M5-04 prediction for route R (forward or reverse; separation x 1.02, radii x 1.01) within +/- 25 %.
  --fusion R (TEST-M6-07, ekf:=true, separation x 1.02 alone; M6 plan §3.4 CALC-M6-04) at the end of the route: the raw
             wheel odometry (raw_* columns, /diff_drive_controller/odom) position error agrees with the CALC-M5-04
             prediction for route R with separation x 1.02 alone within +/- 25 %; the fused odometry
             (odom -> base_footprint, published by the EKF) heading error <= 0.5 deg and position error <= 25 % of
             the raw one.
Percentiles: nearest-rank (the smallest value with at least 95 % of the samples at or below it).
INFO: counts, maxima, end-of-route errors, the worst rest point.
Measure names (used by TEST-M6-08): rest_position, rest_heading, moving_p95_position, moving_p95_heading,
moving_max_position, recovery_travel, drift, fusion_raw, fusion_yaw, fusion_position.
"""
import argparse
import csv
import importlib.util
import json
import math
import os
import sys

REST_POS, REST_YAW = 0.05, math.radians(1.0)
P95_POS, P95_YAW, MAX_POS = 0.10, math.radians(2.0), 0.25
RECOVERY_TRAVEL = 6.0   # m, DEC-065 (amends DEC-063's 4.0 m, which amended DEC-059's 3 m)
MOVE_D, MOVE_A = 0.002, 0.005
DRIFT_MIN, DRIFT_TOL = 3 * REST_POS, 0.25
FUSED_YAW, FUSED_POS_RATIO = math.radians(0.5), 0.25   # M6 plan §3.4 (TEST-M6-07)
_spec = importlib.util.spec_from_file_location('route6', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                     'TEST-M6_route.py'))
route6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(route6)
# CALC-M5-04 end-of-route odometry position error per route (separation x 1.02, radii x 1.01), from TEST-M6_route.py
CALC_M5_04 = {name: route6.predict(name)[0] for name in route6.ROUTES}
# The same with separation x 1.02 alone (radii exact): the TEST-M6-07 injection (CALC-M6-04)
CALC_M5_04_SEP = {name: route6.predict(name, 1.02, 1.0)[0] for name in route6.ROUTES}


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def load(path):
    with open(path, newline='') as f:
        return [{k: float(v) if v != '' else float('nan') for k, v in row.items()} for row in csv.DictReader(f)]


def errors(r):
    return math.hypot(r['est_x'] - r['gt_x'], r['est_y'] - r['gt_y']), abs(wrap(r['est_yaw'] - r['gt_yaw']))


def p95(values):
    if not values:
        return float('nan')
    s = sorted(values)
    return s[max(0, math.ceil(0.95 * len(s)) - 1)]


def moving_flags(track):
    flags = [False]
    for a, b in zip(track, track[1:]):
        flags.append(math.hypot(b['gt_x'] - a['gt_x'], b['gt_y'] - a['gt_y']) > MOVE_D
                     or abs(wrap(b['gt_yaw'] - a['gt_yaw'])) > MOVE_A)
    return flags


def check(prefix, recovery=False, drift=None, fusion=None):
    """Returns (results: list of (measure, ok, text)), info lines, summary dict)."""
    rest, track = load(prefix + '_rest.csv'), load(prefix + '_track.csv')
    if not rest or len(track) < 10:
        raise ValueError(f'too little data: {len(rest)} rest points, {len(track)} track samples')
    res, info, summ = [], [], {}
    t_conv = None
    if recovery:
        within = [errors(r)[0] <= REST_POS and errors(r)[1] <= REST_YAW for r in track]
        k_off = next((k for k, w in enumerate(within) if not w), None)   # the wrong start becomes visible
        k_conv = next((k for k in range(k_off, len(track)) if within[k]), None) if k_off is not None else None
        if k_off is None:
            res.append(('recovery_travel', False, 'the wrong start never appeared in the estimate (no sample outside '
                                                  'the rest bounds): the injection was not tested'))
            t_conv = float('inf')
        else:
            off = track[k_off]
            e = errors(off)
            info.append(f'wrong start visible at simulation time {off["sim_t"]:.1f} s, travel {off["travel"]:.2f} m: '
                        f'error {e[0] * 1000:.1f} mm, {math.degrees(e[1]):.2f} deg')
            conv = track[k_conv] if k_conv is not None else None
            tr = conv['travel'] if conv else float('inf')
            t_conv = conv['sim_t'] if conv else float('inf')
            res.append(('recovery_travel', tr <= RECOVERY_TRAVEL,
                        f'converged to the rest bounds after {tr:.2f} m of travel (<= {RECOVERY_TRAVEL} m)'
                        + (f', at simulation time {t_conv:.1f} s' if conv else ': never')))
            summ['recovery_travel_m'] = tr
    rest_used = [r for r in rest if t_conv is None or r['sim_t'] >= t_conv]
    info.append(f'rest points judged: {len(rest_used)} of {len(rest)}')
    pos = [errors(r)[0] for r in rest_used]
    yaw = [errors(r)[1] for r in rest_used]
    if rest_used:
        i, j = max(range(len(pos)), key=pos.__getitem__), max(range(len(yaw)), key=yaw.__getitem__)
        res.append(('rest_position', max(pos) <= REST_POS,
                    f'rest position error max {max(pos) * 1000:.1f} mm at rest point {int(rest_used[i]["rest_point"])} '
                    f'(<= {REST_POS * 1000:.0f} mm, {len(pos)} rest points)'))
        res.append(('rest_heading', max(yaw) <= REST_YAW,
                    f'rest heading error max {math.degrees(max(yaw)):.3f} deg at rest point '
                    f'{int(rest_used[j]["rest_point"])} (<= {math.degrees(REST_YAW):.1f} deg)'))
        summ.update(rest_pos_max_m=max(pos), rest_yaw_max_deg=math.degrees(max(yaw)))
    else:
        res.append(('rest_position', False, 'no rest point after convergence'))
    flags = moving_flags(track)
    mv = [r for r, f in zip(track, flags) if f and (t_conv is None or r['sim_t'] >= t_conv)]
    mpos = [errors(r)[0] for r in mv]
    myaw = [errors(r)[1] for r in mv]
    info.append(f'track samples {len(track)}, moving {sum(flags)}, judged {len(mv)}')
    if mv:
        k = max(range(len(mpos)), key=mpos.__getitem__)
        res.append(('moving_p95_position', p95(mpos) <= P95_POS,
                    f'moving P95 position error {p95(mpos) * 1000:.1f} mm (<= {P95_POS * 1000:.0f} mm)'))
        res.append(('moving_p95_heading', p95(myaw) <= P95_YAW,
                    f'moving P95 heading error {math.degrees(p95(myaw)):.3f} deg (<= {math.degrees(P95_YAW):.1f} deg)'))
        res.append(('moving_max_position', max(mpos) <= MAX_POS,
                    f'moving maximum position error {max(mpos) * 1000:.1f} mm at simulation time '
                    f'{mv[k]["sim_t"]:.1f} s (<= {MAX_POS * 1000:.0f} mm)'))
        info.append(f'moving maximum heading error {math.degrees(max(myaw)):.3f} deg')
        summ.update(p95_pos_m=p95(mpos), p95_yaw_deg=math.degrees(p95(myaw)), max_pos_m=max(mpos))
    else:
        res.append(('moving_p95_position', False, 'no moving samples to judge'))
    end = rest[-1]
    oe = math.hypot(end['odom_x'] - end['gt_x'], end['odom_y'] - end['gt_y'])
    oy = math.degrees(wrap(end['odom_yaw'] - end['gt_yaw']))
    ee = errors(end)
    info.append(f'end of route: estimate error {ee[0] * 1000:.1f} mm, {math.degrees(ee[1]):.3f} deg; odometry error '
                f'{oe * 1000:.1f} mm, {oy:+.3f} deg; travel {end["travel"]:.2f} m')
    summ.update(odom_end_m=oe, odom_end_yaw_deg=oy)
    if drift:
        pred = CALC_M5_04[drift]
        ok = oe > DRIFT_MIN and abs(oe - pred) <= DRIFT_TOL * pred
        res.append(('drift', ok, f'odometry end-of-route error {oe * 1000:.1f} mm: > {DRIFT_MIN * 1000:.0f} mm and '
                                 f'within +/- {DRIFT_TOL:.0%} of the CALC-M5-04 {drift} prediction {pred * 1000:.0f} mm '
                                 f'({(oe / pred - 1) * 100:+.1f} %)'))
    if fusion:
        pred = CALC_M5_04_SEP[fusion]
        if 'raw_x' not in end or math.isnan(end['raw_x']):
            res.append(('fusion_raw', False, 'no raw-odometry pose recorded at the last rest point'))
        else:
            re_ = math.hypot(end['raw_x'] - end['gt_x'], end['raw_y'] - end['gt_y'])
            ry = math.degrees(wrap(end['raw_yaw'] - end['gt_yaw']))
            res.append(('fusion_raw', abs(re_ - pred) <= DRIFT_TOL * pred,
                        f'raw odometry end-of-route error {re_ * 1000:.1f} mm, {ry:+.3f} deg: within +/- '
                        f'{DRIFT_TOL:.0%} of the CALC-M5-04 {fusion} prediction for separation x 1.02 alone '
                        f'{pred * 1000:.0f} mm ({(re_ / pred - 1) * 100:+.1f} %)'))
            res.append(('fusion_yaw', abs(math.radians(oy)) <= FUSED_YAW,
                        f'fused odometry end-of-route heading error {oy:+.3f} deg (<= {math.degrees(FUSED_YAW):.1f} '
                        f'deg; raw {ry:+.3f} deg)'))
            res.append(('fusion_position', oe <= FUSED_POS_RATIO * re_,
                        f'fused odometry end-of-route position error {oe * 1000:.1f} mm = {oe / re_:.1%} of the raw '
                        f'{re_ * 1000:.1f} mm (<= {FUSED_POS_RATIO:.0%})'))
            summ.update(raw_end_m=re_, raw_end_yaw_deg=ry)
    return res, info, summ


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('prefix')
    ap.add_argument('--recovery', action='store_true')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--drift', choices=sorted(CALC_M5_04))
    g.add_argument('--fusion', choices=sorted(CALC_M5_04_SEP))
    ap.add_argument('--json')
    a = ap.parse_args()
    print(f'# TEST-M6 pose check: {os.path.basename(a.prefix)}; recovery {a.recovery}; drift {a.drift}; '
          f'fusion {a.fusion}')
    try:
        res, info, summ = check(a.prefix, a.recovery, a.drift, a.fusion)
    except (OSError, ValueError, KeyError) as exc:
        print(f'# unusable input: {type(exc).__name__}: {exc}')
        return 2
    for m, ok, text in res:
        print(f'{"PASS" if ok else "FAIL"}  [{m}] {text}')
    for line in info:
        print(f'INFO  {line}')
    fails = [m for m, ok, _ in res if not ok]
    if a.json:
        with open(a.json, 'w') as f:
            json.dump({'failed': fails, **summ}, f, indent=1, sort_keys=True)
    print(f'# result: {"PASS" if not fails else "FAIL (" + ", ".join(fails) + ")"}')
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
