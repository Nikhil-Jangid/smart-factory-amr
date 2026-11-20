#!/usr/bin/env python3
"""TEST-M6-02: localization interface check (REQ-M6-01, -02, -03; docs/testing/test_plan.md §11; M6 Task A).

Usage (the simulation runs: sim.launch.py sensors:=true world:=mapping_arena.sdf; same ROS_DOMAIN_ID):
    python3 TEST-M6-02_interface_check.py pre  <state.json> <maps dir>   before localization.launch.py is started
    python3 TEST-M6-02_interface_check.py main <state.json> <maps dir>   after localization.launch.py is started
<maps dir> is the installed share/amr_bringup/maps (the files the launch file serves).
Run by docs/evidence/M6/TEST-M6-02_procedure.sh. Exit 0 = all PASS, 1 = a FAIL, 2 = invalid run (RTF < 0.5 or
no simulation clock).

pre (5 s of simulation time, localization not running): records the nodes that publish /tf and checks that nobody
publishes map -> odom, /map or /map_amcl yet. The node list is saved to <state.json> for the main step.

main:
  1. Lifecycle: /map_server, /map_server_amcl and /amcl in state 'active' (service get_state; `ros2 lifecycle get`
     does not find Nav2 nodes in Jazzy, Task A gate), within 60 s.
  2. Parameters: use_sim_time true on all three. amcl (DEC-056, DEC-061, DEC-062): laser_max_range 12.0 (DEC-031),
     map_topic 'map_amcl', scan_topic 'scan', frames map / odom / base_footprint, set_initial_pose true at
     (0, 0, 0) (DEC-058), alpha1 0.0016, alpha2-4 0.0004, sigma_hit 0.05. map_server_amcl: topic_name 'map_amcl'.
  3. /map (REQ-M6-01): exactly one publisher, map_server; the received grid equals mapping_arena.yaml + .pgm cell by
     cell (map_server's trinary conversion), frame 'map', resolution and origin as the file (DEC-055).
     /map_amcl (DEC-062): exactly one publisher, map_server_amcl; the same cells; origin = mapping_arena_amcl.yaml,
     which is the reference origin + 0.025 m in x and y.
     amcl subscribes to /map_amcl and not to /map; amcl subscribes to /scan.
  4. No SLAM node (/slam_toolbox) in the graph (REQ-M6-02: SLAM must not run at the same time).
  5. A short drive (0.25 m/s for 4 s, 0.5 rad/s for 3.2 s, stop 2 s; TwistStamped on /cmd_vel at 20 Hz, sim-time
     stamps, as TEST-M5-02) while /tf, /tf_static and /amcl_pose are recorded. It moves the robot past AMCL's update
     thresholds (update_min_d 0.25 m, update_min_a 0.2 rad), so the filter updates and publishes.
  6. Exactly one publisher of map -> odom, by the method of TEST-M5-02 (rclpy gives the publication sequence number,
     which every DDS writer counts on its own from 1; two writers would repeat numbers), attributed to amcl by
     comparison with the pre step: the only node added to the /tf publishers is amcl. Also: each message with
     map -> odom carries only that transform; /tf_static never carries it; the stamps are simulation time
     (within 30 s of the clock: AMCL post-dates the transform by transform_tolerance, 1.0 s).
  7. TF tree: every frame has exactly one parent over all /tf and /tf_static messages; the chain is
     map -> odom -> base_footprint -> base_link -> lidar_mount_link -> laser_frame; map -> laser_frame resolves.
  8. /amcl_pose (REQ-M6-03): geometry_msgs/msg/PoseWithCovarianceStamped from amcl, frame 'map'; after the drive the
     last message has finite, positive variances of x, y and yaw (the filter's spread).
  INFO (logged, no criterion): /amcl_pose messages, the first (start) and last poses, amcl's /tf writer count, RTF.
"""
import importlib.util
import json
import math
import os
import sys
import threading
import time

import yaml

_spec = importlib.util.spec_from_file_location(
    'M2', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'M2', 'TEST-M2_motion_measure.py'))
M2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M2)  # Spinner (TS-030), rclpy, SingleThreadedExecutor (TS-013)
rclpy = M2.rclpy

from geometry_msgs.msg import PoseWithCovarianceStamped, TwistStamped  # noqa: E402
from lifecycle_msgs.srv import GetState  # noqa: E402
from nav_msgs.msg import OccupancyGrid  # noqa: E402
from rcl_interfaces.srv import GetParameters  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402
from rclpy.time import Time  # noqa: E402
from tf2_msgs.msg import TFMessage  # noqa: E402
from tf2_ros import Buffer, TransformListener  # noqa: E402

AMCL = 'amcl'
LIFECYCLE = ['map_server', 'map_server_amcl', AMCL]
CHAIN = [('map', 'odom'), ('odom', 'base_footprint'), ('base_footprint', 'base_link'),
         ('base_link', 'lidar_mount_link'), ('lidar_mount_link', 'laser_frame')]
LATCHED = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
TF_STATIC_QOS = QoSProfile(depth=100, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
AMCL_PARAMS = {  # name: expected value (DEC-031, DEC-056, DEC-058, DEC-061, DEC-062)
    'use_sim_time': True, 'laser_max_range': 12.0, 'map_topic': 'map_amcl', 'scan_topic': 'scan',
    'global_frame_id': 'map', 'odom_frame_id': 'odom', 'base_frame_id': 'base_footprint',
    'set_initial_pose': True, 'initial_pose.x': 0.0, 'initial_pose.y': 0.0, 'initial_pose.yaw': 0.0,
    'alpha1': 0.0016, 'alpha2': 0.0004, 'alpha3': 0.0004, 'alpha4': 0.0004, 'sigma_hit': 0.05,
}


def load_map(yaml_path):
    """The grid map_server serves for a trinary map file: (cells row-major from the bottom row, width, height, meta)."""
    meta = yaml.safe_load(open(yaml_path))
    raw = open(os.path.join(os.path.dirname(yaml_path), meta['image']), 'rb').read()
    hdr, i = [], 0
    while len(hdr) < 4:  # binary PGM (P5): magic, width, height, maxval; '#' lines are comments
        j = raw.index(b'\n', i)
        line, i = raw[i:j], j + 1
        if not line.startswith(b'#'):
            hdr += line.split()
    assert hdr[0] == b'P5', hdr[0]
    w, h = int(hdr[1]), int(hdr[2])
    data = raw[i:i + w * h]
    neg = meta.get('negate', 0)

    def cell(v):
        p = v / 255.0 if neg else (255 - v) / 255.0
        return 100 if p > meta['occupied_thresh'] else (0 if p < meta['free_thresh'] else -1)
    return [cell(data[(h - 1 - r) * w + c]) for r in range(h) for c in range(w)], w, h, meta


class Rec(Node):
    def __init__(self):
        super().__init__('test_m6_02', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.lock = threading.Lock()
        self.tf = []          # (publication_sequence_number, [(parent, child, stamp_ns)])
        self.tf_static = []   # [(parent, child)]
        self.maps = {}        # topic -> first OccupancyGrid
        self.poses = []       # PoseWithCovarianceStamped
        self.create_subscription(TFMessage, '/tf', self.on_tf, 100)
        self.create_subscription(TFMessage, '/tf_static', self.on_tf_static, TF_STATIC_QOS)
        for topic in ('/map', '/map_amcl'):
            self.create_subscription(OccupancyGrid, topic, lambda m, t=topic: self.on_map(t, m), LATCHED)
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self.on_pose, LATCHED)
        self.cmd = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)

    def on_tf(self, msg, info):
        tr = [(t.header.frame_id.lstrip('/'), t.child_frame_id.lstrip('/'),
               t.header.stamp.sec * 10**9 + t.header.stamp.nanosec) for t in msg.transforms]
        with self.lock:
            self.tf.append((info['publication_sequence_number'], tr))

    def on_tf_static(self, msg):
        with self.lock:
            self.tf_static += [(t.header.frame_id.lstrip('/'), t.child_frame_id.lstrip('/')) for t in msg.transforms]

    def on_map(self, topic, msg):
        with self.lock:
            self.maps.setdefault(topic, msg)

    def on_pose(self, msg):
        with self.lock:
            self.poses.append(msg)

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def send(self, v, w):
        m = TwistStamped()
        m.header.stamp = self.get_clock().now().to_msg()
        m.header.frame_id = 'base_footprint'
        m.twist.linear.x, m.twist.angular.z = float(v), float(w)
        self.cmd.publish(m)


class Check:
    def __init__(self):
        self.fail = False

    def __call__(self, ok, text):
        print(f'{"PASS" if ok else "FAIL"}  {text}', flush=True)
        self.fail |= not ok

    @staticmethod
    def info(text):
        print(f'INFO  {text}', flush=True)


def wait(pred, wall_s):
    t_end = time.monotonic() + wall_s
    while time.monotonic() < t_end:
        if pred():
            return True
        time.sleep(0.05)
    return pred()


def wait_sim(rec, sim_s):
    t_end = rec.now_s() + sim_s
    return wait(lambda: rec.now_s() >= t_end, sim_s * 10 + 30)


def call(rec, srv_type, name, req, wall_s=10.0):
    cli = rec.create_client(srv_type, name)
    if not cli.wait_for_service(timeout_sec=wall_s):
        return None
    fut = cli.call_async(req)
    wait(fut.done, wall_s)
    return fut.result() if fut.done() else None


def params(rec, node, names):
    """Values of declared parameters, or {} (a request naming an undeclared parameter returns nothing, TS-038)."""
    r = call(rec, GetParameters, f'/{node}/get_parameters', GetParameters.Request(names=names))
    if not r or len(r.values) != len(names):
        return {}
    conv = {1: 'bool_value', 2: 'integer_value', 3: 'double_value', 4: 'string_value'}
    return {n: getattr(v, conv[v.type]) if v.type in conv else None for n, v in zip(names, r.values)}


def tf_nodes(rec):
    return sorted({p.node_name for p in rec.get_publishers_info_by_topic('/tf')})


def map_to_odom(records):
    return [(seq, tr) for seq, tr in records if any(p == 'map' and c == 'odom' for p, c, _ in tr)]


def yaw(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def pose_text(m):
    p, c = m.pose.pose, m.pose.covariance
    return (f'({p.position.x:+.4f}, {p.position.y:+.4f}) m, yaw {math.degrees(yaw(p.orientation)):+.3f} deg; '
            f'var x {c[0]:.3g} m^2, y {c[7]:.3g} m^2, yaw {c[35]:.3g} rad^2')


def pre(rec, ck, state_path):
    wait_sim(rec, 5.0)
    nodes = tf_nodes(rec)
    with rec.lock:
        m2o = map_to_odom(rec.tf)
    ck.info(f'/tf publisher nodes before localization: {nodes}')
    ck(AMCL not in nodes, f'{AMCL} is not yet a /tf publisher')
    ck(not m2o, f'no map -> odom on /tf before localization starts ({len(m2o)} messages in 5 s of simulation time)')
    for topic in ('/map', '/map_amcl'):
        pubs = rec.get_publishers_info_by_topic(topic)
        ck(not pubs, f'no {topic} publisher before localization starts ({[p.node_name for p in pubs]})')
    json.dump({'tf_nodes': nodes}, open(state_path, 'w'))


def check_grid(ck, topic, msg, cells, w, h, origin, publisher):
    if msg is None:
        ck(False, f'{topic}: no message received within 30 s')
        return
    o = msg.info.origin.position
    diff = sum(1 for a, b in zip(msg.data, cells) if a != b) if len(msg.data) == len(cells) else None
    ok = (msg.header.frame_id == 'map' and abs(msg.info.resolution - 0.05) < 1e-6 and (msg.info.width, msg.info.height)
          == (w, h) and diff == 0 and abs(o.x - origin[0]) < 1e-6 and abs(o.y - origin[1]) < 1e-6)
    ck(ok, f'{topic} from {publisher}: frame {msg.header.frame_id!r}, {msg.info.width} x {msg.info.height} cells '
       f'(file {w} x {h}), resolution {msg.info.resolution:.3f} m, origin ({o.x:.4f}, {o.y:.4f}) '
       f'(file {origin[0]}, {origin[1]}), cells differing from the file: {diff} of {len(cells)}')


def main_check(rec, ck, state_path, maps_dir):
    before = json.load(open(state_path))['tf_nodes']
    # 1. lifecycle states
    t_end = time.monotonic() + 60
    states = {}
    while time.monotonic() < t_end:
        for n in LIFECYCLE:
            if states.get(n) != 'active':
                r = call(rec, GetState, f'/{n}/get_state', GetState.Request(), 5.0)
                states[n] = r.current_state.label if r else None
        if all(states.get(n) == 'active' for n in LIFECYCLE):
            break
        time.sleep(0.5)
    for n in LIFECYCLE:
        ck(states.get(n) == 'active', f'/{n} lifecycle state: {states.get(n)}')
    # 2. parameters
    for n in ('map_server', 'map_server_amcl'):
        v = params(rec, n, ['use_sim_time', 'topic_name'])
        exp_topic = 'map_amcl' if n == 'map_server_amcl' else 'map'
        ck(v.get('use_sim_time') is True and v.get('topic_name') == exp_topic,
           f'/{n}: use_sim_time = {v.get("use_sim_time")}, topic_name = {v.get("topic_name")!r} (expected {exp_topic!r})')
    v = params(rec, AMCL, list(AMCL_PARAMS))
    for name, exp in AMCL_PARAMS.items():
        got = v.get(name)
        ok = (abs(got - exp) < 1e-9) if isinstance(exp, float) and isinstance(got, float) else got == exp
        ck(ok, f'/{AMCL} {name} = {got!r} (expected {exp!r})')
    # 3. maps, publishers and subscriptions
    cells, w, h, meta = load_map(os.path.join(maps_dir, 'mapping_arena.yaml'))
    cells_a, w_a, h_a, meta_a = load_map(os.path.join(maps_dir, 'mapping_arena_amcl.yaml'))
    shift = [round(a - b, 6) for a, b in zip(meta_a['origin'][:2], meta['origin'][:2])]
    ck(cells_a == cells and shift == [0.025, 0.025],
       f'installed map files: AMCL copy has the same cells ({cells_a == cells}), origin shift {shift} m '
       f'(DEC-062: [0.025, 0.025])')
    wait(lambda: len(rec.maps) == 2, 30)
    for topic, node, c, ww, hh, m in (('/map', 'map_server', cells, w, h, meta),
                                      ('/map_amcl', 'map_server_amcl', cells_a, w_a, h_a, meta_a)):
        pubs = [(p.node_name, p.topic_type) for p in rec.get_publishers_info_by_topic(topic)]
        ck(pubs == [(node, 'nav_msgs/msg/OccupancyGrid')], f'{topic} publishers: {pubs}')
        with rec.lock:
            msg = rec.maps.get(topic)
        check_grid(ck, topic, msg, c, ww, hh, m['origin'], node)
    subs = {t: sorted(s.node_name for s in rec.get_subscriptions_info_by_topic(t)) for t in ('/map', '/map_amcl', '/scan')}
    ck(AMCL in subs['/map_amcl'] and AMCL not in subs['/map'],
       f'{AMCL} subscribes to /map_amcl and not to /map (/map: {subs["/map"]}, /map_amcl: {subs["/map_amcl"]})')
    ck(AMCL in subs['/scan'], f'/scan subscribers: {subs["/scan"]}')
    # 4. no SLAM node
    nodes = sorted(rec.get_node_names())
    ck('slam_toolbox' not in nodes, f'no SLAM node in the graph (nodes: {nodes})')
    with rec.lock:
        first = rec.poses[0] if rec.poses else None
    ck.info(f'/amcl_pose at start: {pose_text(first) if first else "none yet"}')
    # 5. drive, recording
    with rec.lock:
        rec.tf.clear()
    sim0, wall0 = rec.now_s(), time.monotonic()
    for v_, w_, secs in [(0.25, 0.0, 4.0), (0.0, 0.5, 3.2), (0.0, 0.0, 2.0)]:
        t_end = rec.now_s() + secs
        while rec.now_s() < t_end and time.monotonic() - wall0 < 120:
            rec.send(v_, w_)
            time.sleep(0.05)
    rec.send(0.0, 0.0)
    wait_sim(rec, 1.0)
    sim1, wall1 = rec.now_s(), time.monotonic()
    rtf = (sim1 - sim0) / max(wall1 - wall0, 1e-9)
    with rec.lock:
        tf = list(rec.tf)
        tf_static = list(rec.tf_static)
        poses = list(rec.poses)
    # 6. single map -> odom publisher
    m2o = map_to_odom(tf)
    seqs = [s for s, _ in m2o]
    ck(len(m2o) > 0, f'map -> odom messages during the drive: {len(m2o)}')
    ck(len(seqs) == len(set(seqs)), f'publication sequence numbers of map -> odom messages all distinct '
       f'({len(set(seqs))} distinct of {len(seqs)}): one writer')
    if seqs:
        ck.info(f'map -> odom sequence numbers {min(seqs)}..{max(seqs)}, gaps {max(seqs) - min(seqs) + 1 - len(seqs)}')
    ck(all(len(tr) == 1 for _, tr in m2o), 'every message with map -> odom carries only that transform')
    after = tf_nodes(rec)
    added = sorted(set(after) - set(before))
    ck(added == [AMCL] and set(before) <= set(after),
       f'/tf publisher nodes: before localization {before}, now {after}; added {added}')
    ck.info(f'/tf writers of {AMCL}: {sum(1 for p in rec.get_publishers_info_by_topic("/tf") if p.node_name == AMCL)}')
    ck(not any(p == 'map' and c == 'odom' for p, c in tf_static), 'map -> odom never on /tf_static')
    stamps = [st for _, tr in m2o for p, c, st in tr if p == 'map']
    ok = bool(stamps) and all(abs(st * 1e-9 - sim1) < 30.0 for st in stamps[-10:])
    last = f'{stamps[-1] * 1e-9:.3f}' if stamps else 'none'
    ck(ok, f'map -> odom stamps are simulation time (last {last} s, sim clock {sim1:.3f} s)')
    # 7. TF tree
    parents = {}
    for p, c in [(p, c) for _, tr in tf for p, c, _ in tr] + tf_static:
        parents.setdefault(c, set()).add(p)
    multi = {c: sorted(ps) for c, ps in parents.items() if len(ps) > 1}
    ck(not multi, f'every frame has one parent ({len(parents)} child frames; multiple parents: {multi})')
    for p, c in CHAIN:
        ck(parents.get(c) == {p}, f'{p} -> {c}')
    try:
        rec.buffer.lookup_transform('map', 'laser_frame', Time())
        ok, err = True, ''
    except Exception as exc:  # noqa: BLE001 - reported
        ok, err = False, f': {type(exc).__name__}: {exc}'
    ck(ok, f'map -> laser_frame resolves through the tree{err}')
    # 8. /amcl_pose
    pubs = [(p.node_name, p.topic_type) for p in rec.get_publishers_info_by_topic('/amcl_pose')]
    ck(pubs == [(AMCL, 'geometry_msgs/msg/PoseWithCovarianceStamped')], f'/amcl_pose publishers: {pubs}')
    lastp = poses[-1] if poses else None
    if lastp:
        c = lastp.pose.covariance
        ok = lastp.header.frame_id == 'map' and all(math.isfinite(c[i]) and c[i] > 0 for i in (0, 7, 35))
        ck(ok, f'/amcl_pose after the drive: frame {lastp.header.frame_id!r}, {pose_text(lastp)}')
    else:
        ck(False, '/amcl_pose: no message received')
    ck.info(f'/amcl_pose messages received: {len(poses)}')
    ck.info(f'drive: {sim1 - sim0:.2f} s simulation time in {wall1 - wall0:.2f} s wall, RTF {rtf:.2f}')
    return rtf


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    if mode not in ('pre', 'main') or len(sys.argv) < 4:
        print(__doc__)
        return 2
    rclpy.init()
    rec = Rec()
    ex = M2.SingleThreadedExecutor()
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()
    ck = Check()
    rtf = None
    print(f'# TEST-M6-02 check mode={mode}, wall {time.strftime("%F %T %Z")}', flush=True)
    try:
        if not wait(lambda: rec.now_s() > 0, 60):
            print('# no /clock within 60 s: INVALID RUN')
            return 2
        if mode == 'pre':
            pre(rec, ck, sys.argv[2])
        else:
            rtf = main_check(rec, ck, sys.argv[2], sys.argv[3])
    finally:
        spin.stop(rec)
    if rtf is not None and rtf < 0.5:
        print(f'# RTF {rtf:.2f} < 0.5: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"FAIL" if ck.fail else "PASS"}')
    return 1 if ck.fail else 0


if __name__ == '__main__':
    sys.exit(main())
