#!/usr/bin/env python3
"""Drive the simulated AMR through simple velocity segments, for demonstration recordings (docs/gallery).

Not a test harness: it measures nothing and decides nothing. Test procedures use the harnesses under
docs/evidence/ instead.

Usage (same ROS_DOMAIN_ID as the running sim.launch.py):
    python3 tools/demo_drive.py <v> <w> <seconds> [<v> <w> <seconds> ...]
      v: linear.x in m/s, w: angular.z in rad/s, seconds: simulation time of the segment.
A zero command follows the last segment. Commands go to /cmd_vel as TwistStamped with simulation-time stamps,
frame base_footprint (DEC-026), at 20 Hz, so the command-freshness guard (DEC-029) passes them on.
The script waits for /clock and the first /diff_drive_controller/odom message before it starts.
"""
import sys
import time

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.parameter import Parameter


def main():
    vals = [float(x) for x in sys.argv[1:]]
    if not vals or len(vals) % 3:
        print(__doc__)
        return 2
    segments = [vals[i:i + 3] for i in range(0, len(vals), 3)]
    rclpy.init()
    node = rclpy.create_node('demo_drive', parameter_overrides=[Parameter('use_sim_time', value=True)])
    pub = node.create_publisher(TwistStamped, '/cmd_vel', 10)
    got_odom = []
    node.create_subscription(Odometry, '/diff_drive_controller/odom', lambda m: got_odom.append(1), 10)
    deadline = time.monotonic() + 120
    while (not got_odom or node.get_clock().now().nanoseconds == 0) and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)
    if not got_odom:
        print('# demo_drive: no odometry within 120 s (controllers not active?)')
        return 1

    def send(v, w):
        msg = TwistStamped()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.header.frame_id = 'base_footprint'
        msg.twist.linear.x, msg.twist.angular.z = v, w
        pub.publish(msg)

    for v, w, secs in segments + [[0.0, 0.0, 1.0]]:
        t_end = node.get_clock().now().nanoseconds + int(secs * 1e9)
        while node.get_clock().now().nanoseconds < t_end:
            send(v, w)
            rclpy.spin_once(node, timeout_sec=0.05)
        print(f'# demo_drive: segment v={v} m/s, w={w} rad/s, {secs} s done')
    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
