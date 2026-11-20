#!/usr/bin/env python3
"""TEST-M6-07: fusion interface check (REQ-M6-09; docs/testing/test_plan.md §11; M6 Task D; DEC-057).

Usage (same ROS_DOMAIN_ID as the simulation; the robot stands still):
    python3 TEST-M6-07_fusion_check.py pre  <state.json>   simulation running with controllers_ekf.yaml (or a test
                                                            copy of it), localization.launch.py NOT yet started
    python3 TEST-M6-07_fusion_check.py main <state.json>   after localization.launch.py ekf:=true is started
Run by docs/evidence/M6/TEST-M6_procedure.sh with FUSION=1. Exit 0 = all PASS, 1 = a FAIL, 2 = invalid run (no clock).
The accuracy part of TEST-M6-07 (raw vs fused odometry, localization bounds) is judged offline by
TEST-M6_pose_check.py --fusion on the route recording.

pre (5 s of simulation time):
  1. diff_drive_controller: enable_odom_tf false (the controllers_ekf.yaml line).
  2. No odom -> base_footprint on /tf: the controller no longer publishes it.
  3. /diff_drive_controller/odom is still published (the EKF's odometry input), child frame base_footprint, yaw-rate
     variance 4.0e-4 (DEC-042).
  4. /imu (the EKF's yaw-rate input): frame imu_link; angular-velocity variances 1.0e-6 on the diagonal (DEC-032),
     to 1e-6 relative (Gazebo carries the value as float32: 9.99999997e-07 on the wire; Task D gate).
     This is the M6 plan §3.4 assumption: robot_localization takes the measurement weight from the message.
  The /tf publisher nodes are saved to <state.json> for the main step.
main (5 s of simulation time after the EKF publishes):
  5. ekf_filter_node parameters as config/ekf.yaml: use_sim_time, two_d_mode, publish_tf, world_frame odom,
     base_link_frame base_footprint, odom0 /diff_drive_controller/odom, imu0 /imu. The query is repeated up to
     3 times while it gets no reply (TS-047: a just-started ekf_node once dropped its get_parameters response,
     "failed to send response ... (timeout)"); a reply with wrong values fails at once.
  6. Exactly one writer of odom -> base_footprint (method of TEST-M5-02 / TEST-M6-02: rclpy gives the publication
     sequence number, which every DDS writer counts on its own from 1; two writers would repeat numbers).
  7. That writer is the EKF: ekf_filter_node is the only node added to the /tf publishers since the pre step, it is the
     only publisher of /odometry/filtered, and every odom -> base_footprint stamp equals a /odometry/filtered stamp
     (robot_localization stamps both outputs from the same filter state).
  8. Stamps are simulation time: every odom -> base_footprint stamp lies within the recording window, widened by 1 s
     on each side (the first message can predate the window start by one period; Task D gate).
  INFO: message counts and rates.
"""
import importlib.util
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('ic', os.path.join(HERE, 'TEST-M6-02_interface_check.py'))
IC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(IC)   # Check, wait, wait_sim, params, tf_nodes; M2 helpers (Spinner, TS-030)
M2, rclpy = IC.M2, IC.rclpy

from nav_msgs.msg import Odometry  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from sensor_msgs.msg import Imu  # noqa: E402
from tf2_msgs.msg import TFMessage  # noqa: E402

EKF = 'ekf_filter_node'
EKF_PARAMS = {'use_sim_time': True, 'two_d_mode': True, 'publish_tf': True, 'world_frame': 'odom',
              'base_link_frame': 'base_footprint', 'odom0': '/diff_drive_controller/odom', 'imu0': '/imu'}
ODOM_WZ_VAR, GYRO_VAR = 4.0e-4, 1.0e-6


class Rec(Node):
    def __init__(self):
        super().__init__('test_m6_07', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.lock = threading.Lock()
        self.o2b = []       # (publication_sequence_number, stamp_ns, transforms in the message)
        self.filtered = []  # stamps (ns) of /odometry/filtered
        self.raw = []       # /diff_drive_controller/odom messages
        self.imu = []       # /imu messages
        self.create_subscription(TFMessage, '/tf', self.on_tf, 200)
        self.create_subscription(Odometry, '/odometry/filtered', self.on_filtered, 200)
        self.create_subscription(Odometry, '/diff_drive_controller/odom', self.on_raw, 200)
        self.create_subscription(Imu, '/imu', self.on_imu, 200)

    def on_tf(self, msg, info):
        for t in msg.transforms:
            if t.header.frame_id.lstrip('/') == 'odom' and t.child_frame_id.lstrip('/') == 'base_footprint':
                with self.lock:
                    self.o2b.append((info['publication_sequence_number'],
                                     t.header.stamp.sec * 10**9 + t.header.stamp.nanosec, len(msg.transforms)))

    def on_filtered(self, msg):
        with self.lock:
            self.filtered.append(msg.header.stamp.sec * 10**9 + msg.header.stamp.nanosec)

    def on_raw(self, msg):
        with self.lock:
            self.raw.append(msg)

    def on_imu(self, msg):
        with self.lock:
            self.imu.append(msg)

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def reset(self):
        with self.lock:
            self.o2b, self.filtered, self.raw, self.imu = [], [], [], []


def pre(rec, ck, state_path):
    p = IC.params(rec, 'diff_drive_controller', ['enable_odom_tf'])
    ck(p.get('enable_odom_tf') is False, f'diff_drive_controller enable_odom_tf = {p.get("enable_odom_tf")} (false)')
    rec.reset()
    IC.wait_sim(rec, 5.0)
    with rec.lock:
        o2b, raw, imu = list(rec.o2b), list(rec.raw), list(rec.imu)
    ck(not o2b, f'no odom -> base_footprint on /tf without the EKF ({len(o2b)} in 5 s of simulation time)')
    ck(len(raw) > 0 and raw[-1].child_frame_id == 'base_footprint'
       and abs(raw[-1].twist.covariance[35] - ODOM_WZ_VAR) < 1e-12,
       f'/diff_drive_controller/odom published ({len(raw)} messages), child frame '
       f'{raw[-1].child_frame_id if raw else None}, yaw-rate variance '
       f'{raw[-1].twist.covariance[35] if raw else None} ({ODOM_WZ_VAR}, DEC-042)')
    cov = list(imu[-1].angular_velocity_covariance) if imu else []
    ck(len(imu) > 0 and imu[-1].header.frame_id == 'imu_link'
       and all(abs(cov[i] - GYRO_VAR) <= 1e-6 * GYRO_VAR for i in (0, 4, 8)),
       f'/imu published ({len(imu)} messages), frame {imu[-1].header.frame_id if imu else None}, angular-velocity '
       f'variances {[cov[i] for i in (0, 4, 8)] if cov else None} ({GYRO_VAR}, DEC-032; M6 plan §3.4 assumption)')
    nodes = IC.tf_nodes(rec)
    ck.info(f'/tf publisher nodes without the EKF: {nodes}')
    json.dump({'tf_nodes': nodes}, open(state_path, 'w'))


def main_check(rec, ck, state_path):
    before = json.load(open(state_path))['tf_nodes']
    ok = IC.wait(lambda: EKF in IC.tf_nodes(rec), 60)
    ck(ok, f'{EKF} publishes /tf within 60 s')
    for attempt in range(1, 4):
        p = IC.params(rec, EKF, list(EKF_PARAMS))
        if p:
            break
        ck.info(f'{EKF} get_parameters query {attempt} of 3: no reply (TS-047)')
    ck(p == EKF_PARAMS, f'{EKF} parameters {p} (expected {EKF_PARAMS})')
    IC.wait(lambda: len(rec.o2b) > 0, 30)
    rec.reset()
    t0 = rec.now_s()
    IC.wait_sim(rec, 5.0)
    t1 = rec.now_s()
    with rec.lock:
        o2b, filtered = list(rec.o2b), set(rec.filtered)
    seqs = [s for s, _, _ in o2b]
    ck(len(o2b) > 0, f'odom -> base_footprint on /tf with the EKF: {len(o2b)} messages in {t1 - t0:.1f} s '
                     f'of simulation time ({len(o2b) / max(t1 - t0, 1e-9):.1f} Hz)')
    ck(len(seqs) == len(set(seqs)), f'publication sequence numbers of odom -> base_footprint all distinct '
                                   f'({len(set(seqs))} distinct of {len(seqs)}): one writer')
    added = sorted(set(IC.tf_nodes(rec)) - set(before))
    ck(EKF in added, f'/tf publisher nodes added since the pre step: {added} (contains {EKF}; amcl is expected too)')
    pubs = sorted(i.node_name for i in rec.get_publishers_info_by_topic('/odometry/filtered'))
    ck(pubs == [EKF], f'/odometry/filtered publishers {pubs} ([{EKF}])')
    unmatched = [s for _, s, _ in o2b if s not in filtered]
    ck(bool(o2b) and not unmatched, f'every odom -> base_footprint stamp equals a /odometry/filtered stamp '
                              f'({len(o2b) - len(unmatched)} of {len(o2b)})')
    st = [s * 1e-9 for _, s, _ in o2b]
    ck(bool(st) and t0 - 1.0 <= min(st) and max(st) <= t1 + 1.0,
       f'odom -> base_footprint stamps are simulation time: {min(st, default=float("nan")):.2f} to '
       f'{max(st, default=float("nan")):.2f} s within the window {t0:.2f} to {t1:.2f} s (+/- 1 s)')
    ck.info(f'transforms per odom -> base_footprint message: {sorted({n for _, _, n in o2b})}; /odometry/filtered '
            f'messages {len(filtered)}')


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in ('pre', 'main') or len(sys.argv) < 3:
        print(__doc__)
        return 2
    rclpy.init()
    rec = Rec()
    ex = M2.SingleThreadedExecutor()
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()
    ck = IC.Check()
    print(f'# TEST-M6-07 fusion check mode={mode}, wall {time.strftime("%F %T %Z")}', flush=True)
    try:
        if not IC.wait(lambda: rec.now_s() > 0, 60):
            print('# no /clock within 60 s: INVALID RUN')
            return 2
        (pre if mode == 'pre' else main_check)(rec, ck, sys.argv[2])
    finally:
        spin.stop(rec)
    print(f'# result: {"FAIL" if ck.fail else "PASS"}')
    return 1 if ck.fail else 0


if __name__ == '__main__':
    sys.exit(main())
