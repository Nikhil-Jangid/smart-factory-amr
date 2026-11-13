#!/usr/bin/env python3
"""TEST-M1-08: documentation / code consistency check for the M1 model.

Usage, from the repository root, with the URDF generated from the current source:
    python3 -I docs/evidence/M1/TEST-M1-08_consistency_check.py <generated.urdf>

Expected values come from the design documents, never from the Xacro files under test:
  * parsed from docs/design/mechanical_geometry.md §2 (parameter table, `Property` column),
    docs/design/mass_inertia.md §1 (mass budget) and docs/design/frames_and_tf.md §2
    (joint and link inventories);
  * typed in below for the derived placements (mechanical_geometry.md §3) and the
    clearance / envelope results CALC-M1-02, -03, -04, -05, -13, -14.
Actual values are the literal properties in amr_properties.xacro and the generated URDF.
Per-link inertia tensors are checked by TEST-M1-03_check.py (CALC-M1-07 to -10, -15), which
TEST-M1-08 runs separately. Prints one line per check; exits 0 only if every check passes.
"""
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.getcwd()
DOC_GEO = 'docs/design/mechanical_geometry.md'
DOC_MASS = 'docs/design/mass_inertia.md'
DOC_TF = 'docs/design/frames_and_tf.md'
PROPS = 'amr_ws/src/amr_description/urdf/amr_properties.xacro'
URDF_SRC = 'amr_ws/src/amr_description/urdf'
failures = 0


def report(ok, label, detail=''):
    global failures
    failures += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {label}{'  [' + detail + ']' if detail else ''}")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()


def num(text):
    """Parse a documented number: Unicode minus, optional +, optional unit."""
    return float(text.strip().replace('−', '-').replace('+', '').split()[0])


def table_rows(text, heading_regex):
    """Rows (lists of cells) of the first Markdown table after a heading matching the regex."""
    m = re.search(heading_regex, text, re.M)
    if not m:
        raise SystemExit(f'heading not found: {heading_regex}')
    rows = []
    for line in text[m.end():].splitlines():
        if line.startswith('|'):
            cells = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip())[1:-1]]
            if not set(''.join(cells)) <= set('-: '):
                rows.append(cells)
        elif rows:
            break
    return rows[1:]  # drop the header row


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


# ------------------------------------------------------------ 1. documented parameters vs properties
def check_parameters():
    print('== 1. Parameters: mechanical_geometry.md §2 and mass_inertia.md §1 vs amr_properties.xacro')
    props = dict(re.findall(r'<xacro:property\s+name="(\w+)"\s+value="([^"]+)"', read(PROPS)))
    literal = {k: float(v) for k, v in props.items() if re.fullmatch(r'-?[\d.]+', v)}
    documented = {}
    for row in table_rows(read(DOC_GEO), r'^## 2\. Parameter table'):
        prop, value = row[1], row[2]
        names = re.findall(r'`([\w*]+)`', prop)
        if not names:
            continue
        name = names[0]
        if name.endswith('_*'):  # lidar_bracket_*: "0.080 × 0.080 × 0.030 m"
            parts = [num(p) for p in value.replace('m', '').split('×')]
            for axis, v in zip('xyz', parts):
                documented[name[:-1] + axis] = v
        else:
            documented[name] = num(value)
    mass_rows = {r[0]: num(r[1].replace('*', '')) for r in table_rows(read(DOC_MASS), r'^## 1\. Mass budget')
                 if r[0] and not r[0].startswith('**') and r[1].replace('.', '').replace('*', '').strip().isdigit()}
    mass_map = {'chassis_mass': 'Chassis + top platform', 'wheel_mass': 'Left drive wheel',
                'caster_mass': 'Caster assembly', 'lidar_bracket_mass': 'LiDAR bracket'}
    report(mass_rows.get('Left drive wheel') == mass_rows.get('Right drive wheel'),
           'mass_inertia.md §1: left and right wheel masses are equal (one `wheel_mass` property)')
    for prop, row in mass_map.items():
        documented[prop] = mass_rows[row]
    for name in sorted(documented):
        report(name in literal and close(literal[name], documented[name]),
               f'{name} = {documented[name]:g} (documented)', f'xacro {literal.get(name)}')
    undocumented = sorted(set(literal) - set(documented))
    report(not undocumented, 'every literal property in amr_properties.xacro is documented',
           ', '.join(undocumented) or f'{len(literal)} literals')
    total = documented['chassis_mass'] + 2 * documented['wheel_mass'] + documented['caster_mass'] + documented['lidar_bracket_mass']
    report(close(total, 9.4), 'documented masses sum to 9.4 kg (CALC-M1-06)', f'{total:g} kg')
    return documented


# ------------------------------------------------------------ 2. frames_and_tf.md §2 vs generated URDF
def origin(elem):
    o = elem.find('origin')
    return ([float(v) for v in o.get('xyz', '0 0 0').split()] if o is not None else [0.0] * 3,
            [float(v) for v in o.get('rpy', '0 0 0').split()] if o is not None else [0.0] * 3)


def triple(text):
    return [num(v) for v in text.strip('()').split(',')]


def check_frames(robot):
    print('== 2. Frames: frames_and_tf.md §2 joint and link inventories vs generated URDF')
    links = {l.get('name'): l for l in robot.findall('link')}
    joints = {j.get('name'): j for j in robot.findall('joint')}
    tf = read(DOC_TF)
    jrows = table_rows(tf, r'^### Joint inventory')
    lrows = table_rows(tf, r'^### Link inventory')
    doc_joints = {r[0].strip('`'): r for r in jrows}
    doc_links = {r[0].strip('`'): r for r in lrows}
    report(set(joints) == set(doc_joints) and len(joints) == 5, '5 joints, names as documented',
           ', '.join(sorted(joints)))
    report(set(links) == set(doc_links) and len(links) == 6, '6 links, names as documented',
           ', '.join(sorted(links)))
    children = {j.find('child').get('link') for j in joints.values()}
    roots = sorted(set(links) - children)
    report(roots == ['base_footprint'], 'single tree rooted at base_footprint', ', '.join(roots))
    for name, row in sorted(doc_joints.items()):
        j = joints[name]
        parent, child = [s.strip(' `') for s in row[2].split('→')]
        xyz, rpy = origin(j)
        axis_doc = None if row[4] in ('—', '-') else triple(row[4])
        axis = [float(v) for v in j.find('axis').get('xyz').split()] if j.find('axis') is not None else None
        ok = (j.get('type') == row[1] and j.find('parent').get('link') == parent
              and j.find('child').get('link') == child and all(map(close, xyz, triple(row[3])))
              and all(close(a, 0.0) for a in rpy)
              and (axis_doc is None and j.get('type') == 'fixed' or axis is not None and all(map(close, axis, axis_doc or []))))
        report(ok, f'joint {name}: {row[1]}, {parent} → {child}, xyz {row[3]}, axis {row[4]}',
               f'URDF xyz {[round(v, 9) for v in xyz]} axis {axis}')
    for name, row in sorted(doc_links.items()):
        inertial = links[name].find('inertial')
        if row[1] in ('—', '-'):
            report(inertial is None, f'link {name}: massless (no <inertial>)')
            continue
        mass = float(inertial.find('mass').get('value'))
        xyz, rpy = origin(inertial)
        ok = close(mass, num(row[1])) and all(map(close, xyz, triple(row[3]))) and all(close(a, 0.0) for a in rpy)
        report(ok, f'link {name}: mass {row[1]} kg, inertial origin {row[3]}',
               f'URDF mass {mass:g}, origin {[round(v, 9) for v in xyz]}')


# ------------------------------------------------------------ 3. derived placements and clearances
def geometry(link, tag):
    v = link.find('visual')
    g = v.find('geometry').find(tag)
    xyz, rpy = origin(v)
    return g, xyz, rpy


def check_geometry(robot, doc):
    print('== 3. Derived placements (mechanical_geometry.md §3) and clearances (CALC-M1-02 to -05, -13, -14) from the generated URDF')
    links = {l.get('name'): l for l in robot.findall('link')}
    joints = {j.get('name'): j for j in robot.findall('joint')}
    base_z = origin(joints['base_footprint_joint'])[0][2]
    box, c_xyz, _ = geometry(links['base_link'], 'box')
    L, W, H = (float(v) for v in box.get('size').split())
    cyl, _, w_rpy = geometry(links['left_wheel_link'], 'cylinder')
    r_w, w_w = float(cyl.get('radius')), float(cyl.get('length'))
    sph, _, _ = geometry(links['caster_link'], 'sphere')
    r_c = float(sph.get('radius'))
    caster = origin(joints['caster_joint'])[0]
    mount = origin(joints['lidar_mount_joint'])[0]
    bbox, b_xyz, _ = geometry(links['lidar_mount_link'], 'box')
    bx, by, bz = (float(v) for v in bbox.get('size').split())
    y_left = origin(joints['left_wheel_joint'])[0][1]
    y_right = origin(joints['right_wheel_joint'])[0][1]
    for collision_link in links.values():
        v, c = collision_link.find('visual'), collision_link.find('collision')
        if v is not None:
            same = ET.tostring(v.find('geometry')) == ET.tostring(c.find('geometry')) and origin(v) == origin(c)
            report(same, f'{collision_link.get("name")}: collision geometry and pose equal the visual')

    # §3 derived placements (typed from mechanical_geometry.md §3)
    checks = [
        ('base_link height above ground (§2, DEC-016)', base_z, 0.075),
        ('chassis centre x (§3)', c_xyz[0], -0.100),
        ('chassis centre z in base_link (§3)', c_xyz[2], 0.035),
        ('wheel joint y, left (§3)', y_left, 0.200),
        ('wheel joint y, right (§3)', y_right, -0.200),
        ('caster centre (§3) x', caster[0], -0.360),
        ('caster centre (§3) z', caster[2], -0.050),
        ('lidar_mount_link origin (§3) x', mount[0], 0.070),
        ('lidar_mount_link origin (§3) z', mount[2], 0.125),
        ('bracket box centre below mount origin (frames_and_tf.md §2)', b_xyz[2], -0.015),
        # CALC-M1-01/-02
        ('CALC-M1-01 chassis front x', c_xyz[0] + L / 2, 0.125),
        ('CALC-M1-01 chassis rear x', c_xyz[0] - L / 2, -0.325),
        ('CALC-M1-02 chassis bottom above ground (ground clearance)', base_z + c_xyz[2] - H / 2, 0.050),
        ('CALC-M1-02 platform top above ground', base_z + c_xyz[2] + H / 2, 0.170),
        ('CALC-M1-02 wheel top above ground', base_z + r_w, 0.150),
        # CALC-M1-03
        ('CALC-M1-03 wheel-to-chassis gap per side', abs(y_left) - w_w / 2 - W / 2, 0.0075),
        ('CALC-M1-03 overall width across wheel outer faces', y_left - y_right + w_w, 0.435),
        # CALC-M1-04
        ('CALC-M1-04 wheel bottom above ground', base_z - r_w, 0.0),
        ('CALC-M1-04 caster bottom above ground', base_z + caster[2] - r_c, 0.0),
        # CALC-M1-05
        ('CALC-M1-05 overall length (chassis front to caster rear)', (c_xyz[0] + L / 2) - (caster[0] - r_c), 0.510),
        ('CALC-M1-05 overall height (bracket top)', base_z + mount[2], 0.200),
        # CALC-M1-14
        ('CALC-M1-14 bracket front set back from chassis front', (c_xyz[0] + L / 2) - (mount[0] + bx / 2), 0.015),
        ('CALC-M1-14 bracket base on the platform (contact, not clearance)', (mount[2] - bz) - (c_xyz[2] + H / 2), 0.0),
    ]
    for label, actual, expected in checks:
        report(close(actual, expected), f'{label} = {expected:g} m', f'{actual:.9f}')
    # CALC-M1-13 (documented to 0.1 mm / 1 mm)
    edge_x, edge_h = c_xyz[0] - L / 2, base_z + c_xyz[2] - H / 2
    clearance = math.hypot(edge_x - caster[0], edge_h - (base_z + caster[2])) - r_c
    report(round(clearance * 1000, 1) == 18.0, 'CALC-M1-13 caster-to-chassis clearance = 18.0 mm (0.1 mm)', f'{clearance * 1000:.4f} mm')
    report(caster[0] + r_c < edge_x, 'CALC-M1-13 caster sphere entirely behind the chassis rear face',
           f'sphere front {caster[0] + r_c:.3f} < rear {edge_x:.3f}')
    swept = max(math.hypot(edge_x, W / 2), abs(caster[0] - r_c))
    report(round(swept, 3) == 0.385, 'CALC-M1-13 swept radius about base_link = 0.385 m', f'{swept:.4f} m')
    report(close(w_rpy[0], math.pi / 2) and close(w_rpy[1], 0) and close(w_rpy[2], 0),
           'OPEN-04: wheel cylinder geometry rotated rpy (pi/2, 0, 0)', str([round(a, 6) for a in w_rpy]))
    # documented parameters reproduced by the generated geometry
    for name, actual in [('chassis_length', L), ('chassis_width', W), ('chassis_height', H), ('wheel_radius', r_w),
                         ('wheel_width', w_w), ('caster_radius', r_c), ('lidar_bracket_x', bx), ('lidar_bracket_y', by),
                         ('lidar_bracket_z', bz), ('wheel_track', y_left - y_right), ('caster_x', caster[0]),
                         ('lidar_mount_x', mount[0]), ('axle_offset_x', -c_xyz[0])]:
        report(close(actual, doc[name]), f'generated URDF reproduces documented {name} = {doc[name]:g}', f'{actual:.9f}')


# ------------------------------------------------------------ 4. scope
def check_scope(robot):
    print('== 4. M1 scope: no meshes, sensors, plugins, controllers or transmissions')
    sources = sorted(f for f in os.listdir(os.path.join(ROOT, URDF_SRC)) if f.endswith('.xacro'))
    trees = [(f'{URDF_SRC}/{f}', ET.parse(os.path.join(ROOT, URDF_SRC, f)).getroot()) for f in sources]
    trees.append(('generated URDF', robot))
    banned = ('mesh', 'gazebo', 'sensor', 'plugin', 'transmission', 'ros2_control')
    for path, root in trees:
        found = {tag: sum(1 for e in root.iter() if e.tag.split('}')[-1] == tag) for tag in banned}
        report(not any(found.values()), f'{path}: no {", ".join(banned)} elements',
               ', '.join(f'{k}={v}' for k, v in found.items() if v) or 'none')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    robot_root = ET.parse(sys.argv[1]).getroot()
    documented = check_parameters()
    check_frames(robot_root)
    try:
        check_geometry(robot_root, documented)
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        # e.g. a link whose visual is no longer the documented primitive (box/cylinder/sphere)
        report(False, 'geometry checks could not run: a documented primitive or joint is missing', repr(exc))
    check_scope(robot_root)
    print(f'== {"ALL CHECKS PASSED" if failures == 0 else f"{failures} CHECK(S) FAILED"}')
    sys.exit(1 if failures else 0)
