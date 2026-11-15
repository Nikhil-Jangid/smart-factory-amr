#!/usr/bin/env python3
"""TEST-M5-02: SLAM interface check (REQ-M5-02, -03; docs/testing/test_plan.md §10; M5 Task A).

Usage (the simulation runs: sim.launch.py sensors:=true world:=mapping_arena.sdf; same ROS_DOMAIN_ID):
    python3 TEST-M5-02_interface_check.py pre  <state.json>   before slam.launch.py is started
    python3 TEST-M5-02_interface_check.py main <state.json>   after slam.launch.py is started
Run by docs/evidence/M5/TEST-M5-02_procedure.sh. Exit 0 = all PASS, 1 = a FAIL, 2 = invalid run (RTF < 0.5 or
no simulation clock).

pre (5 s of simulation time, SLAM not running): records the nodes that publish /tf and checks that nobody publishes
map -> odom and nobody publishes /map yet. The node list is saved to <state.json> for the main step.

main:
  1. SLAM node /slam_toolbox in lifecycle state 'active' (service get_state), within 60 s.
  2. Its parameters (read after the drive, see main_check): use_sim_time true; max_laser_range 12.0 (DEC-048).
     The minimum range: SLAM Toolbox 2.8.5 has no min_laser_range parameter and takes the minimum range from the
     scan message (TS-038), so the check is /scan range_min = 0.12 m (DEC-031).
  3. /scan: slam_toolbox is a subscriber (sensor_msgs/msg/LaserScan).
  4. /map: exactly one publisher, slam_toolbox, nav_msgs/msg/OccupancyGrid; a received map has frame_id 'map' and
     resolution 0.05 m.
  5. A short drive (0.25 m/s for 4 s, 0.5 rad/s for 3.2 s, stop 2 s; TwistStamped on /cmd_vel at 20 Hz, sim-time
     stamps, as tools/demo_drive.py) while /tf, /tf_static, /scan, /map and the pose-graph markers are recorded.
  6. Exactly one publisher of map -> odom. rclpy (Jazzy) does not give the publisher GID of a received message, so
     the check uses what it does give (probed 2026-11-15): the publication sequence number, which every DDS writer
     counts on its own from 1. Two writers of map -> odom would repeat sequence numbers. The writer is attributed to
     slam_toolbox by comparison with the pre step: the only node added to the /tf publishers is slam_toolbox, and
     map -> odom did not exist before it started. Also: each message with map -> odom carries only that transform;
     /tf_static never carries it; the stamps are simulation time.
  7. TF tree: every frame has exactly one parent over all /tf and /tf_static messages; the chain is
     map -> odom -> base_footprint -> base_link -> lidar_mount_link -> laser_frame; map -> laser_frame resolves.
  INFO (logged, no criterion): scans received and their rate, pose-graph nodes, /map messages, sequence gaps, RTF.
  Dropped scans: SLAM Toolbox reports them in its own log (TF message filter); the procedure counts those lines.
"""
import importlib.util
import json
import math
import os
import sys
import threading
import time

_spec = importlib.util.spec_from_file_location(
    'M2', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'M2', 'TEST-M2_motion_measure.py'))
M2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M2)  # Spinner (TS-030), rclpy, SingleThreadedExecutor (TS-013)
rclpy = M2.rclpy

from geometry_msgs.msg import TwistStamped  # noqa: E402
from lifecycle_msgs.srv import GetState  # noqa: E402
from nav_msgs.msg import OccupancyGrid  # noqa: E402
from rcl_interfaces.srv import GetParameters, ListParameters  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402
from rclpy.time import Time  # noqa: E402
from sensor_msgs.msg import LaserScan  # noqa: E402
from tf2_msgs.msg import TFMessage  # noqa: E402
from tf2_ros import Buffer, TransformListener  # noqa: E402
from visualization_msgs.msg import MarkerArray  # noqa: E402

SLAM = 'slam_toolbox'
CHAIN = [('map', 'odom'), ('odom', 'base_footprint'), ('base_footprint', 'base_link'),
         ('base_link', 'lidar_mount_link'), ('lidar_mount_link', 'laser_frame')]
LATCHED = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
TF_STATIC_QOS = QoSProfile(depth=100, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)


class Rec(Node):
    def __init__(self):
        super().__init__('test_m5_02', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.lock = threading.Lock()
        self.tf = []          # (publication_sequence_number, [(parent, child, stamp_ns)])
        self.tf_static = []   # [(parent, child)]
        self.scans = 0
        self.range_min = None
        self.maps = []        # (frame_id, resolution, width, height)
        self.graph = None
        self.create_subscription(TFMessage, '/tf', self.on_tf, 100)
        self.create_subscription(TFMessage, '/tf_static', self.on_tf_static, TF_STATIC_QOS)
        self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.create_subscription(OccupancyGrid, '/map', self.on_map, LATCHED)
        self.create_subscription(MarkerArray, '/slam_toolbox/graph_visualization', self.on_graph, 5)
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

    def on_scan(self, msg):
        with self.lock:
            self.scans += 1
            self.range_min = msg.range_min

    def on_map(self, msg):
        with self.lock:
            self.maps.append((msg.header.frame_id, msg.info.resolution, msg.info.width, msg.info.height))

    def on_graph(self, msg):
        with self.lock:
            self.graph = msg

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


def tf_nodes(rec):
    return sorted({p.node_name for p in rec.get_publishers_info_by_topic('/tf')})


def map_to_odom(records):
    return [(seq, tr) for seq, tr in records if any(p == 'map' and c == 'odom' for p, c, _ in tr)]


def pre(rec, ck, state_path):
    wait_sim(rec, 5.0)
    nodes = tf_nodes(rec)
    with rec.lock:
        m2o = map_to_odom(rec.tf)
    ck.info(f'/tf publisher nodes before SLAM: {nodes}')
    ck(SLAM not in nodes, f'{SLAM} is not yet a /tf publisher')
    ck(not m2o, f'no map -> odom on /tf before SLAM starts ({len(m2o)} messages in 5 s of simulation time)')
    pubs = rec.get_publishers_info_by_topic('/map')
    ck(not pubs, f'no /map publisher before SLAM starts ({[p.node_name for p in pubs]})')
    json.dump({'tf_nodes': nodes}, open(state_path, 'w'))


def main_check(rec, ck, state_path):
    before = json.load(open(state_path))['tf_nodes']
    # 1. lifecycle state
    st = None
    t_end = time.monotonic() + 60
    while time.monotonic() < t_end:
        r = call(rec, GetState, f'/{SLAM}/get_state', GetState.Request(), 5.0)
        st = r.current_state.label if r else None
        if st == 'active':
            break
        time.sleep(0.5)
    ck(st == 'active', f'/{SLAM} lifecycle state: {st}')
    # 3. /scan subscription
    subs = [(s.node_name, s.topic_type) for s in rec.get_subscriptions_info_by_topic('/scan')]
    ck((SLAM, 'sensor_msgs/msg/LaserScan') in subs, f'/scan subscribers: {sorted(subs)}')
    # 4. /map publisher and message
    pubs = [(p.node_name, p.topic_type) for p in rec.get_publishers_info_by_topic('/map')]
    ck(pubs == [(SLAM, 'nav_msgs/msg/OccupancyGrid')], f'/map publishers: {pubs}')
    wait(lambda: rec.maps, 30)
    with rec.lock:
        m = rec.maps[0] if rec.maps else None
    ck(m is not None and m[0] == 'map' and abs(m[1] - 0.05) < 1e-6,
       f'/map message: frame_id {m[0] if m else None!r}, resolution {m[1] if m else None} m'
       + (f', {m[2]} x {m[3]} cells' if m else ''))
    # 5. drive, recording
    with rec.lock:
        rec.tf.clear()
        rec.scans = 0
        n_maps0 = len(rec.maps)
    sim0, wall0 = rec.now_s(), time.monotonic()
    for v, w, secs in [(0.25, 0.0, 4.0), (0.0, 0.5, 3.2), (0.0, 0.0, 2.0)]:
        t_end = rec.now_s() + secs
        while rec.now_s() < t_end and time.monotonic() - wall0 < 120:
            rec.send(v, w)
            time.sleep(0.05)
    rec.send(0.0, 0.0)
    sim1, wall1 = rec.now_s(), time.monotonic()
    rtf = (sim1 - sim0) / max(wall1 - wall0, 1e-9)
    with rec.lock:
        tf = list(rec.tf)
        tf_static = list(rec.tf_static)
        scans, n_maps, graph = rec.scans, len(rec.maps) - n_maps0, rec.graph
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
    ck(added == [SLAM] and set(before) <= set(after),
       f'/tf publisher nodes: before SLAM {before}, now {after}; added {added}')
    ck(not any(p == 'map' and c == 'odom' for p, c in tf_static), 'map -> odom never on /tf_static')
    stamps = [st for _, tr in m2o for p, c, st in tr if p == 'map']
    ok = bool(stamps) and all(abs(st * 1e-9 - sim1) < 30.0 for st in stamps[-10:])
    last = f'{stamps[-1] * 1e-9:.3f}' if stamps else 'none'
    ck(ok, f'map -> odom stamps are simulation time (last {last} s, sim clock {sim1:.3f} s)')
    # 2. parameters, read after the drive: SLAM Toolbox declares max_laser_range only when it registers the LiDAR
    # from the first scan (dry run 2026-11-15: a request right after activation failed); retried for up to 20 s.
    # A request that names an undeclared parameter returns no values at all (TS-038), so only declared names.
    names = ['use_sim_time', 'max_laser_range']
    vals = {}
    t_end = time.monotonic() + 20
    while time.monotonic() < t_end and not vals:
        r = call(rec, GetParameters, f'/{SLAM}/get_parameters', GetParameters.Request(names=names))
        if r and len(r.values) == len(names):
            for n, v in zip(names, r.values):
                vals[n] = v.bool_value if v.type == 1 else v.double_value if v.type == 3 else None
        else:
            time.sleep(1.0)
    ck(vals.get('use_sim_time') is True, f'use_sim_time = {vals.get("use_sim_time")}')
    ck(vals.get('max_laser_range') == 12.0, f'max_laser_range = {vals.get("max_laser_range")} (DEC-048: 12.0)')
    with rec.lock:
        rmin = rec.range_min
    ck(rmin is not None and abs(rmin - 0.12) < 1e-6,
       f'/scan range_min = {rmin} m (DEC-031: 0.12; SLAM Toolbox takes its minimum range from the scan, TS-038)')
    r = call(rec, ListParameters, f'/{SLAM}/list_parameters', ListParameters.Request())
    declared = sorted(r.result.names) if r else None
    ck.info(f'min_laser_range declared by {SLAM}: {"min_laser_range" in declared if declared is not None else None} '
            f'(not read by SLAM Toolbox 2.8.5, TS-038)')
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
    # INFO
    nodes = sum(1 for mk in graph.markers if mk.ns == SLAM and mk.type == 2) if graph else 0
    ck.info(f'drive: {sim1 - sim0:.2f} s simulation time in {wall1 - wall0:.2f} s wall, RTF {rtf:.2f}')
    ck.info(f'scans received during the drive: {scans} ({scans / max(sim1 - sim0, 1e-9):.2f} Hz); '
            f'/map messages: {n_maps}; pose-graph nodes (last marker array): {nodes}')
    return rtf


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
    ck = Check()
    rtf = None
    print(f'# TEST-M5-02 check mode={mode}, wall {time.strftime("%F %T %Z")}', flush=True)
    try:
        if not wait(lambda: rec.now_s() > 0, 60):
            print('# no /clock within 60 s: INVALID RUN')
            return 2
        if mode == 'pre':
            pre(rec, ck, sys.argv[2])
        else:
            rtf = main_check(rec, ck, sys.argv[2])
    finally:
        spin.stop(rec)
    if rtf is not None and rtf < 0.5:
        print(f'# RTF {rtf:.2f} < 0.5: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"FAIL" if ck.fail else "PASS"}')
    return 1 if ck.fail else 0


if __name__ == '__main__':
    sys.exit(main())
