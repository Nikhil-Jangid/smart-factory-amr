"""TS-027 probe in the real launch: ROS /imu (bridge) vs gz-transport /imu (sensor) vs ground truth, stop profile."""
import importlib.util, os, statistics, sys, threading
P = '<home>/Projects/smart-factory-amr/docs/evidence/M3/TEST-M3-D_imu_encoder_measure.py'
spec = importlib.util.spec_from_file_location('d', P); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
from gz.msgs10.imu_pb2 import IMU
M2 = d.M2
M2.rclpy.init(); rec = d.Recorder(); gzimu = []
def on_gz(m):
    with rec.lock:
        gzimu.append((m.header.stamp.sec + m.header.stamp.nsec * 1e-9, m.linear_acceleration.x, m.linear_acceleration.z))
print('# gz subscribe /imu:', rec.gz.subscribe(IMU, '/imu', on_gz))
ex = M2.SingleThreadedExecutor(); ex.add_node(rec)
threading.Thread(target=ex.spin, daemon=True).start(); r = M2.Run(rec)
r.ready()
legs = r.profile([(3.0, 0.5, 0.0), (3.0, 0.0, 0.0)])
t0, t1 = legs[0][0], legs[0][1]
psi0 = r.nearest(rec.gt, t0)[6]
sp = r.body_speed(r.samples(t0 - 0.5, legs[1][1]), psi0)
def m(xs): return statistics.fmean(xs) if xs else float('nan')
def gt_acc(a, b):
    va = min(sp, key=lambda s: abs(s[0] - a)); vb = min(sp, key=lambda s: abs(s[0] - b))
    return (vb[1] - va[1]) / (vb[0] - va[0])
print(f'# leg start {t0:.3f} end {t1:.3f}; ROS imu n {len(rec.imu)}, gz imu n {len(gzimu)}')
for lab, a, b in (('rest before', t0 - 1.0, t0 - 0.05), ('speed-up', t0 + 0.2, t0 + 0.8), ('cruise', t0 + 1.5, t1 - 0.1), ('braking', t1 + 0.1, t1 + 0.4), ('stopped', t1 + 1.0, legs[1][1] - 0.1)):
    ros = rec.imu_between(a, b); g = [s for s in gzimu if a <= s[0] <= b]
    print(f'{lab:12s} [{a - t0:+.2f},{b - t0:+.2f}] gt accel {gt_acc(a, b):+.4f} | ROS /imu ax {m([x[1] for x in ros]):+.4f} az {m([x[3] for x in ros]):+.4f} (n {len(ros)}) | gz /imu ax {m([x[1] for x in g]):+.4f} az {m([x[2] for x in g]):+.4f} (n {len(g)}) | ROS ax s {statistics.pstdev([x[1] for x in ros]) if len(ros)>1 else 0:.4f} min {min([x[1] for x in ros]):+.3f} max {max([x[1] for x in ros]):+.3f}')
ex.shutdown(); sys.stdout.flush(); os._exit(0)
