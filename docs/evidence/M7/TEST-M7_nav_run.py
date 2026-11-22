#!/usr/bin/env python3
"""M7 navigation harness: sends Nav2 goals and records what happens (M7 Task B; M7 plan §6, §8).

Usage (running, same ROS_DOMAIN_ID / GZ_PARTITION: sim.launch.py sensors:=true world:=mapping_arena.sdf,
localization.launch.py, navigation.launch.py):
    python3 TEST-M7_nav_run.py <prefix> --mode sequence|route|invalid|cancel
Modes (goals from TEST-M7_goals.py, the one source of truth, DEC-074/DEC-076):
    sequence  TEST-M7-03: G1 ... G6 one after another through NavigateToPose
    route     TEST-M7-04: G1 -> G3 -> G5 as one NavigateThroughPoses goal (DEC-078)
    invalid   TEST-M7-05: the goal inside P1, then the goal outside the map (NavigateToPose each)
    cancel    TEST-M7-06: NavigateToPose to G1, cancelled after >= 1.0 m of ground-truth travel
Writes (judged offline by TEST-M7_nav_check.py; nothing is judged here):
    <prefix>_track.csv  10 Hz of simulation time: ground truth (Gazebo pose of `amr`), the localization estimate
                        (TF map -> base_footprint AT THE GROUND-TRUTH STAMP, as M6, never "latest"), cumulative
                        ground-truth travel, the active goal label, poses remaining (route mode)
    <prefix>_cmd.csv    every message on /cmd_vel (Nav2's output) and /diff_drive_controller/cmd_vel (the guard's
                        output): topic, clock at receipt, header stamp, v, w
    <prefix>_goals.csv  one row per goal: target, times (sent, accepted, result, cancel requested/accepted), result
                        status, ground truth and estimate at the result and after a 2 s hold, travel, first planned
                        path length and the number of plans seen
    <prefix>_plans.csv  the first /plan published after each goal was sent (label, index, x, y)
    <prefix>_meta.json  run facts: mode, wall time, RTF, /cmd_vel publishers at start and end, missing samples
Exit 0 = run completed and recorded; 2 = invalid run (no ground truth or clock, Nav2 or AMCL not active, RTF < 0.5,
more than 2 % of the 10 Hz samples without an estimate, a goal not answered within its time limit, or the cancel not
reached). A goal that ends ABORTED is recorded, not an invalid run: the checker judges it.

Listen-only: this node publishes nothing on /cmd_vel (DEC-073 requires one publisher, the velocity smoother; the
publisher list is recorded at the start and the end). Ground truth comes from Gazebo (/world/mapping_arena/pose/info)
through the M5 subscriber; Nav2 and AMCL never see it.
"""
import argparse
import csv
import importlib.util
import json
import math
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M5 = _load('map_run', os.path.join(HERE, '..', 'M5', 'TEST-M5_map_run.py'))   # GzNode, Pose_V, WORLD_TOPIC, M2
goals = _load('goals7', os.path.join(HERE, 'TEST-M7_goals.py'))
M2, rclpy = M5.M2, M5.rclpy

from action_msgs.msg import GoalStatus  # noqa: E402
from action_msgs.srv import CancelGoal  # noqa: E402
from geometry_msgs.msg import PoseStamped, TwistStamped  # noqa: E402
from lifecycle_msgs.srv import GetState  # noqa: E402
from nav2_msgs.action import NavigateThroughPoses, NavigateToPose  # noqa: E402
from nav_msgs.msg import Path  # noqa: E402
from rclpy.action import ActionClient  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from rclpy.time import Time  # noqa: E402
from tf2_ros import Buffer, TransformListener  # noqa: E402

SAMPLE_DT = 0.1          # s of simulation time between track samples (10 Hz)
RESOLVE_AFTER = 0.3      # s: resolve a sample once the clock is this far past its stamp (M6)
MISSING_AFTER = 3.0      # s: give up on a sample (M6)
MISSING_MAX = 0.02       # fraction of missing samples above which the run is invalid (M6)
HOLD = 2.0               # s of simulation time after a result before the next goal (settled pose)
CANCEL_HOLD = 8.0        # s after the cancel is accepted: stop (<= 0.15 m) + still for 5 s (DEC-073) + margin
INVALID_LIMIT = 60.0     # s: an invalid goal must be answered within this (DEC-073)
GOAL_LIMIT = 600.0       # s of simulation time: a valid goal not answered by then makes the run invalid
NAV_NODES = ['planner_server', 'controller_server', 'behavior_server', 'bt_navigator', 'velocity_smoother', 'amcl']
STATUS = {GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED', GoalStatus.STATUS_ABORTED: 'ABORTED',
          GoalStatus.STATUS_CANCELED: 'CANCELED', GoalStatus.STATUS_UNKNOWN: 'UNKNOWN'}


def stamp(t):
    return Time(seconds=int(t), nanoseconds=int(round((t - int(t)) * 1e9)))


def pose_msg(node, x, y, yaw_deg):
    p = PoseStamped()
    p.header.frame_id = 'map'
    p.header.stamp = node.get_clock().now().to_msg()
    p.pose.position.x, p.pose.position.y = float(x), float(y)
    yaw = math.radians(yaw_deg)
    p.pose.orientation.z, p.pose.orientation.w = math.sin(yaw / 2), math.cos(yaw / 2)
    return p


class Rec(Node):
    """Listen-only recorder: Gazebo ground truth, TF, /cmd_vel and the guard output, /plan, route feedback."""

    def __init__(self):
        super().__init__('test_m7_nav_run', parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.lock = threading.Lock()
        self.cur = None              # (t, x, y, yaw), latest ground truth
        self.travel, self.last_xy = 0.0, None
        self.next_t = None           # next 10 Hz sample time; None = not sampling
        self.samples = []            # pending (t, x, y, yaw, travel, label, remaining)
        self.label, self.remaining = '', ''
        self.cmd = []                # (topic, clock at receipt, stamp s, v, w)
        self.plans = {}              # label -> first Path after acceptance
        self.plan_count = {}
        self.want_plan = None        # label waiting for its first plan
        self.create_subscription(TwistStamped, '/cmd_vel', lambda m: self.on_cmd('cmd_vel', m), 200)
        self.create_subscription(TwistStamped, '/diff_drive_controller/cmd_vel', lambda m: self.on_cmd('guard', m), 200)
        self.create_subscription(Path, '/plan', self.on_plan, 10)
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.to_pose = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.through = ActionClient(self, NavigateThroughPoses, 'navigate_through_poses')
        self.gz = M5.GzNode()
        self.gz.subscribe(M5.Pose_V, M5.WORLD_TOPIC, self.on_pose)

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_pose(self, msg):
        t = msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9
        for p in msg.pose:
            if p.name == 'amr':
                yaw = M2.rpy(p.orientation.w, p.orientation.x, p.orientation.y, p.orientation.z)[2]
                x, y = p.position.x, p.position.y
                with self.lock:
                    if self.last_xy is not None:
                        self.travel += math.hypot(x - self.last_xy[0], y - self.last_xy[1])
                    self.last_xy = (x, y)
                    self.cur = (t, x, y, yaw)
                    if self.next_t is not None and t >= self.next_t:
                        self.samples.append((t, x, y, yaw, self.travel, self.label, self.remaining))
                        self.next_t = t + SAMPLE_DT

    def truth(self):
        with self.lock:
            return self.cur, self.travel

    def on_cmd(self, topic, m):
        clock = self.now()
        with self.lock:
            if self.next_t is not None:
                self.cmd.append((topic, clock, m.header.stamp.sec + m.header.stamp.nanosec * 1e-9,
                                 m.twist.linear.x, m.twist.angular.z))

    def on_plan(self, m):
        with self.lock:
            lbl = self.label
            if lbl:
                self.plan_count[lbl] = self.plan_count.get(lbl, 0) + 1
            if self.want_plan and self.want_plan not in self.plans:
                self.plans[self.want_plan] = [(p.pose.position.x, p.pose.position.y) for p in m.poses]
                self.want_plan = None

    def set_label(self, label, remaining=''):
        with self.lock:
            self.label, self.remaining = label, remaining

    def tf_at(self, parent, child, t):
        tr = self.buffer.lookup_transform(parent, child, stamp(t))
        q = tr.transform.rotation
        return tr.transform.translation.x, tr.transform.translation.y, M2.rpy(q.w, q.x, q.y, q.z)[2]


def wait(pred, wall_s, tick=None):
    t_end = time.monotonic() + wall_s
    while time.monotonic() < t_end:
        if pred():
            return True
        if tick:
            tick()
        time.sleep(0.05)
    return pred()


class Run:
    def __init__(self, rec, prefix, mode):
        self.rec, self.prefix, self.mode = rec, prefix, mode
        self.track, self.missing, self.rows = [], 0, []
        self.invalid = False

    # --- recording -----------------------------------------------------------------------------------------------
    def resolve(self, final=False):
        now = self.rec.now()
        with self.rec.lock:
            pending = list(self.rec.samples)
        done = []
        for s in pending:
            if not final and now - s[0] < RESOLVE_AFTER:
                continue
            try:
                ex, ey, eyaw = self.rec.tf_at('map', 'base_footprint', s[0])
                self.track.append(list(s[:5]) + [ex, ey, eyaw, s[5], s[6]])
                done.append(s)
            except Exception:  # noqa: BLE001 - data not there yet, or never
                if final or now - s[0] > MISSING_AFTER:
                    self.missing += 1
                    done.append(s)
        if done:
            with self.rec.lock:
                self.rec.samples = [s for s in self.rec.samples if s not in done]

    def hold(self, seconds):
        t_end = self.rec.now() + seconds
        wait(lambda: self.rec.now() >= t_end, seconds * 20 + 10, self.resolve)

    def estimate_at(self, t):
        t_wait = time.monotonic() + 5.0
        while time.monotonic() < t_wait:
            try:
                return self.rec.tf_at('map', 'base_footprint', t)
            except Exception:  # noqa: BLE001 - wait for the buffer
                self.resolve()
                time.sleep(0.05)
        return ('', '', '')

    def snapshot(self):
        """Ground truth now, the estimate at its stamp, and the travel."""
        (t, gx, gy, gyaw), travel = self.rec.truth()
        return [t, gx, gy, gyaw, *self.estimate_at(t), travel]

    # --- readiness -----------------------------------------------------------------------------------------------
    def wait_ready(self):
        if not wait(lambda: self.rec.truth()[0] is not None and self.rec.now() > 0, 90):
            print('# no ground truth on ' + M5.WORLD_TOPIC + ' or no /clock within 90 s')
            return False
        t_end = time.monotonic() + 120
        states = {}
        for n in NAV_NODES:
            cli = self.rec.create_client(GetState, f'/{n}/get_state')
            while time.monotonic() < t_end and states.get(n) != 'active':
                if cli.wait_for_service(timeout_sec=2.0):
                    fut = cli.call_async(GetState.Request())
                    wait(fut.done, 5)
                    states[n] = fut.result().current_state.label if fut.done() and fut.result() else None
                if states.get(n) != 'active':
                    time.sleep(0.5)
        bad = {n: s for n, s in states.items() if s != 'active'} or {n: None for n in NAV_NODES if n not in states}
        if bad:
            print(f'# not active within 120 s: {bad}')
            return False
        if not (self.rec.to_pose.wait_for_server(timeout_sec=30) and self.rec.through.wait_for_server(timeout_sec=30)):
            print('# navigation action servers not available')
            return False
        if not wait(lambda: self._tf_ok(), 60):
            print('# no TF map -> base_footprint within 60 s')
            return False
        return True

    def _tf_ok(self):
        try:
            self.rec.buffer.lookup_transform('map', 'base_footprint', Time())
            return True
        except Exception:  # noqa: BLE001 - not yet
            return False

    # --- goals ---------------------------------------------------------------------------------------------------
    def send(self, label, client, goal_msg, limit, cancel_after=None):
        """Send one goal, record it; returns False if the run became invalid."""
        row = {'label': label, 'cancel_req_t': '', 'cancel_acc_t': '', 'cancel_travel': '', 'cancel_code': ''}
        self.rec.set_label(label, '')
        with self.rec.lock:
            self.rec.want_plan = label   # from the send: the first plan can arrive before the acceptance (dry run)
        start = self.snapshot()
        row['sent_t'] = self.rec.now()
        fb = {}

        def on_fb(m):
            r = getattr(m.feedback, 'number_of_poses_remaining', None)
            if r is not None:
                self.rec.set_label(label, int(r))
            fb['n'] = fb.get('n', 0) + 1
        fut = client.send_goal_async(goal_msg, feedback_callback=on_fb)
        wait(fut.done, 30, self.resolve)
        handle = fut.result() if fut.done() else None
        row['accepted'] = bool(handle and handle.accepted)
        row['accepted_t'] = self.rec.now() if row['accepted'] else ''
        status = 'REJECTED' if handle is not None and not handle.accepted else 'NO_RESPONSE' if handle is None else None
        if row['accepted']:
            rfut = handle.get_result_async()
            t_limit = self.rec.now() + limit
            while not rfut.done() and self.rec.now() < t_limit:
                if cancel_after is not None and row['cancel_req_t'] == '' and self.rec.truth()[1] - start[7] >= cancel_after:
                    row['cancel_req_t'] = self.rec.now()
                    cfut = handle.cancel_goal_async()
                    wait(cfut.done, 10, self.resolve)
                    resp = cfut.result() if cfut.done() else None
                    row['cancel_code'] = resp.return_code if resp is not None else 'NO_RESPONSE'
                    if resp is not None and resp.return_code == CancelGoal.Response.ERROR_NONE:
                        row['cancel_acc_t'] = self.rec.now()
                        row['cancel_travel'] = self.rec.truth()[1] - start[7]
                self.resolve()
                time.sleep(0.05)
            status = STATUS.get(rfut.result().status, str(rfut.result().status)) if rfut.done() else 'TIMEOUT'
        row['status'] = status
        row['result_t'] = self.rec.now()
        at_result = self.snapshot()
        self.rec.set_label('', '')
        self.hold(CANCEL_HOLD if cancel_after is not None else HOLD)
        settled = self.snapshot()
        with self.rec.lock:
            plan = self.rec.plans.get(label, [])
            row['plans_seen'] = self.rec.plan_count.get(label, 0)
        row['plan_length'] = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(plan, plan[1:])) if plan else ''
        row['feedback_msgs'] = fb.get('n', 0)
        row.update({f'start_{k}': v for k, v in zip(SNAP, start)})
        row.update({f'result_{k}': v for k, v in zip(SNAP, at_result)})
        row.update({f'settled_{k}': v for k, v in zip(SNAP, settled)})
        self.rows.append(row)
        print(f'INFO  {label}: {status} after {row["result_t"] - row["sent_t"]:.1f} s; settled truth '
              f'({settled[1]:+.3f}, {settled[2]:+.3f}) m, {math.degrees(settled[3]):+.2f} deg; travel '
              f'{settled[7] - start[7]:.2f} m; first plan {f"{row['plan_length']:.2f} m" if plan else "none"} '
              f'({row["plans_seen"]} plans)', flush=True)
        if status in ('TIMEOUT', 'NO_RESPONSE'):
            print(f'# {label}: no result within the limit: INVALID RUN')
            return False
        if cancel_after is not None and row['cancel_acc_t'] == '':
            print(f'# {label}: cancel not accepted (or {cancel_after} m of travel not reached): INVALID RUN')
            return False
        return True

    def go(self):
        G = goals.GOALS
        if self.mode == 'sequence':
            for g in goals.SEQUENCE:
                m = NavigateToPose.Goal()
                m.pose = pose_msg(self.rec, *G[g])
                if not self.send(g, self.rec.to_pose, m, GOAL_LIMIT):
                    return False
        elif self.mode == 'route':
            m = NavigateThroughPoses.Goal()
            m.poses = [pose_msg(self.rec, *G[g]) for g in goals.ROUTE]
            return self.send('route_' + '-'.join(goals.ROUTE), self.rec.through, m, GOAL_LIMIT)
        elif self.mode == 'invalid':
            for name, pose in goals.INVALID.items():
                m = NavigateToPose.Goal()
                m.pose = pose_msg(self.rec, *pose)
                if not self.send(name, self.rec.to_pose, m, INVALID_LIMIT + 30):
                    return False
        elif self.mode == 'cancel':
            m = NavigateToPose.Goal()
            m.pose = pose_msg(self.rec, *G[goals.CANCEL_GOAL])
            return self.send('cancel_' + goals.CANCEL_GOAL, self.rec.to_pose, m, GOAL_LIMIT,
                             cancel_after=goals.CANCEL_AFTER)
        return True

    # --- output --------------------------------------------------------------------------------------------------
    def write(self, meta):
        fmt = lambda v: f'{v:.6f}' if isinstance(v, float) else v  # noqa: E731
        with open(self.prefix + '_track.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['sim_t', 'gt_x', 'gt_y', 'gt_yaw', 'travel', 'est_x', 'est_y', 'est_yaw', 'goal', 'remaining'])
            for r in sorted(self.track, key=lambda r: r[0]):
                w.writerow([fmt(v) for v in r])
        with open(self.prefix + '_cmd.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['topic', 'clock', 'stamp', 'v', 'w'])
            with self.rec.lock:
                cmds = list(self.rec.cmd)
            for c in cmds:
                w.writerow([c[0], f'{c[1]:.6f}', f'{c[2]:.9f}', repr(c[3]), repr(c[4])])
        cols = (['label', 'goal_x', 'goal_y', 'goal_yaw_deg', 'accepted', 'status', 'sent_t', 'accepted_t', 'result_t',
                 'cancel_req_t', 'cancel_acc_t', 'cancel_travel', 'cancel_code', 'plan_length', 'plans_seen',
                 'feedback_msgs'] + [f'{p}_{k}' for p in ('start', 'result', 'settled') for k in SNAP])
        with open(self.prefix + '_goals.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(cols)
            for r in self.rows:
                gx, gy, gyaw = target(r['label'])
                r.update(goal_x=gx, goal_y=gy, goal_yaw_deg=gyaw)
                w.writerow([fmt(r.get(c, '')) for c in cols])
        with open(self.prefix + '_plans.csv', 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['label', 'index', 'x', 'y'])
            with self.rec.lock:
                plans = dict(self.rec.plans)
            for lbl, pts in plans.items():
                for i, (x, y) in enumerate(pts):
                    w.writerow([lbl, i, f'{x:.4f}', f'{y:.4f}'])
        with open(self.prefix + '_meta.json', 'w') as f:
            json.dump(meta, f, indent=1)


SNAP = ['t', 'gt_x', 'gt_y', 'gt_yaw', 'est_x', 'est_y', 'est_yaw', 'travel']


def target(label):
    """The final target pose of a goal label (route: its last goal)."""
    if label in goals.GOALS:
        return goals.GOALS[label]
    if label in goals.INVALID:
        return goals.INVALID[label]
    if label.startswith('route_'):
        return goals.GOALS[goals.ROUTE[-1]]
    if label.startswith('cancel_'):
        return goals.GOALS[goals.CANCEL_GOAL]
    raise KeyError(label)


def publishers(rec):
    return sorted(f'{i.node_name} {i.topic_type}' for i in rec.get_publishers_info_by_topic('/cmd_vel'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('prefix')
    ap.add_argument('--mode', choices=['sequence', 'route', 'invalid', 'cancel'], required=True)
    args = ap.parse_args()
    rclpy.init()
    rec = Rec()
    ex = M2.SingleThreadedExecutor()
    ex.add_node(rec)
    spin = M2.Spinner(ex).start()
    run = Run(rec, args.prefix, args.mode)
    print(f'# TEST-M7 navigation run, wall {time.strftime("%F %T %Z")}; mode {args.mode}; goals TEST-M7_goals.py',
          flush=True)
    meta = {'mode': args.mode, 'wall_start': time.strftime('%F %T %Z')}
    ok = False
    try:
        if not run.wait_ready():
            return 2
        time.sleep(1.0)                      # discovery settles before the publisher list is read
        meta['cmd_vel_publishers_start'] = publishers(rec)
        with rec.lock:
            rec.next_t = rec.cur[0]          # start 10 Hz sampling and command recording
        sim0, wall0 = rec.now(), time.monotonic()
        ok = run.go()
        sim1, wall1 = rec.now(), time.monotonic()
        meta['cmd_vel_publishers_end'] = publishers(rec)
        t_flush = time.monotonic() + 3
        while time.monotonic() < t_flush and rec.samples:
            run.resolve()
            time.sleep(0.1)
        run.resolve(final=True)
        with rec.lock:
            rec.next_t = None
    finally:
        spin.stop(rec)
    rtf = (sim1 - sim0) / max(wall1 - wall0, 1e-9)
    n = len(run.track) + run.missing
    meta.update(sim_duration=sim1 - sim0, wall_duration=wall1 - wall0, rtf=rtf, track_samples=len(run.track),
                missing_samples=run.missing, travel=rec.travel, goals=len(run.rows))
    run.write(meta)
    print(f'INFO  run: {sim1 - sim0:.1f} s simulation time in {wall1 - wall0:.1f} s wall, RTF {rtf:.2f}; '
          f'{len(run.track)} track samples ({run.missing} missing of {n}); {len(rec.cmd)} command messages; travel '
          f'{rec.travel:.2f} m; /cmd_vel publishers {meta["cmd_vel_publishers_start"]} -> '
          f'{meta["cmd_vel_publishers_end"]}', flush=True)
    invalid = not ok
    if rtf < 0.5:
        print(f'# RTF {rtf:.2f} < 0.5: INVALID RUN')
        invalid = True
    if n == 0 or run.missing > MISSING_MAX * n:
        print(f'# {run.missing} of {n} track samples missing (> {MISSING_MAX:.0%}): INVALID RUN')
        invalid = True
    if invalid:
        return 2
    print('# result: run completed and recorded (judged by TEST-M7_nav_check.py)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
