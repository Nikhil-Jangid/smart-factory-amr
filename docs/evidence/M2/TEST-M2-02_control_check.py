#!/usr/bin/env python3
"""TEST-M2-02: element-level check of the enabled (use_ros2_control:=true) AMR model.

Usage: python3 -I TEST-M2-02_control_check.py <enabled.urdf> <enabled.sdf> <controllers_file>
Expected values come from DEC-023 (structure) and DEC-024 (surfaces), not from the Xacro files.
Replaces the two M1-scope assertions of TEST-M1-03 (REQ-M1-09, -10) for the enabled variant.
"""
import sys
import xml.etree.ElementTree as ET

failures = 0


def report(ok, label, detail=''):
    global failures
    failures += 0 if ok else 1
    print(f'{"PASS" if ok else "FAIL"}  {label}' + (f'  [{detail}]' if detail else ''))


urdf, sdf, controllers = ET.parse(sys.argv[1]).getroot(), ET.parse(sys.argv[2]).getroot(), sys.argv[3]
print(f'== URDF: {sys.argv[1].split("/")[-1]}')
report(len(urdf.findall('link')) == 6 and len(urdf.findall('joint')) == 5, '6 links / 5 joints (M1 tree unchanged)',
       f'{len(urdf.findall("link"))} / {len(urdf.findall("joint"))}')
rc = urdf.findall('ros2_control')
report(len(rc) == 1 and rc[0].get('type') == 'system', 'exactly one <ros2_control type="system">')
report(rc[0].findtext('hardware/plugin') == 'gz_ros2_control/GazeboSimSystem', 'hardware plugin gz_ros2_control/GazeboSimSystem',
       rc[0].findtext('hardware/plugin'))
joints = {j.get('name'): j for j in rc[0].findall('joint')}
report(sorted(joints) == ['left_wheel_joint', 'right_wheel_joint'], 'only the two wheel joints', ', '.join(sorted(joints)))
for name, j in sorted(joints.items()):
    cmd = [c.get('name') for c in j.findall('command_interface')]
    st = [s.get('name') for s in j.findall('state_interface')]
    report(cmd == ['velocity'] and sorted(st) == ['position', 'velocity'], f'{name}: command [velocity], state [position, velocity]',
           f'command {cmd}, state {st}')
plug = [p for p in urdf.iter('plugin') if p.get('filename') == 'gz_ros2_control-system']
report(len(plug) == 1 and plug[0].get('name') == 'gz_ros2_control::GazeboSimROS2ControlPlugin',
       'Gazebo plugin gz_ros2_control-system / GazeboSimROS2ControlPlugin')
report(plug[0].findtext('parameters') == controllers, 'plugin <parameters> = controllers file passed by argument', plug[0].findtext('parameters'))
for side in ('left', 'right'):
    link = next(l for l in urdf.findall('link') if l.get('name') == f'{side}_wheel_link')
    geo = [g.tag for g in link.find('collision/geometry')]
    vis = [g.tag for g in link.find('visual/geometry')]
    rad = link.find('collision/geometry/sphere').get('radius') if geo == ['sphere'] else None
    report(geo == ['sphere'] and rad == '0.075' and vis == ['cylinder'],
           f'{side}_wheel_link: collision sphere r 0.075 (DEC-028), visual cylinder unchanged', f'collision {geo} r {rad}, visual {vis}')
report(not list(urdf.iter('mesh')), 'no <mesh> elements (REQ-M1-10 intent)')
report(not list(urdf.iter('sensor')), 'no <sensor> elements (no active sensors in M2)')

print(f'== SDF: {sys.argv[2].split("/")[-1]}')
expected = {'left_wheel_link_collision': '1', 'right_wheel_link_collision': '1',
            'base_footprint_fixed_joint_lump__caster_link_collision_1': '0.01'}
found = {}
for link in sdf.iter('link'):
    for c in link.findall('collision'):
        f = c.find('surface/friction/ode')
        found[c.get('name')] = None if f is None else (f.findtext('mu'), f.findtext('mu2'))
for name, mu in expected.items():
    got = found.get(name)
    report(got is not None and all(v is not None and float(v) == float(mu) for v in got),
           f'{name}: mu = mu2 = {mu} (DEC-024)', str(got))
others = {n: v for n, v in found.items() if n not in expected}
report(all(v is None for v in others.values()), 'no surface parameters on other collisions (chassis, bracket)', str(others))
for tag in ('kp', 'kd', 'max_vel', 'min_depth', 'torsional', 'slip1', 'slip2', 'fdir1'):
    report(not list(sdf.iter(tag)), f'no <{tag}> element (DEC-024)')
report(len(sdf.findall('.//plugin[@filename="gz_ros2_control-system"]')) == 1, 'plugin present in the SDF')
links = [l.get('name') for l in sdf.iter('link')]
report(links == ['base_footprint', 'left_wheel_link', 'right_wheel_link'], 'SDF lumping unchanged: 3 links', ', '.join(links))
print(f'== {"ALL CHECKS PASSED" if failures == 0 else f"{failures} CHECK(S) FAILED"}')
sys.exit(1 if failures else 0)
