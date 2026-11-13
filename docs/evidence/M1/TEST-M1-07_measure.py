#!/usr/bin/env python3
"""TEST-M1-07: measure the rest stability of the spawned AMR in Gazebo Harmonic.

Usage (Gazebo running with the model already spawned, same GZ_PARTITION):
    python3 -I TEST-M1-07_measure.py [world] [model] [window_s]      (defaults: empty amr 30)

Data sources (installed gz tools, observed on 2026-10-21):
  /world/<world>/pose/info  gz.msgs.Pose_V, header stamp = simulation time; the entry named
                            <model> is the model frame (= base_footprint) in the world frame.
  /world/<world>/stats      sim_time, real_time, real_time_factor.
  gz model -m <model> -p    cross-check of the final pose (6 decimals, RPY in rad).

Samples: P0 = first pose read (shortly after spawn); A = first pose with sim time
>= t(P0) + 1.0 s (after the spawn transient); B = first pose with sim time >= t(A) + window_s.
Intermediate poses are read about once per second between A and B.

Orientation: quaternion (x, y, z, w) -> roll, pitch, yaw with the ROS/Gazebo fixed-axis
X-Y-Z convention (R = Rz(yaw) Ry(pitch) Rx(roll)), reported in degrees.

Thresholds (OPEN-07, DEC-019, provisional; docs/testing/test_plan.md TEST-M1-07):
|dz| < 2 mm (B - A), |roll| and |pitch| < 0.5 deg (at A and B), horizontal drift < 5 mm (B - A).
"No visible jitter" is a visual criterion observed by me; this script only reports the
numeric spread of z, roll and pitch between A and B as supporting data.
Exits 0 if every numeric threshold is met, 1 otherwise, 2 if the measurement could not be made.
"""
import math
import re
import subprocess
import sys

WORLD = sys.argv[1] if len(sys.argv) > 1 else 'empty'
MODEL = sys.argv[2] if len(sys.argv) > 2 else 'amr'
WINDOW = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
LIMIT_DZ, LIMIT_TILT_DEG, LIMIT_DRIFT = 0.002, 0.5, 0.005


def echo_once(topic):
    out = subprocess.run(['gz', 'topic', '-e', '-t', topic, '-n', '1'],
                         capture_output=True, text=True, timeout=10)
    if out.returncode != 0 or not out.stdout.strip():
        raise RuntimeError(f'no message on {topic} (exit {out.returncode}): {out.stderr.strip()}')
    return out.stdout


def stamp(text, field):
    """Seconds from a `field { sec: .. nsec: .. }` block; protobuf text omits zero fields."""
    m = re.search(field + r'\s*\{([^}]*)\}', text)
    body = m.group(1) if m else ''
    sec = re.search(r'sec:\s*(\d+)', body.replace('nsec', 'n_s'))
    nsec = re.search(r'nsec:\s*(\d+)', body)
    return (int(sec.group(1)) if sec else 0) + (int(nsec.group(1)) if nsec else 0) * 1e-9


def read_stats():
    text = echo_once(f'/world/{WORLD}/stats')
    rtf = re.search(r'real_time_factor:\s*([-\d.eE+]+)', text)
    return stamp(text, 'sim_time'), stamp(text, 'real_time'), float(rtf.group(1)) if rtf else float('nan')


def read_pose():
    text = echo_once(f'/world/{WORLD}/pose/info')
    t = stamp(text, 'stamp')
    for block in re.split(r'\npose \{', text):
        if re.search(r'^\s*name:\s*"' + re.escape(MODEL) + r'"\s*$', block, re.M):
            def vec(name, keys, default):
                m = re.search(name + r'\s*\{([^}]*)\}', block)
                body = m.group(1) if m else None
                if body is None:
                    return list(default)
                vals = []
                for k, d in zip(keys, default):
                    v = re.search(r'\b' + k + r':\s*([-\d.eE+]+)', body)
                    vals.append(float(v.group(1)) if v else (0.0 if m else d))
                return vals
            pos = vec('position', 'xyz', (0.0, 0.0, 0.0))
            quat = vec('orientation', 'xyzw', (0.0, 0.0, 0.0, 1.0))
            return t, pos, quat
    raise RuntimeError(f'model "{MODEL}" not found in /world/{WORLD}/pose/info')


def rpy_deg(q):
    x, y, z, w = q
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return [math.degrees(a) for a in (roll, pitch, yaw)]


def show(label, s):
    t, p, q = s
    r = rpy_deg(q)
    print(f'{label}: sim_time {t:.3f} s  position (m) [{p[0]:+.9f} {p[1]:+.9f} {p[2]:+.9f}]  '
          f'quaternion (xyzw) [{q[0]:+.3e} {q[1]:+.3e} {q[2]:+.3e} {q[3]:.15f}]  '
          f'RPY (deg) [{r[0]:+.6f} {r[1]:+.6f} {r[2]:+.6f}]')


def wait_until(t_target):
    while True:
        s = read_pose()
        if s[0] >= t_target:
            return s


def main():
    print(f'# TEST-M1-07 measurement: world "{WORLD}", model "{MODEL}", window {WINDOW} s of sim time')
    print('# thresholds: |dz| < 2 mm, |roll|,|pitch| < 0.5 deg, horizontal drift < 5 mm (OPEN-07, provisional)')
    p0 = read_pose(); show('P0 (first read after spawn)', p0)
    a = wait_until(p0[0] + 1.0); stats_a = read_stats(); show('A  (>= P0 + 1 s)        ', a)
    print(f'   stats near A: sim_time {stats_a[0]:.3f} s, real_time {stats_a[1]:.3f} s, real_time_factor {stats_a[2]:.4f}')
    series = [a]
    while series[-1][0] < a[0] + WINDOW:
        series.append(wait_until(min(series[-1][0] + 1.0, a[0] + WINDOW)))
    b = series[-1]; stats_b = read_stats(); show(f'B  (>= A + {WINDOW:g} s)       ', b)
    print(f'   stats near B: sim_time {stats_b[0]:.3f} s, real_time {stats_b[1]:.3f} s, real_time_factor {stats_b[2]:.4f}')
    cross = subprocess.run(['gz', 'model', '-m', MODEL, '-p'], capture_output=True, text=True, timeout=15)
    print('# cross-check, gz model -m', MODEL, '-p (exit', str(cross.returncode) + '):')
    print('\n'.join(('#   ' + line).rstrip() for line in cross.stdout.strip().splitlines()))

    dt_sim = b[0] - a[0]; dt_real = stats_b[1] - stats_a[1]
    rtf_window = (stats_b[0] - stats_a[0]) / dt_real if dt_real > 0 else float('nan')
    dz = b[1][2] - a[1][2]
    drift = math.hypot(b[1][0] - a[1][0], b[1][1] - a[1][1])
    ra, rb = rpy_deg(a[2]), rpy_deg(b[2])
    zs = [s[1][2] for s in series]; rolls = [rpy_deg(s[2])[0] for s in series]; pitches = [rpy_deg(s[2])[1] for s in series]
    print(f'# {len(series)} pose samples from A to B (about 1 per second of sim time)')
    print(f'sim time A -> B: {dt_sim:.3f} s; real time between the stats reads: {dt_real:.3f} s; '
          f'RTF over the window: {rtf_window:.4f}')
    print(f'spread A..B: z {1000 * (max(zs) - min(zs)):.6f} mm, roll {max(rolls) - min(rolls):.6f} deg, '
          f'pitch {max(pitches) - min(pitches):.6f} deg')
    checks = [
        (f'|dz| = {abs(dz) * 1000:.6f} mm < 2 mm', abs(dz) < LIMIT_DZ),
        (f'|roll| A {abs(ra[0]):.6f} deg, B {abs(rb[0]):.6f} deg < 0.5 deg', max(abs(ra[0]), abs(rb[0])) < LIMIT_TILT_DEG),
        (f'|pitch| A {abs(ra[1]):.6f} deg, B {abs(rb[1]):.6f} deg < 0.5 deg', max(abs(ra[1]), abs(rb[1])) < LIMIT_TILT_DEG),
        (f'horizontal drift = {drift * 1000:.6f} mm < 5 mm', drift < LIMIT_DRIFT),
        (f'window covers {dt_sim:.3f} s >= {WINDOW:g} s of sim time', dt_sim >= WINDOW),
    ]
    for text, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {text}")
    print(f'yaw change A -> B (information only): {rb[2] - ra[2]:+.6f} deg')
    ok = all(c[1] for c in checks)
    print('== ALL NUMERIC CRITERIA MET' if ok else '== NUMERIC CRITERIA NOT MET')
    return 0 if ok else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f'MEASUREMENT ERROR: {exc}')
        sys.exit(2)
