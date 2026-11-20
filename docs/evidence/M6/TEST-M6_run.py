#!/usr/bin/env python3
"""M6 localization-run harness: drives a test route and records the localization pose (M6 Task B).

Usage (simulation and localization running: sim.launch.py sensors:=true world:=<world> + localization.launch.py; same
ROS_DOMAIN_ID / GZ_PARTITION):
    python3 TEST-M6_run.py <prefix> [--route forward|reverse] [--wrong-start]
Writes <prefix>_rest.csv (one row per rest point) and <prefix>_track.csv (10 Hz). Judging is offline:
TEST-M6_pose_check.py. Exit 0 = route driven and recorded, 1 = the robot left the path (safety stop), 2 = invalid run
(RTF < 0.5, no ground truth, localization not ready, a leg timed out, the wrong start not taken, or more than 2 % of
the 10 Hz samples without a pose).

Driving: the M5 ground-truth follower (DEC-049), imported from docs/evidence/M5/TEST-M5_map_run.py unchanged (gains,
speeds, rest-point settling, cross-track safety stop 0.30 m). Route: TEST-M6_route.py (the M5 route forward or reversed).
Ground truth (the `amr` pose on /world/mapping_arena/pose/info) steers the robot only; AMCL never sees it.

Recording (M6 plan §3.2): the estimate is TF map -> base_footprint looked up AT THE GROUND-TRUTH STAMP, never "latest":
AMCL post-dates map -> odom by transform_tolerance (1.0 s), and the odometry TF lags the truth by up to one controller
period, so a latest lookup would mix times. Ground-truth samples are taken every 0.1 s of simulation time; each is
resolved once the TF buffer has data 0.3 s past its stamp (tf2 interpolates between the two neighbouring transforms).
A sample still unresolved 3 s after its stamp is recorded as missing. Also recorded: odom -> base_footprint (the
odometry pose, TEST-M6-05/-07 drift), and the ground-truth travel (cumulative distance of the robot centre).
At rest points also the raw wheel-odometry pose from /diff_drive_controller/odom (the message nearest the ground-truth
stamp, within 0.05 s; empty if none): without the EKF it equals odom -> base_footprint; with ekf:=true (TEST-M6-07)
odom -> base_footprint is the fused pose and this column keeps the raw one (M6 Task D).
Rest points: as M5 (after 1 s of zero command and 0.2 s below 5 mm/s), with the TF lookups also at the ground-truth
stamp.

Wrong start (--wrong-start, TEST-M6-04, M6 plan §3.3): before the route, an initial pose offset from the truth by
(+0.30, +0.40) m (0.50 m) and +15 deg is published on /initialpose (frame map) with the covariance that RViz's
"2D Pose Estimate" sends (x, y variance 0.25 m^2, yaw variance 0.0685 rad^2: sigma 0.5 m and 15 deg). The run
continues once /amcl_pose reports a pose within 0.05 m and 1 deg of the injected one (AMCL took it).
"""
import argparse
import csv
import importlib.util
import math
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M5 = _load('map_run', os.path.join(HERE, '..', 'M5', 'TEST-M5_map_run.py'))   # follower, Rec, M2 helpers
route6 = _load('route6', os.path.join(HERE, 'TEST-M6_route.py'))
M2, rclpy = M5.M2, M5.rclpy

from geometry_msgs.msg import PoseWithCovarianceStamped  # noqa: E402
from nav_msgs.msg import Odometry  # noqa: E402
from lifecycle_msgs.srv import GetState  # noqa: E402
from rclpy.duration import Duration  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402
from rclpy.time import Time  # noqa: E402

SAMPLE_DT = 0.1          # s of simulation time between track samples (10 Hz)
RESOLVE_AFTER = 0.3      # s: resolve a sample once the clock is this far past its stamp
MISSING_AFTER = 3.0      # s: give up on a sample
MISSING_MAX = 0.02       # fraction of missing samples above which the run is invalid
RAW_MATCH = 0.05         # s: largest stamp difference for the raw-odometry pose at a rest point
WRONG = (0.30, 0.40, math.radians(15.0))
RVIZ_COV = (0.25, 0.25, 0.06853891909122467)   # x, y variance m^2; yaw variance rad^2 (RViz 2D Pose Estimate)
LATCHED = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)


def stamp(t):
    return Time(seconds=int(t), nanoseconds=int(round((t - int(t)) * 1e9)))


class Rec6(M5.Rec):
    """The M5 recorder plus a 10 Hz ground-truth sample queue, /initialpose and /amcl_pose."""

    def __init__(self):
        self.samples = []          # pending (t, x, y, yaw, travel); set before the base class subscribes to Gazebo
        self.travel = 0.0
        self.last_xy = None
        self.next_t = None
        super().__init__()
        self.init_pub = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
        self.amcl_pose = None
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.on_amcl, LATCHED)
        self.raw = []              # (t, x, y, yaw) from /diff_drive_controller/odom, the last 5 s
        self.create_subscription(Odometry, '/diff_drive_controller/odom', self.on_raw, 50)

    def on_raw(self, msg):
        p, q = msg.pose.pose.position, msg.pose.pose.orientation
        t = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        with self.lock:
            self.raw.append((t, p.x, p.y, M2.rpy(q.w, q.x, q.y, q.z)[2]))
            while self.raw and self.raw[0][0] < t - 5.0:
                self.raw.pop(0)

    def raw_at(self, t):
        with self.lock:
            best = min(self.raw, key=lambda r: abs(r[0] - t), default=None)
        return best[1:] if best is not None and abs(best[0] - t) <= RAW_MATCH else ('', '', '')

    def on_amcl(self, msg):
        with self.lock:
            self.amcl_pose = msg

    def on_pose(self, msg):
        super().on_pose(msg)
        cur = self.truth()
        if cur is None:
            return
        t, x, y, yaw = cur
        with self.lock:
            if self.last_xy is not None:
                self.travel += math.hypot(x - self.last_xy[0], y - self.last_xy[1])
            self.last_xy = (x, y)
            if self.next_t is not None and t >= self.next_t:
                self.samples.append((t, x, y, yaw, self.travel))
                self.next_t = t + SAMPLE_DT

    def start_sampling(self):
        t0 = self.truth()[0]   # truth() takes the lock itself (threading.Lock is not re-entrant)
        with self.lock:
            self.next_t = t0

    def tf_at(self, parent, child, t):
        tr = self.buffer.lookup_transform(parent, child, stamp(t))
        q = tr.transform.rotation
        return tr.transform.translation.x, tr.transform.translation.y, M2.rpy(q.w, q.x, q.y, q.z)[2]


class Run6(M5.Run):
    def __init__(self, rec, prefix, waypoints):
        super().__init__(rec, prefix + '_rest.csv')
        self.prefix, self.wps = prefix, waypoints
        self.track, self.missing = [], 0
        self.track_lock = threading.Lock()

    def tick(self):
        self.resolve()
        time.sleep(0.05)

    def resolve(self, final=False):
        now = self.rec.now()
        with self.rec.lock:
            pending = list(self.rec.samples)
        done = []
        for s in pending:
            t = s[0]
            if not final and now - t < RESOLVE_AFTER:
                continue
            try:
                ex, ey, eyaw = self.rec.tf_at('map', 'base_footprint', t)
                ox, oy, oyaw = self.rec.tf_at('odom', 'base_footprint', t)
                self.track.append([t, s[4], s[1], s[2], s[3], ex, ey, eyaw, ox, oy, oyaw])
                done.append(s)
            except Exception:  # noqa: BLE001 - data not there yet, or never
                if final or now - t > MISSING_AFTER:
                    self.missing += 1
                    done.append(s)
        if done:
            with self.rec.lock:
                self.rec.samples = [s for s in self.rec.samples if s not in done]

    def wait_ready(self):
        t_end = time.monotonic() + 90
        while time.monotonic() < t_end and (self.rec.truth() is None or self.rec.now() <= 0):
            time.sleep(0.1)
        if self.rec.truth() is None:
            print('# no ground truth on ' + M5.WORLD_TOPIC)
            return False
        cli = self.rec.create_client(GetState, '/amcl/get_state')
        state = None
        while time.monotonic() < t_end:
            if cli.wait_for_service(timeout_sec=2.0):
                fut = cli.call_async(GetState.Request())
                t0 = time.monotonic()
                while not fut.done() and time.monotonic() - t0 < 5:
                    time.sleep(0.05)
                state = fut.result().current_state.label if fut.done() and fut.result() else None
                if state == 'active':
                    break
            time.sleep(0.5)
        if state != 'active':
            print(f'# AMCL not active (state {state})')
            return False
        while time.monotonic() < t_end:
            try:
                self.rec.tf('map', 'base_footprint')
                return True
            except Exception:  # noqa: BLE001 - not yet available
                time.sleep(0.2)
        print('# no TF map -> base_footprint within 90 s')
        return False

    def wrong_start(self):
        _, gx, gy, gyaw = self.rec.truth()
        x, y, yaw = gx + WRONG[0], gy + WRONG[1], gyaw + WRONG[2]
        m = PoseWithCovarianceStamped()
        m.header.frame_id = 'map'
        m.pose.pose.position.x, m.pose.pose.position.y = x, y
        m.pose.pose.orientation.z, m.pose.pose.orientation.w = math.sin(yaw / 2), math.cos(yaw / 2)
        m.pose.covariance[0], m.pose.covariance[7], m.pose.covariance[35] = RVIZ_COV
        t_end = time.monotonic() + 20
        while time.monotonic() < t_end:
            m.header.stamp = self.rec.get_clock().now().to_msg()
            self.rec.init_pub.publish(m)
            t1 = time.monotonic() + 2
            while time.monotonic() < t1:
                with self.rec.lock:
                    a = self.rec.amcl_pose
                if a is not None:
                    q = a.pose.pose.orientation
                    ayaw = M2.rpy(q.w, q.x, q.y, q.z)[2]
                    if (math.hypot(a.pose.pose.position.x - x, a.pose.pose.position.y - y) < 0.05
                            and abs(M2.wrap(ayaw - yaw)) < math.radians(1.0)):
                        print(f'INFO  wrong start taken: /initialpose ({x:+.3f}, {y:+.3f}) m, '
                              f'{math.degrees(yaw):+.2f} deg; truth ({gx:+.3f}, {gy:+.3f}) m, '
                              f'{math.degrees(gyaw):+.2f} deg; offset 0.500 m, +15.00 deg', flush=True)
                        return True
                time.sleep(0.1)
        print('# /amcl_pose did not take the wrong start within 20 s: INVALID RUN')
        return False

    def rest_point(self, idx, wp):
        # As M5 (settle, then the rest test), with the lookups at the ground-truth stamp.
        t_settle = self.rec.now() + 1.0
        while self.rec.now() < t_settle:
            self.rec.send(0.0, 0.0)
            self.tick()
        t_end, still_since = self.rec.now() + 5.0, None
        while self.rec.now() < t_end:
            self.rec.send(0.0, 0.0)
            sp = self.rec.speed
            if sp is not None and sp < M5.REST_V:
                still_since = still_since or self.rec.now()
                if self.rec.now() - still_since >= M5.REST_HOLD:
                    break
            else:
                still_since = None
            self.tick()
        t, gx, gy, gyaw = self.rec.truth()
        t_wait = time.monotonic() + 5.0
        while True:
            try:
                ex, ey, eyaw = self.rec.tf_at('map', 'base_footprint', t)
                ox, oy, oyaw = self.rec.tf_at('odom', 'base_footprint', t)
                mx, my, myaw = self.rec.tf_at('map', 'odom', t)
                break
            except Exception as exc:  # noqa: BLE001 - wait for the buffer, then report
                if time.monotonic() > t_wait:
                    print(f'# rest point {idx}: TF lookup at the ground-truth stamp failed: {type(exc).__name__}: {exc}')
                    self.invalid = True
                    return
                self.tick()
        rx, ry, ryaw = self.rec.raw_at(t)
        ee, eye = math.hypot(ex - gx, ey - gy), M2.wrap(eyaw - gyaw)
        oe, oye = math.hypot(ox - gx, oy - gy), M2.wrap(oyaw - gyaw)
        with self.rec.lock:
            travel = self.rec.travel
        print(f'INFO  rest point {idx:2d} at {wp}, travel {travel:6.2f} m: estimate error {ee * 1000:6.1f} mm, '
              f'{math.degrees(eye):+6.3f} deg; odometry error {oe * 1000:6.1f} mm, {math.degrees(oye):+7.3f} deg',
              flush=True)
        self.rows.append([idx, f'{t:.3f}', travel, gx, gy, gyaw, ex, ey, eyaw, ox, oy, oyaw, mx, my, myaw,
                          rx, ry, ryaw])

    def go(self):
        wps = self.wps
        self.rec.start_sampling()
        sim0, wall0 = self.rec.now(), time.monotonic()
        self.rest_point(0, wps[0])
        for i, ((a, b), (_L, h, _turn)) in enumerate(zip(zip(wps, wps[1:]), M5.route.legs(wps)), 1):
            if not self.turn_to(h) or not self.drive_leg(a, b):
                if not self.fail:
                    print(f'# leg {i} did not finish in time: INVALID RUN')
                    self.invalid = True
                return sim0, wall0
            self.rest_point(i, b)
        return sim0, wall0

    def write(self):
        with open(self.prefix + '_rest.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['rest_point', 'sim_t', 'travel', 'gt_x', 'gt_y', 'gt_yaw', 'est_x', 'est_y', 'est_yaw',
                        'odom_x', 'odom_y', 'odom_yaw', 'm2o_x', 'm2o_y', 'm2o_yaw', 'raw_x', 'raw_y', 'raw_yaw'])
            for r in self.rows:
                w.writerow([r[0], r[1]] + [v if v == '' else f'{v:.6f}' for v in r[2:]])
        with open(self.prefix + '_track.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['sim_t', 'travel', 'gt_x', 'gt_y', 'gt_yaw', 'est_x', 'est_y', 'est_yaw', 'odom_x', 'odom_y',
                        'odom_yaw'])
            for r in sorted(self.track):
                w.writerow([f'{r[0]:.3f}'] + [f'{v:.6f}' for v in r[1:]])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('prefix')
    ap.add_argument('--route', choices=sorted(route6.ROUTES), default='forward')
    ap.add_argument('--wrong-start', action='store_true')
    args = ap.parse_args()
    rclpy.init()
    rec = Rec6()
    ex = M2.SingleThreadedExecutor()
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()
    run = Run6(rec, args.prefix, route6.ROUTES[args.route])
    print(f'# TEST-M6 localization run, wall {time.strftime("%F %T %Z")}; route {args.route} '
          f'({len(run.wps) - 1} legs, TEST-M6_route.py); wrong start {args.wrong_start}; follower gains K_TURN '
          f'{M5.K_TURN}, K_HEAD {M5.K_HEAD}, K_DIST {M5.K_DIST} (DEC-049)', flush=True)
    invalid = False
    try:
        if not run.wait_ready():
            return 2
        if args.wrong_start and not run.wrong_start():
            return 2
        sim0, wall0 = run.go()
        sim1, wall1 = rec.now(), time.monotonic()
        rec.send(0.0, 0.0)
        t_flush = time.monotonic() + 3
        while time.monotonic() < t_flush and rec.samples:
            run.resolve()
            time.sleep(0.1)
        run.resolve(final=True)
    finally:
        spin.stop(rec)
    run.write()
    rtf = (sim1 - sim0) / max(wall1 - wall0, 1e-9)
    n = len(run.track) + run.missing
    print(f'INFO  route: {sim1 - sim0:.1f} s simulation time in {wall1 - wall0:.1f} s wall, RTF {rtf:.2f}; max '
          f'cross-track {run.max_cross * 1000:.1f} mm; {len(run.rows)} rest points, {len(run.track)} track samples '
          f'({run.missing} missing of {n}); travel {rec.travel:.2f} m')
    if rtf < 0.5:
        print(f'# RTF {rtf:.2f} < 0.5: INVALID RUN')
        invalid = True
    if n == 0 or run.missing > MISSING_MAX * n:
        print(f'# {run.missing} of {n} track samples missing (> {MISSING_MAX:.0%}): INVALID RUN')
        invalid = True
    if run.invalid or invalid:
        return 2
    if run.fail:
        print('# result: FAIL (safety stop)')
        return 1
    print('# result: route driven and recorded (judged by TEST-M6_pose_check.py)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
