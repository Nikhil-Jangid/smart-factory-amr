"""TEST-M3-04 part 2: the default sim.launch.py (no sensors, no world argument) is the M2 launch (DEC-034).

Run with plain python3 (rclpy; TS-011) while `sim.launch.py headless:=true` runs and both controllers are
active. Usage: python3 TEST-M3-04_default_check.py <output file for the published robot_description>
  - writes the robot_description published by robot_state_publisher (transient local) to the output file,
    for a byte comparison with the M2 expansion by the procedure;
  - no /scan or /imu topic and no sensor_bridge node exist.
Exit 0 only if every check passes.
"""
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

failures = 0


def report(ok, msg):
    global failures
    failures += 0 if ok else 1
    print(('PASS  ' if ok else 'FAIL  ') + msg)


def main(out):
    rclpy.init()
    node = Node('test_m3_04_default_check')
    got = []
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
    node.create_subscription(String, '/robot_description', lambda m: got.append(m.data), qos)
    deadline = time.monotonic() + 15.0
    while not got and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
    for _ in range(20):  # let discovery settle before listing the graph
        rclpy.spin_once(node, timeout_sec=0.05)
    topics = sorted(name for name, _ in node.get_topic_names_and_types())
    nodes = sorted(name for name, _ in node.get_node_names_and_namespaces())
    node.destroy_node()
    rclpy.shutdown()
    report(bool(got), 'robot_description received from robot_state_publisher')
    if got:
        with open(out, 'w') as f:
            f.write(got[0])
    report(not {'/scan', '/imu'} & set(topics), f'no /scan or /imu topic (topics: {topics})')
    report('sensor_bridge' not in nodes, f'no sensor_bridge node (nodes: {nodes})')
    print('== ALL CHECKS PASSED' if failures == 0 else f'== {failures} CHECK(S) FAILED')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
