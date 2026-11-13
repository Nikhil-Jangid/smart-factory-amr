"""gz-only probe: JointController wheel velocity ramp in a running gz sim server; IMU vs ground truth."""
import os, statistics, sys, threading, time
from gz.transport13 import Node
from gz.msgs10.imu_pb2 import IMU
from gz.msgs10.pose_v_pb2 import Pose_V
from gz.msgs10.double_pb2 import Double
node = Node(); lock = threading.Lock(); imu = []; gt = []
def on_imu(m):
    with lock: imu.append((m.header.stamp.sec + m.header.stamp.nsec * 1e-9, m.linear_acceleration.x, m.linear_acceleration.z))
def on_pose(m):
    t = m.header.stamp.sec + m.header.stamp.nsec * 1e-9
    for p in m.pose:
        if p.name == 'amr':
            with lock: gt.append((t, p.position.x)); break
node.subscribe(IMU, '/imu', on_imu); node.subscribe(Pose_V, '/world/sensor_test/pose/info', on_pose)
pl = node.advertise('/model/amr/joint/left_wheel_joint/cmd_vel', Double); pr = node.advertise('/model/amr/joint/right_wheel_joint/cmd_vel', Double)
time.sleep(3.0)
def now():
    with lock: return gt[-1][0] if gt else 0.0
def send(v):
    d = Double(); d.data = v / 0.075; pl.publish(d); pr.publish(d)
marks = {}
t = now(); marks['start'] = t
while now() - t < 1.0: send(0.5 * (now() - t)); time.sleep(0.002)
marks['ramp_end'] = now()
while now() - marks['ramp_end'] < 1.5: send(0.5); time.sleep(0.005)
marks['brake'] = now(); tb = marks['brake']
while now() - tb < 0.5: send(max(0.0, 0.5 - 1.0 * (now() - tb))); time.sleep(0.002)
marks['stop'] = now()
while now() - marks['stop'] < 1.0: send(0.0); time.sleep(0.01)
with lock: I = list(imu); G = list(gt)
def vel(tc):
    a = min(G, key=lambda s: abs(s[0] - (tc - 0.05))); b = min(G, key=lambda s: abs(s[0] - (tc + 0.05)))
    return (b[1] - a[1]) / (b[0] - a[0])
def m(x): return statistics.fmean(x) if x else float('nan')
print('# marks', {k: round(v, 3) for k, v in marks.items()}, 'imu n', len(I), 'gt n', len(G))
s = marks['start']
for lab, a, b in (('rest', s - 1.5, s - 0.1), ('speed-up', s + 0.2, marks['ramp_end'] - 0.1), ('cruise', marks['ramp_end'] + 0.3, marks['brake'] - 0.1), ('braking', marks['brake'] + 0.1, marks['stop'] - 0.1), ('stopped', marks['stop'] + 0.3, marks['stop'] + 0.9)):
    ga = (vel(b) - vel(a)) / (b - a)
    ii = [x for x in I if a <= x[0] <= b]
    print(f'{lab:9s} [{a - s:+.2f},{b - s:+.2f}] gt accel {ga:+.4f} (v {vel(a):+.3f} -> {vel(b):+.3f}) | gz /imu ax {m([x[1] for x in ii]):+.4f} az {m([x[2] for x in ii]):+.4f} (n {len(ii)})')
sys.stdout.flush(); os._exit(0)
