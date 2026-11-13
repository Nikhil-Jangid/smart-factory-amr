"""Task C LiDAR checks: TEST-M3-05 (range and noise) and TEST-M3-06 (FOV, self-returns, blind zone).

Usage, with `sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf` running (robot at the origin,
yaw 0) and both controllers active; plain python3 (rclpy and gz-transport; TS-011):
    python3 TEST-M3-C_lidar_check.py range <world.sdf>     TEST-M3-05
    python3 TEST-M3-C_lidar_check.py fov <world.sdf>       TEST-M3-06
Geometry: the target boxes are read from the world file (test_plan.md §7.1). The laser pose is the measured
ground-truth pose of the robot (Gazebo /world/sensor_test/pose/info, averaged over the window) composed with
the fixed laser offset (0.070, 0, 0.230) m (DEC-030, verified by TEST-M3-03). For beam i the bearing is
yaw + angle_min + i * angle_increment, taken from each message; r_true is the 2D distance from the laser
origin to the first box face along the beam, counting only boxes whose height spans the laser z
(sensors.md §7.2 error definition). Beams within 1 degree of a target's angular edge are excluded.
Window (sensors.md §7.2): settle 2.0 s after the first /scan stamp; then
  range: at least 20 scans, extended until every range target has n >= 1000 samples (at most 300 scans);
  fov:   20 scans (2.0 s).
Checks:
  TEST-M3-05 (REQ-M3-07): S1-S4 (sensors.md §7.4; TEST-M3_noise_stats.py) per target distance 1.0, 3.0, 6.0 m,
      sigma_r = 0.01 m (DEC-031), bias <= 0.010 m. Non-finite returns on target-face beams are counted.
  TEST-M3-06 (REQ-M3-08):
      D6 in every window scan, each of the targets at 0, +90, -90 and 180 deg gives >= 3 finite returns with
         |median(r - r_true)| <= 0.05 m;
      D7 0 finite returns closer than 0.45 m in all window scans (open area: nothing within 0.45 m of the laser);
      D8 0 finite returns in the low target's whole bearing sector (no edge exclusion) in all window scans.
      Recorded (INFO): angular registration of the target edges, returns on both sides of the +-180 deg seam,
      -inf / +inf counts, and the blind-zone characterization (laser height and tilt from ground truth).
Validity: RTF over the window (scan stamps vs wall time) >= 0.5, else exit 2 (repeat).
Exit 0 = all checks pass, 1 = a check failed, 2 = invalid run.
"""
import math
import os
import statistics
import sys
import threading
import time
import xml.etree.ElementTree as ET

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import LaserScan
from gz.transport13 import Node as GzNode
from gz.msgs10.pose_v_pb2 import Pose_V

def _load_stats():
    """Import the shared S1-S4 module (its file name has a hyphen, so importlib is used)."""
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TEST-M3_noise_stats.py')
    spec = importlib.util.spec_from_file_location('test_m3_noise_stats', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.s1_s4


s1_s4 = _load_stats()

LASER_OFFSET = (0.070, 0.0, 0.230)   # m in base_footprint (DEC-030; TEST-M3-03)
SETTLE = 2.0
EDGE = math.radians(1.0)
SIGMA_R, BIAS_LIMIT = 0.01, 0.010
RANGE_TARGETS = {'target_front_1m': 1.0, 'target_left_3m': 3.0, 'target_rear_6m': 6.0}
FOV_TARGETS = {'target_front_1m': 0.0, 'target_left_3m': 90.0, 'target_right_2m': -90.0, 'target_rear_6m': 180.0}
LOW_TARGET = 'target_low'
WORLD_TOPIC = '/world/sensor_test/pose/info'
failures = 0


def report(ok, msg):
    global failures
    failures += 0 if ok else 1
    print(('PASS  ' if ok else 'FAIL  ') + msg)


def info(msg):
    print('INFO  ' + msg)


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def load_boxes(world_file):
    """Static box models: name -> (cx, cy, cz, sx, sy, sz); yaw must be 0 (axis-aligned)."""
    boxes = {}
    for model in ET.parse(world_file).getroot().iter('model'):
        size = model.find('link/collision/geometry/box/size')
        if size is None:
            continue
        x, y, z, r, p, yw = (float(v) for v in model.find('pose').text.split())
        assert abs(r) + abs(p) + abs(yw) == 0, f'{model.get("name")} is not axis-aligned'
        boxes[model.get('name')] = (x, y, z) + tuple(float(v) for v in size.text.split())
    return boxes


def ray_box(ox, oy, phi, box):
    """2D slab intersection of the ray (ox, oy, phi) with the box footprint; distance to entry or None."""
    cx, cy, _, sx, sy, _ = box
    dx, dy = math.cos(phi), math.sin(phi)
    tmin, tmax = -math.inf, math.inf
    for o, d, lo, hi in ((ox, dx, cx - sx / 2, cx + sx / 2), (oy, dy, cy - sy / 2, cy + sy / 2)):
        if abs(d) < 1e-12:
            if not lo <= o <= hi:
                return None
            continue
        t1, t2 = (lo - o) / d, (hi - o) / d
        tmin, tmax = max(tmin, min(t1, t2)), min(tmax, max(t1, t2))
    return tmin if tmax >= tmin > 0 else None


def sector(ox, oy, box):
    """Centre bearing and half-width of the box as seen from (ox, oy) (corners of its footprint)."""
    cx, cy, _, sx, sy, _ = box
    centre = math.atan2(cy - oy, cx - ox)
    rel = [wrap(math.atan2(cy + a * sy / 2 - oy, cx + b * sx / 2 - ox) - centre) for a in (-1, 1) for b in (-1, 1)]
    return centre, min(rel), max(rel)


class Recorder(Node):
    def __init__(self):
        super().__init__('test_m3_c_lidar_check')
        qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=100, reliability=ReliabilityPolicy.RELIABLE)
        self.lock = threading.Lock()
        self.scans, self.t0, self.gt = [], None, []
        self.create_subscription(LaserScan, '/scan', self.on_scan, qos)
        self.gz = GzNode()
        self.gz.subscribe(Pose_V, WORLD_TOPIC, self.on_pose)

    def on_scan(self, m):
        ts = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        if self.t0 is None:
            self.t0 = ts
        if ts >= self.t0 + SETTLE:
            self.scans.append((ts, time.monotonic(), m))

    def on_pose(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9
        for p in msg.pose:
            if p.name == 'amr':
                with self.lock:
                    self.gt.append((t, p.position.x, p.position.y, p.position.z,
                                    p.orientation.w, p.orientation.x, p.orientation.y, p.orientation.z))


def rpy(qw, qx, qy, qz):
    roll = math.atan2(2 * (qw * qx + qy * qz), 1 - 2 * (qx * qx + qy * qy))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (qw * qy - qz * qx))))
    yaw = math.atan2(2 * (qw * qz + qx * qy), 1 - 2 * (qy * qy + qz * qz))
    return roll, pitch, yaw


def laser_pose(gt):
    """Mean robot pose over the window, composed with the laser offset: (lx, ly, lz, yaw, roll, pitch)."""
    x = statistics.fmean(g[1] for g in gt); y = statistics.fmean(g[2] for g in gt); z = statistics.fmean(g[3] for g in gt)
    angles = [rpy(*g[4:]) for g in gt]
    roll = statistics.fmean(a[0] for a in angles); pitch = statistics.fmean(a[1] for a in angles)
    yaw = math.atan2(statistics.fmean(math.sin(a[2]) for a in angles), statistics.fmean(math.cos(a[2]) for a in angles))
    ox, oy, oz = LASER_OFFSET
    return x + ox * math.cos(yaw) - oy * math.sin(yaw), y + ox * math.sin(yaw) + oy * math.cos(yaw), z + oz, yaw, roll, pitch


def beams(m):
    return [(i, m.angle_min + i * m.angle_increment, r) for i, r in enumerate(m.ranges)]


def main(mode, world_file):
    rclpy.init()
    node = Recorder()
    boxes = load_boxes(world_file)
    print(f'# world {os.path.basename(world_file)}: targets ' +
          ', '.join(f'{k} centre ({b[0]:.3f}, {b[1]:.3f}, {b[2]:.3f}) size ({b[3]:.2f}, {b[4]:.2f}, {b[5]:.2f})'
                    for k, b in sorted(boxes.items())))
    start = time.monotonic()
    while time.monotonic() - start < 120.0:
        rclpy.spin_once(node, timeout_sec=0.05)
        n = len(node.scans)
        if mode == 'fov' and n >= 20:
            break
        if mode == 'range' and n >= 20 and (n >= 300 or (n % 5 == 0 and range_counts_ok(node, boxes))):
            break
    scans = node.scans[:20] if mode == 'fov' else list(node.scans)
    with node.lock:
        gt = [g for g in node.gt if scans and scans[0][0] - 0.5 <= g[0] <= scans[-1][0] + 0.5]
    node.destroy_node()
    rclpy.shutdown()
    if len(scans) < 20 or not gt:
        print(f'INVALID: {len(scans)} window scans, {len(gt)} ground-truth samples within 120 s wall time')
        return 2
    rtf = (scans[-1][0] - scans[0][0]) / max(1e-9, scans[-1][1] - scans[0][1])
    lx, ly, lz, yaw, roll, pitch = laser_pose(gt)
    print(f'# window: settle {SETTLE} s after the first /scan stamp ({node.t0:.3f} s); {len(scans)} scans, '
          f'stamps {scans[0][0]:.3f} .. {scans[-1][0]:.3f} s; RTF {rtf:.3f}')
    print(f'# laser pose from ground truth ({len(gt)} samples): x {lx:+.5f} y {ly:+.5f} z {lz:.5f} m, '
          f'yaw {math.degrees(yaw):+.5f} deg, roll {math.degrees(roll):+.5f} deg, pitch {math.degrees(pitch):+.5f} deg')
    m0 = scans[0][2]
    print(f'# scan fields: angle_min {m0.angle_min:.9f} angle_increment {m0.angle_increment:.9f} rad, '
          f'{len(m0.ranges)} ranges, range {m0.range_min:.3f}..{m0.range_max:.3f} m')
    if rtf < 0.5:
        print(f'INVALID: RTF {rtf:.3f} < 0.5 (sensors.md §7.5); repeat')
        return 2
    pose = (lx, ly, lz, yaw)
    if mode == 'range':
        check_range(scans, boxes, pose)
    else:
        check_fov(scans, boxes, pose, roll, pitch)
    print('== ALL CHECKS PASSED' if failures == 0 else f'== {failures} CHECK(S) FAILED')
    return 1 if failures else 0


def face_samples(scans, boxes, pose, name, margin=EDGE):
    """(error list, non-finite count, beams per scan) for target `name`, edge beams excluded."""
    lx, ly, lz, yaw = pose
    centre, lo, hi = sector(lx, ly, boxes[name])
    tall = {k: b for k, b in boxes.items() if b[2] - b[5] / 2 <= lz <= b[2] + b[5] / 2}
    errs, nonfinite, per_scan = [], 0, 0
    for _, _, m in scans:
        count = 0
        for i, th, r in beams(m):
            phi = yaw + th
            rel = wrap(phi - centre)
            if not lo + margin <= rel <= hi - margin:
                continue
            hits = [(ray_box(lx, ly, phi, b), k) for k, b in tall.items()]
            hits = [h for h in hits if h[0] is not None]
            if not hits or min(hits)[1] != name:
                continue
            count += 1
            if math.isfinite(r):
                errs.append(r - min(hits)[0])
            else:
                nonfinite += 1
        per_scan = max(per_scan, count)
    return errs, nonfinite, per_scan


def range_counts_ok(node, boxes):
    with node.lock:
        gt = list(node.gt[-200:])
    if not gt:
        return False
    pose = laser_pose(gt)[:4]
    return all(len(face_samples(node.scans, boxes, pose, k)[0]) >= 1000 for k in RANGE_TARGETS)


def check_range(scans, boxes, pose):
    from_stats = []
    for name, dist in RANGE_TARGETS.items():
        errs, nonfinite, per_scan = face_samples(scans, boxes, pose, name)
        centre, lo, hi = sector(pose[0], pose[1], boxes[name])
        print(f'== TEST-M3-05 {name}: nominal {dist} m at bearing {math.degrees(wrap(centre - pose[3])):+.2f} deg, '
              f'half-width {math.degrees(hi):.2f} deg; {per_scan} face beams per scan after the 1 deg edge exclusion; '
              f'non-finite face returns: {nonfinite}')
        report(len(errs) >= 1000, f'{name}: n = {len(errs)} finite target-face samples >= 1000 (sensors.md §7.2)')
        checks, summary = s1_s4(errs, SIGMA_R, BIAS_LIMIT, f'{dist:.1f} m', 'm')
        print('      ' + summary)
        for ok, text in checks:
            report(ok, text)
        from_stats.append((dist, errs))
    return from_stats


def check_fov(scans, boxes, pose, roll, pitch):
    lx, ly, lz, yaw = pose
    print('== D6 targets at 0, +90, -90, 180 deg: >= 3 finite returns and |median(r - r_true)| <= 0.05 m in every scan')
    for name, bearing in FOV_TARGETS.items():
        worst_n, worst_med = 10**9, 0.0
        for k in range(len(scans)):
            errs, _, _ = face_samples([scans[k]], boxes, pose, name)
            worst_n = min(worst_n, len(errs))
            med = abs(statistics.median(errs)) if errs else math.inf
            worst_med = max(worst_med, med)
        report(worst_n >= 3 and worst_med <= 0.05,
               f'{name} ({bearing:+.0f} deg): min finite returns per scan {worst_n} >= 3; '
               f'max |median error| {worst_med:.4f} m <= 0.05 m ({len(scans)} scans)')

    print('== D7 no self-returns: finite returns closer than 0.45 m (open area: nothing within 0.45 m of the laser)')
    close = sum(1 for _, _, m in scans for r in m.ranges if math.isfinite(r) and r < 0.45)
    neg = sum(1 for _, _, m in scans for r in m.ranges if r == -math.inf)
    pos = sum(1 for _, _, m in scans for r in m.ranges if r == math.inf)
    nearest = min((r for _, _, m in scans for r in m.ranges if math.isfinite(r)), default=math.nan)
    report(close == 0, f'{close} finite returns < 0.45 m in {len(scans)} scans == 0 (nearest finite return {nearest:.4f} m)')
    info(f'-inf (closer than range_min) returns: {neg}; +inf (no return) returns: {pos} of {360 * len(scans)}')

    print('== D8 blind zone: low target (top below the 0.230 m scan plane), whole bearing sector, no edge exclusion')
    b = boxes[LOW_TARGET]
    centre, lo, hi = sector(lx, ly, b)
    top = b[2] + b[5] / 2
    finite_in = 0; beams_in = 0
    for _, _, m in scans:
        for i, th, r in beams(m):
            if lo <= wrap(yaw + th - centre) <= hi:
                beams_in += 1
                finite_in += math.isfinite(r)
    report(finite_in == 0, f'{LOW_TARGET}: sector {math.degrees(wrap(centre + lo - yaw)):+.2f} to '
                           f'{math.degrees(wrap(centre + hi - yaw)):+.2f} deg ({beams_in // len(scans)} beams per scan), '
                           f'finite returns {finite_in} == 0 over {len(scans)} scans')
    dist = math.hypot(b[0] - lx, b[1] - ly)
    info(f'blind-zone characterization: laser at z {lz:.4f} m (nominal 0.230), tilt roll {math.degrees(roll):+.4f} / '
         f'pitch {math.degrees(pitch):+.4f} deg; plane height at the low target ({dist:.3f} m): '
         f'{lz + dist * math.tan(pitch):.4f} m; low target top {top:.3f} m, i.e. {lz - top:.3f} m below the plane, '
         f'not detected. Plane height at 12 m (range_max): {lz + 12 * math.tan(pitch):.4f} m. '
         f'Any object whose top is below the plane is invisible to this LiDAR (DEC-030; M8 depth camera, DEC-037)')

    print('== Angular registration and coverage (INFO)')
    for name in ('target_front_1m', 'target_rear_6m'):
        geo = set(); got = set()
        centre, lo, hi = sector(lx, ly, boxes[name])
        m = scans[0][2]
        for i, th, r in beams(m):
            if lo <= wrap(yaw + th - centre) <= hi:
                geo.add(i)
            if math.isfinite(r) and abs(r - (ray_box(lx, ly, yaw + th, boxes[name]) or -9)) < 0.05:
                got.add(i)
        info(f'{name}: beams geometrically on the target {len(geo)}, beams returning the target range (+-0.05 m) '
             f'{len(got)}, symmetric difference {sorted(geo ^ got)} (edge beams only expected)')
    m = scans[0][2]
    first, last = m.ranges[0], m.ranges[-1]
    info(f'seam: beam 0 ({math.degrees(m.angle_min):+.3f} deg) {first:.4f} m and beam {len(m.ranges) - 1} '
         f'({math.degrees(m.angle_min + (len(m.ranges) - 1) * m.angle_increment):+.3f} deg) {last:.4f} m: '
         f'both on the rear target (expected about 6.0 m)')


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] not in ('range', 'fov'):
        print(__doc__)
        code = 2
    else:
        code = main(sys.argv[1], sys.argv[2])
    sys.stdout.flush()
    os._exit(code)  # gz-transport aborts during interpreter teardown (as TEST-M2_motion_measure.py)
