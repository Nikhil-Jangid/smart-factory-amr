#!/usr/bin/env python3
"""TEST-M3-11: M2 motion regression with the sensors on (REQ-M3-13; docs/testing/test_plan.md §7.2).

Usage (repository root, ROS and amr_ws sourced; plain python3, TS-011): python3 TEST-M3-11_m2_regression.py <mode>
  <mode>: linear (TEST-M2-05), rotate (TEST-M2-06), stop or timeout (TEST-M2-07).
Launch under test (TEST-M3-11_procedure.sh):
  ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0
Why this world: the stock empty.sdf loads no Sensors and no IMU system, so "sensors on" there would publish no
/scan or /imu and render nothing. sensor_test.sdf loads both; the spawn (0, -20) m is the Task D point whose
clearance is checked statically (TEST-M3-D_clearance_check.py).

What is reused unchanged:
  - the M2 harness TEST-M2_motion_measure.py: its Run class, its four mode functions and their DEC-027 criteria;
  - the Task D Recorder (TEST-M3-D_imu_encoder_measure.py), which adds the ground truth of this world,
    /world/sensor_test/pose/info, to the M2 recorder (whose /world/empty subscription then stays silent).
This file adds only: the sensor-liveness INFO (the sensors really ran during the motion) and the ground-truth
excursion. Since DEC-040 (REQ-TA-01) the spin thread is the shared M2.Spinner (teardown-safe; it prints the
thread-end state as "# TS-030 check: ..."). The first TEST-M3-11 runs used a threading.excepthook capture instead.
Exit 0 = all criteria passed, 1 = a criterion failed, 2 = invalid run (e.g. RTF < 0.5, missing data; repeated).
"""
import importlib.util
import os
import statistics
import sys
import time

from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('test_m3_d', os.path.join(HERE, 'TEST-M3-D_imu_encoder_measure.py'))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
M2 = D.M2
MODES = ('linear', 'rotate', 'stop', 'timeout')


class Recorder(D.Recorder):
    """Task D recorder (M2 data + /imu + sensor_test ground truth) plus /scan stamps."""

    def __init__(self):
        super().__init__()
        self.scan = []
        qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=50, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.create_subscription(LaserScan, '/scan', self.on_scan, qos)

    def on_scan(self, m):
        with self.lock:
            self.scan.append(m.header.stamp.sec + m.header.stamp.nanosec * 1e-9)


def sensor_liveness(r, t0, t1):
    """INFO: /scan and /imu were published at their rates during the motion (sensors really on)."""
    with r.rec.lock:
        scan = [t for t in r.rec.scan if t0 <= t <= t1]
        imu = [s[0] for s in r.rec.imu if t0 <= s[0] <= t1]
    span = t1 - t0
    for name, st, nominal in (('/scan', scan, 10.0), ('/imu', imu, 100.0)):
        rate = (len(st) - 1) / (st[-1] - st[0]) if len(st) > 1 else 0.0
        gap = max((b - a for a, b in zip(st, st[1:])), default=float('nan'))
        r.info(f'{name} during the profile: {len(st)} messages over {span:.2f} s of simulation time, '
               f'{rate:.2f} Hz (nominal {nominal:g}), largest gap {gap * 1000:.1f} ms')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in MODES:
        print(__doc__)
        return 2
    M2.rclpy.init()
    rec = Recorder()
    ex = M2.SingleThreadedExecutor()  # as M2 (TS-013)
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()  # TS-030 fix (REQ-TA-01); replaces the TS-030 capture of the first runs
    r = M2.Run(rec)
    print(f'# TEST-M3-11 harness mode={mode} (M2 mode function unchanged), wall {time.strftime("%F %T %Z")}, '
          f'ground truth {D.WORLD_TOPIC}, sensors on')
    try:
        if r.ready():
            t0 = rec.sim()
            M2.MODES[mode](r)
            t1 = rec.sim()
            sensor_liveness(r, t0, t1)
            D.excursion(r, t0, t1)
    except (StopIteration, IndexError, ZeroDivisionError, statistics.StatisticsError, ValueError) as exc:
        print(f'INVALID  missing data for an evaluation ({type(exc).__name__}: {exc})')
        r.invalid = True
    finally:
        spin.stop(rec)
    with rec.lock:
        print(f'# samples: ground truth {len(rec.gt)}, odometry {len(rec.odom)}, joint_states {len(rec.js)}, '
              f'imu {len(rec.imu)}, scan {len(rec.scan)}')
    if r.invalid:
        print('# result: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"ALL CRITERIA PASSED" if r.fails == 0 else f"{r.fails} CRITERION/CRITERIA FAILED"}')
    return 1 if r.fails else 0


if __name__ == '__main__':
    code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    # os._exit, as M2: the gz-transport node aborts during normal interpreter teardown.
    os._exit(code)
