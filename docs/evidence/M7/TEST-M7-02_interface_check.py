#!/usr/bin/env python3
"""TEST-M7-02: navigation interface check (REQ-M7-01, -02, -03; docs/testing/test_plan.md §12; M7 Task A).

Usage (running, same ROS_DOMAIN_ID: sim.launch.py sensors:=true world:=mapping_arena.sdf, localization.launch.py,
navigation.launch.py):
    python3 TEST-M7-02_interface_check.py
Run by docs/evidence/M7/TEST-M7-02_procedure.sh.
Exit 0 = all PASS, 1 = a FAIL, 2 = invalid run (RTF < 0.5 or no simulation clock).

Checks:
  1. Lifecycle (REQ-M7-01): planner_server, controller_server, behavior_server, bt_navigator and velocity_smoother
     'active' within 90 s (service get_state); map_server, map_server_amcl and amcl still 'active'.
  2. Parameters: use_sim_time true on the five servers and both costmap nodes (REQ-M7-01). The M7 values of
     config/nav2.yaml as read back from the running nodes: RPP controller (DEC-067), NavFn (DEC-068) with tolerance 0.0 and allow_unknown false
     (DEC-077, from R1), goal checker
     0.10 m / 0.10 rad (DEC-073), stamped commands on controller, behaviors and smoother, smoother limits = DEC-025,
     smoother stamps its own output (TS-050), odometry /diff_drive_controller/odom (DEC-070), behaviors 'wait' only,
     the package's own behavior trees (DEC-071).
  3. Map (REQ-M7-01, DEC-062): the global costmap subscribes to /map; no costmap subscribes to /map_amcl; the global
     costmap is in frame 'map' with the size, resolution and origin of /map (its static layer sized it from /map).
  4. Footprint (REQ-M7-02, DEC-069): the 'footprint' parameter of both costmaps equals CALC-M7-01. The published
     footprints (/local_costmap/published_footprint, /global_costmap/published_footprint), transformed into
     base_link, equal CALC-M7-01 padded by the costmap's footprint_padding (Nav2 moves each vertex outwards by the
     padding in x and in y), within 0.005 m (transform timing).
  5. Command path (REQ-M7-03): /cmd_vel has one publisher, velocity_smoother, type geometry_msgs/msg/TwistStamped,
     and cmd_vel_guard subscribes; cmd_vel_nav is published by controller_server and behavior_server and read only by
     velocity_smoother; /diff_drive_controller/cmd_vel is published only by cmd_vel_guard.
  6. A short navigation goal, (1.0, 0.0, 0 deg) in 'map' (2 m from any mapped wall; interface check, not one of the
     DEC-074 goals), through the NavigateToPose action while /cmd_vel and the guard output are recorded:
     the goal SUCCEEDS; non-zero commands are sent; every /cmd_vel stamp is simulation time within the guard window
     (|clock - stamp| <= 0.5 s, DEC-029); every /cmd_vel message is forwarded by the guard (matched by velocity and
     the guard's stamp rule min(stamp, clock), from R1, TS-052; zero drops); every command is within DEC-025 (-0.25 <= v <= 0.5 m/s, |w| <= 1.0 rad/s).
  INFO (logged, no criterion): footprint_padding, the local costmap's layers, stamp ages, command extremes, final
  pose in 'map', RTF.
"""
import importlib.util
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

from action_msgs.msg import GoalStatus  # noqa: E402
from geometry_msgs.msg import PolygonStamped, TwistStamped  # noqa: E402
from lifecycle_msgs.srv import GetState  # noqa: E402
from nav2_msgs.action import NavigateToPose  # noqa: E402
from nav_msgs.msg import OccupancyGrid  # noqa: E402
from rcl_interfaces.srv import GetParameters  # noqa: E402
from rclpy.action import ActionClient  # noqa: E402
from rclpy.duration import Duration  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402
from rclpy.time import Time  # noqa: E402
from tf2_ros import Buffer, TransformListener  # noqa: E402

SERVERS = ['planner_server', 'controller_server', 'behavior_server', 'bt_navigator', 'velocity_smoother']
LOCALIZATION = ['map_server', 'map_server_amcl', 'amcl']
COSTMAPS = {'local': 'local_costmap/local_costmap', 'global': 'global_costmap/global_costmap'}
CALC_M7_01 = [(0.125, 0.175), (0.075, 0.2175), (-0.075, 0.2175), (-0.325, 0.175), (-0.385, 0.025), (-0.385, -0.025),
              (-0.325, -0.175), (-0.075, -0.2175), (0.075, -0.2175), (0.125, -0.175)]  # m, base_link (DEC-069)
GOAL = (1.0, 0.0, 0.0)  # x m, y m, yaw rad in 'map'
GUARD_WINDOW = 0.5  # s, cmd_vel_guard cmd_vel_timeout (DEC-029)
CLAMP_MAX_NS = 10_000_000  # ns, largest guard stamp clamp accepted as forwarded (TS-052)
V_MAX, V_MIN, W_MAX = 0.5, -0.25, 1.0  # DEC-025
EPS = 1e-6
STAMPED = {'enable_stamped_cmd_vel': True}
PARAMS = {  # node: {name: expected}; floats compared within 1e-9, lists element-wise
    'controller_server': {**STAMPED, 'odom_topic': '/diff_drive_controller/odom',
                          'FollowPath.plugin': 'nav2_regulated_pure_pursuit_controller::RegulatedPurePursuitController',
                          'FollowPath.desired_linear_vel': 0.30, 'FollowPath.allow_reversing': False,
                          'FollowPath.rotate_to_heading_angular_vel': 1.0, 'FollowPath.max_angular_accel': 2.0,
                          'general_goal_checker.xy_goal_tolerance': 0.10,
                          'general_goal_checker.yaw_goal_tolerance': 0.10},
    'planner_server': {'GridBased.plugin': 'nav2_navfn_planner::NavfnPlanner', 'GridBased.tolerance': 0.0,
                       'GridBased.allow_unknown': False},
    'behavior_server': {**STAMPED, 'behavior_plugins': ['wait']},
    'velocity_smoother': {**STAMPED, 'stamp_smoothed_velocity_with_smoothing_time': True,
                          'odom_topic': '/diff_drive_controller/odom',
                          'max_velocity': [0.5, 0.0, 1.0], 'min_velocity': [-0.25, 0.0, -1.0],
                          'max_accel': [0.5, 0.0, 2.0], 'max_decel': [-1.0, 0.0, -2.0]},
    'bt_navigator': {'odom_topic': '/diff_drive_controller/odom'},
}
BT_FILES = {'default_nav_to_pose_bt_xml': 'amr_bringup/behavior_trees/navigate_to_pose.xml',
            'default_nav_through_poses_bt_xml': 'amr_bringup/behavior_trees/navigate_through_poses.xml'}
LATCHED = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)


class Rec(Node):
    def __init__(self):
        super().__init__('test_m7_02', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.lock = threading.Lock()
        self.recording = False
        self.cmd_in = []    # (wall receipt, clock s at receipt, stamp ns, v, w)
        self.cmd_out = []   # (stamp ns, v, w)
        self.footprints = {}  # 'local' / 'global' -> PolygonStamped (last)
        self.grids = {}       # '/map', '/global_costmap/costmap' -> OccupancyGrid (first)
        self.create_subscription(TwistStamped, '/cmd_vel', self.on_in, 100)
        self.create_subscription(TwistStamped, '/diff_drive_controller/cmd_vel', self.on_out, 100)
        for k in COSTMAPS:
            self.create_subscription(PolygonStamped, f'/{k}_costmap/published_footprint',
                                     lambda m, k=k: self.on_fp(k, m), 10)
        for topic in ('/map', '/global_costmap/costmap'):
            self.create_subscription(OccupancyGrid, topic, lambda m, t=topic: self.on_grid(t, m), LATCHED)
        self.nav = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_in(self, m):
        with self.lock:
            if self.recording:
                self.cmd_in.append((time.monotonic(), self.now_s(), m.header.stamp.sec * 10**9 + m.header.stamp.nanosec,
                                    m.twist.linear.x, m.twist.angular.z))

    def on_out(self, m):
        with self.lock:
            if self.recording:
                self.cmd_out.append((m.header.stamp.sec * 10**9 + m.header.stamp.nanosec,
                                     m.twist.linear.x, m.twist.angular.z))

    def on_fp(self, k, m):
        with self.lock:
            self.footprints[k] = m

    def on_grid(self, topic, m):
        with self.lock:
            self.grids.setdefault(topic, m)


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
    conv = {1: 'bool_value', 2: 'integer_value', 3: 'double_value', 4: 'string_value', 7: 'integer_array_value',
            8: 'double_array_value', 9: 'string_array_value'}
    out = {}
    for n, v in zip(names, r.values):
        x = getattr(v, conv[v.type]) if v.type in conv else None
        out[n] = list(x) if v.type in (7, 8, 9) else x
    return out


def same(got, exp):
    if isinstance(exp, float):
        return isinstance(got, float) and abs(got - exp) < 1e-9
    if isinstance(exp, list) and exp and isinstance(exp[0], float):
        return isinstance(got, list) and len(got) == len(exp) and all(abs(a - b) < 1e-9 for a, b in zip(got, exp))
    return got == exp


def padded(points, pad):
    """nav2_costmap_2d padFootprint: every coordinate moved away from the origin by pad (sign of the coordinate)."""
    return [(x + math.copysign(pad, x), y + math.copysign(pad, y)) for x, y in points]


def to_base_link(rec, msg):
    """The polygon's points in base_link, using the transform at the message stamp (or None)."""
    try:
        t = rec.buffer.lookup_transform('base_link', msg.header.frame_id, Time.from_msg(msg.header.stamp),
                                        timeout=Duration(seconds=2.0))
    except Exception:  # noqa: BLE001 - reported as no transform
        return None
    q, p = t.transform.rotation, t.transform.translation
    yaw = math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
    c, s = math.cos(yaw), math.sin(yaw)
    return [(c * pt.x - s * pt.y + p.x, s * pt.x + c * pt.y + p.y) for pt in msg.polygon.points]


def topic_nodes(infos):
    return sorted((i.node_name, i.topic_type) for i in infos)


def check(rec, ck):
    # 1. lifecycle states
    names = SERVERS + LOCALIZATION
    states, t_end = {}, time.monotonic() + 90
    while time.monotonic() < t_end:
        for n in names:
            if states.get(n) != 'active':
                r = call(rec, GetState, f'/{n}/get_state', GetState.Request(), 5.0)
                states[n] = r.current_state.label if r else None
        if all(states.get(n) == 'active' for n in names):
            break
        time.sleep(0.5)
    for n in names:
        ck(states.get(n) == 'active', f'/{n} lifecycle state: {states.get(n)}')
    # 2. parameters
    for n in SERVERS + list(COSTMAPS.values()):
        v = params(rec, n, ['use_sim_time'])
        ck(v.get('use_sim_time') is True, f'/{n} use_sim_time = {v.get("use_sim_time")}')
    for n, exp in PARAMS.items():
        v = params(rec, n, list(exp))
        for name, e in exp.items():
            ck(same(v.get(name), e), f'/{n} {name} = {v.get(name)!r} (expected {e!r})')
    v = params(rec, 'bt_navigator', list(BT_FILES))
    for name, tail in BT_FILES.items():
        got = v.get(name) or ''
        ck(got.endswith(tail) and os.path.isfile(got), f'/bt_navigator {name} = <share>/{tail if got.endswith(tail) else got!r} '
           f'(file exists: {os.path.isfile(got)})')
    # 3. map
    subs = {t: sorted(s.node_name for s in rec.get_subscriptions_info_by_topic(t)) for t in ('/map', '/map_amcl')}
    ck('global_costmap' in subs['/map'], f'/map subscribers: {subs["/map"]} (global_costmap expected)')
    ck(not any('costmap' in n for n in subs['/map_amcl']), f'/map_amcl subscribers: {subs["/map_amcl"]} (no costmap)')
    wait(lambda: len(rec.grids) == 2, 30)
    with rec.lock:
        m, g = rec.grids.get('/map'), rec.grids.get('/global_costmap/costmap')
    if m and g:
        mo, go = m.info.origin.position, g.info.origin.position
        ok = (g.header.frame_id == 'map' and (g.info.width, g.info.height) == (m.info.width, m.info.height)
              and abs(g.info.resolution - m.info.resolution) < 1e-6 and abs(go.x - mo.x) < 1e-6
              and abs(go.y - mo.y) < 1e-6)
        ck(ok, f'/global_costmap/costmap: frame {g.header.frame_id!r}, {g.info.width} x {g.info.height} cells, resolution '
           f'{g.info.resolution:.3f} m, origin ({go.x:.4f}, {go.y:.4f}); /map: {m.info.width} x {m.info.height}, '
           f'{m.info.resolution:.3f} m, ({mo.x:.4f}, {mo.y:.4f})')
    else:
        ck(False, f'/map received: {m is not None}; /global_costmap/costmap received: {g is not None} (30 s)')
    lp = params(rec, COSTMAPS['local'], ['plugins'])
    gp = params(rec, COSTMAPS['global'], ['plugins'])
    ck.info(f'costmap layers: local {lp.get("plugins")}, global {gp.get("plugins")}')
    # 4. footprint
    for k, n in COSTMAPS.items():
        v = params(rec, n, ['footprint', 'footprint_padding'])
        try:
            fp = [tuple(p) for p in yaml.safe_load(v.get('footprint') or '[]')]
        except yaml.YAMLError:
            fp = []
        ok = len(fp) == len(CALC_M7_01) and all(abs(a - b) < 1e-9 for p, q in zip(fp, CALC_M7_01) for a, b in zip(p, q))
        ck(ok, f'/{n} footprint parameter equals CALC-M7-01 ({len(fp)} vertices)')
        pad = v.get('footprint_padding')
        ck.info(f'/{n} footprint_padding = {pad} m (installed default, kept)')
        wait(lambda: k in rec.footprints, 15)
        with rec.lock:
            msg = rec.footprints.get(k)
        pts = to_base_link(rec, msg) if msg else None
        exp = padded(CALC_M7_01, pad or 0.0)
        if pts and len(pts) == len(exp):
            err = max(math.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(pts, exp))
            ck(err <= 0.005, f'/{k}_costmap/published_footprint (frame {msg.header.frame_id!r}) in base_link equals '
               f'CALC-M7-01 padded by {pad} m: largest vertex difference {err:.4f} m')
        else:
            ck(False, f'/{k}_costmap/published_footprint: message {msg is not None}, '
               f'vertices {len(pts) if pts else None} (expected {len(exp)})')
    # 5. command path
    pubs = topic_nodes(rec.get_publishers_info_by_topic('/cmd_vel'))
    ck(pubs == [('velocity_smoother', 'geometry_msgs/msg/TwistStamped')], f'/cmd_vel publishers: {pubs}')
    s = sorted(i.node_name for i in rec.get_subscriptions_info_by_topic('/cmd_vel') if i.node_name != rec.get_name())
    ck(s == ['cmd_vel_guard'], f'/cmd_vel subscribers (besides this checker): {s}')
    pubs = topic_nodes(rec.get_publishers_info_by_topic('/cmd_vel_nav'))
    ck(pubs == [('behavior_server', 'geometry_msgs/msg/TwistStamped'), ('controller_server', 'geometry_msgs/msg/TwistStamped')],
       f'/cmd_vel_nav publishers: {pubs}')
    s = sorted(i.node_name for i in rec.get_subscriptions_info_by_topic('/cmd_vel_nav'))
    ck(s == ['velocity_smoother'], f'/cmd_vel_nav subscribers: {s}')
    pubs = topic_nodes(rec.get_publishers_info_by_topic('/diff_drive_controller/cmd_vel'))
    ck(pubs == [('cmd_vel_guard', 'geometry_msgs/msg/TwistStamped')], f'/diff_drive_controller/cmd_vel publishers: {pubs}')
    # 6. navigation goal
    ck(rec.nav.wait_for_server(timeout_sec=30.0), 'NavigateToPose action server /navigate_to_pose available')
    goal = NavigateToPose.Goal()
    goal.pose.header.frame_id = 'map'
    goal.pose.header.stamp = rec.get_clock().now().to_msg()
    goal.pose.pose.position.x, goal.pose.pose.position.y = GOAL[0], GOAL[1]
    goal.pose.pose.orientation.z, goal.pose.pose.orientation.w = math.sin(GOAL[2] / 2), math.cos(GOAL[2] / 2)
    with rec.lock:
        rec.recording = True
    sim0, wall0 = rec.now_s(), time.monotonic()
    fut = rec.nav.send_goal_async(goal)
    wait(fut.done, 30)
    handle = fut.result() if fut.done() else None
    status = None
    if handle and handle.accepted:
        rfut = handle.get_result_async()
        wait(rfut.done, 180)
        status = rfut.result().status if rfut.done() else None
    sim1, wall1 = rec.now_s(), time.monotonic()
    wait(lambda: False, 1.0)  # let the last forwarded messages arrive
    with rec.lock:
        rec.recording = False
        cin, cout = list(rec.cmd_in), list(rec.cmd_out)
    rtf = (sim1 - sim0) / max(wall1 - wall0, 1e-9)
    label = {GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED', GoalStatus.STATUS_ABORTED: 'ABORTED',
             GoalStatus.STATUS_CANCELED: 'CANCELED'}.get(status, str(status))
    ck(bool(handle and handle.accepted) and status == GoalStatus.STATUS_SUCCEEDED,
       f'goal ({GOAL[0]}, {GOAL[1]}, {math.degrees(GOAL[2]):.0f} deg): accepted {bool(handle and handle.accepted)}, '
       f'result {label}')
    nonzero = [c for c in cin if abs(c[3]) > EPS or abs(c[4]) > EPS]
    ck(len(nonzero) > 0, f'/cmd_vel messages during the goal: {len(cin)}, non-zero: {len(nonzero)}')
    ages = [c[1] - c[2] * 1e-9 for c in cin]
    ck(bool(ages) and all(abs(a) <= GUARD_WINDOW for a in ages),
       f'every /cmd_vel stamp is simulation time within the guard window: |clock - stamp| '
       f'{min(map(abs, ages)) if ages else float("nan"):.3f}..{max(map(abs, ages)) if ages else float("nan"):.3f} s '
       f'(<= {GUARD_WINDOW} s)')
    # The guard forwards stamp = min(stamp, guard clock) (cmd_vel_guard.cpp): a forwarded stamp may be up to a few ms
    # before the input stamp (TS-052). Match one-to-one by identical velocity and 0 <= input - output stamp <= 10 ms.
    pool, missed, clamped = {}, [], 0
    for o in cout:
        pool.setdefault((o[1], o[2]), []).append(o[0])
    for c in cin:
        cands = pool.get((c[3], c[4]), [])
        ok = [s for s in cands if 0 <= c[2] - s <= CLAMP_MAX_NS]
        if not ok:
            missed.append(c)
            continue
        cands.remove(max(ok))
        clamped += c[2] != max(ok)
    ck(not missed, f'guard forwarded every /cmd_vel message: {len(cin) - len(missed)} of {len(cin)} matched by velocity '
       f'and the guard stamp rule ({clamped} with the stamp clamped; {len(cout)} guard outputs)')
    vs, ws = [c[3] for c in cin], [c[4] for c in cin]
    ok = bool(cin) and min(vs) >= V_MIN - EPS and max(vs) <= V_MAX + EPS and max(map(abs, ws)) <= W_MAX + EPS
    ck(ok, f'commands within DEC-025: v {min(vs, default=0):.3f}..{max(vs, default=0):.3f} m/s '
       f'(limits {V_MIN}..{V_MAX}), |w| max {max(map(abs, ws), default=0):.3f} rad/s (limit {W_MAX})')
    try:
        t = rec.buffer.lookup_transform('map', 'base_footprint', Time())
        q = t.transform.rotation
        ck.info(f'final pose in map (AMCL estimate): ({t.transform.translation.x:+.3f}, {t.transform.translation.y:+.3f}) m, '
                f'yaw {math.degrees(math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y ** 2 + q.z ** 2))):+.2f} deg')
    except Exception as exc:  # noqa: BLE001 - informational
        ck.info(f'final pose: no map -> base_footprint ({type(exc).__name__})')
    ck.info(f'goal: {sim1 - sim0:.2f} s simulation time in {wall1 - wall0:.2f} s wall, RTF {rtf:.2f}')
    return rtf


def main():
    rclpy.init()
    rec = Rec()
    ex = M2.SingleThreadedExecutor()
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()
    ck = Check()
    rtf = None
    print(f'# TEST-M7-02 check, wall {time.strftime("%F %T %Z")}', flush=True)
    try:
        if not wait(lambda: rec.now_s() > 0, 60):
            print('# no /clock within 60 s: INVALID RUN')
            return 2
        rtf = check(rec, ck)
    finally:
        spin.stop(rec)
    if rtf is not None and rtf < 0.5:
        print(f'# RTF {rtf:.2f} < 0.5: INVALID RUN (repeat)')
        return 2
    print(f'# result: {"FAIL" if ck.fail else "PASS"}')
    return 1 if ck.fail else 0


if __name__ == '__main__':
    sys.exit(main())
