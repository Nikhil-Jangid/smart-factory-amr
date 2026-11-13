#!/usr/bin/env python3
"""M4 odometry harness (TEST-M4-02, -04 to -08, and the TEST-M4-03 recording; test_plan.md §9; DEC-044, DEC-045).

Usage (with the default M2 simulation running, sensors off, DEC-045):
    python3 TEST-M4_odom_measure.py <mode> [csv]   (not -I: isolated mode drops the ROS PYTHONPATH)
Modes: interface (TEST-M4-02), straight (-04), rotate (-05), square_ccw, square_cw (-06), circle (-07),
       twist (-08), record <csv> (input of TEST-M4-03).

Reuses the M2 harness (TEST-M2_motion_measure.py): the Gazebo ground-truth reader, the simulation-time estimate
(TS-013), the command sender, the rest detection and the teardown-safe Spinner (TS-030, REQ-TA-01).

Error definition (plan §3.4, DEC-044): odometry minus ground truth, compared at REST POINTS only (zero command
held, ground-truth speed < 5 mm/s), so the result does not depend on the timing of the two streams. Each pose
change is expressed in its own start pose (SE(2) relative motion), which removes the fixed offset between the
`odom` frame and the world:
    d = R(-psi_start) (p_end - p_start)       (body-frame displacement, m)
    dpsi = sum of wrapped yaw increments       (unwrapped heading change, rad; correct beyond ±180°)
    position error = |d_odom - d_gt|, yaw error = dpsi_odom - dpsi_gt.
"translation ≤ 20 mm" in TEST-M4-05 is read as this odometry-vs-ground-truth position error (stated before any
formal run); the ground-truth drift of the robot during the rotation is printed as INFO.
Exit 0 = all PASS, 1 = a FAIL, 2 = invalid run (RTF < 0.5, missing data, or a gap in the recording).
"""
import csv
import importlib.util
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('test_m2_measure', os.path.join(HERE, '..', 'M2', 'TEST-M2_motion_measure.py'))
M2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M2)
from nav_msgs.msg import Odometry  # noqa: E402

CONTROLLERS = os.path.join(HERE, '..', '..', '..', 'amr_ws', 'src', 'amr_bringup', 'config', 'controllers.yaml')
V, W = 0.2, 0.5        # m/s, rad/s: the M2 profile speeds
HOLD = 3.0             # s of zero command after each motion before the rest point
COV_DIAG = (0, 7, 14, 21, 28, 35)


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


class Rec(M2.Recorder):
    """M2 recorder plus the odometry twist, covariance and receipt time (TEST-M4-02, -08)."""

    def __init__(self):
        super().__init__('m4_measure')
        self.odom_full = []

    def on_odom(self, m):
        super().on_odom(m)
        t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        with self.lock:
            self.odom_full.append((t, m.twist.twist.linear.x, m.twist.twist.angular.z,
                                   tuple(m.pose.covariance[i] for i in COV_DIAG),
                                   tuple(m.twist.covariance[i] for i in COV_DIAG), self.sim()))


class Run(M2.Run):
    def series(self, s, t0, t1):
        with self.rec.lock:
            return [x for x in s if t0 <= x[0] <= t1]

    def rel(self, s, t0, t1, ix, iy, ipsi):
        """Body-frame displacement and unwrapped heading change of series s between t0 and t1."""
        win = self.series(s, t0, t1)
        a, b = win[0], win[-1]
        dx, dy = b[ix] - a[ix], b[iy] - a[iy]
        c, sn = math.cos(a[ipsi]), math.sin(a[ipsi])
        dpsi = sum(wrap(q[ipsi] - p[ipsi]) for p, q in zip(win, win[1:]))
        return (c * dx + sn * dy, -sn * dx + c * dy, dpsi, a[0], b[0])

    def rest_ok(self, t, label):
        tr = self.at_rest_time(t - HOLD + 0.5, t)
        ok = tr is not None
        self.check(ok, f'{label}: robot at rest at the comparison point (ground-truth speed < {M2.REST * 1000:.0f} mm/s'
                       f' for {M2.REST_HOLD} s{"" if ok else "; NOT at rest"})')
        return ok

    def move(self, steps):
        """Rest point, motion steps [(duration, v, w)], zero for HOLD; returns (t_start, t_end) rest points."""
        t_a = self.rec.sim()
        self.wait_sim(t_a + 0.5, 0.0, 0.0)
        t_a = self.rec.sim()
        self.profile([*steps, (HOLD, 0.0, 0.0)])
        return t_a, self.rec.sim()

    def compare(self, label, t_a, t_b, pos_tol=None, yaw_tol_deg=None, dist_tol=None):
        o = self.rel(self.rec.odom, t_a, t_b, 1, 2, 3)
        g = self.rel(self.rec.gt, t_a, t_b, 1, 2, 6)
        perr = math.hypot(o[0] - g[0], o[1] - g[1])
        yerr = math.degrees(o[2] - g[2])
        self.info(f'{label}: ground truth d = ({g[0]:+.4f}, {g[1]:+.4f}) m, dpsi {math.degrees(g[2]):+.3f} deg; '
                  f'odometry d = ({o[0]:+.4f}, {o[1]:+.4f}) m, dpsi {math.degrees(o[2]):+.3f} deg')
        if dist_tol is not None:
            dg, do = math.hypot(g[0], g[1]), math.hypot(o[0], o[1])
            rel = (do - dg) / dg
            self.check(abs(rel) <= dist_tol, f'{label}: distance error {(do - dg) * 1000:+.2f} mm = {rel * 100:+.4f} % '
                                             f'of {dg:.4f} m, |.| <= {dist_tol * 100:g} %')
        if pos_tol is not None:
            self.check(perr <= pos_tol, f'{label}: position error {perr * 1000:.2f} mm <= {pos_tol * 1000:g} mm')
        if yaw_tol_deg is not None:
            self.check(abs(yerr) <= yaw_tol_deg, f'{label}: yaw error {yerr:+.4f} deg, |.| <= {yaw_tol_deg:g} deg')
        return perr, yerr


def expected_cov():
    """pose/twist covariance diagonals configured in controllers.yaml (installed default: zeros)."""
    txt = open(CONTROLLERS).read()
    out = []
    for key in ('pose_covariance_diagonal', 'twist_covariance_diagonal'):
        m = re.search(rf'^\s*{key}:\s*\[([^\]]*)\]', txt, re.M)
        out.append(tuple(float(x) for x in m.group(1).split(',')) if m else (0.0,) * 6)
    return out


def m_interface(r):
    t0 = r.rec.sim()
    wall0 = time.time()
    r.profile([(5.0, V, 0.0), (3.0, 0.0, W), (2.0, 0.0, 0.0)])
    t1 = r.rec.sim()
    r.rtf(t0, wall0)
    od = r.series(r.rec.odom, t0, t1)
    full = r.series(r.rec.odom_full, t0, t1)
    tf = r.series(r.rec.tf, t0, t1)
    frames = {(o[4], o[5]) for o in od}
    r.check(frames == {('odom', 'base_footprint')}, f'odometry frame ids {sorted(frames)} == [(odom, base_footprint)]')
    rate = (len(od) - 1) / (od[-1][0] - od[0][0])
    r.check(abs(rate - 50.0) <= 1.0, f'odometry rate {rate:.3f} Hz over {len(od)} messages, 50 Hz ± 2 %')
    lag = [f[5] - f[0] for f in full]
    r.check(all(-0.05 <= x <= 0.2 for x in lag),
            f'stamps on simulation time: receipt time - stamp in [{min(lag):+.4f}, {max(lag):+.4f}] s, within [-0.05, +0.2] s')
    exp_p, exp_t = expected_cov()
    pc = {f[3] for f in full}
    tc = {f[4] for f in full}
    r.check(pc == {exp_p} and tc == {exp_t},
            f'covariance diagonals equal controllers.yaml: pose {sorted(pc)} vs {exp_p}; twist {sorted(tc)} vs {exp_t}')
    r.check(all(x > 0 for x in exp_p + exp_t), 'covariance diagonals configured and not zero (REQ-M4-07, DEC-042)')
    stamps = [x[0] for x in tf]
    r.check(len(stamps) == len(set(stamps)), f'odom -> base_footprint TF: {len(stamps)} transforms, no duplicate stamp '
                                             '(a second publisher would duplicate or interleave)')
    r.check(abs(len(tf) - len(od)) <= 2, f'TF count {len(tf)} equals odometry count {len(od)} (± 2)')
    by_t = {round(o[0], 6): o for o in od}
    worst_p = worst_y = 0.0
    matched = 0
    for x in tf:
        o = by_t.get(round(x[0], 6))
        if o:
            matched += 1
            worst_p = max(worst_p, math.hypot(x[1] - o[1], x[2] - o[2]))
            worst_y = max(worst_y, abs(math.degrees(wrap(x[3] - o[3]))))
    r.check(matched >= 0.95 * len(tf) and worst_p <= 0.001 and worst_y <= 0.1,
            f'TF equals odometry at the same stamp: {matched}/{len(tf)} matched, max {worst_p * 1000:.4f} mm, '
            f'{worst_y:.5f} deg (<= 1 mm, 0.1 deg)')


def m_straight(r):
    wall0 = time.time()
    for name, v in (('forward', V), ('reverse', -V)):
        t_a, t_b = r.move([(10.0, v, 0.0)])
        if r.rest_ok(t_b, name):
            o = r.rel(r.rec.odom, t_a, t_b, 1, 2, 3)
            g = r.rel(r.rec.gt, t_a, t_b, 1, 2, 6)
            r.compare(name, t_a, t_b, dist_tol=0.005)
            herr = math.degrees(o[2] - g[2])
            r.check(abs(herr) <= 0.5, f'{name}: heading error {herr:+.4f} deg, |.| <= 0.5 deg')
    r.rtf(r.rec.sim() - 26.0, wall0)


def m_rotate(r):
    wall0 = time.time()
    for name, w in (('rotate +360', W), ('rotate -360', -W)):
        t_a, t_b = r.move([(4 * math.pi, 0.0, w)])
        if r.rest_ok(t_b, name):
            r.compare(name, t_a, t_b, pos_tol=0.020, yaw_tol_deg=1.0)
            g = r.series(r.rec.gt, t_a, t_b)
            drift = max(math.hypot(x[1] - g[0][1], x[2] - g[0][2]) for x in g)
            r.info(f'{name}: ground-truth max translation during the turn {drift * 1000:.2f} mm')
    r.rtf(r.rec.sim() - 2 * (4 * math.pi + HOLD + 0.5), wall0)


def square(r, sign):
    name = 'square CCW' if sign > 0 else 'square CW'
    wall0 = time.time()
    steps = []
    for _ in range(4):
        steps += [(5.0, V, 0.0), (1.0, 0.0, 0.0), (math.pi / 2 / W, 0.0, sign * W), (1.0, 0.0, 0.0)]
    t_a, t_b = r.move(steps)
    if r.rest_ok(t_b, name):
        r.compare(name, t_a, t_b, pos_tol=0.020, yaw_tol_deg=1.0)
    r.rtf(t_a, wall0)


def m_circle(r):
    wall0 = time.time()
    t_a, t_b = r.move([(10 * math.pi, V, 0.2)])
    if r.rest_ok(t_b, 'circle'):
        r.compare('circle', t_a, t_b, pos_tol=0.020, yaw_tol_deg=1.0)
    r.rtf(t_a, wall0)


def m_twist(r):
    """Cruise means of the published twist vs ground truth (the rolling mean lags ~0.05 s; cruise only)."""
    wall0 = time.time()
    for name, v, w, dur in (('straight', V, 0.0, 6.0), ('rotate', 0.0, W, 6.0)):
        t_a = r.rec.sim()
        legs = r.profile([(dur, v, w), (2.0, 0.0, 0.0)])
        c0, c1 = legs[0][0] + 1.5, legs[0][1] - 0.2
        tw = r.series(r.rec.odom_full, c0, c1)
        g = r.samples(c0, c1)
        sp = [s for s in r.body_speed(g, g[0][6]) if c0 <= s[0] <= c1]
        if v:
            ref = sum(s[1] for s in sp) / len(sp)
            est = sum(x[1] for x in tw) / len(tw)
        else:
            ref = sum(s[2] for s in sp) / len(sp)
            est = sum(x[2] for x in tw) / len(tw)
        rel = (est - ref) / ref
        r.check(abs(rel) <= 0.02 and math.copysign(1, est) == math.copysign(1, ref),
                f'{name}: odometry twist mean {est:+.5f}, ground truth {ref:+.5f} ({"m/s" if v else "rad/s"}), '
                f'error {rel * 100:+.3f} %, |.| <= 2 %, sign equal ({len(tw)} / {len(sp)} samples)')
    r.rtf(t_a - 8.0, wall0)


def m_record(r, path):
    """Mixed profile for the offline recomputation (TEST-M4-03): straight, arc, rotation, reverse, stop."""
    t_a = r.rec.sim()
    wall0 = time.time()
    r.profile([(3.0, V, 0.0), (4.0, V, 0.3), (3.0, 0.0, -W), (2.0, -0.15, 0.0), (2.0, 0.0, 0.0)])
    t_b = r.rec.sim()
    r.rtf(t_a, wall0)
    js = r.series(r.rec.js, t_a - 0.5, t_b)
    od = r.series(r.rec.odom, t_a, t_b)
    gaps = [b[0] - a[0] for a, b in zip(js, js[1:])]
    ok = bool(js) and max(gaps) <= 0.015 and min(gaps) > 0.005
    if not ok:
        print(f'INVALID  joint_states not continuous at 100 Hz (gaps {min(gaps or [0]):.4f} to {max(gaps or [0]):.4f} s)')
        r.invalid = True
        return
    r.info(f'recorded {len(js)} joint_states (gaps {min(gaps):.4f}-{max(gaps):.4f} s) and {len(od)} odometry messages')
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['kind', 't', 'a', 'b', 'c'])
        for j in js:
            w.writerow(['js', f'{j[0]:.9f}', repr(j[1][0]), repr(j[2][0]), ''])
        for o in od:
            w.writerow(['odom', f'{o[0]:.9f}', repr(o[1]), repr(o[2]), repr(o[3])])
    r.info(f'wrote {path}')


MODES = {'interface': m_interface, 'straight': m_straight, 'rotate': m_rotate,
         'square_ccw': lambda r: square(r, +1), 'square_cw': lambda r: square(r, -1),
         'circle': m_circle, 'twist': m_twist}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in MODES and not (mode == 'record' and len(sys.argv) > 2):
        print(__doc__)
        return 2
    M2.rclpy.init()
    rec = Rec()
    ex = M2.SingleThreadedExecutor()  # as M2 (TS-013)
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()  # TS-030 fix (REQ-TA-01)
    r = Run(rec)
    print(f'# TEST-M4 harness mode={mode}, wall {time.strftime("%F %T %Z")}')
    try:
        if r.ready():
            m_record(r, sys.argv[2]) if mode == 'record' else MODES[mode](r)
    finally:
        spin.stop(rec)
    with rec.lock:
        print(f'# samples: ground truth {len(rec.gt)}, odometry {len(rec.odom)}, joint_states {len(rec.js)}, tf {len(rec.tf)}')
    if r.invalid:
        print('# result: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"ALL CRITERIA PASSED" if r.fails == 0 else f"{r.fails} CRITERION/CRITERIA FAILED"}')
    return 1 if r.fails else 0


if __name__ == '__main__':
    code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)  # as M2: gz-transport aborts during interpreter teardown
