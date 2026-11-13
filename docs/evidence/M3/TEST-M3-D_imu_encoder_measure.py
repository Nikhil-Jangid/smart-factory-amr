#!/usr/bin/env python3
"""Task D harness: TEST-M3-07 (IMU at rest), TEST-M3-08 (IMU in motion), TEST-M3-09 (encoders).

Usage, with `sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0` running; plain python3
(rclpy and gz-transport; TS-011):
    python3 TEST-M3-D_imu_encoder_measure.py <imu_rest | imu_motion | encoders>
Reuses the M2 harness docs/evidence/M2/TEST-M2_motion_measure.py **unchanged** (imported, not copied or edited,
so the M2 evidence stays as recorded): its Recorder (simulation time from the Gazebo pose stream, TS-013;
/cmd_vel TwistStamped at 50 Hz through cmd_vel_guard), Run (profiles, ready/settle 2.0 s, RTF validity) and data
helpers. This file only (a) subscribes to the ground truth of the sensor test world, /world/sensor_test/pose/info
(the M2 Recorder's /world/empty subscription then receives nothing), (b) records /imu, and (c) adds the M3 checks.
Spawn: y = -20 m (test_plan.md §7.1; clearance checked by TEST-M3-D_clearance_check.py before the runs). Each
mode prints the robot's ground-truth excursion from the spawn point.

Modes and checks (sensors.md §7.2-7.4; CALC-M3-02 expected values; g = 9.8 m/s^2):
  imu_rest   (TEST-M3-07, 1 run): zero command; window 10.0 s of simulation time after the 2.0 s settle; IMU
             samples selected by header stamp. D9: mean specific force z > 0. S1-S4 on six channels:
             accel x, y, z (expected 0, 0, +9.8; sigma 0.01 m/s^2; |bias| <= 0.02 m/s^2) and gyro x, y, z
             (expected 0; sigma 0.001 rad/s; |bias| <= 0.001 rad/s) (TEST-M3_noise_stats.py).
  imu_motion (TEST-M3-08, 3 runs): profiles from the M2 harness.
             D10: the TEST-M2-06 rotate profile: +0.5 rad/s for 2 pi s (half a turn), 3 s stop, -0.5 rad/s for
                  2 pi s, 3 s stop.
                  Steady window per leg: [leg start + 1.0 s, leg end - 0.2 s]. Mean gyro z (IMU samples in the
                  window) vs mean ground-truth yaw rate (unwrapped yaw change / time between the ground-truth
                  samples nearest the window ends): correct sign and within +-3 %.
             D11: the TEST-M2-07 stop profile, 0.5 m/s for 3.0 s then 0 for 3.0 s. Ramp = from the first time the
                  ground-truth forward speed reaches 10 % to the first time it reaches 90 % of the plateau speed
                  (mean speed over [leg start + 1.5 s, leg end - 0.2 s]); ground-truth acceleration
                  = (v_90 - v_10) / (t_90 - t_10); mean accel x of the IMU samples in [t_10, t_90]: correct sign
                  and within +-20 %. The ground-truth pitch over the ramp is reported (gravity leaks into accel x
                  as g sin(pitch)).
  encoders   (TEST-M3-09, 3 runs): D12.
             The TEST-M2-05 linear profile (0.2 m/s 5 s, stop 3 s, -0.2 m/s 5 s, stop 3 s): for each leg (with
             its stop), (dtheta_L + dtheta_R) / 2 * r from /joint_states vs the ground-truth displacement along
             the start heading: same sign and within +-2 %.
             The TEST-M2-06 rotate profile: in each rotation leg dtheta_L and dtheta_R have opposite signs, with
             the right wheel positive for +wz (REP-103, CCW positive).
Exit 0 = all PASS, 1 = a FAIL, 2 = invalid run (RTF < 0.5 or missing data; repeat).
"""
import importlib.util
import math
import os
import statistics
import sys
import time

from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu
from gz.msgs10.pose_v_pb2 import Pose_V

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M2 = _load('test_m2_motion_measure', os.path.join(HERE, '..', 'M2', 'TEST-M2_motion_measure.py'))
s1_s4 = _load('test_m3_noise_stats', os.path.join(HERE, 'TEST-M3_noise_stats.py')).s1_s4

WORLD_TOPIC = '/world/sensor_test/pose/info'
G = 9.8
SIGMA_A, SIGMA_W = 0.01, 0.001          # DEC-032
BIAS_A, BIAS_W = 0.02, 0.001            # sensors.md §7.4 S1
REST_WINDOW = 10.0
SPAWN = (0.0, -20.0)


class Recorder(M2.Recorder):
    def __init__(self):
        super().__init__('m3_d_measure')
        self.imu = []
        qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=200, reliability=ReliabilityPolicy.RELIABLE)
        self.create_subscription(Imu, '/imu', self.on_imu, qos)
        self.gz.subscribe(Pose_V, WORLD_TOPIC, self.on_pose)

    def on_imu(self, m):
        a, w = m.linear_acceleration, m.angular_velocity
        with self.lock:
            self.imu.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, a.x, a.y, a.z, w.x, w.y, w.z))

    def imu_between(self, t0, t1):
        with self.lock:
            return [s for s in self.imu if t0 <= s[0] <= t1]


def excursion(r, t0, t1):
    g = r.gt_between(t0, t1)
    if not g:
        return
    dx = [s[1] - SPAWN[0] for s in g]; dy = [s[2] - SPAWN[1] for s in g]
    r.info(f'ground-truth excursion from the spawn point (0, -20): x {min(dx):+.3f} .. {max(dx):+.3f} m, '
           f'y {min(dy):+.3f} .. {max(dy):+.3f} m (clearance budget in TEST-M3-D_clearance_check.py)')


def unwrapped_yaw(win):
    yaw, prev = 0.0, win[0][6]
    for g in win[1:]:
        yaw += M2.wrap(g[6] - prev); prev = g[6]
    return yaw


def mode_imu_rest(r):
    sim0, wall0 = r.rec.sim(), time.time()
    t0 = r.rec.sim()
    r.wait_sim(t0 + REST_WINDOW + 0.3, 0.0, 0.0)
    r.rtf(sim0, wall0)
    s = r.rec.imu_between(t0, t0 + REST_WINDOW - 1e-6)
    gt = r.gt_between(t0, t0 + REST_WINDOW)
    sp = r.body_speed(r.samples(t0, t0 + REST_WINDOW), 0.0)
    r.info(f'window {t0:.3f} .. {t0 + REST_WINDOW:.3f} s: {len(s)} IMU samples; ground-truth max speed '
           f'{max(x[3] for x in sp) * 1000:.3f} mm/s, max tilt {r.tilt(t0, t0 + REST_WINDOW):.4f} deg ({len(gt)} samples)')
    if len(s) < 0.98 * REST_WINDOW * 100:
        print(f'INVALID  only {len(s)} IMU samples in the window')
        r.invalid = True
        return
    mean_az = statistics.fmean(x[3] for x in s)
    r.check(mean_az > 0, f'D9: mean specific force z {mean_az:+.5f} m/s^2 > 0 (+g on +Z, gravity up in imu_link)')
    channels = (('accel x', 1, 0.0, SIGMA_A, BIAS_A, 'm/s^2'), ('accel y', 2, 0.0, SIGMA_A, BIAS_A, 'm/s^2'),
                ('accel z', 3, G, SIGMA_A, BIAS_A, 'm/s^2'), ('gyro x', 4, 0.0, SIGMA_W, BIAS_W, 'rad/s'),
                ('gyro y', 5, 0.0, SIGMA_W, BIAS_W, 'rad/s'), ('gyro z', 6, 0.0, SIGMA_W, BIAS_W, 'rad/s'))
    for label, k, expected, sigma, bias, unit in channels:
        checks, summary = s1_s4([x[k] - expected for x in s], sigma, bias, label, unit)
        print('      ' + summary + f' (expected {expected:g})')
        for ok, text in checks:
            r.check(ok, text)
    excursion(r, t0, t0 + REST_WINDOW)


def eval_gyro(r, leg):
    t0, t1, _, wz = leg
    a, b = t0 + 1.0, t1 - 0.2
    win = r.gt_between(a, b)
    ga, gb = win[0], win[-1]
    gt_rate = unwrapped_yaw(win) / (gb[0] - ga[0])
    imu = r.rec.imu_between(ga[0], gb[0])
    gyro = statistics.fmean(x[6] for x in imu)
    err = (gyro - gt_rate) / gt_rate
    name = f'rotate {"+" if wz > 0 else "-"}{abs(wz)}'
    r.check(math.copysign(1, gyro) == math.copysign(1, gt_rate) == math.copysign(1, wz) and abs(err) <= 0.03,
            f'D10 {name}: mean gyro z {gyro:+.5f} rad/s vs ground-truth yaw rate {gt_rate:+.5f} rad/s '
            f'({err * 100:+.3f} %; sign; |.| <= 3 %) over {gb[0] - ga[0]:.3f} s, {len(imu)} IMU samples')
    r.info(f'{name}: mean accel x/y {statistics.fmean(x[1] for x in imu):+.4f} / {statistics.fmean(x[2] for x in imu):+.4f} '
           f'm/s^2 (expected 0: the IMU is on the rotation axis, CALC-M3-02)')


def eval_accel(r, leg):
    t0, t1, vx, _ = leg
    psi0 = r.nearest(r.rec.gt, t0)[6]
    sp = r.body_speed(r.samples(t0 - 0.5, t1), psi0)
    plateau = statistics.fmean(s[1] for s in sp if t0 + 1.5 <= s[0] <= t1 - 0.2)
    s10 = next(s for s in sp if s[0] >= t0 - 0.1 and s[1] >= 0.1 * plateau)
    s90 = next(s for s in sp if s[0] >= s10[0] and s[1] >= 0.9 * plateau)
    gt_acc = (s90[1] - s10[1]) / (s90[0] - s10[0])
    imu = r.rec.imu_between(s10[0], s90[0])
    ax = statistics.fmean(x[1] for x in imu)
    err = (ax - gt_acc) / gt_acc
    pitch = [math.degrees(g[5]) for g in r.gt_between(s10[0], s90[0])]
    r.check(math.copysign(1, ax) == math.copysign(1, gt_acc) == math.copysign(1, vx) and abs(err) <= 0.20,
            f'D11 accelerate to {vx} m/s: mean accel x {ax:+.4f} m/s^2 vs ground-truth acceleration {gt_acc:+.4f} m/s^2 '
            f'({err * 100:+.2f} %; sign; |.| <= 20 %) over the 10-90 % ramp {s10[0] - t0:+.3f} .. {s90[0] - t0:+.3f} s '
            f'({len(imu)} IMU samples; plateau {plateau:.4f} m/s)')
    r.info(f'ramp ground-truth pitch {min(pitch):+.4f} .. {max(pitch):+.4f} deg -> g sin(pitch) up to '
           f'{G * math.sin(math.radians(max(abs(p) for p in pitch))):.4f} m/s^2 in accel x')


def mode_imu_motion(r):
    sim0, wall0 = r.rec.sim(), time.time()
    T = math.pi / 0.5
    legs = r.profile([(T, 0.0, 0.5), (3.0, 0.0, 0.0), (T, 0.0, -0.5), (3.0, 0.0, 0.0), (3.0, 0.5, 0.0), (3.0, 0.0, 0.0)])
    r.rtf(sim0, wall0)
    eval_gyro(r, legs[0])
    eval_gyro(r, legs[2])
    eval_accel(r, legs[4])
    excursion(r, legs[0][0], legs[-1][1])


def wheel_delta(r, t0, t1):
    a, b = r.nearest(r.rec.js, t0), r.nearest(r.rec.js, t1)
    return b[1][0] - a[1][0], b[2][0] - a[2][0], a[0], b[0]


def mode_encoders(r):
    sim0, wall0 = r.rec.sim(), time.time()
    lin = r.profile([(5.0, 0.2, 0.0), (3.0, 0.0, 0.0), (5.0, -0.2, 0.0), (3.0, 0.0, 0.0)])
    T = math.pi / 0.5
    rot = r.profile([(T, 0.0, 0.5), (3.0, 0.0, 0.0), (T, 0.0, -0.5), (3.0, 0.0, 0.0)])
    r.rtf(sim0, wall0)
    for leg, stop in ((lin[0], lin[1]), (lin[2], lin[3])):
        t0, t_end = leg[0], stop[1]
        g0, g1 = r.nearest(r.rec.gt, t0), r.nearest(r.rec.gt, t_end)
        psi0 = g0[6]
        along = (g1[1] - g0[1]) * math.cos(psi0) + (g1[2] - g0[2]) * math.sin(psi0)
        dl, dr, ja, jb = wheel_delta(r, g0[0], g1[0])
        enc = (dl + dr) / 2 * M2.WHEEL_RADIUS
        err = (enc - along) / along
        name = 'forward' if leg[2] > 0 else 'reverse'
        r.check(math.copysign(1, enc) == math.copysign(1, along) == math.copysign(1, leg[2]) and abs(err) <= 0.02,
                f'D12 {name}: encoder travel (dtheta_L + dtheta_R)/2 * r = ({dl:+.4f} {dr:+.4f}) rad -> {enc:+.5f} m vs '
                f'ground truth {along:+.5f} m ({err * 100:+.4f} %; sign; |.| <= 2 %); stamps js {ja:.3f}/{jb:.3f}, '
                f'gt {g0[0]:.3f}/{g1[0]:.3f} s')
    for leg, stop in ((rot[0], rot[1]), (rot[2], rot[3])):
        t0, t_end, _, wz = leg[0], stop[1], leg[2], leg[3]
        dl, dr, _, _ = wheel_delta(r, t0, t_end)
        yaw = unwrapped_yaw(r.gt_between(t0, t_end))
        sgn = 1 if wz > 0 else -1
        name = f'rotate {"+" if wz > 0 else "-"}'
        r.check(dl * dr < 0 and sgn * dr > 0 > sgn * dl,
                f'D12 {name}: dtheta_L {dl:+.4f} rad, dtheta_R {dr:+.4f} rad: opposite signs, right '
                f'{"positive" if sgn > 0 else "negative"} for wz {wz:+.1f} rad/s')
        r.info(f'{name}: wheel arc r*(dtheta_R - dtheta_L)/2 {M2.WHEEL_RADIUS * (dr - dl) / 2:+.5f} m vs '
               f'(track / 2) * ground-truth yaw {0.2 * yaw:+.5f} m (yaw {math.degrees(yaw):+.3f} deg; informational)')
    excursion(r, lin[0][0], rot[-1][1])


MODES = {'imu_rest': mode_imu_rest, 'imu_motion': mode_imu_motion, 'encoders': mode_encoders}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in MODES:
        print(__doc__)
        return 2
    M2.rclpy.init()
    rec = Recorder()
    ex = M2.SingleThreadedExecutor()  # as M2 (TS-013)
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()  # TS-030 fix (REQ-TA-01)
    r = M2.Run(rec)
    print(f'# TEST-M3 Task D harness mode={mode}, wall {time.strftime("%F %T %Z")}, ground truth {WORLD_TOPIC}')
    try:
        if r.ready():
            MODES[mode](r)
    except (StopIteration, IndexError, ZeroDivisionError, statistics.StatisticsError) as exc:
        print(f'INVALID  missing data for an evaluation ({type(exc).__name__}: {exc})')
        r.invalid = True
    finally:
        spin.stop(rec)
    with rec.lock:
        print(f'# samples: ground truth {len(rec.gt)}, imu {len(rec.imu)}, joint_states {len(rec.js)}, odometry {len(rec.odom)}')
    if r.invalid:
        print('# result: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"ALL CRITERIA PASSED" if r.fails == 0 else f"{r.fails} CRITERION/CRITERIA FAILED"}')
    return 1 if r.fails else 0


if __name__ == '__main__':
    code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)  # gz-transport aborts during interpreter teardown (as the M2 harness)
