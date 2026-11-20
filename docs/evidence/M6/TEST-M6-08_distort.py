#!/usr/bin/env python3
"""TEST-M6-08: pose-checker sensitivity (REQ-M6-10; test_plan §11; M6 Task B). Standard library only (CI).

Usage: python3 -I TEST-M6-08_distort.py <recorded prefix>
<recorded prefix>_rest.csv and _track.csv are a recorded localization run (TEST-M6_run.py). The tool writes four
distorted copies to a temporary folder and runs TEST-M6_pose_check.py's check() on the original and on each copy
(default criteria, no --recovery or --drift). Exit 0 if the original PASSES and every copy FAILS on its expected
measure (other measures may fail too; they are reported); 1 otherwise; 2 on unusable input.

Distortions of the estimate (est_x, est_y, est_yaw; ground truth and odometry untouched):
  offset   +0.08 m in x, in every rest point and track sample        -> expected FAIL: rest_position (bound 0.05 m)
  rotation +1.5 deg of heading, in every rest point and track sample -> expected FAIL: rest_heading (bound 1.0 deg)
  jump     +0.30 m in x in one track sample: the moving sample in the middle of the moving samples
                                                                     -> expected FAIL: moving_max_position (0.25 m)
  delay    the track estimate replaced by the estimate 0.5 s earlier (linear interpolation, heading unwrapped;
           the first 0.5 s keep the first sample); rest points unchanged (at rest a delay changes nothing)
                                                                     -> expected FAIL: moving_p95_position (0.10 m)
The offset (0.08 m) is below the moving P95 bound and the rotation (1.5 deg) below the moving P95 heading bound, so
each tests the rest criterion alone; the jump changes one sample, which the P95 measures must not notice.
"""
import csv
import importlib.util
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('pose_check', os.path.join(HERE, 'TEST-M6_pose_check.py'))
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)

EXPECTED = {'offset': 'rest_position', 'rotation': 'rest_heading', 'jump': 'moving_max_position',
            'delay': 'moving_p95_position'}


def read(path):
    with open(path, newline='') as f:
        r = csv.DictReader(f)
        return r.fieldnames, [dict(row) for row in r]


def write(path, fields, rows):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def shift(rows, dx=0.0, dyaw=0.0):
    for r in rows:
        r['est_x'] = f'{float(r["est_x"]) + dx:.6f}'
        r['est_yaw'] = f'{pc.wrap(float(r["est_yaw"]) + dyaw):.6f}'


def delayed(track, d):
    t = [float(r['sim_t']) for r in track]
    x = [float(r['est_x']) for r in track]
    y = [float(r['est_y']) for r in track]
    yaw, acc = [], None
    for r in track:   # unwrap the heading before interpolating
        a = float(r['est_yaw'])
        acc = a if acc is None else acc + pc.wrap(a - acc)
        yaw.append(acc)
    out, j = [], 0
    for r, ti in zip(track, t):
        tq = ti - d
        while j + 1 < len(t) and t[j + 1] <= tq:
            j += 1
        if tq <= t[0]:
            vals = (x[0], y[0], yaw[0])
        elif j + 1 >= len(t):
            vals = (x[-1], y[-1], yaw[-1])
        else:
            f = (tq - t[j]) / (t[j + 1] - t[j])
            vals = tuple(v[j] + f * (v[j + 1] - v[j]) for v in (x, y, yaw))
        r = dict(r)
        r['est_x'], r['est_y'], r['est_yaw'] = f'{vals[0]:.6f}', f'{vals[1]:.6f}', f'{pc.wrap(vals[2]):.6f}'
        out.append(r)
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = sys.argv[1]
    try:
        fr, rest = read(src + '_rest.csv')
        ft, track = read(src + '_track.csv')
    except OSError as exc:
        print(f'# unusable input: {exc}')
        return 2
    tmp = tempfile.mkdtemp()
    ok = True
    try:
        flags = pc.moving_flags([{k: float(v) for k, v in r.items()} for r in track])
        moving = [i for i, f in enumerate(flags) if f]
        mid = moving[len(moving) // 2] if moving else None
        cases = {'original': (rest, track)}
        r, t = [dict(x) for x in rest], [dict(x) for x in track]
        shift(r, dx=0.08), shift(t, dx=0.08)
        cases['offset'] = (r, t)
        r, t = [dict(x) for x in rest], [dict(x) for x in track]
        shift(r, dyaw=math.radians(1.5)), shift(t, dyaw=math.radians(1.5))
        cases['rotation'] = (r, t)
        t = [dict(x) for x in track]
        if mid is not None:
            shift([t[mid]], dx=0.30)
        cases['jump'] = ([dict(x) for x in rest], t)
        cases['delay'] = ([dict(x) for x in rest], delayed(track, 0.5))
        print(f'# TEST-M6-08 checker sensitivity: recorded run {os.path.basename(src)} ({len(rest)} rest points, '
              f'{len(track)} track samples, {len(moving)} moving); jump at track sample {mid} '
              f'(simulation time {track[mid]["sim_t"] if mid is not None else "-"} s)')
        for name, (r, t) in cases.items():
            p = os.path.join(tmp, name)
            write(p + '_rest.csv', fr, r)
            write(p + '_track.csv', ft, t)
            res, _info, _summ = pc.check(p)
            failed = [m for m, good, _ in res if not good]
            if name == 'original':
                good = not failed
                want = 'PASS'
            else:
                good = EXPECTED[name] in failed
                want = f'FAIL on {EXPECTED[name]}'
            ok &= good
            print(f'{"PASS" if good else "FAIL"}  {name:8s} expected {want:32s} got '
                  f'{"PASS" if not failed else "FAIL on " + ", ".join(failed)}')
            for m, good_m, text in res:
                print(f'        {"pass" if good_m else "FAIL"}  [{m}] {text}')
    finally:
        shutil.rmtree(tmp)
    print(f'# result: {"PASS" if ok else "FAIL"}')
    # Runner overall line (tools/run_suite.py reads '# overall:'; added in M6 Task E for the m6 and ci suites)
    print(f'# overall: {"ALL CHECKS PASSED" if ok else "AT LEAST ONE CHECK FAILED"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
