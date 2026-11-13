#!/usr/bin/env python3
"""TEST-M3-14 (g), supplementary: an invalid DEC-038 configuration is refused visibly.

Gazebo Sim 8 gives a system's Configure() no way to fail the load. So "refuse to load" means: the ImuDecimator
logs a gzerr "invalid configuration, NOT active" line and neither subscribes nor publishes. Gazebo keeps running
and gz /imu (hence ROS /imu, which only bridges it) stays silent. This check proves that behaviour in a real
Gazebo server at its default verbosity (as sim.launch.py starts it: `gz sim -r -s`, no -v).

Usage (repository root, ROS and amr_ws sourced): python3 TEST-M3-14_invalid_config_check.py <model.urdf>
  <model.urdf>: amr.urdf.xacro expanded with use_sensors:=true only. No ros2_control, so no ROS is needed; the
  wheels are idle.
Cases, each in a fresh `gz sim -r -s --iterations 4000` server, with a minimal world (1 ms step; Physics and Imu
systems; ground plane; the model converted with `gz sdf -p`):
  valid       the unmodified model                      -> active line once, no error, /imu_raw ~1000 Hz,
                                                           /imu ~100 Hz (control case)
  bad_rate    plugin <raw_rate> 500 (10 x 100 != 500)    -> error line naming raw_rate, /imu_raw published,
                                                           /imu silent (0 messages)
  bad_sensor  IMU <update_rate> 100 (sensor != raw_rate) -> error line naming the sensor update_rate, /imu_raw
                                                           published, /imu silent
INFO (valid case, robot at rest): the raw-sample independence that the DEC-038 covariance propagation assumes (item 8).
  It reports the raw sigma per channel vs the derived setting; the largest |autocorrelation| at lags 1-10 ms per
  channel; and the variance of the 10-sample block means divided by (raw variance / 10). That ratio is ~1 for
  independent samples. Material correlation would call for investigating the variance calculation (DEC-038 item 8).
Exit 0 = all PASS, 1 = a FAIL.
"""
import os
import re
import subprocess
import sys
import tempfile
import threading
import time

from gz.msgs10.imu_pb2 import IMU
from gz.transport13 import Node

URDF = sys.argv[1]
fails = 0


def check(ok, text):
    global fails
    print(('PASS  ' if ok else 'FAIL  ') + text)
    fails += 0 if ok else 1


def world_for(model_sdf):
    model = model_sdf[model_sdf.index('<model'):model_sdf.rindex('</model>') + len('</model>')]
    return f"""<?xml version='1.0'?>
<sdf version='1.9'><world name='m3_14g'>
  <physics name='1ms' type='ignored'><max_step_size>0.001</max_step_size><real_time_factor>1.0</real_time_factor></physics>
  <plugin filename='gz-sim-physics-system' name='gz::sim::systems::Physics'/>
  <plugin filename='gz-sim-imu-system' name='gz::sim::systems::Imu'/>
  <model name='ground_plane'><static>true</static><link name='link'>
    <collision name='c'><geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry></collision>
  </link></model>
  {model}
</world></sdf>"""


def run_case(name, urdf_text, tmp):
    upath, spath, wpath = (os.path.join(tmp, f'{name}.{ext}') for ext in ('urdf', 'sdf', 'world.sdf'))
    open(upath, 'w').write(urdf_text)
    sdf = subprocess.run(['gz', 'sdf', '-p', upath], capture_output=True, text=True, check=True).stdout
    open(spath, 'w').write(sdf)
    open(wpath, 'w').write(world_for(sdf))
    part = f'm3_14g_{name}_{os.getpid()}'
    env = dict(os.environ, GZ_PARTITION=part)
    os.environ['GZ_PARTITION'] = part
    counts = {'/imu_raw': 0, '/imu': 0}
    raw = []
    lock = threading.Lock()
    node = Node()

    def counter(topic):
        def cb(_msg):
            with lock:
                counts[topic] += 1
                if topic == '/imu_raw':
                    a, w = _msg.linear_acceleration, _msg.angular_velocity
                    raw.append((_msg.header.stamp.sec * 1000 + round(_msg.header.stamp.nsec / 1e6),
                                a.x, a.y, a.z, w.x, w.y, w.z))
        return cb
    for topic in counts:
        node.subscribe(IMU, topic, counter(topic))
    proc = subprocess.Popen(['gz', 'sim', '-r', '-s', '--iterations', '4000', wpath], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = proc.communicate(timeout=120)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()
    time.sleep(0.5)
    for topic in counts:
        node.unsubscribe(topic)
    with lock:
        c = dict(counts)
    lines = [l for l in out.splitlines() if 'ImuDecimator' in l]
    print(f'# case {name}: gz sim exit {proc.returncode}; messages /imu_raw {c["/imu_raw"]}, /imu {c["/imu"]}; '
          f'plugin output lines:')
    for l in lines:
        print('#   ' + re.sub(r'\x1b\[[0-9;]*m', '', l).replace(tmp, '<tmp>'))
    return proc.returncode, c, '\n'.join(lines), sorted(raw)


def info_independence(raw):
    import math
    import statistics
    raw = [x for x in raw if x[0] >= 1000]   # skip the first second (settling on the ground plane)
    names = ('accel x', 'accel y', 'accel z', 'gyro x', 'gyro y', 'gyro z')
    derived = (0.01 * math.sqrt(10),) * 3 + (0.001 * math.sqrt(10),) * 3
    for c, name in enumerate(names, start=1):
        x = [v[c] for v in raw]
        m = statistics.fmean(x)
        d = [v - m for v in x]
        var = sum(v * v for v in d) / len(d)
        rmax = max(abs(sum(d[i] * d[i + lag] for i in range(len(d) - lag)) / (len(d) * var)) for lag in range(1, 11))
        means = [statistics.fmean(x[i:i + 10]) for i in range(0, len(x) - 9, 10)]
        ratio = statistics.pvariance(means) / (var / 10)
        print(f'INFO  {name}: raw sigma {math.sqrt(var):.6f} (derived setting {derived[c - 1]:.6f}); max |r| at lags '
              f'1-10 ms {rmax:.3f}; var(10-sample means) / (raw var / 10) = {ratio:.3f} over {len(x)} samples, '
              f'{len(means)} blocks')


def main():
    base = open(URDF).read()
    assert base.count('<raw_rate>1000</raw_rate>') == 1 and base.count('<update_rate>1000</update_rate>') == 1
    bad_rate = base.replace('<raw_rate>1000</raw_rate>', '<raw_rate>500</raw_rate>')
    bad_sensor = base.replace('<update_rate>1000</update_rate>', '<update_rate>100</update_rate>')
    with tempfile.TemporaryDirectory() as tmp:
        rc, c, txt, raw = run_case('valid', base, tmp)
        check(rc == 0 and txt.count('active: /imu_raw (1000 Hz) -> /imu (100 Hz)') == 1 and 'invalid' not in txt
              and c['/imu_raw'] >= 3000 and 300 <= c['/imu'] <= 400,
              f'valid (control): exit {rc}; active line once, no error; /imu_raw {c["/imu_raw"]} (>= 3000 of ~4000), '
              f'/imu {c["/imu"]} (300..400 of ~400)')
        info_independence(raw)
        rc, c, txt, _ = run_case('bad_rate', bad_rate, tmp)
        check(rc == 0 and 'invalid configuration, NOT active' in txt and 'raw_rate 500 Hz must equal block_size 10'
              in txt and 'active: ' not in txt and c['/imu_raw'] >= 3000 and c['/imu'] == 0,
              f'bad_rate: exit {rc}; error line visible at default verbosity and names raw_rate; /imu_raw {c["/imu_raw"]} '
              f'(still published), /imu {c["/imu"]} (== 0: silent)')
        rc, c, txt, _ = run_case('bad_sensor', bad_sensor, tmp)
        check(rc == 0 and 'invalid configuration, NOT active' in txt and 'IMU sensor update_rate 100 Hz must equal'
              in txt and 'active: ' not in txt and c['/imu_raw'] >= 300 and c['/imu'] == 0,
              f'bad_sensor: exit {rc}; error line visible at default verbosity and names the sensor update_rate; '
              f'/imu_raw {c["/imu_raw"]} (still published, ~400 at 100 Hz), /imu {c["/imu"]} (== 0: silent)')
    print(f'# result: {"ALL CRITERIA PASSED" if fails == 0 else f"{fails} CRITERION/CRITERIA FAILED"}')
    return 1 if fails else 0


if __name__ == '__main__':
    code = main()
    sys.stdout.flush()
    os._exit(code)
