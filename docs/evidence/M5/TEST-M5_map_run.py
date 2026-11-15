#!/usr/bin/env python3
"""M5 mapping-run harness: drives the Selected route and records the poses at every rest point (M5 Task B).

Usage (simulation and SLAM running: sim.launch.py sensors:=true world:=mapping_arena.sdf + slam.launch.py; same
ROS_DOMAIN_ID / GZ_PARTITION):  python3 TEST-M5_map_run.py <rest_points.csv>
Exit 0 = route driven and every pose criterion PASS, 1 = a criterion FAIL or the robot left the path, 2 = invalid run
(RTF < 0.5, no ground truth, SLAM not ready, or a leg timed out). The map is saved by the calling procedure.

Route: TEST-M5_route.py (CALC-M5-02, Selected). Driving (DEC-049): a waypoint follower steered by Gazebo ground truth
(the `amr` pose on /world/mapping_arena/pose/info), proportional control only:
  - turn in place: w = clip(K_TURN * e_yaw, +/-0.5 rad/s), v = 0, until |e_yaw| < 0.5 deg; a 180-degree turn is made
    to the left (as the route prediction assumes);
  - straight leg: v = clip(K_DIST * s, 0, 0.25 m/s), where s is the remaining distance along the leg; w = clip(K_HEAD *
    e, +/-0.5 rad/s), where e is the heading error to the waypoint (to the leg direction in the last 0.3 m, where
    the bearing to a point becomes ill-defined); the leg ends when s < 0.01 m;
  - rest point: zero command for 1.0 s (plan §3.2), then until the ground-truth speed stays below 5 mm/s for 0.2 s.
No I or D term (DEC-049): the simulation has no steady disturbance to integrate away, and D would amplify pose noise.
Ground truth steers the robot only; SLAM never sees it. Commands: TwistStamped on /cmd_vel, 20 Hz, simulation-time
stamps, frame base_footprint (DEC-026/029), as tools/demo_drive.py.

At each rest point (the start and every waypoint) the harness records: ground truth; the SLAM pose = TF
map -> base_footprint; the odometry pose = TF odom -> base_footprint; TF map -> odom. Errors are SLAM minus truth and
odometry minus truth (position distance, wrapped yaw difference). The map frame is the world frame (Task A gate).
Pose criterion (TEST-M5-04, DEC-047): SLAM error <= 0.05 m and <= 1.0 deg at every rest point. Path safety: the
ground-truth distance from the planned leg (cross-track) must stay below 0.30 m (route clearance margin 0.8 m), or the
run stops (FAIL). The odometry error is reported (INFO; the TEST-M5-06 drift measure).
"""
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


M2 = _load('M2', os.path.join(HERE, '..', 'M2', 'TEST-M2_motion_measure.py'))   # Spinner (TS-030), rpy, wrap
route = _load('route', os.path.join(HERE, 'TEST-M5_route.py'))
rclpy = M2.rclpy

from geometry_msgs.msg import TwistStamped  # noqa: E402
from gz.msgs10.pose_v_pb2 import Pose_V  # noqa: E402
from gz.transport13 import Node as GzNode  # noqa: E402
from lifecycle_msgs.srv import GetState  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from rclpy.time import Time  # noqa: E402
from tf2_ros import Buffer, TransformListener  # noqa: E402

K_TURN, K_HEAD, K_DIST = 2.0, 2.0, 1.0
W_MAX, V_MAX = route.W, route.V
YAW_DONE, DIST_DONE, NEAR = math.radians(0.5), 0.01, 0.30
REST_V, REST_HOLD = 0.005, 0.2
POSE_MAX, YAW_MAX = 0.05, math.radians(1.0)
CROSS_MAX = 0.30
WORLD_TOPIC = '/world/mapping_arena/pose/info'


class Rec(Node):
    def __init__(self):
        super().__init__('test_m5_map_run', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.lock = threading.Lock()
        self.gt = None          # (t, x, y, yaw)
        self.gt_prev = None
        self.speed = None       # ground-truth speed, m/s
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.gz = GzNode()
        self.gz.subscribe(Pose_V, WORLD_TOPIC, self.on_pose)

    def on_pose(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9
        for p in msg.pose:
            if p.name == 'amr':
                yaw = M2.rpy(p.orientation.w, p.orientation.x, p.orientation.y, p.orientation.z)[2]
                with self.lock:
                    if self.gt is not None and t - self.gt[0] >= 0.05:
                        self.speed = math.hypot(p.position.x - self.gt[1], p.position.y - self.gt[2]) / (t - self.gt[0])
                        self.gt_prev = self.gt
                    if self.gt is None or t - self.gt[0] >= 0.05:
                        self.gt = (t, p.position.x, p.position.y, yaw)
                    self.cur = (t, p.position.x, p.position.y, yaw)

    def truth(self):
        with self.lock:
            return getattr(self, 'cur', None)

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def send(self, v, w):
        m = TwistStamped()
        m.header.stamp = self.get_clock().now().to_msg()
        m.header.frame_id = 'base_footprint'
        m.twist.linear.x, m.twist.angular.z = float(v), float(w)
        self.pub.publish(m)

    def tf(self, parent, child):
        t = self.buffer.lookup_transform(parent, child, Time())
        q = t.transform.rotation
        return t.transform.translation.x, t.transform.translation.y, M2.rpy(q.w, q.x, q.y, q.z)[2]


def clip(v, lim):
    return max(-lim, min(lim, v))


class Run:
    def __init__(self, rec, csv_path):
        self.rec, self.fail, self.invalid = rec, False, False
        self.rows = []
        self.csv_path = csv_path
        self.max_cross = 0.0

    def tick(self):
        time.sleep(0.05)   # 20 Hz command rate (wall); stamps and timing use simulation time

    def wait_ready(self):
        t_end = time.monotonic() + 90
        while time.monotonic() < t_end and (self.rec.truth() is None or self.rec.now() <= 0):
            time.sleep(0.1)
        if self.rec.truth() is None:
            print('# no ground truth on ' + WORLD_TOPIC)
            return False
        cli = self.rec.create_client(GetState, '/slam_toolbox/get_state')
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
            print(f'# SLAM not active (state {state})')
            return False
        while time.monotonic() < t_end:   # the map frame exists once SLAM has processed its first scan
            try:
                self.rec.tf('map', 'base_footprint')
                return True
            except Exception:  # noqa: BLE001 - not yet available
                time.sleep(0.2)
        print('# no TF map -> base_footprint within 90 s')
        return False

    def turn_to(self, heading, left_if_half=True):
        t_end = self.rec.now() + 30.0
        first = True
        while self.rec.now() < t_end:
            _, _, _, yaw = self.rec.truth()
            e = M2.wrap(heading - yaw)
            if first and left_if_half and abs(e) > 2.5:
                e = abs(e)
            first = False
            if abs(e) < YAW_DONE:
                self.rec.send(0.0, 0.0)
                return True
            self.rec.send(0.0, clip(K_TURN * e, W_MAX))
            self.tick()
            # after the first step the turn direction follows the error, which no longer wraps
        return False

    def drive_leg(self, a, b):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        leg_h = math.atan2(uy, ux)
        t_end = self.rec.now() + L / V_MAX * 2 + 20.0
        while self.rec.now() < t_end:
            _, x, y, yaw = self.rec.truth()
            s = (b[0] - x) * ux + (b[1] - y) * uy
            cross = abs(-(x - a[0]) * uy + (y - a[1]) * ux)
            self.max_cross = max(self.max_cross, cross)
            if cross > CROSS_MAX:
                self.rec.send(0.0, 0.0)
                print(f'FAIL  robot left the path: cross-track {cross:.3f} m > {CROSS_MAX} m on leg {a} -> {b}')
                self.fail = True
                return False
            if s < DIST_DONE:
                self.rec.send(0.0, 0.0)
                return True
            target = leg_h if s < NEAR else math.atan2(b[1] - y, b[0] - x)
            e = M2.wrap(target - yaw)
            self.rec.send(clip(K_DIST * s, V_MAX) if s > 0 else 0.0, clip(K_HEAD * e, W_MAX))
            self.tick()
        return False

    def rest_point(self, idx, wp):
        t_settle = self.rec.now() + 1.0
        while self.rec.now() < t_settle:
            self.rec.send(0.0, 0.0)
            self.tick()
        t_end, still_since = self.rec.now() + 5.0, None
        while self.rec.now() < t_end:
            self.rec.send(0.0, 0.0)
            sp = self.rec.speed
            if sp is not None and sp < REST_V:
                still_since = still_since or self.rec.now()
                if self.rec.now() - still_since >= REST_HOLD:
                    break
            else:
                still_since = None
            self.tick()
        t, gx, gy, gyaw = self.rec.truth()
        try:
            sx, sy, syaw = self.rec.tf('map', 'base_footprint')
            ox, oy, oyaw = self.rec.tf('odom', 'base_footprint')
            mx, my, myaw = self.rec.tf('map', 'odom')
        except Exception as exc:  # noqa: BLE001 - reported
            print(f'FAIL  rest point {idx}: TF lookup failed: {type(exc).__name__}: {exc}')
            self.fail = True
            return
        se, sye = math.hypot(sx - gx, sy - gy), M2.wrap(syaw - gyaw)
        oe, oye = math.hypot(ox - gx, oy - gy), M2.wrap(oyaw - gyaw)
        ok = se <= POSE_MAX and abs(sye) <= YAW_MAX
        self.fail |= not ok
        print(f'{"PASS" if ok else "FAIL"}  rest point {idx:2d} at W{idx} {wp}: SLAM error {se * 1000:6.1f} mm, '
              f'{math.degrees(sye):+6.3f} deg (<= {POSE_MAX * 1000:.0f} mm, 1.0 deg); odometry error {oe * 1000:7.1f} mm, '
              f'{math.degrees(oye):+7.3f} deg; map->odom ({mx:+.3f}, {my:+.3f}, {math.degrees(myaw):+.2f} deg)',
              flush=True)
        self.rows.append([idx, f'{t:.3f}', gx, gy, gyaw, sx, sy, syaw, ox, oy, oyaw, mx, my, myaw, se, sye, oe, oye])

    def go(self):
        wps = route.WAYPOINTS
        sim0, wall0 = self.rec.now(), time.monotonic()
        self.rest_point(0, wps[0])
        for i, ((a, b), (_L, h, _turn)) in enumerate(zip(zip(wps, wps[1:]), route.legs(wps)), 1):
            if not self.turn_to(h) or not self.drive_leg(a, b):
                if not self.fail:
                    print(f'# leg {i} did not finish in time: INVALID RUN')
                    self.invalid = True
                return sim0, wall0
            self.rest_point(i, b)
        return sim0, wall0

    def write(self):
        with open(self.csv_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['rest_point', 'sim_t', 'gt_x', 'gt_y', 'gt_yaw', 'slam_x', 'slam_y', 'slam_yaw', 'odom_x',
                        'odom_y', 'odom_yaw', 'm2o_x', 'm2o_y', 'm2o_yaw', 'slam_err_m', 'slam_yaw_err',
                        'odom_err_m', 'odom_yaw_err'])
            for r in self.rows:
                w.writerow([r[0], r[1]] + [f'{v:.6f}' for v in r[2:]])


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    rclpy.init()
    rec = Rec()
    ex = M2.SingleThreadedExecutor()
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()
    run = Run(rec, sys.argv[1])
    print(f'# TEST-M5 mapping run, wall {time.strftime("%F %T %Z")}; route {len(route.WAYPOINTS) - 1} legs '
          f'(TEST-M5_route.py); gains K_TURN {K_TURN}, K_HEAD {K_HEAD}, K_DIST {K_DIST}', flush=True)
    try:
        if not run.wait_ready():
            return 2
        sim0, wall0 = run.go()
        sim1, wall1 = rec.now(), time.monotonic()
        rec.send(0.0, 0.0)
    finally:
        spin.stop(rec)
    run.write()
    rtf = (sim1 - sim0) / max(wall1 - wall0, 1e-9)
    print(f'INFO  route: {sim1 - sim0:.1f} s simulation time in {wall1 - wall0:.1f} s wall, RTF {rtf:.2f}; max '
          f'cross-track {run.max_cross * 1000:.1f} mm; {len(run.rows)} rest points written to '
          f'{os.path.basename(sys.argv[1])}')
    if run.rows:
        last = run.rows[-1]
        print(f'INFO  end of route: odometry error {last[16] * 1000:.1f} mm, {math.degrees(last[17]):+.3f} deg '
              f'(drift that SLAM removed); SLAM error {last[14] * 1000:.1f} mm, {math.degrees(last[15]):+.3f} deg')
    if rtf < 0.5:
        print(f'# RTF {rtf:.2f} < 0.5: INVALID RUN')
        return 2
    if run.invalid:
        return 2
    ok = not run.fail and len(run.rows) == len(route.WAYPOINTS)
    print(f'# result: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
