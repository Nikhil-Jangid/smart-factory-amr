"""TS-027 bounded scratch investigation: physics-reported link acceleration vs ground truth vs IMU.

Usage: python3 exp.py <engine: dart|bullet-fs> <case> <robot.sdf> [run]
Runs a gz-sim 8 TestFixture headless (no ROS), the M3 robot model (amr.urdf.xacro use_sensors:=true -> gz sdf -p),
1 ms step, the IMU system only. Every physics step records the base_footprint ground-truth world velocity and the
physics-reported world linear acceleration (Link.world_linear_acceleration = the WorldLinearAcceleration component,
filled by the Physics system from the engine frame data, the same source as the IMU). IMU messages on /imu are
collected through gz-transport. Prints per-phase means.

Cases (wheel joints are revolute about +y; +wheel speed = +x travel):
  rest        no command, 3 s
  freefall    spawned 1.0 m up; no contact for ~0.4 s
  wheel_vel   wheel JointVelocityCmd (the gz_ros2_control velocity path): 0 -> 0.5 m/s in 1.0 s (0.5 m/s^2),
              hold 1.0 s, 0.5 -> 0 in 0.5 s (-1.0 m/s^2), hold 1.0 s
  wheel_force wheel joint torque (effort path) +0.18 N m per wheel for 1.0 s, -0.36 N m for 0.5 s, then 0
  ext_force   wheels free; external world force on base_footprint +4.7 N x for 1.0 s, -9.4 N for 0.5 s
  float_force world gravity 0, robot 1 m up, +4.7 N x for 1.0 s, -9.4 N for 0.5 s (pure forward dynamics)
"""
import math
import os
import re
import sys
import threading

ENGINE, CASE, ROBOT = sys.argv[1], sys.argv[2], sys.argv[3]
RUN = sys.argv[4] if len(sys.argv) > 4 else '1'
os.environ['GZ_PARTITION'] = f'ts027_{ENGINE}_{CASE}_{RUN}_{os.getpid()}'

from gz.common5 import set_verbosity  # noqa: E402
from gz.sim8 import TestFixture, World, Model, Link, Joint, world_entity  # noqa: E402
from gz.math7 import Vector3d  # noqa: E402
from gz.transport13 import Node  # noqa: E402
from gz.msgs10.imu_pb2 import IMU  # noqa: E402

set_verbosity(1)
R_WHEEL = 0.075
T_END = {'rest': 3.0, 'freefall': 0.40, 'float_force': 3.0}.get(CASE, 4.0)

model = open(ROBOT).read()
model = model[model.index('<model'):model.rindex('</model>') + len('</model>')]
model = re.sub(r"<sensor name='lidar'.*?</sensor>", '', model, flags=re.S)
z0 = 1.0 if CASE in ('freefall', 'float_force') else 0.0
model = model.replace('<model', f'<model', 1)
model = re.sub(r"(<model name='[^']*'>)", rf"\1<pose>0 {os.environ.get('Y0', '0')} {z0} 0 0 0</pose>", model, count=1)
engine_xml = {'dart': '', 'bullet-fs': '<engine><filename>gz-physics-bullet-featherstone-plugin</filename></engine>'}[ENGINE]
gravity = '0 0 0' if CASE == 'float_force' else '0 0 -9.8'
ground = '' if CASE == 'float_force' else """
    <model name='ground_plane'><static>true</static><link name='link'>
      <collision name='c'><geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry></collision>
    </link></model>"""
world = f"""<?xml version='1.0'?>
<sdf version='1.9'><world name='ts027'>
  <physics name='1ms' type='ignored'><max_step_size>0.001</max_step_size><real_time_factor>0</real_time_factor></physics>
  <gravity>{gravity}</gravity>
  <plugin filename='gz-sim-physics-system' name='gz::sim::systems::Physics'>{engine_xml}</plugin>
  <plugin filename='gz-sim-imu-system' name='gz::sim::systems::Imu'/>
  {os.environ.get('EXTRA_SYS', '')}
  {ground}
  {model}
</world></sdf>"""
wpath = f'<scratch>/w_{ENGINE}_{CASE}.sdf'
open(wpath, 'w').write(world)

rows = []      # (t, vx, vz, ax_phys, az_phys)
imu = []       # (t, ax, ay, az, gz)
lock = threading.Lock()
st = {}


def on_imu(msg):
    with lock:
        imu.append((msg.header.stamp.sec + msg.header.stamp.nsec * 1e-9, msg.linear_acceleration.x,
                    msg.linear_acceleration.y, msg.linear_acceleration.z, msg.angular_velocity.z))


node = Node()
node.subscribe(IMU, '/imu', on_imu)


def wheel_speed(t):  # wheel_vel profile, m/s
    if t < 0.5:
        return 0.0
    t -= 0.5
    if t < 1.0:
        return 0.5 * t
    if t < 2.0:
        return 0.5
    if t < 2.5:
        return 0.5 - 1.0 * (t - 2.0)
    return 0.0


def phase_value(t, a, b):
    t -= 0.5
    if 0 <= t < 1.0:
        return a
    if 1.0 <= t < 1.5:
        return b
    return 0.0


def pre(info, ecm):
    t = info.sim_time.total_seconds() if hasattr(info.sim_time, 'total_seconds') else info.sim_time
    if 'link' not in st:
        w = World(world_entity(ecm))
        m = Model(w.model_by_name(ecm, 'amr'))
        if not m.valid(ecm):
            names = [Model(e).name(ecm) for e in w.models(ecm)]
            m = Model([e for e in w.models(ecm) if Model(e).name(ecm) != 'ground_plane'][0])
        st['link'] = Link(m.link_by_name(ecm, 'base_footprint'))
        st['link'].enable_velocity_checks(ecm, True)
        if os.environ.get('NOACC') != '1':
            st['link'].enable_acceleration_checks(ecm, True)
        st['jl'] = Joint(m.joint_by_name(ecm, 'left_wheel_joint'))
        st['jr'] = Joint(m.joint_by_name(ecm, 'right_wheel_joint'))
    if CASE == 'wheel_vel_zoh':  # 100 Hz zero-order hold (controller_manager update_rate), phase PHASE ms
        ph = int(os.environ.get('PHASE', '0')) * 1e-3
        tk = math.floor((t - ph) / 0.01 + 1e-6) * 0.01 + ph
        w_cmd = wheel_speed(tk) / R_WHEEL
        st['jl'].set_velocity(ecm, [w_cmd])
        st['jr'].set_velocity(ecm, [w_cmd])
    if CASE == 'wheel_vel':
        w_cmd = wheel_speed(t) / R_WHEEL
        st['jl'].set_velocity(ecm, [w_cmd])
        st['jr'].set_velocity(ecm, [w_cmd])
    elif CASE == 'wheel_force':
        tau = phase_value(t, 0.18, -0.36)
        st['jl'].set_force(ecm, [tau])
        st['jr'].set_force(ecm, [tau])
    elif CASE in ('ext_force', 'float_force'):
        f = phase_value(t, 4.7, -9.4)
        if f:
            st['link'].add_world_force(ecm, Vector3d(f, 0, 0))


def post(info, ecm):
    t = info.sim_time.total_seconds() if hasattr(info.sim_time, 'total_seconds') else info.sim_time
    lk = st['link']
    v = lk.world_linear_velocity(ecm)
    a = lk.world_linear_acceleration(ecm)
    if v is None:
        return
    rows.append((t, v.x(), v.z(), a.x() if a is not None else float('nan'), a.z() if a is not None else float('nan')))


fx = TestFixture(wpath)
fx.on_pre_update(pre)
fx.on_post_update(post)
fx.finalize()
srv = fx.server()
srv.run(True, int(T_END * 1000), False)
import time  # noqa: E402
time.sleep(0.5)
with lock:
    im = list(imu)


def mean(xs):
    return sum(xs) / len(xs) if xs else float('nan')


def true_acc(t0, t1):
    """Ground-truth mean acceleration = (v(t1) - v(t0)) / (t1 - t0) from the recorded velocity."""
    a = min(rows, key=lambda r: abs(r[0] - t0))
    b = min(rows, key=lambda r: abs(r[0] - t1))
    return (b[1] - a[1]) / (b[0] - a[0]), (b[2] - a[2]) / (b[0] - a[0])


def report(label, t0, t1):
    ph = [r for r in rows if t0 <= r[0] <= t1]
    ii = [s for s in im if t0 <= s[0] <= t1]
    tx, tz = true_acc(t0, t1)
    print(f'{label:28s} [{t0:.2f},{t1:.2f}] s: true ax {tx:+.4f} az {tz:+.4f} | physics-reported ax '
          f'{mean([r[3] for r in ph]):+.4f} az {mean([r[4] for r in ph]):+.4f} (n {len(ph)}) | IMU ax '
          f'{mean([s[1] for s in ii]):+.4f} az {mean([s[3] for s in ii]):+.4f} (n {len(ii)}) m/s^2')


print(f'# engine {ENGINE}, case {CASE}, run {RUN}: {len(rows)} physics steps, {len(im)} IMU messages; '
      f'final vx {rows[-1][1]:+.4f} m/s' if rows else '# no rows')
if CASE == 'rest':
    report('rest', 1.0, 3.0)
elif CASE == 'freefall':
    report('free fall', 0.05, 0.30)
else:
    report('settle (no input)', 0.1, 0.45)
    report('phase 1 (speed-up)', 0.6, 1.4)
    report('phase 2 (braking)', 1.55, 1.95) if not CASE.startswith('wheel_vel') else report('hold (constant 0.5 m/s)', 1.6, 2.4)
    if CASE.startswith('wheel_vel'):
        report('phase 2 (braking)', 2.55, 2.95)
    report('after', 3.2 if CASE.startswith('wheel_vel') else 2.2, T_END - 0.05)
ph1 = [r[3] for r in rows if 0.6 <= r[0] <= 1.4]
if ph1 and ph1[0] == ph1[0]:
    print(f'# speed-up per-step physics ax: max {max(ph1):+.3f}, steps > 0.1: {sum(x > 0.1 for x in ph1)} of {len(ph1)}; IMU stamps mod 10 ms (ms): {sorted(set(round((s[0] * 1000) % 10) for s in im))}')
# per-step trace excerpt around the ramp start (every 20 ms)
print('# trace t, vx, physics ax (every 0.1 s)')
for r in rows[::100]:
    print(f'#  {r[0]:.3f} {r[1]:+.4f} {r[3]:+.4f}')
sys.stdout.flush()
os._exit(0)
