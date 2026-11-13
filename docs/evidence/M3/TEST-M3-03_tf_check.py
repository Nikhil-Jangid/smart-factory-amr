"""TEST-M3-03 TF check (REQ-M3-03; DEC-036 D5).

Run while robot_state_publisher publishes the sensors-on model and joint_state_publisher publishes the
wheel joints. Looks up the transforms at full floating-point precision (tf2_echo prints 3 decimals only).
  D5: lidar_mount_link -> laser_frame = (0, 0, 0.030) m (DEC-030) and base_link -> imu_link = (0, 0, 0)
      (DEC-032), identity rotation, each component to 1e-6 m / 1e-6 (quaternion).
  Derived (consistency): base_footprint -> laser_frame = (0.070, 0, 0.230) m (scan plane, CALC-M3-01) and
      base_footprint -> imu_link = (0, 0, 0.075) m.
  Single tree: the frame set is the M1 tree plus laser_frame and imu_link, every frame except the root has
      exactly one parent, and the root is base_footprint.
Exit 0 only if every check passes.
"""
import sys
import time

import rclpy
import yaml
from rclpy.node import Node
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener

TOL = 1e-6
EXPECTED = {
    ('lidar_mount_link', 'laser_frame'): (0.0, 0.0, 0.030),   # D5, DEC-030
    ('base_link', 'imu_link'): (0.0, 0.0, 0.0),               # D5, DEC-032
    ('base_footprint', 'laser_frame'): (0.070, 0.0, 0.230),   # derived: scan plane 0.230 m
    ('base_footprint', 'imu_link'): (0.0, 0.0, 0.075),        # derived: axle height
}
FRAMES = {'base_footprint', 'base_link', 'left_wheel_link', 'right_wheel_link', 'caster_link',
          'lidar_mount_link', 'laser_frame', 'imu_link'}
failures = 0


def report(ok, msg):
    global failures
    failures += 0 if ok else 1
    print(('PASS  ' if ok else 'FAIL  ') + msg)


def main():
    rclpy.init()
    node = Node('test_m3_03_tf_check')
    buf = Buffer()
    TransformListener(buf, node)
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
        if all(buf.can_transform(p, c, Time()) for p, c in EXPECTED):
            break
    for (parent, child), xyz in EXPECTED.items():
        try:
            t = buf.lookup_transform(parent, child, Time()).transform
        except Exception as exc:  # report and continue
            report(False, f'{parent} -> {child}: lookup failed ({exc})')
            continue
        got = (t.translation.x, t.translation.y, t.translation.z)
        q = (t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w)
        ok_t = all(abs(a - b) <= TOL for a, b in zip(got, xyz))
        ok_r = all(abs(a - b) <= TOL for a, b in zip(q, (0.0, 0.0, 0.0, 1.0)))
        report(ok_t and ok_r, f'{parent} -> {child}: translation ({got[0]:.9f}, {got[1]:.9f}, {got[2]:.9f}) m == {xyz} '
                              f'and rotation (x y z w) ({q[0]:.9f}, {q[1]:.9f}, {q[2]:.9f}, {q[3]:.9f}) == identity, to 1e-6')
    for _ in range(10):
        rclpy.spin_once(node, timeout_sec=0.1)
    tree = yaml.safe_load(buf.all_frames_as_yaml()) or {}
    parents = {child: info['parent'] for child, info in tree.items()}
    frames = set(parents) | set(parents.values())
    roots = sorted(frames - set(parents))
    print('tf frames and parents:', sorted(parents.items()))
    report(frames == FRAMES, f'frame set {sorted(frames)} == M1 tree + laser_frame + imu_link')
    report(roots == ['base_footprint'], f'single tree with root {roots} == [base_footprint] (each child has one parent)')
    node.destroy_node()
    rclpy.shutdown()
    print('== ALL CHECKS PASSED' if failures == 0 else f'== {failures} CHECK(S) FAILED')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
