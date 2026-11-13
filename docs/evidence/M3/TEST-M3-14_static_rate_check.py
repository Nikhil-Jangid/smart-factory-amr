#!/usr/bin/env python3
"""TEST-M3-14 (f): static rate-consistency check for DEC-038 item 9 (dependency on DEC-026).

Usage (repository root, ROS sourced): python3 -I TEST-M3-14_static_rate_check.py <controllers.yaml> <model.urdf>
                                                                                   <world.sdf> [<world.sdf> ...]
  <model.urdf>: amr.urdf.xacro expanded with use_ros2_control:=true use_sensors:=true (the simulation model).
Checks, from the files actually used by the launch:
  1. The IMU decimator plugin is present once, and its input topic is published by exactly one IMU sensor.
  2. raw_rate = block_size x output_rate, and the IMU sensor's <update_rate> = raw_rate.
  3. The output (block) period is an integer multiple of the controller period 1 / controller_manager.update_rate,
     so every block holds the same number of command steps (allowed: 100, 200, 500, 1000 Hz for a 100 Hz output).
  4. The raw period is an integer multiple of every world's physics step (max_step_size), so the sensor samples
     exactly once per raw period.
Exit 0 = all PASS, 1 = a FAIL.
"""
import re
import sys
import xml.etree.ElementTree as ET

fails = 0


def check(ok, text):
    global fails
    print(('PASS  ' if ok else 'FAIL  ') + text)
    fails += 0 if ok else 1


def is_int_ratio(a, b):
    """True if a / b is a positive integer within a relative 1e-9."""
    q = a / b
    return q >= 1 - 1e-9 and abs(q - round(q)) <= 1e-9 * max(1.0, q)


ctrl, urdf, worlds = sys.argv[1], sys.argv[2], sys.argv[3:]
m = re.search(r'controller_manager:\s*\n\s*ros__parameters:\s*\n(?:\s+.*\n)*?\s+update_rate:\s*([0-9.]+)', open(ctrl).read())
controller_rate = float(m.group(1)) if m else float('nan')
print(f'# controller_manager.update_rate = {controller_rate:g} Hz ({ctrl.split("/")[-1]})')

root = ET.parse(urdf).getroot()
plugins = [p for g in root.iter('gazebo') for p in g.iter('plugin') if p.get('name') == 'amr_gazebo_plugins::ImuDecimator']
check(len(plugins) == 1, f'1. decimator plugin elements in the model: {len(plugins)} == 1 '
      f'(filename {plugins[0].get("filename") if plugins else None})')
p = plugins[0]
block, raw_rate, out_rate = int(p.findtext('block_size')), float(p.findtext('raw_rate')), float(p.findtext('output_rate'))
topic_in = p.findtext('input_topic')
imus = [s for s in root.iter('sensor') if s.get('type') == 'imu' and s.findtext('topic') == topic_in]
check(len(imus) == 1, f'1. IMU sensors publishing input_topic {topic_in}: {len(imus)} == 1; output_topic '
      f'{p.findtext("output_topic")}')
sensor_rate = float(imus[0].findtext('update_rate'))
check(abs(raw_rate - block * out_rate) <= 1e-9 * raw_rate and abs(sensor_rate - raw_rate) <= 1e-9 * raw_rate,
      f'2. raw_rate {raw_rate:g} Hz = block_size {block} x output_rate {out_rate:g} Hz; IMU <update_rate> '
      f'{sensor_rate:g} Hz = raw_rate')
check(is_int_ratio(controller_rate, out_rate),
      f'3. output period {1000 / out_rate:g} ms / controller period {1000 / controller_rate:g} ms = '
      f'{controller_rate / out_rate:g}, a positive integer (DEC-038 item 9, DEC-026)')
for w in worlds:
    # Regex, not an XML parser: the stock empty.sdf has '--' inside a comment (not well-formed XML; sdformat accepts it).
    text = re.sub(r'<!--.*?-->', '', open(w).read(), flags=re.S)
    steps = re.findall(r'<max_step_size>\s*([0-9.eE+-]+)\s*</max_step_size>', text)
    if len(steps) != 1:
        check(False, f'4. {w.split("/")[-1]}: expected one <max_step_size>, found {len(steps)}')
        continue
    step = float(steps[0])
    check(is_int_ratio(1.0 / raw_rate, step),
          f'4. {w.split("/")[-1]}: raw period {1000 / raw_rate:g} ms / physics step {step * 1000:g} ms = '
          f'{(1.0 / raw_rate) / step:g}, a positive integer')
print(f'# result: {"ALL CRITERIA PASSED" if fails == 0 else f"{fails} CRITERION/CRITERIA FAILED"}')
sys.exit(1 if fails else 0)
