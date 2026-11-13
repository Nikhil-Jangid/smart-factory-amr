"""LOWOBS investigation measurement (throwaway). Settles 2 s after the first scan, then records
5 s of simulation time: LiDAR returns per target and per bearing class; depth-camera points above
the floor per target (MODE A). Robot spawned at the origin at rest, so world = base_footprint.
Env: MODE (A|B), LX, LZ (laser position in base_footprint)."""
import math, os, sys, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import LaserScan, PointCloud2
from sensor_msgs_py import point_cloud2

MODE = os.environ['MODE']; LX = float(os.environ['LX']); LZ = float(os.environ['LZ'])
SETTLE, WINDOW = 2.0, 5.0
# targets: name, x0, x1, y0, y1, top height (m) -- from lowobs_world.sdf
TARGETS = [('t1_dropped_part 0.03 m', 0.775, 0.825, 0.175, 0.225, 0.03),
           ('t2_low_tote 0.08 m', 1.10, 1.30, -0.45, -0.25, 0.08),
           ('t3_box 0.15 m', 1.65, 1.95, 0.30, 0.60, 0.15),
           ('t4_EUR_pallet_proxy 0.144 m', 2.80, 3.60, -0.60, 0.60, 0.144),
           ('t5_rear_box 0.40 m', -1.65, -1.35, -0.15, 0.15, 0.40),
           ('t6_right_box 0.40 m', -0.15, 0.15, -1.65, -1.35, 0.40)]
CAM_T = np.array([0.135, 0.0, 0.19]); CAM_PITCH = 0.4363323129985824   # trial extrinsics (sensors_A.xacro)

def st(s): return s.sec + s.nanosec * 1e-9

class M(Node):
    def __init__(self):
        super().__init__('lowobs_measure', parameter_overrides=[rclpy.parameter.Parameter('use_sim_time', value=True)])
        self.clock = None; self.t0 = None; self.scans = []; self.clouds = []; self.wall = {}
        self.create_subscription(Clock, '/clock', lambda m: setattr(self, 'clock', st(m.clock)), 10)
        self.create_subscription(LaserScan, '/scan', self.on_scan, qos_profile_sensor_data)
        if MODE == 'A': self.create_subscription(PointCloud2, '/depth/points', self.on_cloud, qos_profile_sensor_data)
    def win(self, ts):
        if self.t0 is None: return False
        ok = self.t0 + SETTLE <= ts < self.t0 + SETTLE + WINDOW
        if ok:
            self.wall.setdefault('first', (ts, time.monotonic())); self.wall['last'] = (ts, time.monotonic())
        return ok
    def on_scan(self, m):
        ts = st(m.header.stamp)
        if self.t0 is None: self.t0 = ts
        if self.win(ts): self.scans.append(m)
    def on_cloud(self, m):
        if self.win(st(m.header.stamp)) and len(self.clouds) < 60:
            pts = point_cloud2.read_points_numpy(m, field_names=('x', 'y', 'z'))
            self.clouds.append((m.header.frame_id, pts[np.isfinite(pts).all(1)], len(pts)))   # beyond the far clip: +-inf
    def done(self): return self.t0 is not None and self.clock is not None and self.clock > self.t0 + SETTLE + WINDOW + 0.3

def in_box(px, py, t, m=0.05): return (px >= t[1] - m) & (px <= t[2] + m) & (py >= t[3] - m) & (py <= t[4] + m)

def main():
    rclpy.init(); n = M(); t_end = time.monotonic() + 150
    while rclpy.ok() and not n.done() and time.monotonic() < t_end: rclpy.spin_once(n, timeout_sec=0.1)
    print(f'# MODE {MODE}; laser at ({LX:.3f}, 0, {LZ:.3f}) m in base_footprint; window {WINDOW} s after {SETTLE} s settle')
    (s0, w0), (s1, w1) = n.wall['first'], n.wall['last']; print(f'# real-time factor over the window: {(s1 - s0) / (w1 - w0):.3f}')
    S = n.scans; print(f'# scans in window: {len(S)}; frame_id {sorted({s.header.frame_id for s in S})}')
    R = np.array([s.ranges for s in S]); a = S[0].angle_min + S[0].angle_increment * np.arange(R.shape[1])
    fin = np.isfinite(R)
    print(f'# beams finite in every scan: {int(fin.all(0).sum())}/360; +inf always: {int((R == np.inf).all(0).sum())}; -inf always: {int((R == -np.inf).all(0).sum())}; nan always: {int(np.isnan(R).all(0).sum())}')
    nf = np.where(~fin.all(0))[0]
    if len(nf):
        deg = np.round(np.degrees(a[nf])).astype(int); vals = sorted({str(v) for v in R[:, nf].ravel() if not np.isfinite(v)})
        print(f'# non-finite bearings (deg): {deg.min()} .. {deg.max()} (count {len(nf)}; contiguous runs: {runs(deg)}); values {vals}')
    near = np.where(fin & (R < 0.45))
    print(f'# finite returns closer than 0.45 m (self-returns): {len(near[0])}')
    px = LX + R * np.cos(a); py = R * np.sin(a)
    if os.environ.get('BEARING_DUMP'):
        med = np.median(R, 0)
        print('# per-bearing median range (m), bearings 90..180 and -180..-90, with the expected first hit if the beam reaches the target:')
        for k in list(range(270, 360)) + list(range(0, 91)):
            d = int(round(math.degrees(a[k]))); ex = LX + med[k] * math.cos(a[k]), med[k] * math.sin(a[k])
            print(f'#   {d:+4d} deg  median {med[k]:8.3f}  endpoint ({ex[0]:+.3f}, {ex[1]:+.3f})')
    for t in TARGETS:
        hits = (fin & in_box(px, py, t)).sum(1)
        det = (hits >= 1).mean()
        print(f'LIDAR  {t[0]:30s} beams on target per scan: mean {hits.mean():5.1f}; detected in {100 * det:5.1f} % of scans -> {"DETECTED" if det >= 0.9 else "NOT DETECTED"}')
    if MODE == 'A':
        C = n.clouds; print(f'# depth clouds analysed: {len(C)}; frame_id {sorted({c[0] for c in C})}; points per cloud: {np.mean([c[2] for c in C]):.0f}, finite {np.mean([len(c[1]) for c in C]):.0f}')
        c, s_ = math.cos(CAM_PITCH), math.sin(CAM_PITCH)
        Ry = np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])        # body pitch (nose down for +pitch)
        conv = {'link (x fwd, y left, z up)': np.eye(3),
                'optical (z fwd, x right, y down)': np.array([[0, 0, 1], [-1, 0, 0], [0, -1, 0]])}
        best = None
        for name, Rc in conv.items():
            P = (Ry @ Rc @ C[0][1].T).T + CAM_T
            med = float(np.median(P[:, 2])); print(f'# convention {name}: median point height {med:+.4f} m')
            if best is None or abs(med) < abs(best[1]): best = (name, med, Rc)
        print(f'# using convention: {best[0]} (floor is the majority of points)')
        Rc = best[2]; per = {t[0]: [] for t in TARGETS}; ztop = {t[0]: [] for t in TARGETS}; spurious = []; floor_z = []
        for _, pts, _n in C:
            P = (Ry @ Rc @ pts.T).T + CAM_T; x, y, z = P[:, 0], P[:, 1], P[:, 2]
            used = np.zeros(len(P), bool)
            for t in TARGETS:
                m = in_box(x, y, t, 0.03); above = m & (z > 0.015); used |= m
                per[t[0]].append(int(above.sum())); ztop[t[0]].append(float(z[above].max()) if above.any() else float('nan'))
            free = ~used & (np.abs(x) < 4.7) & (np.abs(y) < 4.7)
            spurious.append(int((free & (z > 0.015)).sum())); floor_z.append(z[free & (z < 0.015)])
        fz = np.concatenate(floor_z); print(f'# floor points: n {len(fz)}, z mean {fz.mean():+.5f} m, sd {fz.std():.5f} m')
        print(f'# points > 0.015 m above the floor outside every target: max per cloud {max(spurious)}')
        for t in TARGETS:
            k = np.array(per[t[0]]); det = (k >= 10).mean(); zt = np.nanmedian(ztop[t[0]]) if det else float('nan')
            print(f'DEPTH  {t[0]:30s} points above 0.015 m: median {np.median(k):7.0f}; detected (>= 10 pts) in {100 * det:5.1f} % of clouds; '
                  f'median top height {zt:.3f} m -> {"DETECTED" if det >= 0.9 else "NOT DETECTED"}')

def runs(deg):
    out = []; d = sorted(set(int(x) for x in deg))
    for v in d:
        if out and v == out[-1][1] + 1: out[-1][1] = v
        else: out.append([v, v])
    return ', '.join(f'{p}..{q}' for p, q in out)

if __name__ == '__main__': main()
