"""TS-027 C4 offline study, stage 1: record the raw 1 kHz IMU and per-step ground truth in a gz.sim8 TestFixture.

Usage: python3 c4_fixture.py <robot.sdf> <case: rest|zoh> <noise: R0|R1|R2> <phase ms> <out.json>
  Model: the launch expansion without the gz_ros2_control plugin (TS-027 E2), IMU update_rate changed to 1000 Hz.
  Noise: R0 = no noise (clean transients); R1 = the DEC-032 values unchanged (accel 0.01 m/s^2, gyro 0.001 rad/s)
         applied per raw sample; R2 = raw values scaled by sqrt(10) (0.0316228, 0.00316228), the white-noise
         prediction for a 10-sample mean to keep 0.01 / 0.001 at the output. R2 is a scratch variant only.
  rest: 12 s, no command. zoh: wheel velocity command held for 10 ms (100 Hz, as controller_manager / DEC-026),
        phase = offset in ms: 0.5 s wait, 0 -> 0.5 m/s at 0.5 m/s^2 (1.0 s), hold 1.0 s, 0.5 -> 0 at -1.0 m/s^2
        (0.5 s), hold 1.0 s; plus an in-place rotation leg 0.5 rad/s for 1.5 s (wheel speeds +-0.1 m/s, held 10 ms,
        with the same 2.0 rad/s^2 limit ramp as DEC-025) to exercise the gyro path.
Output JSON: raw IMU samples [t, ax, ay, az, gx, gy, gz] and per-step ground truth [t, vx_body, wz].
"""
import json
import math
import os
import re
import sys
import threading
import time

ROBOT, CASE, NOISE, PHASE, OUT = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
os.environ['GZ_PARTITION'] = f'ts027c4_{CASE}_{NOISE}_{PHASE}_{os.getpid()}'
from gz.common5 import set_verbosity  # noqa: E402
from gz.sim8 import TestFixture, World, Model, Link, Joint, world_entity  # noqa: E402
import gz.math7  # noqa: E402,F401  (registers Vector3d/Pose3d for the gz.sim8 return values)
from gz.transport13 import Node  # noqa: E402
from gz.msgs10.imu_pb2 import IMU  # noqa: E402
set_verbosity(1)

R_WHEEL, HALF_TRACK = 0.075, 0.200
SIG = {'R0': (0.0, 0.0), 'R1': (0.01, 0.001), 'R2': (0.01 * math.sqrt(10), 0.001 * math.sqrt(10))}[NOISE]
T_END = 12.0 if CASE == 'rest' else 7.0

m = open(ROBOT).read()
m = m[m.index('<model'):m.rindex('</model>') + len('</model>')]
m = re.sub(r"<sensor name='lidar'.*?</sensor>", '', m, flags=re.S)
imu = re.search(r"<sensor name='imu'.*?</sensor>", m, flags=re.S).group(0)
imu2 = imu.replace('<update_rate>100</update_rate>', '<update_rate>1000</update_rate>')
lin = re.search(r'<linear_acceleration>.*?</linear_acceleration>', imu2, flags=re.S).group(0)
ang = re.search(r'<angular_velocity>.*?</angular_velocity>', imu2, flags=re.S).group(0)
imu2 = imu2.replace(lin, lin.replace('<stddev>0.01</stddev>', f'<stddev>{SIG[0]}</stddev>'))
imu2 = imu2.replace(ang, ang.replace('<stddev>0.001</stddev>', f'<stddev>{SIG[1]}</stddev>'))
assert imu2.count('<update_rate>1000</update_rate>') == 1
m = m.replace(imu, imu2)
world = f"""<?xml version='1.0'?>
<sdf version='1.9'><world name='c4'>
  <physics name='1ms' type='ignored'><max_step_size>0.001</max_step_size><real_time_factor>0</real_time_factor></physics>
  <gravity>0 0 -9.8</gravity>
  <plugin filename='gz-sim-physics-system' name='gz::sim::systems::Physics'/>
  <plugin filename='gz-sim-imu-system' name='gz::sim::systems::Imu'/>
  <model name='ground_plane'><static>true</static><link name='link'>
    <collision name='c'><geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry></collision>
  </link></model>
  {m}
</world></sdf>"""
wpath = os.path.join(os.path.dirname(os.path.abspath(OUT)), f'w_{CASE}_{NOISE}_{PHASE}.sdf')
open(wpath, 'w').write(world)

lock = threading.Lock()
raw, gt, st = [], [], {}


def on_imu(msg):
    a, w = msg.linear_acceleration, msg.angular_velocity
    with lock:
        raw.append([msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9, a.x, a.y, a.z, w.x, w.y, w.z])


node = Node()
node.subscribe(IMU, '/imu', on_imu)


def lin_speed(t):
    t -= 0.5
    if t < 0:
        return 0.0
    if t < 1.0:
        return 0.5 * t
    if t < 2.0:
        return 0.5
    if t < 2.5:
        return 0.5 - (t - 2.0)
    return 0.0


def yaw_rate(t):
    t -= 4.0
    if t < 0 or t > 2.0:
        return 0.0
    if t < 0.25:
        return 2.0 * t
    if t < 1.5:
        return 0.5
    if t < 1.75:
        return 0.5 - 2.0 * (t - 1.5)
    return 0.0


def secs(info):
    s = info.sim_time
    return s.total_seconds() if hasattr(s, 'total_seconds') else s


def pre(info, ecm):
    t = secs(info)
    if 'link' not in st:
        w = World(world_entity(ecm))
        mo = Model(w.model_by_name(ecm, 'amr'))
        st['link'] = Link(mo.link_by_name(ecm, 'base_footprint'))
        st['link'].enable_velocity_checks(ecm, True)
        st['jl'] = Joint(mo.joint_by_name(ecm, 'left_wheel_joint'))
        st['jr'] = Joint(mo.joint_by_name(ecm, 'right_wheel_joint'))
    if CASE == 'zoh':
        ph = PHASE * 1e-3
        tk = math.floor((t - ph) / 0.01 + 1e-6) * 0.01 + ph
        v, wz = lin_speed(tk), yaw_rate(tk)
        st['jl'].set_velocity(ecm, [(v - wz * HALF_TRACK) / R_WHEEL])
        st['jr'].set_velocity(ecm, [(v + wz * HALF_TRACK) / R_WHEEL])


def post(info, ecm):
    lk = st['link']
    v = lk.world_linear_velocity(ecm)
    w = lk.world_angular_velocity(ecm)
    p = lk.world_pose(ecm)
    if v is None or w is None:
        return
    yaw = p.rot().yaw()
    gt.append([secs(info), v.x() * math.cos(yaw) + v.y() * math.sin(yaw), w.z()])


fx = TestFixture(wpath)
fx.on_pre_update(pre)
fx.on_post_update(post)
fx.finalize()
fx.server().run(True, int(T_END * 1000), False)
time.sleep(0.5)
with lock:
    r = list(raw)
json.dump({'case': CASE, 'noise': NOISE, 'phase_ms': PHASE, 'sigma_raw': SIG, 'raw': r, 'gt': gt}, open(OUT, 'w'))
print(f'# {CASE} {NOISE} phase {PHASE}: {len(r)} raw IMU samples, {len(gt)} gt steps -> {OUT}')
sys.stdout.flush()
os._exit(0)
