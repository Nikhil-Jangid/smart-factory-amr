"""TEST-M3-04 topics, rates, frames and stamps (REQ-M3-04 to -06; DEC-036 D1-D4; sensors.md §7.2, §7.3).

Run with plain python3 (rclpy; TS-011) while sim.launch.py runs with sensors:=true world:=sensor_test.sdf
and both controllers are active. Window (sensors.md §7.2): settle 2.0 s of simulation time after the first
/scan message, then 10.0 s of simulation time; every message stamped inside the window is evaluated.
  D1  /scan sensor_msgs/msg/LaserScan in laser_frame; /imu sensor_msgs/msg/Imu in imu_link (every message);
      /joint_states sensor_msgs/msg/JointState with both wheel positions (REQ-M3-06).
  D2  rate (N - 1) / (t_last - t_first) from header stamps: /scan 10 Hz, /imu 100 Hz, /joint_states 100 Hz,
      each +-2 %.
  D3  stamps strictly increasing; |stamp - latest /clock at receipt| <= 0.1 s for every message.
      Added for re-test 1 (DEC-038, accepted 2026-11-03), before that run: every /imu stamp is a multiple of 10 ms
      (the block-mean output is stamped with the newest raw sample of an aligned block).
  D4  LaserScan angle_min, angle_max, angle_increment, range_min, range_max = DEC-031 values to 1e-6;
      len(ranges) == 360 (every message).
Validity (sensors.md §7.5): RTF = simulation time / wall time over the window; RTF < 0.5 -> exit 2 (invalid,
repeat). Exit 0 only if every check passes; 1 if any check fails.
"""
import math
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import Imu, JointState, LaserScan

SETTLE, WINDOW, TIMEOUT_WALL = 2.0, 10.0, 90.0
STAMP_TOL = 0.1
D4 = {  # DEC-031 (sensors.md §6.1: max_angle = pi - 2 pi / 360 for exact 1 degree steps)
    'angle_min': -math.pi,
    'angle_max': math.pi - 2 * math.pi / 360,
    'angle_increment': math.pi / 180,
    'range_min': 0.12,
    'range_max': 12.0,
}
TYPES = {'/scan': 'sensor_msgs/msg/LaserScan', '/imu': 'sensor_msgs/msg/Imu',
         '/joint_states': 'sensor_msgs/msg/JointState'}
WHEELS = {'left_wheel_joint', 'right_wheel_joint'}
failures = 0


def report(ok, msg):
    global failures
    failures += 0 if ok else 1
    print(('PASS  ' if ok else 'FAIL  ') + msg)


def sec(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


class Recorder(Node):
    def __init__(self):
        super().__init__('test_m3_04_topics_check',
                         parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=200, reliability=ReliabilityPolicy.RELIABLE)
        self.clock = None
        self.t0 = None
        self.data = {'/scan': [], '/imu': [], '/joint_states': []}  # (stamp, latest clock at receipt, msg)
        self.wall_start = self.wall_end = None
        self.create_subscription(Clock, '/clock', self.on_clock, 10)
        self.create_subscription(LaserScan, '/scan', lambda m: self.on_msg('/scan', m), qos)
        self.create_subscription(Imu, '/imu', lambda m: self.on_msg('/imu', m), qos)
        self.create_subscription(JointState, '/joint_states', lambda m: self.on_msg('/joint_states', m), qos)

    def on_clock(self, m):
        self.clock = sec(m.clock)
        if self.t0 is not None:
            if self.wall_start is None and self.clock >= self.t0 + SETTLE:
                self.wall_start = (time.monotonic(), self.clock)
            if self.wall_end is None and self.clock >= self.t0 + SETTLE + WINDOW:
                self.wall_end = (time.monotonic(), self.clock)

    def on_msg(self, topic, m):
        ts = sec(m.header.stamp)
        if topic == '/scan' and self.t0 is None:
            self.t0 = ts
        if self.t0 is not None and self.t0 + SETTLE <= ts < self.t0 + SETTLE + WINDOW:
            self.data[topic].append((ts, self.clock, m))

    def done(self):
        return self.wall_end is not None and self.clock > self.t0 + SETTLE + WINDOW + 0.2


def rate(samples):
    ts = [s for s, _, _ in samples]
    if len(ts) < 2 or ts[-1] <= ts[0]:
        return float('nan'), False
    return (len(ts) - 1) / (ts[-1] - ts[0]), all(b > a for a, b in zip(ts, ts[1:]))


def main():
    rclpy.init()
    n = Recorder()
    start = time.monotonic()
    while time.monotonic() - start < TIMEOUT_WALL and not (n.t0 is not None and n.done()):
        rclpy.spin_once(n, timeout_sec=0.05)
    types = dict(n.get_topic_names_and_types())
    n.destroy_node()
    rclpy.shutdown()
    if n.t0 is None or not n.done():
        print(f'FAIL  window not completed within {TIMEOUT_WALL} s wall time (first /scan stamp: {n.t0})')
        return 1

    rtf = (n.wall_end[1] - n.wall_start[1]) / (n.wall_end[0] - n.wall_start[0])
    print(f'# window: {SETTLE} s after the first /scan stamp ({n.t0:.3f} s), then {WINDOW} s of simulation time')
    print(f'# RTF over the window: {rtf:.3f}')
    print('# messages in window: ' + ', '.join(f'{k} {len(v)}' for k, v in n.data.items()))

    print('== D1 topic, type, frame_id')
    for topic, typ in TYPES.items():
        got = types.get(topic, [])
        report(got == [typ], f'{topic} type {got} == [{typ}]')
    for topic, frame in (('/scan', 'laser_frame'), ('/imu', 'imu_link')):
        frames = sorted({m.header.frame_id for _, _, m in n.data[topic]})
        report(frames == [frame], f'{topic} frame_id of every message {frames} == [{frame}]')
    js = n.data['/joint_states']
    ok = bool(js) and all(WHEELS <= set(m.name) and all(math.isfinite(p) for p in m.position) for _, _, m in js)
    report(ok, f'/joint_states: every message has {sorted(WHEELS)} with finite positions '
               f'(names {list(js[-1][2].name) if js else None})')

    print('== D2 rate from header stamps (nominal +-2 %); D3 stamps increasing')
    for topic, nominal in (('/scan', 10.0), ('/imu', 100.0), ('/joint_states', 100.0)):
        r, inc = rate(n.data[topic])
        report(abs(r - nominal) <= 0.02 * nominal, f'{topic} rate {r:.4f} Hz == {nominal:g} Hz +-2 % '
                                                   f'(n = {len(n.data[topic])})')
        report(inc, f'{topic} stamps strictly increasing')
    imu_stamps = [m.header.stamp for _, _, m in n.data['/imu']]
    off = [f'{st.sec}.{st.nanosec:09d}' for st in imu_stamps if st.nanosec % 10_000_000]
    report(bool(imu_stamps) and not off, f'/imu stamps on the 10 ms grid: {len(imu_stamps) - len(off)} of '
                                         f'{len(imu_stamps)} (DEC-038){"; first off-grid " + off[0] if off else ""}')

    print(f'== D3 |stamp - latest /clock at receipt| <= {STAMP_TOL} s')
    for topic, samples in n.data.items():
        signed = sorted((c - s, s) for s, c, _ in samples if c is not None)  # (clock - stamp, stamp)
        worst = max((abs(d), s) for d, s in signed) if signed else (float('nan'), None)
        report(bool(samples) and len(signed) == len(samples) and worst[0] <= STAMP_TOL,
               f'{topic} max |stamp - clock| {worst[0]:.4f} s over {len(signed)} messages (worst at stamp {worst[1]})')
        if signed:  # diagnostics only: positive = message received after its stamp in simulation time
            d = [x for x, _ in signed]
            print(f'      clock - stamp: min {d[0]:+.4f} p50 {d[len(d) // 2]:+.4f} p95 {d[int(0.95 * (len(d) - 1))]:+.4f} '
                  f'max {d[-1]:+.4f} s; messages over {STAMP_TOL} s: {sum(abs(x) > STAMP_TOL for x in d)}')

    print('== D4 LaserScan fields == DEC-031 (1e-6); 360 ranges')
    scans = [m for _, _, m in n.data['/scan']]
    for field, value in D4.items():
        got = sorted({getattr(m, field) for m in scans})
        report(bool(got) and all(abs(g - value) <= 1e-6 for g in got),
               f'{field} {[f"{g:.9f}" for g in got]} == {value:.9f}')
    counts = sorted({len(m.ranges) for m in scans})
    report(counts == [360], f'len(ranges) {counts} == [360]')

    if rtf < 0.5:
        print(f'# INVALID run: RTF {rtf:.3f} < 0.5 (sensors.md §7.5); repeat')
        return 2
    print('== ALL CHECKS PASSED' if failures == 0 else f'== {failures} CHECK(S) FAILED')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
