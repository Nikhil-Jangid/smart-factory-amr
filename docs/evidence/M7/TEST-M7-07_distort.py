#!/usr/bin/env python3
"""TEST-M7-07: navigation-checker sensitivity (REQ-M7-10; test_plan §12; M7 Task B). Standard library only (CI).

Usage: python3 -I TEST-M7-07_distort.py <recorded prefix>
<recorded prefix>_{track,cmd,goals,plans}.csv and _meta.json are a recorded `--mode sequence` run (TEST-M7_nav_run.py).
The tool writes five distorted copies to a temporary folder and runs TEST-M7_nav_check.py's check() with the TEST-M7-03
criteria on the original and on each copy. Exit 0 if the original PASSES and every copy FAILS on its expected measure
(other measures may fail too; they are reported); 1 otherwise; 2 on unusable input.

Distortions (M7 plan §8, DEC-073 bounds; each changes one measured quantity):
  arrival_offset   the last goal's settled ground truth moved +0.20 m in x        -> expected FAIL: arrival_position (0.15 m)
  arrival_rotate   the last goal's settled ground-truth heading +10 deg          -> expected FAIL: arrival_heading (7.0 deg)
  path_into_obst   the 1 s of track around the closest approach to an obstacle moved towards that obstacle until the
                   footprint gap is 0.03 m; the estimate moved with it, so localization errors are unchanged
                                                                                 -> expected FAIL: clearance (0.10 m)
  cmd_fast         one forward /cmd_vel command (and its guard output, so nothing counts as dropped) set to 0.6 m/s
                                                                                 -> expected FAIL: cmd_limits (0.5 m/s)
  loc_shift        the estimate moved +0.30 m in x in every track sample          -> expected FAIL: moving_p95_position
                                                                                    (0.10 m; also moving_max_position)
"""
import csv
import importlib.util
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('nav_check', os.path.join(HERE, 'TEST-M7_nav_check.py'))
nc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nc)
goals = nc.goals

TEST = 'TEST-M7-03'
EXPECTED = {'arrival_offset': 'arrival_position', 'arrival_rotate': 'arrival_heading',
            'path_into_obst': 'clearance', 'cmd_fast': 'cmd_limits', 'loc_shift': 'moving_p95_position'}
FILES = ('track', 'cmd', 'goals', 'plans')


def read(path):
    with open(path, newline='') as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(path, fields, rows):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def copy(src, dst):
    for k in FILES:
        shutil.copy(f'{src}_{k}.csv', f'{dst}_{k}.csv')
    shutil.copy(f'{src}_meta.json', f'{dst}_meta.json')


def edit(prefix, key, fn):
    fields, rows = read(f'{prefix}_{key}.csv')
    write(f'{prefix}_{key}.csv', fields, fn(rows))


def arrival_offset(rows):
    rows[-1]['settled_gt_x'] = f'{float(rows[-1]["settled_gt_x"]) + 0.20:.6f}'
    return rows


def arrival_rotate(rows):
    rows[-1]['settled_gt_yaw'] = f'{nc.pc.wrap(float(rows[-1]["settled_gt_yaw"]) + math.radians(10.0)):.6f}'
    return rows


def path_into_obst(rows):
    boxes = goals.route5.world_boxes(goals.WORLD)
    fp = goals.footprint()
    best = (math.inf, None, None)
    for i, r in enumerate(rows):
        poly = goals.place(fp, float(r['gt_x']), float(r['gt_y']), float(r['gt_yaw']))
        for n, b in boxes.items():
            d = goals.poly_dist(poly, goals.box_poly(b))
            if d < best[0]:
                best = (d, i, b)
    d, i, b = best
    x, y = float(rows[i]['gt_x']), float(rows[i]['gt_y'])
    cx, cy = min(max(x, b[0]), b[1]), min(max(y, b[2]), b[3])     # closest point of the box to the centre
    L = math.hypot(cx - x, cy - y)
    sx, sy = (cx - x) / L * (d - 0.03), (cy - y) / L * (d - 0.03)
    t0 = float(rows[i]['sim_t'])
    for r in rows:
        if abs(float(r['sim_t']) - t0) <= 0.5:
            for k, s in (('gt_x', sx), ('est_x', sx), ('gt_y', sy), ('est_y', sy)):
                r[k] = f'{float(r[k]) + s:.6f}'
    return rows


def cmd_fast(rows):
    cin = [r for r in rows if r['topic'] == 'cmd_vel' and float(r['v']) > 0.1]
    c = cin[len(cin) // 2]
    out = [r for r in rows if r['topic'] == 'guard' and r['v'] == c['v'] and r['w'] == c['w']
           and 0 <= float(c['stamp']) - float(r['stamp']) <= nc.CLAMP_MAX]
    for r in [c] + out[-1:]:
        r['v'] = repr(0.6)
    return rows


def loc_shift(rows):
    for r in rows:
        r['est_x'] = f'{float(r["est_x"]) + 0.30:.6f}'
    return rows


DISTORT = {'arrival_offset': ('goals', arrival_offset), 'arrival_rotate': ('goals', arrival_rotate),
           'path_into_obst': ('track', path_into_obst), 'cmd_fast': ('cmd', cmd_fast), 'loc_shift': ('track', loc_shift)}


def run(prefix):
    try:
        res, _ = nc.check(prefix, TEST)
    except nc.Unusable as exc:
        return None, str(exc)
    return {n: ok for n, ok, _ in res}, '; '.join(t for n, ok, t in res if not ok)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = sys.argv[1]
    print(f'# TEST-M7-07 checker sensitivity on {os.path.basename(src)} ({TEST} criteria)')
    base, why = run(src)
    if base is None:
        print(f'# unusable input: {why}')
        return 2
    ok = all(base.values())
    print(f'{"PASS" if ok else "FAIL"}  original log: {"all criteria PASS" if ok else "FAILS: " + why}')
    tmp = tempfile.mkdtemp(prefix='m7_07_')
    try:
        for name, (key, fn) in DISTORT.items():
            dst = os.path.join(tmp, name)
            copy(src, dst)
            edit(dst, key, fn)
            got, why = run(dst)
            if got is None:
                print(f'FAIL  {name}: copy unusable ({why})')
                ok = False
                continue
            failed = sorted(n for n, v in got.items() if not v)
            hit = EXPECTED[name] in failed
            ok &= hit
            print(f'{"PASS" if hit else "FAIL"}  {name}: expected FAIL on {EXPECTED[name]}; failed measures {failed}')
    finally:
        shutil.rmtree(tmp)
    print(f'# result: {"PASS" if ok else "FAIL"} (1 original PASS and {len(DISTORT)} distortions FAIL required)')
    # TS-056: tools/run_suite.py judges the last '# overall:' line (no 'FAIL' word in a pass)
    print('# overall: ALL CHECKS PASSED' if ok else '# overall: AT LEAST ONE CHECK FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
