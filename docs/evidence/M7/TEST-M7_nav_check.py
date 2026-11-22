#!/usr/bin/env python3
"""M7 offline navigation checker (DEC-073 bounds; M7 Task B). Standard library only (runs in CI).

Usage: python3 -I TEST-M7_nav_check.py <prefix> --test TEST-M7-03|TEST-M7-04|TEST-M7-05|TEST-M7-06 [--json <file>]
Reads <prefix>_track.csv, _cmd.csv, _goals.csv, _plans.csv and _meta.json written by TEST-M7_nav_run.py. Exit 0 = every
criterion PASS, 1 = a FAIL, 2 = unusable input (missing files, wrong mode, run facts invalid: RTF < 0.5 or > 2 % of
the samples missing).

Criteria (DEC-073; M7 plan §3.3, §3.4, §8). Geometry from TEST-M7_goals.py (world file, nav2.yaml footprint, goals).
  TEST-M7-03 (mode sequence) and TEST-M7-04 (mode route):
    status        every goal SUCCEEDED (TEST-M7-03: the six goals in SEQUENCE order; TEST-M7-04: the one route goal)
    arrival       per goal, the ground truth after the 2 s hold vs the target: position <= 0.15 m, heading <= 7.0 deg
    clearance     every 10 Hz sample of the whole run: the footprint at the ground-truth pose keeps >= 0.10 m from
                  every obstacle of the world file, L1 included
    cmd_limits    every /cmd_vel message within DEC-025: -0.25 <= v <= 0.5 m/s, |w| <= 1.0 rad/s
    cmd_stamps    every /cmd_vel stamp within the guard window: |clock at receipt - stamp| <= 0.5 s (DEC-029)
    guard_drops   every /cmd_vel message forwarded by cmd_vel_guard: zero drops. Matched one-to-one by identical
                  velocity and the guard's stamp rule, forwarded stamp = min(stamp, guard clock): at or up to 10 ms
                  before the input stamp (an exact-stamp match counted 5 clamped stamps as drops in the Task B dry run)
    publishers    /cmd_vel has exactly one publisher, velocity_smoother (TwistStamped), at the start and the end
    moving_*      DEC-059 moving bounds on the samples while the robot moves (definition and percentile of
                  TEST-M6_pose_check.py, imported): P95 position <= 0.10 m, P95 heading <= 2.0 deg, max <= 0.25 m
    time          per goal, accepted -> result <= 2.0 x nominal; nominal = first planned path length / 0.30 m/s +
                  heading change / 0.5 rad/s. Heading change (this checker's definition of the DEC-073 term): the
                  first plan resampled every 0.5 m of arc length; |turn from the start heading to the first segment|
                  + sum of |turns between segments| + |turn from the last segment to the goal heading|.
  TEST-M7-05 (mode invalid):
    invalid_status  each invalid goal ends ABORTED or REJECTED
    invalid_time    answered within 60 s of being sent
    invalid_motion  ground-truth travel while the goal is active and during the hold after it <= 0.05 m
    (cmd_limits, cmd_stamps, guard_drops and publishers as above; a log without any command passes them here, as
    refused goals send none; in the other tests an empty command log fails)
  TEST-M7-06 (mode cancel):
    cancel_status   the goal ends CANCELED; the cancel was requested after >= 1.0 m of travel (a run fact: else the
                    run is unusable, exit 2)
    cancel_stop     ground-truth travel from the cancel's acceptance to the end of the hold <= 0.15 m
    cancel_still    after the cancel, a 5 s window in which the robot moves at <= 0.01 m/s throughout (10 Hz samples)
    (cmd_limits, cmd_stamps, guard_drops and publishers as above)
INFO: per-goal values, the worst clearance sample and obstacle, command extremes, RTF.
Measure names (used by TEST-M7-07): status, arrival_position, arrival_heading, clearance, cmd_limits, cmd_stamps,
guard_drops, publishers, moving_p95_position, moving_p95_heading, moving_max_position, time, invalid_status,
invalid_time, invalid_motion, cancel_status, cancel_stop, cancel_still.
"""
import argparse
import csv
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


goals = _load('goals7', os.path.join(HERE, 'TEST-M7_goals.py'))
pc = _load('pose_check', os.path.join(HERE, '..', 'M6', 'TEST-M6_pose_check.py'))

ARRIVE_POS, ARRIVE_YAW = 0.15, math.radians(7.0)
CLEARANCE = goals.CLEARANCE                  # 0.10 m
V_MAX, V_MIN, W_MAX = 0.5, -0.25, 1.0        # DEC-025
GUARD_WINDOW = 0.5                           # s, DEC-029
CLAMP_MAX = 0.010                            # s, largest stamp clamp accepted as "forwarded" (see match_guard)
NOMINAL_V, NOMINAL_W, TIME_FACTOR = 0.30, 0.5, 2.0
RESAMPLE = 0.5                               # m, plan resampling for the heading change
INVALID_TIME, INVALID_MOTION = 60.0, 0.05
CANCEL_STOP, STILL_V, STILL_T = 0.15, 0.01, 5.0
RTF_MIN, MISSING_MAX = 0.5, 0.02
PUBLISHER = ['velocity_smoother geometry_msgs/msg/TwistStamped']
MODES = {'TEST-M7-03': 'sequence', 'TEST-M7-04': 'route', 'TEST-M7-05': 'invalid', 'TEST-M7-06': 'cancel'}
EPS = 1e-9


class Unusable(Exception):
    pass


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def read_csv(path):
    if not os.path.isfile(path):
        raise Unusable(f'missing {os.path.basename(path)}')
    with open(path, newline='') as f:
        return [{k: num(v) for k, v in row.items()} for row in csv.DictReader(f)]


def load(prefix):
    data = {k: read_csv(f'{prefix}_{k}.csv') for k in ('track', 'cmd', 'goals', 'plans')}
    if not os.path.isfile(prefix + '_meta.json'):
        raise Unusable('missing _meta.json')
    with open(prefix + '_meta.json') as f:
        data['meta'] = json.load(f)
    return data


def resample(pts, step=RESAMPLE):
    """Points every `step` m of arc length along a polyline (first and last kept)."""
    if len(pts) < 2:
        return list(pts)
    out, carry = [pts[0]], 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        pos = step - carry
        while pos <= seg:
            out.append((a[0] + (b[0] - a[0]) * pos / seg, a[1] + (b[1] - a[1]) * pos / seg))
            pos += step
        carry = (carry + seg) % step
    if math.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) > 1e-6:
        out.append(pts[-1])
    return out


def heading_change(plan, start_yaw, goal_yaw):
    pts = resample(plan)
    hs = [math.atan2(b[1] - a[1], b[0] - a[0]) for a, b in zip(pts, pts[1:])
          if math.hypot(b[0] - a[0], b[1] - a[1]) > 1e-6]
    if not hs:
        return abs(pc.wrap(goal_yaw - start_yaw))
    return (abs(pc.wrap(hs[0] - start_yaw)) + sum(abs(pc.wrap(b - a)) for a, b in zip(hs, hs[1:]))
            + abs(pc.wrap(goal_yaw - hs[-1])))


def travel_at(track, t):
    """Ground-truth travel at simulation time t (linear interpolation in the 10 Hz track)."""
    prev = None
    for r in track:
        if r['sim_t'] >= t:
            if prev is None:
                return r['travel']
            f = (t - prev['sim_t']) / max(r['sim_t'] - prev['sim_t'], EPS)
            return prev['travel'] + f * (r['travel'] - prev['travel'])
        prev = r
    return track[-1]['travel'] if track else float('nan')


def match_guard(cin, cout):
    """One-to-one match of /cmd_vel messages to guard outputs. The guard forwards a command unchanged except
    stamp = min(stamp, guard clock) (cmd_vel_guard.cpp), so a match has the same v and w and a forwarded stamp at or
    up to CLAMP_MAX before the input stamp (the smoother can stamp 1 ms ahead of the guard's clock; Task B dry run).
    Returns (unmatched inputs, number matched with a clamped stamp)."""
    pool = {}
    for c in cout:
        pool.setdefault((c['v'], c['w']), []).append(c['stamp'])
    missed, clamped = [], 0
    for c in cin:
        cands = pool.get((c['v'], c['w']), [])
        ok = [s for s in cands if -EPS <= c['stamp'] - s <= CLAMP_MAX + EPS]
        if not ok:
            missed.append(c)
            continue
        s = max(ok)                     # the latest admissible stamp: the exact one if present
        cands.remove(s)
        clamped += abs(c['stamp'] - s) > 1e-6
    return missed, clamped


def check_commands(cmd, meta, res, info, require=True):
    """require=False (TEST-M7-05): a run with no command at all is correct (the goals are refused before any
    motion), so the command criteria hold for an empty log; elsewhere an empty log means a broken recording."""
    cin = [c for c in cmd if c['topic'] == 'cmd_vel']
    some = bool(cin) or not require
    cout = [c for c in cmd if c['topic'] == 'guard']
    vs, ws = [c['v'] for c in cin], [c['w'] for c in cin]
    bad = [c for c in cin if not (V_MIN - EPS <= c['v'] <= V_MAX + EPS and abs(c['w']) <= W_MAX + EPS)]
    res.append(('cmd_limits', some and not bad,
                f'/cmd_vel within DEC-025: {len(cin) - len(bad)} of {len(cin)}; v {min(vs, default=0):.3f}..'
                f'{max(vs, default=0):.3f} m/s (limits {V_MIN}..{V_MAX}), |w| max {max(map(abs, ws), default=0):.3f} '
                f'rad/s (limit {W_MAX})'))
    ages = [abs(c['clock'] - c['stamp']) for c in cin]
    res.append(('cmd_stamps', some and max(ages, default=0.0) <= GUARD_WINDOW,
                f'/cmd_vel stamps within the guard window: |clock - stamp| max {max(ages, default=float("nan")):.3f} s '
                f'(<= {GUARD_WINDOW} s)'))
    missed, clamped = match_guard(cin, cout)
    res.append(('guard_drops', some and not missed,
                f'guard forwarded {len(cin) - len(missed)} of {len(cin)} /cmd_vel messages (zero drops required; '
                f'{clamped} forwarded with the stamp clamped to the guard clock)'))
    p0, p1 = meta.get('cmd_vel_publishers_start'), meta.get('cmd_vel_publishers_end')
    res.append(('publishers', p0 == PUBLISHER and p1 == PUBLISHER,
                f'/cmd_vel publishers at start {p0}, at end {p1} (expected {PUBLISHER})'))


def check_clearance(track, res, info):
    boxes = goals.route5.world_boxes(goals.WORLD)
    polys = {n: goals.box_poly(b) for n, b in boxes.items()}
    fp = goals.footprint()
    worst = (math.inf, None, None)
    for r in track:
        poly = goals.place(fp, r['gt_x'], r['gt_y'], r['gt_yaw'])
        for n, bp in polys.items():
            d = goals.poly_dist(poly, bp)
            if d < worst[0]:
                worst = (d, n, r['sim_t'])
    res.append(('clearance', bool(track) and worst[0] >= CLEARANCE - EPS,
                f'clearance footprint (ground truth) to world obstacles, L1 included: minimum {worst[0]:.3f} m to '
                f'{worst[1]} at simulation time {worst[2]} (>= {CLEARANCE} m; {len(track)} samples)'))


def check_moving(track, res, info):
    flags = pc.moving_flags(track)
    mv = [r for r, f in zip(track, flags) if f and isinstance(r['est_x'], float) and not math.isnan(r['est_x'])]
    if not mv:
        res.append(('moving_p95_position', False, 'no moving samples to judge'))
        return
    errs = [pc.errors(r) for r in mv]
    mpos, myaw = [e[0] for e in errs], [e[1] for e in errs]
    res.append(('moving_p95_position', pc.p95(mpos) <= pc.P95_POS,
                f'moving P95 position error {pc.p95(mpos) * 1000:.1f} mm (<= {pc.P95_POS * 1000:.0f} mm)'))
    res.append(('moving_p95_heading', pc.p95(myaw) <= pc.P95_YAW,
                f'moving P95 heading error {math.degrees(pc.p95(myaw)):.3f} deg (<= {math.degrees(pc.P95_YAW):.1f} deg)'))
    res.append(('moving_max_position', max(mpos) <= pc.MAX_POS,
                f'moving maximum position error {max(mpos) * 1000:.1f} mm (<= {pc.MAX_POS * 1000:.0f} mm)'))
    info.append(f'track samples {len(track)}, moving {sum(flags)}, judged {len(mv)}; maximum heading error '
                f'{math.degrees(max(myaw)):.3f} deg')


def check_navigation(test, d, res, info):
    rows, plans = d['goals'], {}
    for p in d['plans']:
        plans.setdefault(p['label'], []).append((int(p['index']), p['x'], p['y']))
    want = goals.SEQUENCE if test == 'TEST-M7-03' else ['route_' + '-'.join(goals.ROUTE)]
    labels = [r['label'] for r in rows]
    res.append(('status', labels == want and all(r['status'] == 'SUCCEEDED' for r in rows),
                'results: ' + ', '.join(f'{r["label"]} {r["status"]}' for r in rows) + f' (expected {want}, all SUCCEEDED)'))
    pos_ok, yaw_ok, time_ok, ptxt, ytxt, ttxt = True, True, True, [], [], []
    for r in rows:
        gyaw = math.radians(r['goal_yaw_deg'])
        e = math.hypot(r['settled_gt_x'] - r['goal_x'], r['settled_gt_y'] - r['goal_y'])
        ey = abs(pc.wrap(r['settled_gt_yaw'] - gyaw))
        pos_ok &= e <= ARRIVE_POS + EPS
        yaw_ok &= ey <= ARRIVE_YAW + EPS
        ptxt.append(f'{r["label"]} {e:.3f}')
        ytxt.append(f'{r["label"]} {math.degrees(ey):.2f}')
        plan = [(x, y) for _, x, y in sorted(plans.get(r['label'], []))]
        if not plan or not isinstance(r['plan_length'], float):
            time_ok = False
            ttxt.append(f'{r["label"]} no plan recorded')
            continue
        nominal = r['plan_length'] / NOMINAL_V + heading_change(plan, r['start_gt_yaw'], gyaw) / NOMINAL_W
        dur = r['result_t'] - r['accepted_t'] if isinstance(r['accepted_t'], float) else float('inf')
        time_ok &= dur <= TIME_FACTOR * nominal + EPS
        ttxt.append(f'{r["label"]} {dur:.1f}/{nominal:.1f} s ({dur / nominal:.2f}x)')
    res.append(('arrival_position', bool(rows) and pos_ok,
                f'arrival position error (ground truth after the hold) m: {", ".join(ptxt)} (<= {ARRIVE_POS})'))
    res.append(('arrival_heading', bool(rows) and yaw_ok,
                f'arrival heading error deg: {", ".join(ytxt)} (<= {math.degrees(ARRIVE_YAW):.1f})'))
    res.append(('time', bool(rows) and time_ok,
                f'goal time accepted -> result / nominal: {", ".join(ttxt)} (<= {TIME_FACTOR}x)'))
    check_clearance(d['track'], res, info)
    check_moving(d['track'], res, info)


def check_invalid(d, res, info):
    rows = d['goals']
    want = list(goals.INVALID)
    labels = [r['label'] for r in rows]
    res.append(('invalid_status', labels == want and all(r['status'] in ('ABORTED', 'REJECTED') for r in rows),
                'results: ' + ', '.join(f'{r["label"]} {r["status"]}' for r in rows) + f' (expected {want}, '
                'ABORTED or REJECTED)'))
    t = [(r['label'], r['result_t'] - r['sent_t']) for r in rows]
    res.append(('invalid_time', bool(rows) and all(v <= INVALID_TIME + EPS for _, v in t),
                'answered after ' + ', '.join(f'{lbl} {v:.1f} s' for lbl, v in t) + f' (<= {INVALID_TIME:.0f} s)'))
    m = [(r['label'], r['settled_travel'] - r['start_travel']) for r in rows]
    res.append(('invalid_motion', bool(rows) and all(v <= INVALID_MOTION + EPS for _, v in m),
                'ground-truth travel ' + ', '.join(f'{lbl} {v * 1000:.1f} mm' for lbl, v in m) +
                f' (<= {INVALID_MOTION * 1000:.0f} mm)'))


def check_cancel(d, res, info):
    rows, track = d['goals'], d['track']
    if len(rows) != 1 or not isinstance(rows[0]['cancel_acc_t'], float):
        raise Unusable('cancel mode needs one goal row with an accepted cancel')
    r = rows[0]
    if not r['cancel_travel'] >= goals.CANCEL_AFTER - EPS:
        raise Unusable(f'cancel requested after {r["cancel_travel"]} m of travel (< {goals.CANCEL_AFTER} m)')
    res.append(('cancel_status', r['status'] == 'CANCELED',
                f'result {r["status"]} (CANCELED expected); cancel accepted after {r["cancel_travel"]:.3f} m of travel'))
    t0 = r['cancel_acc_t']
    stop = r['settled_travel'] - travel_at(track, t0)
    res.append(('cancel_stop', stop <= CANCEL_STOP + EPS,
                f'travel from the cancel acceptance to the end of the hold {stop * 1000:.1f} mm (<= {CANCEL_STOP * 1000:.0f} mm)'))
    after = [x for x in track if x['sim_t'] >= t0]
    found = None
    for i, a in enumerate(after):
        window = [x for x in after[i:] if x['sim_t'] <= a['sim_t'] + STILL_T + EPS]
        if window[-1]['sim_t'] < a['sim_t'] + STILL_T - 0.1 - EPS:
            break                                    # not enough samples left for a 5 s window
        speeds = [math.hypot(q['gt_x'] - p['gt_x'], q['gt_y'] - p['gt_y']) / max(q['sim_t'] - p['sim_t'], EPS)
                  for p, q in zip(window, window[1:])]
        if speeds and max(speeds) <= STILL_V:
            found = (a['sim_t'] - t0, max(speeds))
            break
    res.append(('cancel_still', found is not None,
                f'still (<= {STILL_V} m/s) for {STILL_T:.0f} s: ' + (f'from {found[0]:.1f} s after the cancel, '
                f'maximum speed {found[1] * 1000:.2f} mm/s' if found else 'no such window in the recording')))


def check(prefix, test):
    d = load(prefix)
    meta = d['meta']
    if meta.get('mode') != MODES[test]:
        raise Unusable(f'mode {meta.get("mode")!r} recorded; {test} needs {MODES[test]!r}')
    n = meta.get('track_samples', 0) + meta.get('missing_samples', 0)
    if meta.get('rtf', 0) < RTF_MIN or n == 0 or meta.get('missing_samples', 0) > MISSING_MAX * n:
        raise Unusable(f'run facts invalid: RTF {meta.get("rtf")}, missing {meta.get("missing_samples")} of {n}')
    res, info = [], [f'RTF {meta["rtf"]:.2f}; {meta["sim_duration"]:.1f} s simulation time; travel '
                     f'{meta["travel"]:.2f} m; {meta["missing_samples"]} of {n} samples missing']
    if test in ('TEST-M7-03', 'TEST-M7-04'):
        check_navigation(test, d, res, info)
    elif test == 'TEST-M7-05':
        check_invalid(d, res, info)
    else:
        check_cancel(d, res, info)
    check_commands(d['cmd'], meta, res, info, require=test != 'TEST-M7-05')
    return res, info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('prefix')
    ap.add_argument('--test', choices=sorted(MODES), required=True)
    ap.add_argument('--json')
    args = ap.parse_args()
    print(f'# M7 navigation check ({args.test}): {os.path.basename(args.prefix)}')
    try:
        res, info = check(args.prefix, args.test)
    except Unusable as exc:
        print(f'# unusable input: {exc}')
        return 2
    for name, ok, text in res:
        print(f'{"PASS" if ok else "FAIL"}  {name}: {text}')
    for text in info:
        print(f'INFO  {text}')
    fails = [n for n, ok, _ in res if not ok]
    if args.json:
        with open(args.json, 'w') as f:
            json.dump({'test': args.test, 'results': {n: ok for n, ok, _ in res}}, f, indent=1)
    print(f'# result: {"PASS" if not fails else "FAIL (" + ", ".join(fails) + ")"}')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
