#!/usr/bin/env python3
"""M2 motion-test harness (TEST-M2-03 to -08, -10; procedures in docs/testing/test_plan.md §6).

Usage (with the M2 simulation running, or for `startup` started together with it):
    python3 TEST-M2_motion_measure.py <mode>   (not -I: isolated mode drops the ROS PYTHONPATH)
Modes: startup, fault, tfcheck, linear, rotate, stop, timeout, stale, wallclock, domainswitch, limits, rest.

Ground truth: the `amr` model pose in the world from Gazebo `/world/empty/pose/info` (gz-transport,
simulation-time stamped). Controller outputs: /diff_drive_controller/odom, /joint_states and
/diff_drive_controller/cmd_vel_out. Commands: geometry_msgs/TwistStamped on /cmd_vel at 50 Hz,
stamped in simulation time unless the mode says otherwise.
Simulation time is taken from the Gazebo pose stream stamps (same clock as /clock), extrapolated
between the bursty samples with the wall clock times the measured real-time factor. It is not taken
from a /clock subscription: processing the 1 kHz /clock in this Python process starved its callbacks
and stretched its timing (TS-013). The ROS node therefore runs with use_sim_time false, and every
stamped command still carries simulation time. Criteria: DEC-027 (and DEC-019 for
`rest`). Each criterion prints PASS/FAIL with the measured value. Exit 0 = all PASS, 1 = a FAIL,
2 = invalid run (RTF < 0.5 or missing data; repeat the run, it is not a failure).
"""
import math
import os
import subprocess
import sys
import threading
import time
import traceback

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from tf2_msgs.msg import TFMessage
from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V

WHEEL_RADIUS = 0.075   # m, wheel_radius in amr_properties.xacro
RATE = 50.0            # Hz command rate
SETTLE = 2.0           # s of sim time with zero command before measuring
REST = 0.005           # m/s: "at rest" speed
REST_HOLD = 0.2        # s the speed must stay below REST


def rpy(qw, qx, qy, qz):
    """Fixed-axis X-Y-Z roll, pitch, yaw (rad) from a quaternion (as TEST-M1-07)."""
    roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (qw * qy - qz * qx))))
    yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
    return roll, pitch, yaw


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


class Spinner:
    """Teardown-safe executor thread for every formal harness (TS-030 fix; REQ-TA-01, DEC-040 (c)).

    rclpy Jazzy Executor.shutdown() does not wait for a thread still inside spin(): it sets its flag, then
    destroys the guard condition that thread may be waiting on (troubleshooting.md TS-030). Here the thread
    spins with spin_once() and a stop flag; stop() sets the flag, joins the thread, and only then shuts down
    the executor, the node and the rclpy context. Any exception in the thread is printed in full and
    reported, never lost to a truncated teardown.
    """

    def __init__(self, executor):
        self.ex = executor
        self.flag = threading.Event()
        self.error = None
        self.thread = threading.Thread(target=self._run, daemon=True, name='spin')

    def _run(self):
        try:
            while not self.flag.is_set():
                self.ex.spin_once(timeout_sec=0.05)
        except Exception as exc:  # noqa: BLE001 - reported in full, then the thread ends
            self.error = f'{type(exc).__name__}: {exc}'
            sys.stderr.write('# TS-030 check: exception in the spin thread:\n' + traceback.format_exc())
            sys.stderr.flush()

    def start(self):
        self.thread.start()
        return self

    def stop(self, node, timeout=2.0):
        """Stop and join the spin thread, then shut down; prints and returns the thread-end state."""
        self.flag.set()
        self.thread.join(timeout)
        alive = self.thread.is_alive()
        self.ex.shutdown()
        node.destroy_node()
        rclpy.try_shutdown()
        state = (f'still alive after {timeout:g} s' if alive else
                 f'raised: {self.error}' if self.error else 'ended cleanly')
        print(f'# TS-030 check: spin thread {state}')
        return state


class Recorder(Node):
    def __init__(self, name='m2_measure'):
        super().__init__(name, parameter_overrides=[Parameter('use_sim_time', value=False)])
        self.lock = threading.RLock()  # re-entrant: sim() is also called while holding it
        # Simulation time from the Gazebo pose stream (TS-013): the stream arrives in bursts, so
        # between samples the time is extrapolated with the wall clock scaled by the measured
        # real-time factor, never decreasing. Anchors: latest (sim, wall) and the first one.
        self.sim_anchor = None    # (sim, wall) of the latest pose message
        self.sim_first = None     # (sim, wall) of the first pose message
        self.sim_last_out = 0.0
        self.gt, self.odom, self.js, self.out, self.tf = [], [], [], [], []
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.create_subscription(Odometry, '/diff_drive_controller/odom', self.on_odom, 50)
        self.create_subscription(JointState, '/joint_states', self.on_js, 50)
        self.create_subscription(TwistStamped, '/diff_drive_controller/cmd_vel_out', self.on_out, 50)
        self.create_subscription(TFMessage, '/tf', self.on_tf, 100)
        self.gz = GzNode()
        self.gz.subscribe(Pose_V, '/world/empty/pose/info', self.on_pose)

    def sim(self):
        with self.lock:
            if self.sim_anchor is None:
                return 0.0
            (s0, w0), (s1, w1) = self.sim_first, self.sim_anchor
            rtf = (s1 - s0) / (w1 - w0) if w1 - w0 > 1.0 else 1.0
            est = s1 + (time.monotonic() - w1) * min(max(rtf, 0.0), 1.5)
            self.sim_last_out = max(self.sim_last_out, est)
            return self.sim_last_out

    def on_pose(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9
        with self.lock:
            now = time.monotonic()
            if self.sim_anchor is None or t > self.sim_anchor[0]:
                self.sim_anchor = (t, now)
                if self.sim_first is None:
                    self.sim_first = (t, now)
        for p in msg.pose:
            if p.name == 'amr':
                r, pi, y = rpy(p.orientation.w, p.orientation.x, p.orientation.y, p.orientation.z)
                with self.lock:
                    self.gt.append((t, p.position.x, p.position.y, p.position.z, r, pi, y))

    def on_odom(self, m):
        q = m.pose.pose.orientation
        with self.lock:
            self.odom.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.pose.pose.position.x,
                              m.pose.pose.position.y, rpy(q.w, q.x, q.y, q.z)[2], m.header.frame_id, m.child_frame_id))

    def on_js(self, m):
        d = dict(zip(m.name, zip(m.position, m.velocity)))
        if 'left_wheel_joint' in d and 'right_wheel_joint' in d:
            with self.lock:
                self.js.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9,
                                d['left_wheel_joint'], d['right_wheel_joint']))

    def on_out(self, m):
        with self.lock:
            self.out.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, m.twist.linear.x, m.twist.angular.z))

    def on_tf(self, m):
        for t in m.transforms:
            if t.header.frame_id == 'odom' and t.child_frame_id == 'base_footprint':
                q = t.transform.rotation
                with self.lock:
                    self.tf.append((t.header.stamp.sec + t.header.stamp.nanosec * 1e-9, t.transform.translation.x,
                                    t.transform.translation.y, rpy(q.w, q.x, q.y, q.z)[2]))

    def send(self, vx, wz, stamp_offset=0.0, clock_node=None):
        msg = TwistStamped()
        if clock_node is not None:  # wall-clock stamps (characterization only)
            ns = clock_node.get_clock().now().nanoseconds
        else:
            ns = int((self.sim() + stamp_offset) * 1e9)
        msg.header.stamp.sec, msg.header.stamp.nanosec = ns // 10**9, ns % 10**9
        msg.header.frame_id = 'base_footprint'
        msg.twist.linear.x, msg.twist.angular.z = float(vx), float(wz)
        self.pub.publish(msg)


class Run:
    def __init__(self, rec):
        self.rec, self.fails, self.invalid = rec, 0, False

    def wait_sim(self, until, vx=None, wz=0.0, **kw):
        """Sleep until sim time `until`; if vx is given, publish (vx, wz) at RATE meanwhile."""
        next_pub = 0.0
        while self.rec.sim() < until:
            if vx is not None and self.rec.sim() >= next_pub:
                self.rec.send(vx, wz, **kw)
                next_pub = self.rec.sim() + 1.0 / RATE
            time.sleep(0.002)

    def profile(self, steps, **kw):
        """steps: [(duration, vx, wz)]; returns [(t_start, t_end, vx, wz)] in sim time."""
        legs = []
        for dur, vx, wz in steps:
            t0 = self.rec.sim()
            self.wait_sim(t0 + dur, vx, wz, **kw)
            legs.append((t0, self.rec.sim(), vx, wz))
        return legs

    def ready(self, timeout_wall=90.0):
        """Wait for ground truth and the first odometry message (drive controller active), then settle."""
        t_end = time.time() + timeout_wall
        while time.time() < t_end:
            with self.rec.lock:
                ok = bool(self.rec.gt) and bool(self.rec.odom) and self.rec.sim() > 0
            if ok:
                break
            time.sleep(0.05)
        else:
            print('INVALID: no ground truth or odometry within 90 s wall time')
            self.invalid = True
            return False
        self.wait_sim(self.rec.sim() + SETTLE, 0.0, 0.0)
        return True

    def check(self, ok, text):
        print(f'{"PASS" if ok else "FAIL"}  {text}')
        if not ok:
            self.fails += 1

    def info(self, text):
        print(f'INFO  {text}')

    # --- data helpers -------------------------------------------------------------------------
    def gt_between(self, t0, t1):
        with self.rec.lock:
            return [g for g in self.rec.gt if t0 <= g[0] <= t1]

    def nearest(self, series, t):
        with self.rec.lock:
            return min(series, key=lambda s: abs(s[0] - t)) if series else None

    def grid(self, t0, t1, dt=0.01):
        """Ground truth resampled on a dt grid (nearest earlier sample). Each entry keeps the
        sample's own simulation stamp, so differences use the true time base (the stream is
        about 59 Hz; grid times would bias finite differences by up to 17 ms)."""
        g = self.gt_between(t0 - 0.2, t1 + 0.2)
        out, j = [], 0
        t = t0
        while t <= t1 and g:
            while j + 1 < len(g) and g[j + 1][0] <= t:
                j += 1
            out.append(g[j])
            t += dt
        return out

    def samples(self, t0, t1):
        """Raw ground-truth samples (unique stamps, ~59 Hz) around [t0, t1]."""
        return self.gt_between(t0 - 0.2, t1 + 0.2)

    def body_speed(self, grid, psi0, h=3):
        """Forward speed (projected on the start heading psi0) and yaw rate: central difference on the
        raw samples over 2h = 6 sample intervals (about 0.1 s at 59 Hz, test_plan.md §6.1)."""
        sp = []
        for i in range(h, len(grid) - h):
            a, b = grid[i - h], grid[i + h]
            dt = b[0] - a[0]
            if dt <= 0:
                continue
            v = ((b[1] - a[1]) * math.cos(psi0) + (b[2] - a[2]) * math.sin(psi0)) / dt
            w = wrap(b[6] - a[6]) / dt
            sp.append((grid[i][0], v, w, math.hypot(b[1] - a[1], b[2] - a[2]) / dt))
        return sp

    def at_rest_time(self, t_from, t_to):
        """First time >= t_from from which the ground-truth speed stays < REST for REST_HOLD."""
        sp = self.body_speed(self.samples(t_from, t_to), 0.0)
        for i, s in enumerate(sp):
            if s[0] < t_from:
                continue
            window = [x for x in sp[i:] if x[0] <= s[0] + REST_HOLD]
            # the window must span REST_HOLD to within one sample interval (17 ms)
            if window and window[-1][0] >= s[0] + REST_HOLD - 0.02 and all(x[3] < REST for x in window):
                return s[0]
        return None

    def rtf(self, sim0, wall0):
        r = (self.rec.sim() - sim0) / max(1e-9, time.time() - wall0)
        ok = r >= 0.5
        print(f'{"INFO" if ok else "INVALID"}  RTF over the measurement window = {r:.3f} (valid if >= 0.5)')
        if not ok:
            self.invalid = True
        return r

    def tilt(self, t0, t1):
        g = self.gt_between(t0, t1)
        return max(max(abs(math.degrees(s[4])), abs(math.degrees(s[5]))) for s in g)

    def odom_delta(self, t0, t1):
        a, b = self.nearest(self.rec.odom, t0), self.nearest(self.rec.odom, t1)
        return a, b

    def wheels(self, t0, t1):
        with self.rec.lock:
            return [j for j in self.rec.js if t0 <= j[0] <= t1]

    # --- evaluations --------------------------------------------------------------------------
    def eval_linear(self, leg, t_end, target):
        t0, t1, vx, _ = leg
        g0 = self.nearest(self.rec.gt, t0); g1 = self.nearest(self.rec.gt, t_end)
        psi0 = g0[6]
        win = self.gt_between(t0, t_end)
        along = (g1[1] - g0[1]) * math.cos(psi0) + (g1[2] - g0[2]) * math.sin(psi0)
        lateral = max(abs(-(g[1] - g0[1]) * math.sin(psi0) + (g[2] - g0[2]) * math.cos(psi0)) for g in win)
        dpsi = math.degrees(wrap(g1[6] - psi0))
        name = 'forward' if vx > 0 else 'reverse'
        self.check(abs(along - target) <= 0.05 * abs(target) and math.copysign(1, along) == math.copysign(1, target),
                   f'{name}: displacement along start heading {along:+.4f} m, target {target:+.3f} m ± 5 %')
        self.check(lateral <= 0.020, f'{name}: max |lateral| {lateral * 1000:.2f} mm <= 20 mm')
        self.check(abs(dpsi) <= 1.0, f'{name}: heading change {dpsi:+.4f} deg, |.| <= 1 deg')
        cruise = self.wheels(t0 + 1.0, t1)
        sgn = 1 if vx > 0 else -1
        okw = bool(cruise) and all(sgn * j[1][1] > 0 and sgn * j[2][1] > 0 for j in cruise)
        self.check(okw, f'{name}: both wheel velocities {"> 0" if sgn > 0 else "< 0"} in cruise '
                        f'({len(cruise)} samples; mean L {sum(j[1][1] for j in cruise) / max(1, len(cruise)):+.4f}, '
                        f'R {sum(j[2][1] for j in cruise) / max(1, len(cruise)):+.4f} rad/s)')
        o0, o1 = self.odom_delta(t0, t_end)
        o_along = (o1[1] - o0[1]) * math.cos(o0[3]) + (o1[2] - o0[2]) * math.sin(o0[3])
        ratio = o_along / along if along else float('nan')
        self.check(math.copysign(1, o_along) == math.copysign(1, along) and 0.5 <= ratio <= 1.5,
                   f'{name}: odometry displacement {o_along:+.4f} m, ratio to ground truth {ratio:.4f} (sign; 0.5-1.5)')
        tl = self.tilt(t0, t_end)
        self.check(tl < 1.0, f'{name}: max |roll|,|pitch| {tl:.4f} deg < 1 deg')
        w = self.wheels(t0, t_end)
        if w:
            rot = (abs(w[-1][1][0] - w[0][1][0]) + abs(w[-1][2][0] - w[0][2][0])) / 2
            slip = 1 - abs(along) / (WHEEL_RADIUS * rot) if rot else float('nan')
            self.info(f'{name}: wheel rolling distance r*mean|dtheta| {WHEEL_RADIUS * rot:.4f} m, slip {slip * 100:+.3f} %')

    def eval_rotate(self, leg, t_end):
        t0, t1, _, wz = leg
        win = self.gt_between(t0, t_end)
        yaw, prev = 0.0, win[0][6]
        for g in win[1:]:
            yaw += wrap(g[6] - prev); prev = g[6]
        deg = math.degrees(yaw)
        name = 'rotate +' if wz > 0 else 'rotate -'
        target = 180.0 * (1 if wz > 0 else -1)
        self.check(abs(deg - target) <= 9.0, f'{name}: yaw change {deg:+.3f} deg, target {target:+.0f} deg ± 5 %')
        trans = max(math.hypot(g[1] - win[0][1], g[2] - win[0][2]) for g in win)
        self.check(trans <= 0.020, f'{name}: max base_footprint translation {trans * 1000:.2f} mm <= 20 mm')
        cruise = self.wheels(t0 + 1.0, t1)
        sgn = 1 if wz > 0 else -1
        okw = bool(cruise) and all(sgn * j[2][1] > 0 > sgn * j[1][1] for j in cruise)
        self.check(okw, f'{name}: right wheel {"> 0 >" if sgn > 0 else "< 0 <"} left wheel velocity in cruise ({len(cruise)} samples)')
        with self.rec.lock:
            od = [o for o in self.rec.odom if t0 <= o[0] <= t_end]
        oy, prev = 0.0, od[0][3]
        for o in od[1:]:
            oy += wrap(o[3] - prev); prev = o[3]
        ratio = oy / yaw if yaw else float('nan')
        self.check(math.copysign(1, oy) == math.copysign(1, yaw) and 0.5 <= ratio <= 1.5,
                   f'{name}: odometry yaw change {math.degrees(oy):+.3f} deg, ratio {ratio:.4f} (sign; 0.5-1.5)')
        tl = self.tilt(t0, t_end)
        self.check(tl < 1.0, f'{name}: max |roll|,|pitch| {tl:.4f} deg < 1 deg')


def mode_linear(r):
    sim0, wall0 = r.rec.sim(), time.time()
    legs = r.profile([(5.0, 0.2, 0.0), (3.0, 0.0, 0.0), (5.0, -0.2, 0.0), (3.0, 0.0, 0.0)])
    r.rtf(sim0, wall0)
    r.eval_linear(legs[0], legs[1][1], 0.980)
    r.eval_linear(legs[2], legs[3][1], -0.980)


def mode_rotate(r):
    sim0, wall0 = r.rec.sim(), time.time()
    T = math.pi / 0.5
    legs = r.profile([(T, 0.0, 0.5), (3.0, 0.0, 0.0), (T, 0.0, -0.5), (3.0, 0.0, 0.0)])
    r.rtf(sim0, wall0)
    r.eval_rotate(legs[0], legs[1][1])
    r.eval_rotate(legs[2], legs[3][1])


def mode_stop(r):
    sim0, wall0 = r.rec.sim(), time.time()
    legs = r.profile([(3.0, 0.5, 0.0), (3.0, 0.0, 0.0)])
    r.rtf(sim0, wall0)
    t0 = legs[1][0]
    sp = r.body_speed(r.samples(legs[0][0], t0), r.nearest(r.rec.gt, legs[0][0])[6])
    r.info(f'peak ground-truth speed before the zero command {max(s[1] for s in sp):.4f} m/s (limit 0.5)')
    tr = r.at_rest_time(t0, legs[1][1])
    dist = math.hypot(*(a - b for a, b in zip(r.nearest(r.rec.gt, legs[1][1])[1:3], r.nearest(r.rec.gt, t0)[1:3])))
    r.check(tr is not None and tr - t0 <= 0.70, f'stop: at rest {"never" if tr is None else f"{tr - t0:.3f} s"} after the zero command <= 0.70 s')
    r.check(dist <= 0.150, f'stop: distance after the zero command {dist:.4f} m <= 0.150 m (expected 0.125 m)')
    try:  # INFO only: missing data here must never fail or invalidate the run
        stop_timing_info(r, t0, legs[1][1])
    except (StopIteration, ValueError) as exc:
        r.info(f'stop timing not available ({type(exc).__name__}: {exc})')


def interp_xy(series, t):
    """Ground-truth (x, y) linearly interpolated at simulation time t (the stream is about 59 Hz)."""
    for a, b in zip(series, series[1:]):
        if a[0] <= t <= b[0]:
            f = (t - a[0]) / (b[0] - a[0]) if b[0] > a[0] else 0.0
            return a[1] + f * (b[1] - a[1]), a[2] + f * (b[2] - a[2])
    raise ValueError(f'no ground-truth samples around t = {t:.3f} s')


def stop_timing_info(r, t0, t_end):
    """DEC-040 (d), REQ-TA-02: INFO only, no criterion. t0 is the harness's estimate of the simulation time
    of the zero command; the stop criterion above takes the ground-truth sample nearest to it. The braking
    onset is the stamp of the first /diff_drive_controller/cmd_vel_out value below the peak (controller
    cycle 10 ms, so +/- 10 ms resolution)."""
    with r.rec.lock:
        out = [o for o in r.rec.out if t0 - 0.5 <= o[0] <= t_end]
        gt = [g for g in r.rec.gt if t0 - 0.5 <= g[0] <= t_end]
    peak = max(o[1] for o in out if o[0] <= t0)
    onset = next(o[0] for o in out if o[0] > t0 - 0.5 and o[1] < peak - 1e-3)
    rest = r.nearest(r.rec.gt, t_end)[1:3]
    d_t0 = math.dist(interp_xy(gt, t0), rest)
    d_on = math.dist(interp_xy(gt, onset), rest)
    r.info(f'stop timing: first decrease of cmd_vel_out {1000 * (onset - t0):+.1f} ms after the estimated zero-command time')
    r.info(f'stop timing: distance with interpolated ground truth {d_t0:.4f} m from the estimated zero-command time, '
           f'{d_on:.4f} m from the braking onset (expected 0.125 m from the onset)')


def mode_timeout(r):
    sim0, wall0 = r.rec.sim(), time.time()
    legs = r.profile([(3.0, 0.2, 0.0)])
    t_last = legs[0][1]
    r.wait_sim(t_last + 3.0)  # publishing stopped
    r.rtf(sim0, wall0)
    with r.rec.lock:
        out = [o for o in r.rec.out if o[0] >= t_last - 0.1]
    base = max((o for o in out if o[0] <= t_last), key=lambda o: o[0], default=None)
    dec = next((o for o in out if o[0] > t_last and base and o[1] < base[1] - 1e-3), None)
    r.check(dec is not None and dec[0] - t_last <= 0.52,
            f'timeout: cmd_vel_out starts decreasing {"never" if dec is None else f"{dec[0] - t_last:.3f} s"} after the last message <= 0.52 s')
    tr = r.at_rest_time(t_last, t_last + 3.0)
    r.check(tr is not None and tr - t_last <= 0.90, f'timeout: at rest {"never" if tr is None else f"{tr - t_last:.3f} s"} after the last message <= 0.90 s')


def mode_stale(r):
    sim0, wall0 = r.rec.sim(), time.time()
    t0 = r.rec.sim()
    r.wait_sim(t0 + 2.0, 0.2, 0.0, stamp_offset=-1.0)
    r.wait_sim(r.rec.sim() + 1.0)
    r.rtf(sim0, wall0)
    win = r.gt_between(t0, r.rec.sim())
    d = max(math.hypot(g[1] - win[0][1], g[2] - win[0][2]) for g in win)
    r.check(d < 0.005, f'stale: commands stamped 1.0 s old -> displacement {d * 1000:.3f} mm < 5 mm')


def mode_wallclock(r):
    wall = Node('m2_wallclock_publisher')  # no use_sim_time: stamps are wall-clock time
    sim0, wall0 = r.rec.sim(), time.time()
    t0 = r.rec.sim()
    r.wait_sim(t0 + 2.0, 0.2, 0.0, clock_node=wall)
    t_last = r.rec.sim()
    r.wait_sim(t_last + 3.0)
    r.rtf(sim0, wall0)
    win = r.gt_between(t0, t_last)
    moved = math.hypot(win[-1][1] - win[0][1], win[-1][2] - win[0][2])
    tr = r.at_rest_time(t_last, t_last + 3.0)
    after = math.hypot(*(a - b for a, b in zip(r.nearest(r.rec.gt, t_last + 3.0)[1:3], r.nearest(r.rec.gt, t_last)[1:3])))
    r.info(f'wallclock (characterization): displacement while publishing {moved:.4f} m; '
           f'at rest {"never" if tr is None else f"{tr - t_last:.3f} s"} after the last message; displacement in the 3 s after {after:.4f} m')
    # Formal suite 1 recorded this as a characterization (HAZARD, TS-015). Since DEC-029 the
    # command-freshness guard must reject such commands: no motion is the pass criterion.
    r.check(moved < 0.005, f'wallclock: commands stamped in wall-clock time cause no motion: {moved * 1000:.3f} mm < 5 mm (DEC-029)')
    r.check(after < 0.005, f'wallclock: no motion after the last message either: {after * 1000:.3f} mm < 5 mm')
    wall.destroy_node()


def mode_domainswitch(r):
    """Freshness expiry through a clock-domain switch (DEC-029): 0.2 m/s with simulation-time stamps for
    3.0 s, then the same command with wall-clock stamps for 3.0 s. The guard must reject the second
    stream, so the controller times out after the last valid command: DEC-027 timeout criterion."""
    wall = Node('m2_wallclock_publisher')  # no use_sim_time: wall-clock stamps
    sim0, wall0 = r.rec.sim(), time.time()
    legs = r.profile([(3.0, 0.2, 0.0)])
    t_valid = legs[0][1]
    r.wait_sim(t_valid + 3.0, 0.2, 0.0, clock_node=wall)
    r.wait_sim(r.rec.sim() + 1.0)
    r.rtf(sim0, wall0)
    sp = r.body_speed(r.samples(legs[0][0], t_valid), r.nearest(r.rec.gt, legs[0][0])[6])
    tr = r.at_rest_time(t_valid, t_valid + 4.0)
    p0, p1 = r.nearest(r.rec.gt, t_valid), r.nearest(r.rec.gt, t_valid + 4.0)
    dist = math.hypot(p1[1] - p0[1], p1[2] - p0[2])
    r.info(f'domainswitch: last valid (simulation-time) command at t={t_valid:.3f} s, speed then {sp[-1][1]:+.4f} m/s; '
           f'then wall-clock-stamped commands (stamp domain: wall time) for 3.0 s')
    r.check(tr is not None and tr - t_valid <= 0.90,
            f'domainswitch: at rest {"never" if tr is None else f"{tr - t_valid:.3f} s"} after the last valid command <= 0.90 s (DEC-027 timeout criterion)')
    r.info(f'domainswitch: distance after the last valid command {dist:.4f} m (recorded; timeout 0.5 s x 0.2 m/s + slowing 0.02 m = 0.12 m expected)')
    end = r.at_rest_time(t_valid + 3.0, t_valid + 4.0)
    r.check(end is not None, 'domainswitch: robot at rest at the end of the wall-clock stream (final stopped condition)')
    wall.destroy_node()


def mode_limits(r):
    sim0, wall0 = r.rec.sim(), time.time()
    legs = r.profile([(3.0, 1.0, 0.0), (3.0, -0.5, 0.0), (2.0, 0.0, 0.0), (2.0, 0.0, 2.0), (2.0, 0.0, 0.0)])
    r.rtf(sim0, wall0)
    t0, t1 = legs[0][0], legs[-1][1]
    with r.rec.lock:
        out = [o for o in r.rec.out if t0 <= o[0] <= t1]
    r.check(bool(out) and all(-0.25 - 1e-6 <= o[1] <= 0.5 + 1e-6 for o in out),
            f'limits: cmd_vel_out linear within [-0.25, 0.50] m/s (min {min(o[1] for o in out):+.4f}, max {max(o[1] for o in out):+.4f})')
    r.check(all(abs(o[2]) <= 1.0 + 1e-6 for o in out), f'limits: |cmd_vel_out angular| <= 1.0 rad/s (max {max(abs(o[2]) for o in out):.4f})')
    psi0 = r.nearest(r.rec.gt, t0)[6]
    sp = r.body_speed(r.samples(t0, legs[2][1]), psi0)
    acc_up, acc_dn = [], []
    for i in range(3, len(sp) - 3):  # acceleration: central difference of the speed over ~0.1 s
        a = (sp[i + 3][1] - sp[i - 3][1]) / (sp[i + 3][0] - sp[i - 3][0])
        v = sp[i][1]
        # Classify only where |v| >= 0.05 m/s: the speed and acceleration differences each span
        # 0.1 s, so within 0.1 s of a zero crossing (|v| < 0.05 m/s at 0.5 m/s^2) the windows mix
        # the slowing and speeding-up phases (preliminary run: 0.58 m/s^2 at v = -0.02 m/s).
        if abs(v) >= 0.05:
            (acc_up if v * a > 0 else acc_dn).append((abs(a), sp[i][0] - t0, v))
    up, dn = max(acc_up), max(acc_dn)
    r.check(up[0] <= 0.55, f'limits: measured acceleration while speeding up max {up[0]:.4f} m/s^2 <= 0.55 (at t+{up[1]:.3f} s, v {up[2]:+.4f} m/s)')
    r.check(dn[0] <= 1.10, f'limits: measured acceleration while slowing down max {dn[0]:.4f} m/s^2 <= 1.10 (at t+{dn[1]:.3f} s, v {dn[2]:+.4f} m/s)')
    r.check(max(s[1] for s in sp) <= 0.525 and min(s[1] for s in sp) >= -0.2625,
            f'limits: ground-truth speed range [{min(s[1] for s in sp):+.4f}, {max(s[1] for s in sp):+.4f}] m/s within limits x 1.05')
    spw = r.body_speed(r.samples(legs[3][0], legs[4][1]), psi0)
    alph = [abs((spw[i + 3][2] - spw[i - 3][2]) / (spw[i + 3][0] - spw[i - 3][0])) for i in range(3, len(spw) - 3)]
    r.check(max(abs(s[2]) for s in spw) <= 1.05, f'limits: ground-truth yaw rate max {max(abs(s[2]) for s in spw):.4f} rad/s <= 1.05')
    r.check(max(alph) <= 2.2, f'limits: measured angular acceleration max {max(alph):.4f} rad/s^2 <= 2.2')
    tl = r.tilt(t0, t1)
    r.check(tl < 1.0, f'limits: max |roll|,|pitch| {tl:.4f} deg < 1 deg')


def mode_startup(r):
    """Publish 0.2 m/s from the start, before the controllers exist."""
    wall0 = time.time()
    while time.time() - wall0 < 90:
        r.rec.send(0.2, 0.0)
        with r.rec.lock:
            first_odom = r.rec.odom[0][0] if r.rec.odom else None
            spawn = r.rec.gt[0][0] if r.rec.gt else None
        if first_odom is not None:
            break
        time.sleep(1.0 / RATE)
    if first_odom is None or spawn is None:
        print('FAIL  startup: no odometry (drive controller not active) within 90 s wall time')
        r.fails += 1
        return
    r.check(first_odom - spawn <= 10.0, f'startup: drive controller active (first odometry) {first_odom - spawn:.3f} s of sim time after spawn <= 10 s')
    pre = r.gt_between(spawn, first_odom)
    d = max(math.hypot(g[1] - pre[0][1], g[2] - pre[0][2]) for g in pre)
    r.check(d < 0.005, f'startup: displacement before activation {d * 1000:.3f} mm < 5 mm (command 0.2 m/s published throughout)')
    t = r.rec.sim()
    r.wait_sim(t + 3.0, 0.2, 0.0)
    after = r.gt_between(first_odom, r.rec.sim())
    r.info(f'startup: displacement in the 3 s after activation {math.hypot(after[-1][1] - after[0][1], after[-1][2] - after[0][2]):.4f} m (commands then apply)')


def mode_fault(r):
    t0 = r.rec.sim()
    r.wait_sim(t0 + 2.0, 0.2, 0.0)
    t_sw = r.rec.sim()
    res = subprocess.run(['ros2', 'control', 'switch_controllers', '--deactivate', 'diff_drive_controller'],
                         capture_output=True, text=True, timeout=30)
    r.info(f'switch_controllers --deactivate diff_drive_controller: exit {res.returncode}; '
           f'{(res.stdout + res.stderr).strip().splitlines()[-1:] if (res.stdout + res.stderr).strip() else ""}')
    r.wait_sim(r.rec.sim() + 3.0, 0.2, 0.0)
    g = r.samples(t_sw, r.rec.sim())
    sp = r.body_speed(g, r.nearest(r.rec.gt, t0)[6])
    w = r.wheels(r.rec.sim() - 0.5, r.rec.sim())
    end_speed = sp[-1][1] if sp else float('nan')
    r.info(f'fault (characterization): ground-truth speed at deactivation {sp[0][1]:+.4f} m/s, 3 s later {end_speed:+.4f} m/s; '
           f'last wheel velocities L {w[-1][1][1] if w else float("nan"):+.4f}, R {w[-1][2][1] if w else float("nan"):+.4f} rad/s')
    behaviour = 'stops' if abs(end_speed) < REST else ('coasts or keeps moving' if abs(end_speed) > 0.05 else 'slows')
    r.info(f'fault: behaviour after deactivation: {behaviour}')
    r.check(True, 'fault: behaviour recorded (characterization; coasting would be reported as a hazard)')


def mode_tfcheck(r):
    r.wait_sim(r.rec.sim() + 4.0, 0.1, 0.2)
    r.wait_sim(r.rec.sim() + 1.0, 0.0, 0.0)
    with r.rec.lock:
        odom, tf = list(r.rec.odom), list(r.rec.tf)
    frames = {(o[4], o[5]) for o in odom}
    r.check(frames == {('odom', 'base_footprint')}, f'odometry frame ids {sorted(frames)} == [(odom, base_footprint)]')
    by_t = {round(o[0], 6): o for o in odom}
    pairs = [(t, by_t[round(t[0], 6)]) for t in tf if round(t[0], 6) in by_t]
    dpos = max(math.hypot(t[1] - o[1], t[2] - o[2]) for t, o in pairs) if pairs else float('nan')
    dyaw = max(abs(math.degrees(wrap(t[3] - o[3]))) for t, o in pairs) if pairs else float('nan')
    r.check(bool(pairs) and dpos <= 0.001 and dyaw <= 0.1,
            f'TF odom->base_footprint equals odometry at the same stamp: {len(pairs)} pairs, max {dpos * 1000:.6f} mm, {dyaw:.6f} deg')


def mode_rest(r):
    """TEST-M1-07 method with active controllers and zero command; OPEN-07 thresholds (DEC-019, provisional)."""
    sim0, wall0 = r.rec.sim(), time.time()
    tA = r.rec.sim() + 1.0
    r.wait_sim(tA + 30.0 + 0.5, 0.0, 0.0)
    r.rtf(sim0, wall0)
    a = next(g for g in r.gt_between(tA, tA + 1.0))
    b = next(g for g in r.gt_between(a[0] + 30.0, a[0] + 31.0))
    win = r.gt_between(a[0], b[0])
    print(f'INFO  A: t={a[0]:.3f} s pos=({a[1]:.9f}, {a[2]:.9f}, {a[3]:.9f}) roll={math.degrees(a[4]):.6f} pitch={math.degrees(a[5]):.6f} deg')
    print(f'INFO  B: t={b[0]:.3f} s pos=({b[1]:.9f}, {b[2]:.9f}, {b[3]:.9f}) roll={math.degrees(b[4]):.6f} pitch={math.degrees(b[5]):.6f} deg')
    dz = b[3] - a[3]; drift = math.hypot(b[1] - a[1], b[2] - a[2])
    r.info(f'spread A..B: z {1000 * (max(g[3] for g in win) - min(g[3] for g in win)):.6f} mm, '
           f'roll {math.degrees(max(g[4] for g in win) - min(g[4] for g in win)):.6f} deg, '
           f'pitch {math.degrees(max(g[5] for g in win) - min(g[5] for g in win)):.6f} deg')
    r.check(abs(dz) < 0.002, f'rest: |dz| = {abs(dz) * 1000:.6f} mm < 2 mm')
    r.check(max(abs(a[4]), abs(b[4])) < math.radians(0.5), f'rest: |roll| A {abs(math.degrees(a[4])):.6f}, B {abs(math.degrees(b[4])):.6f} deg < 0.5 deg')
    r.check(max(abs(a[5]), abs(b[5])) < math.radians(0.5), f'rest: |pitch| A {abs(math.degrees(a[5])):.6f}, B {abs(math.degrees(b[5])):.6f} deg < 0.5 deg')
    r.check(drift < 0.005, f'rest: horizontal drift = {drift * 1000:.6f} mm < 5 mm')


MODES = {'linear': mode_linear, 'rotate': mode_rotate, 'stop': mode_stop, 'timeout': mode_timeout,
         'stale': mode_stale, 'wallclock': mode_wallclock, 'domainswitch': mode_domainswitch, 'limits': mode_limits, 'startup': mode_startup,
         'fault': mode_fault, 'tfcheck': mode_tfcheck, 'rest': mode_rest}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in MODES:
        print(__doc__)
        return 2
    rclpy.init()
    rec = Recorder()
    ex = SingleThreadedExecutor()  # MultiThreadedExecutor starved the gz-transport callbacks (TS-013)
    ex.add_node(rec)
    spin = Spinner(ex).start()  # TS-030 fix (REQ-TA-01)
    r = Run(rec)
    print(f'# TEST-M2 harness mode={mode}, wall {time.strftime("%F %T %Z")}')
    try:
        if mode == 'startup' or r.ready():
            MODES[mode](r)
    finally:
        spin.stop(rec)
    with rec.lock:
        print(f'# samples: ground truth {len(rec.gt)}, odometry {len(rec.odom)}, joint_states {len(rec.js)}, '
              f'cmd_vel_out {len(rec.out)}, tf {len(rec.tf)}')
    if r.invalid:
        print('# result: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"ALL CRITERIA PASSED" if r.fails == 0 else f"{r.fails} CRITERION/CRITERIA FAILED"}')
    return 1 if r.fails else 0


if __name__ == '__main__':
    code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    # os._exit: the gz-transport node aborts during interpreter teardown ("terminate called
    # without an active exception"), which would replace this exit code with a core-dump code.
    os._exit(code)
