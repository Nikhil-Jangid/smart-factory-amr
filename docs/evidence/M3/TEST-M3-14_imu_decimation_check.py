#!/usr/bin/env python3
"""TEST-M3-14 harness: DEC-038 IMU decimation in the real launch (docs/testing/test_plan.md §7.3).

Usage, with `sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0` running; plain python3:
    python3 TEST-M3-14_imu_decimation_check.py
Reuses the Task D harness TEST-M3-D_imu_encoder_measure.py (and through it the M2 harness) **unchanged**, imported:
its Recorder (ROS /imu, /joint_states, ground truth of the sensor test world), Run (profiles, RTF validity) and
helpers. This file adds a gz-transport subscription to the raw IMU, gz /imu_raw (1 kHz, internal to Gazebo), and the
full ROS /imu message (orientation, covariances).
Profile (DEC-025 limits): rotate +0.5 rad/s for 2 pi s (half a turn), stop 3 s, 0.5 m/s for 3 s, stop 3 s.

Checks (ROS /imu outputs with stamp t and the raw samples t - 9 ... t ms):
  (a) every output whose 10 raw samples were recorded equals their per-axis mean on all six rate channels
      (|diff| <= 1e-9) and carries the newest raw stamp t; orientation = the raw sample at t (<= 1e-12);
      orientation covariance = the raw one; rate covariances = raw / 10 (relative 1e-6); at least 95 % of the
      outputs in the recording are checked.
  (b) /imu stamps: every stamp a multiple of 10 ms; consecutive stamps exactly 10 ms apart over the whole recording
      (100 Hz in simulation time, no missing or repeated output); raw stamps exactly 1 ms apart (no raw gap).
      The plugin's own counters (startup, dropped, duplicates, resets) are checked by the procedure from its
      shutdown line in the launch log.
  (c) braking: mean accel x over the deceleration ramp (ground-truth speed from 90 % down to 10 % of the plateau)
      vs the ground-truth deceleration (v_10 - v_90) / (t_10 - t_90): correct sign and within +-20 % (accepted
      with DEC-038).
  (d) cruise: mean accel x over [leg start + 1.5 s, leg end - 0.2 s] within +-0.02 m/s^2 of 0 (DEC-036 S1 limit).
  (e) gyro: the D10 criterion on the rotate leg (mean gyro z within +-3 % of the ground-truth yaw rate, sign).
      Published rate covariance diagonals = DEC-032 sigma_output^2 (1e-6 (rad/s)^2, 1e-4 (m/s^2)^2; float
      precision, relative 1e-6).
  INFO: the acceleration ramp (D11 quantity), the controller-step delay histogram (raw samples with |accel x|
      > 1 m/s^2 in the linear legs, output stamp minus step stamp; expected 8-9 ms, TS-027_C4_delay.log), the
      transient (largest output during the ramps), and the orientation yaw change over the rotate leg vs ground truth
      (the orientation is simulator-derived, not ground truth, DEC-032).
Exit 0 = all PASS, 1 = a FAIL, 2 = invalid run (RTF < 0.5 or missing data; repeat).
"""
import collections
import importlib.util
import math
import os
import statistics
import sys
import time

from gz.msgs10.imu_pb2 import IMU

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('test_m3_d', os.path.join(HERE, 'TEST-M3-D_imu_encoder_measure.py'))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
M2 = D.M2

BLOCK = 10
SIGMA_A, SIGMA_W = D.SIGMA_A, D.SIGMA_W   # DEC-032, at the output
MS = 1_000_000


def ns_of(sec, nsec):
    return sec * 1_000_000_000 + nsec


class Recorder(D.Recorder):
    def __init__(self):
        super().__init__()
        self.raw = {}          # ms -> (ns, ax, ay, az, gx, gy, gz, (qx, qy, qz, qw), ocov, gcov, acov)
        self.raw_dup = 0
        self.full = []         # (ns, ax, ay, az, gx, gy, gz, (qx, qy, qz, qw), ocov, gcov, acov)
        if not self.gz.subscribe(IMU, '/imu_raw', self.on_raw):
            raise RuntimeError('cannot subscribe gz /imu_raw')

    def on_raw(self, m):
        ns = ns_of(m.header.stamp.sec, m.header.stamp.nsec)
        a, w, q = m.linear_acceleration, m.angular_velocity, m.orientation
        rec = (ns, a.x, a.y, a.z, w.x, w.y, w.z, (q.x, q.y, q.z, q.w), tuple(m.orientation_covariance.data),
               tuple(m.angular_velocity_covariance.data), tuple(m.linear_acceleration_covariance.data))
        with self.lock:
            k = ns // MS
            if k in self.raw:
                self.raw_dup += 1
            self.raw[k] = rec

    def on_imu(self, m):
        super().on_imu(m)
        a, w, q = m.linear_acceleration, m.angular_velocity, m.orientation
        with self.lock:
            self.full.append((ns_of(m.header.stamp.sec, m.header.stamp.nanosec), a.x, a.y, a.z, w.x, w.y, w.z,
                              (q.x, q.y, q.z, q.w), tuple(m.orientation_covariance),
                              tuple(m.angular_velocity_covariance), tuple(m.linear_acceleration_covariance)))


def rel_close(x, y, tol):
    return abs(x - y) <= tol * max(abs(x), abs(y), 1e-30)


def check_exactness(r, raw, outs):
    checked, worst, worst_q, bad_stamp, bad_cov, incomplete = 0, 0.0, 0.0, 0, 0, 0
    for o in outs:
        if o[0] % MS:
            bad_stamp += 1
            continue
        t = o[0] // MS
        blk = [raw.get(k) for k in range(t - BLOCK + 1, t + 1)]
        if any(b is None for b in blk):
            incomplete += 1
            continue
        checked += 1
        newest = blk[-1]
        if newest[0] != o[0]:
            bad_stamp += 1
        for c in range(1, 7):
            worst = max(worst, abs(o[c] - sum(b[c] for b in blk) / BLOCK))
        worst_q = max(worst_q, max(abs(x - y) for x, y in zip(o[7], newest[7])))
        ocov_ok = all(rel_close(x, y, 1e-6) or x == y for x, y in zip(o[8], newest[8]))
        gcov_ok = all(rel_close(x, y / BLOCK, 1e-6) or x == y == 0 for x, y in zip(o[9], newest[9]))
        acov_ok = all(rel_close(x, y / BLOCK, 1e-6) or x == y == 0 for x, y in zip(o[10], newest[10]))
        if not (ocov_ok and gcov_ok and acov_ok and len(o[9]) == len(newest[9]) == 9):
            bad_cov += 1
    share = checked / len(outs) if outs else 0.0
    r.check(share >= 0.95 and worst <= 1e-9 and worst_q <= 1e-12 and bad_stamp == 0 and bad_cov == 0,
            f'(a) {checked} of {len(outs)} outputs checked against their 10 raw samples ({share * 100:.1f} %; '
            f'{incomplete} at the recording edges without all raw samples): max |output - raw mean| {worst:.2e} '
            f'(<= 1e-9, six channels); stamp = newest raw stamp: {len(outs) - incomplete - bad_stamp} of '
            f'{len(outs) - incomplete}; orientation = newest raw sample, max |dq| {worst_q:.1e} (<= 1e-12); '
            f'covariances (orientation copied, rates / 10) wrong in {bad_cov}')


def check_grid(r, raw, outs):
    st = [o[0] for o in outs]
    off = sum(1 for s in st if s % (BLOCK * MS))
    d = collections.Counter((b - a) / MS for a, b in zip(st, st[1:]))
    ks = sorted(raw)
    dr = collections.Counter(b - a for a, b in zip(ks, ks[1:]))
    r.check(off == 0 and set(d) == {float(BLOCK)} and set(dr) == {1} and r.rec.raw_dup == 0,
            f'(b) /imu: {len(st)} stamps, {off} off the 10 ms grid; spacing histogram (ms) {dict(d)} (all 10 ms '
            f'= 100 Hz in simulation time, no missing or repeated output); raw /imu_raw: {len(ks)} samples, spacing '
            f'histogram (ms) {dict(dr)}, repeated stamps {r.rec.raw_dup}')
    return st


def check_braking(r, leg, stop):
    t0, t1, vx, _ = leg
    psi0 = r.nearest(r.rec.gt, t0)[6]
    sp = r.body_speed(r.samples(t0 - 0.5, stop[1]), psi0)
    plateau = statistics.fmean(s[1] for s in sp if t0 + 1.5 <= s[0] <= t1 - 0.2)
    s90 = next(s for s in sp if s[0] >= t1 - 0.1 and s[1] <= 0.9 * plateau)
    s10 = next(s for s in sp if s[0] >= s90[0] and s[1] <= 0.1 * plateau)
    gt_dec = (s10[1] - s90[1]) / (s10[0] - s90[0])
    imu = r.rec.imu_between(s90[0], s10[0])
    ax = statistics.fmean(x[1] for x in imu)
    err = (ax - gt_dec) / gt_dec
    r.check(math.copysign(1, ax) == math.copysign(1, gt_dec) == -math.copysign(1, vx) and abs(err) <= 0.20,
            f'(c) braking from {vx} m/s: mean accel x {ax:+.4f} m/s^2 vs ground-truth deceleration {gt_dec:+.4f} '
            f'm/s^2 ({err * 100:+.2f} %; sign; |.| <= 20 %) over the 90-10 % ramp {s90[0] - t1:+.3f} .. '
            f'{s10[0] - t1:+.3f} s after the stop command ({len(imu)} IMU samples)')
    cruise = r.rec.imu_between(t0 + 1.5, t1 - 0.2)
    mc = statistics.fmean(x[1] for x in cruise)
    r.check(abs(mc) <= 0.02, f'(d) cruise at {plateau:.4f} m/s: mean accel x {mc:+.5f} m/s^2 (|.| <= 0.02, DEC-036 S1) '
            f'over {len(cruise)} IMU samples')
    return plateau


def info_ramp_and_delay(r, raw, st, leg, stop):
    t0, t1 = leg[0], leg[1]
    psi0 = r.nearest(r.rec.gt, t0)[6]
    sp = r.body_speed(r.samples(t0 - 0.5, t1), psi0)
    plateau = statistics.fmean(s[1] for s in sp if t0 + 1.5 <= s[0] <= t1 - 0.2)
    s10 = next(s for s in sp if s[0] >= t0 - 0.1 and s[1] >= 0.1 * plateau)
    s90 = next(s for s in sp if s[0] >= s10[0] and s[1] >= 0.9 * plateau)
    gt_acc = (s90[1] - s10[1]) / (s90[0] - s10[0])
    imu = r.rec.imu_between(s10[0], s90[0])
    ax = statistics.fmean(x[1] for x in imu)
    r.info(f'acceleration ramp (D11 quantity): mean accel x {ax:+.4f} m/s^2 vs ground truth {gt_acc:+.4f} m/s^2 '
           f'({(ax - gt_acc) / gt_acc * 100:+.2f} %), {len(imu)} IMU samples')
    lo, hi = round((t0 - 0.1) * 1000), round((stop[1]) * 1000)
    steps = [k for k in sorted(raw) if lo <= k <= hi and abs(raw[k][1]) > 1.0]
    outs_ms = sorted(s // MS for s in st)
    phase = collections.Counter(k % BLOCK for k in steps)
    delay = collections.Counter(min(o for o in outs_ms if o >= k) - k for k in steps if outs_ms and outs_ms[-1] >= k)
    r.info(f'controller-step delay: {len(steps)} raw steps (|accel x| > 1 m/s^2), stamp mod 10 ms histogram '
           f'{dict(sorted(phase.items()))}; output stamp minus step stamp (ms) histogram {dict(sorted(delay.items()))}'
           f' (expected 8-9 ms)')
    up = r.rec.imu_between(t0, t0 + 1.2)
    down = r.rec.imu_between(t1, t1 + 0.7)
    r.info(f'transient: largest output accel x during speed-up {max(x[1] for x in up):+.3f} m/s^2, during braking '
           f'{min(x[1] for x in down):+.3f} m/s^2 (one output per 10 ms block; DEC-025 limits 0.5 / -1.0 m/s^2)')


def info_orientation(r, leg):
    t0, t1 = leg[0] + 1.0, leg[1] - 0.2
    with r.rec.lock:
        win = [o for o in r.rec.full if t0 <= o[0] * 1e-9 <= t1]
    if len(win) < 2:
        return

    def yaw(q):
        x, y, z, w = q
        return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    imu_yaw = sum(M2.wrap(yaw(b[7]) - yaw(a[7])) for a, b in zip(win, win[1:]))
    gt = r.gt_between(win[0][0] * 1e-9, win[-1][0] * 1e-9)
    gt_yaw = D.unwrapped_yaw(gt)
    r.info(f'orientation: yaw change of the /imu orientation over the rotate window {math.degrees(imu_yaw):+.3f} deg vs '
           f'ground truth {math.degrees(gt_yaw):+.3f} deg (simulator-derived orientation, not ground truth; DEC-032)')


def check_cov_values(r, outs):
    g = {o[9][0] for o in outs} | {o[9][4] for o in outs} | {o[9][8] for o in outs}
    a = {o[10][0] for o in outs} | {o[10][4] for o in outs} | {o[10][8] for o in outs}
    ok = all(rel_close(x, SIGMA_W ** 2, 1e-6) for x in g) and all(rel_close(x, SIGMA_A ** 2, 1e-6) for x in a)
    r.check(ok, f'(e) published covariance diagonals: angular velocity {sorted(g)} == {SIGMA_W ** 2:g} (rad/s)^2, '
                f'linear acceleration {sorted(a)} == {SIGMA_A ** 2:g} (m/s^2)^2 (DEC-032 sigma at the output)')


def run_checks(r):
    sim0, wall0 = r.rec.sim(), time.time()
    T = math.pi / 0.5
    legs = r.profile([(T, 0.0, 0.5), (3.0, 0.0, 0.0), (3.0, 0.5, 0.0), (3.0, 0.0, 0.0)])
    r.rtf(sim0, wall0)
    with r.rec.lock:
        raw = dict(r.rec.raw)
        outs = sorted(r.rec.full)
    check_exactness(r, raw, outs)
    st = check_grid(r, raw, outs)
    check_braking(r, legs[2], legs[3])
    D.eval_gyro(r, legs[0])
    check_cov_values(r, outs)
    info_ramp_and_delay(r, raw, st, legs[2], legs[3])
    info_orientation(r, legs[0])
    D.excursion(r, legs[0][0], legs[-1][1])


def main():
    M2.rclpy.init()
    rec = Recorder()
    ex = M2.SingleThreadedExecutor()
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()  # TS-030 fix (REQ-TA-01)
    r = M2.Run(rec)
    print(f'# TEST-M3-14 harness, wall {time.strftime("%F %T %Z")}, ground truth {D.WORLD_TOPIC}, raw gz /imu_raw')
    try:
        if r.ready():
            run_checks(r)
    except (StopIteration, IndexError, ZeroDivisionError, statistics.StatisticsError, ValueError) as exc:
        print(f'INVALID  missing data for an evaluation ({type(exc).__name__}: {exc})')
        r.invalid = True
    finally:
        spin.stop(rec)
    with rec.lock:
        print(f'# samples: ground truth {len(rec.gt)}, ROS imu {len(rec.full)}, raw imu {len(rec.raw)}, '
              f'joint_states {len(rec.js)}')
    if r.invalid:
        print('# result: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"ALL CRITERIA PASSED" if r.fails == 0 else f"{r.fails} CRITERION/CRITERIA FAILED"}')
    return 1 if r.fails else 0


if __name__ == '__main__':
    code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)
