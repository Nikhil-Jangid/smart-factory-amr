"""TS-027 C4 scratch prototype: 1 kHz Gazebo IMU (/imu_raw) -> 100 Hz block-mean IMU (/imu), gz-transport side.

Filter F1 (selected by the offline study, c4_offline_study.log): output at every raw stamp that is a multiple of
10 ms, value = arithmetic mean of the raw samples with stamps in (t - 10 ms, t] for linear acceleration and
angular velocity, per axis; orientation, frame id and covariances copied from the newest sample; header stamp =
the newest raw stamp t. A boxcar of N = 10 at 1 kHz has linear phase, group delay (N - 1) / 2 = 4.5 ms relative to
the stamp, and transmission nulls at 100 Hz and its harmonics (the controller command-hold rate).
The ROS side is unchanged: the existing sensor_bridge maps gz /imu -> ROS /imu.
Diagnostics (env C4_STATS): blocks published, blocks with a sample count != 10, raw stamp gaps.
Scratch only; not a production component.
"""
import os
import signal
import sys
import threading
import time

from gz.msgs10.imu_pb2 import IMU
from gz.transport13 import Node

N = 10
lock = threading.Lock()
buf = []                       # (stamp_ns, msg)
stats = {'raw': 0, 'out': 0, 'short': 0, 'gaps': 0, 'last_ns': None, 'counts': {}}
node = Node()
pub = node.advertise('/imu', IMU)


def on_raw(msg):
    ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nsec
    with lock:
        stats['raw'] += 1
        if stats['last_ns'] is not None and ns - stats['last_ns'] != 1_000_000:
            stats['gaps'] += 1
        stats['last_ns'] = ns
        buf.append((ns, msg))
        ms = round(ns / 1e6)
        if ms % N != 0:
            return
        lo = ns - N * 1_000_000
        block = [m for t, m in buf if lo < t <= ns]
        buf[:] = [(t, m) for t, m in buf if t > ns]         # the next window is (t, t + 10 ms]
        n = len(block)
        stats['counts'][n] = stats['counts'].get(n, 0) + 1
        if n != N:
            stats['short'] += 1
        out = IMU()
        out.CopyFrom(msg)                                   # header (stamp t, frame), entity name, orientation
        for f in ('x', 'y', 'z'):
            setattr(out.linear_acceleration, f, sum(getattr(b.linear_acceleration, f) for b in block) / n)
            setattr(out.angular_velocity, f, sum(getattr(b.angular_velocity, f) for b in block) / n)
        pub.publish(out)
        stats['out'] += 1


def write_stats(*_):
    path = os.environ.get('C4_STATS')
    if path:
        with lock:
            s = dict(stats)
        with open(path, 'w') as fh:
            fh.write(f"raw {s['raw']} out {s['out']} blocks_not_10 {s['short']} raw_stamp_gaps {s['gaps']} "
                     f"block_size_histogram {dict(sorted(s['counts'].items()))}\n")
    os._exit(0)


signal.signal(signal.SIGINT, write_stats)
signal.signal(signal.SIGTERM, write_stats)
if not node.subscribe(IMU, '/imu_raw', on_raw):
    sys.exit('subscribe /imu_raw failed')
while True:
    time.sleep(1.0)
