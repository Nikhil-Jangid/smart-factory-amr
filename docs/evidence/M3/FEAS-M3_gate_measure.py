"""FEAS-M3 gate measurement (throwaway). Run with plain python3 (TS-011).
Settle 2.0 s of simulation time after the first /scan, then record a 10.0 s window of /scan, /imu,
/joint_states; report frames, rates (from header stamps), LaserScan fields, target ranges, IMU stats, RTF."""
import math, statistics as st, sys, time
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import Imu, JointState, LaserScan

SETTLE, WINDOW = 2.0, 10.0
LASER_X = 0.070  # laser_frame x in the world (robot at the origin, yaw 0)


def t(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


class Gate(Node):
    def __init__(self):
        super().__init__('feas_m3_gate', parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        self.clock = None; self.t0 = None; self.max_lag = 0.0
        self.scans, self.imus, self.js = [], [], []
        self.wall = {}
        self.create_subscription(Clock, '/clock', self.on_clock, 10)
        self.create_subscription(LaserScan, '/scan', self.on_scan, qos_profile_sensor_data)
        self.create_subscription(Imu, '/imu', self.on_imu, qos_profile_sensor_data)
        self.create_subscription(JointState, '/joint_states', self.on_js, 50)

    def on_clock(self, m):
        self.clock = t(m.clock)

    def in_window(self, ts):
        if self.t0 is None:
            return False
        return self.t0 + SETTLE <= ts < self.t0 + SETTLE + WINDOW

    def lag(self, ts):
        if self.clock is not None:
            self.max_lag = max(self.max_lag, abs(self.clock - ts))

    def on_scan(self, m):
        ts = t(m.header.stamp)
        if self.t0 is None:
            self.t0 = ts
        if self.in_window(ts):
            self.lag(ts); self.scans.append(m)
            self.wall.setdefault('start', (time.monotonic(), ts)); self.wall['end'] = (time.monotonic(), ts)

    def on_imu(self, m):
        ts = t(m.header.stamp)
        if self.in_window(ts):
            self.lag(ts); self.imus.append(m)

    def on_js(self, m):
        ts = t(m.header.stamp)
        if self.in_window(ts):
            self.js.append(m)

    def done(self):
        return self.t0 is not None and self.clock is not None and self.clock > self.t0 + SETTLE + WINDOW + 0.2


def rate(msgs):
    ts = [t(m.header.stamp) for m in msgs]
    inc = all(b > a for a, b in zip(ts, ts[1:]))
    return (len(ts) - 1) / (ts[-1] - ts[0]) if len(ts) > 1 else float('nan'), inc


fails = 0
def rep(ok, msg, critical=True):
    global fails
    if critical and not ok:
        fails += 1
    print(('PASS  ' if ok else ('FAIL  ' if critical else 'NOTE  ')) + msg)


def main():
    rclpy.init(); n = Gate(); deadline = time.monotonic() + 240
    while rclpy.ok() and not n.done() and time.monotonic() < deadline:
        rclpy.spin_once(n, timeout_sec=0.05)
    print(f'# window: settle {SETTLE} s after first /scan stamp, then {WINDOW} s of simulation time')
    rep(len(n.scans) > 0, f'/scan received in window: {len(n.scans)} messages')
    rep(len(n.imus) > 0, f'/imu received in window: {len(n.imus)} messages')
    rep(len(n.js) > 0, f'/joint_states received in window: {len(n.js)} messages')
    if not (n.scans and n.imus and n.js):
        print('== GATE INCOMPLETE: missing data'); sys.exit(2)
    (ws, ss), (we, se) = n.wall['start'], n.wall['end']
    rtf = (se - ss) / (we - ws) if we > ws else float('nan')
    rep(rtf >= 0.5, f'real-time factor over the window: {rtf:.3f} (>= 0.5)')
    print(f'# max |stamp - latest /clock| at receipt: {n.max_lag:.4f} s')
    # ---- G2 LiDAR
    s0 = n.scans[0]
    rep({m.header.frame_id for m in n.scans} == {'laser_frame'}, f'/scan frame_id: {sorted({m.header.frame_id for m in n.scans})}')
    r, inc = rate(n.scans); rep(abs(r - 10.0) <= 0.2 and inc, f'/scan rate {r:.4f} Hz (10 Hz +-2 %), stamps increasing: {inc}')
    print(f'# LaserScan fields: angle_min {s0.angle_min:.9f} angle_max {s0.angle_max:.9f} angle_increment {s0.angle_increment:.9f} '
          f'({math.degrees(s0.angle_increment):.6f} deg) range_min {s0.range_min} range_max {s0.range_max} len {len(s0.ranges)}')
    rep(len(s0.ranges) == 360 and abs(s0.angle_increment - math.radians(1.0)) < 1e-6 and abs(s0.angle_min + math.pi) < 1e-6,
        'LaserScan: 360 samples at exactly 1.0 deg from -pi')
    rep(abs(s0.range_min - 0.12) < 1e-6 and abs(s0.range_max - 12.0) < 1e-6, 'LaserScan range_min 0.12, range_max 12.0')
    ang = lambda i: s0.angle_min + i * s0.angle_increment
    targets = {  # name: (beam predicate, expected range function)
        'front 0 deg (face x=2.40)': (lambda a: abs(a) <= math.radians(10), lambda a: (2.40 - LASER_X) / math.cos(a)),
        'rear 180 deg (face x=-2.90)': (lambda a: abs(abs(a) - math.pi) <= math.radians(8), lambda a: (2.90 + LASER_X) / abs(math.cos(a))),
        'right -90 deg (face y=-1.90)': (lambda a: abs(a + math.pi / 2) <= math.radians(12), lambda a: 1.90 / abs(math.sin(a))),
    }
    for name, (sel, f) in targets.items():
        errs = [m.ranges[i] - f(ang(i)) for m in n.scans for i in range(len(m.ranges)) if sel(ang(i)) and math.isfinite(m.ranges[i])]
        if len(errs) < 2:
            rep(False, f'LiDAR target {name}: only {len(errs)} finite returns'); continue
        mu, sd = st.fmean(errs), st.stdev(errs)
        rep(abs(mu) <= 0.010, f'LiDAR target {name}: n={len(errs)} mean error {mu*1000:+.2f} mm (<= 10 mm), sd {sd*1000:.2f} mm (configured 10 mm)')
    low = [m.ranges[i] for m in n.scans for i in range(len(m.ranges)) if abs(ang(i) - math.pi / 2) <= math.radians(12) and math.isfinite(m.ranges[i]) and m.ranges[i] < 12.0]
    rep(len(low) == 0, f'low target (0.15 m high, +90 deg) below the 0.230 m scan plane: {len(low)} finite returns (expected 0, blind zone)')
    near = sum(1 for m in n.scans for x in m.ranges if math.isfinite(x) and x < 0.45)
    rep(near == 0, f'returns closer than 0.45 m (self-returns): {near}')
    # ---- G3 IMU
    rep({m.header.frame_id for m in n.imus} == {'imu_link'}, f'/imu frame_id: {sorted({m.header.frame_id for m in n.imus})}')
    r, inc = rate(n.imus); rep(abs(r - 100.0) <= 2.0 and inc, f'/imu rate {r:.4f} Hz (100 Hz +-2 %), stamps increasing: {inc}')
    for lab, get, sd_cfg in (('accel', lambda m: m.linear_acceleration, 0.01), ('gyro', lambda m: m.angular_velocity, 0.001)):
        for ax in 'xyz':
            v = [getattr(get(m), ax) for m in n.imus]
            print(f'# IMU {lab} {ax}: n={len(v)} mean {st.fmean(v):+.6f} sd {st.stdev(v):.6f} (configured sd {sd_cfg})')
    az = st.fmean(m.linear_acceleration.z for m in n.imus)
    rep(az > 0 and abs(az - 9.8) <= 0.05, f'IMU gravity: mean accel z {az:+.5f} m/s^2 (+g up, specific force; 9.8 +- 0.05)')
    q = n.imus[-1].orientation
    print(f'# IMU orientation (last): x {q.x:.6f} y {q.y:.6f} z {q.z:.6f} w {q.w:.6f}')
    # ---- G4 joint_states
    r, inc = rate(n.js)
    print(f'# /joint_states names: {list(n.js[0].name)}')
    rep(math.isfinite(r) and inc, f'/joint_states measured rate {r:.4f} Hz (stamps increasing: {inc}) -- recorded for DEC-036 D2')
    print('== GATE CRITICAL CHECKS PASSED' if fails == 0 else f'== {fails} CRITICAL CHECK(S) FAILED')
    n.destroy_node(); rclpy.shutdown(); sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
