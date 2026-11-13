#!/usr/bin/env python3
"""TEST-M1-03: check the generated URDF (a) and Gazebo SDF (b) against the M1 design documents.

Usage: python3 -I TEST-M1-03_check.py <amr.urdf> <amr.sdf>

Expected values are typed in from docs/design/mechanical_geometry.md (§2, §3),
docs/design/mass_inertia.md (CALC-M1-04, -06 to -10, -15) and docs/design/frames_and_tf.md (§2).
They are deliberately not read from amr_properties.xacro, so the check is independent of the code.
Prints one line per check and exits 0 only if every check passes.
"""
import math
import sys
import xml.etree.ElementTree as ET

failures = 0


def report(ok, label, detail=''):
    global failures
    failures += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {label}{'  [' + detail + ']' if detail else ''}")


def sig4(x):
    """Round to 4 significant figures (the reporting precision in mass_inertia.md)."""
    return 0.0 if x == 0 else round(x, 3 - int(math.floor(math.log10(abs(x)))))


def vec(text):
    return [float(v) for v in text.split()]


def close(a, b, tol=1e-9):
    return all(abs(x - y) <= tol for x, y in zip(a, b)) and len(a) == len(b)


# ---------------------------------------------------------------- expected design values
LINKS = {'base_footprint', 'base_link', 'left_wheel_link', 'right_wheel_link', 'caster_link', 'lidar_mount_link'}
JOINTS = {  # name: (type, parent, child, origin xyz, axis)
    'base_footprint_joint': ('fixed', 'base_footprint', 'base_link', [0, 0, 0.075], None),
    'left_wheel_joint': ('continuous', 'base_link', 'left_wheel_link', [0, 0.200, 0], [0, 1, 0]),
    'right_wheel_joint': ('continuous', 'base_link', 'right_wheel_link', [0, -0.200, 0], [0, 1, 0]),
    'caster_joint': ('fixed', 'base_link', 'caster_link', [-0.360, 0, -0.050], None),
    'lidar_mount_joint': ('fixed', 'base_link', 'lidar_mount_link', [0.070, 0, 0.125], None),
}
# link: (mass, inertial origin xyz, (Ixx, Iyy, Izz) as documented to 4 s.f.)
INERTIALS = {
    'base_link': (8.0, [-0.100, 0, 0.035], (0.09127, 0.1446, 0.2167)),               # CALC-M1-07
    'left_wheel_link': (0.5, [0, 0, 0], (7.542e-4, 1.406e-3, 7.542e-4)),            # CALC-M1-08, Iyy axial
    'right_wheel_link': (0.5, [0, 0, 0], (7.542e-4, 1.406e-3, 7.542e-4)),
    'caster_link': (0.2, [0, 0, 0], (5.000e-5, 5.000e-5, 5.000e-5)),                # CALC-M1-09
    'lidar_mount_link': (0.2, [0, 0, -0.015], (1.217e-4, 1.217e-4, 2.133e-4)),      # CALC-M1-10
}
# link: (geometry tag, attributes, visual/collision origin xyz, rpy)
GEOMETRY = {
    'base_link': ('box', {'size': [0.450, 0.350, 0.120]}, [-0.100, 0, 0.035], [0, 0, 0]),
    'left_wheel_link': ('cylinder', {'radius': [0.075], 'length': [0.035]}, [0, 0, 0], [math.pi / 2, 0, 0]),
    'right_wheel_link': ('cylinder', {'radius': [0.075], 'length': [0.035]}, [0, 0, 0], [math.pi / 2, 0, 0]),
    'caster_link': ('sphere', {'radius': [0.025]}, [0, 0, 0], [0, 0, 0]),
    'lidar_mount_link': ('box', {'size': [0.080, 0.080, 0.030]}, [0, 0, -0.015], [0, 0, 0]),
}


def origin_of(elem):
    o = elem.find('origin')
    xyz = vec(o.get('xyz', '0 0 0')) if o is not None else [0, 0, 0]
    rpy = vec(o.get('rpy', '0 0 0')) if o is not None else [0, 0, 0]
    return xyz, rpy


# ---------------------------------------------------------------- (a) URDF level
def check_urdf(path):
    print(f'== (a) URDF level: {path}')
    robot = ET.parse(path).getroot()
    links = {l.get('name'): l for l in robot.findall('link')}
    joints = {j.get('name'): j for j in robot.findall('joint')}
    report(set(links) == LINKS, f'6 links with the designed names (found {len(links)})')
    report(set(joints) == set(JOINTS), f'5 joints with the designed names (found {len(joints)})')

    for name, (jtype, parent, child, xyz, axis) in JOINTS.items():
        j = joints[name]
        oxyz, orpy = origin_of(j)
        ok = (j.get('type') == jtype and j.find('parent').get('link') == parent
              and j.find('child').get('link') == child and close(oxyz, xyz) and close(orpy, [0, 0, 0]))
        if axis is not None:
            ok = ok and close(vec(j.find('axis').get('xyz')), axis)
        report(ok, f'joint {name}: {jtype}, {parent} -> {child}, xyz {xyz}, axis {axis}',
               f'xyz {oxyz} rpy {orpy}')

    report(links['base_footprint'].find('inertial') is None, 'base_footprint is massless (root)')
    total = 0.0
    for name, (mass, cxyz, moments) in INERTIALS.items():
        inertial = links[name].find('inertial')
        m = float(inertial.find('mass').get('value'))
        total += m
        oxyz, orpy = origin_of(inertial)
        t = inertial.find('inertia')
        ixx, iyy, izz = (float(t.get(k)) for k in ('ixx', 'iyy', 'izz'))
        off = [float(t.get(k)) for k in ('ixy', 'ixz', 'iyz')]
        report(abs(m - mass) <= 1e-9 and close(oxyz, cxyz) and close(orpy, [0, 0, 0]),
               f'{name}: mass {mass} kg, inertial origin {cxyz}', f'mass {m}, xyz {oxyz}')
        report(tuple(sig4(v) for v in (ixx, iyy, izz)) == moments and off == [0, 0, 0],
               f'{name}: (Ixx, Iyy, Izz) = {moments} to 4 s.f., off-diagonal 0',
               f'{ixx:.6g}, {iyy:.6g}, {izz:.6g}')
        report(min(ixx, iyy, izz) > 0 and ixx + iyy >= izz and ixx + izz >= iyy and iyy + izz >= ixx,
               f'{name}: moments > 0 and triangle inequality')
    report(abs(total - 9.4) <= 1e-9, 'total mass 9.4 kg (CALC-M1-06)', f'{total:.6g} kg')

    for name, (tag, attrs, gxyz, grpy) in GEOMETRY.items():
        for kind in ('visual', 'collision'):
            e = links[name].find(kind)
            g = e.find('geometry').find(tag)
            oxyz, orpy = origin_of(e)
            ok = g is not None and close(oxyz, gxyz) and close(orpy, grpy)
            if g is not None:
                ok = ok and all(close(vec(g.get(k)), v) for k, v in attrs.items())
            report(ok, f'{name} {kind}: {tag} {attrs} at xyz {gxyz} rpy {[round(a, 4) for a in grpy]}')

    # CALC-M1-04: lowest points of wheels and caster at ground level (z = 0 in base_footprint)
    base_z = vec(joints['base_footprint_joint'].find('origin').get('xyz'))[2]
    for wheel in ('left_wheel_joint', 'right_wheel_joint'):
        z = base_z + vec(joints[wheel].find('origin').get('xyz'))[2] - 0.075
        report(abs(z) <= 1e-9, f'{wheel}: wheel bottom at z = 0 above ground', f'{z:.3g} m')
    z = base_z + vec(joints['caster_joint'].find('origin').get('xyz'))[2] - 0.025
    report(abs(z) <= 1e-9, 'caster bottom at z = 0 above ground', f'{z:.3g} m')

    # Element-level checks: xacro copies XML comments into the URDF, so a plain text search
    # would also match comments that merely say "no meshes" (TS-007).
    meshes = sum(1 for _ in robot.iter('mesh'))
    files = [e.get('filename') for e in robot.iter() if e.get('filename')]
    report(meshes == 0 and not files, 'no <mesh> elements or filename references (REQ-M1-10)',
           f'{meshes} mesh, {len(files)} filename')
    extras = sum(1 for tag in ('gazebo', 'sensor', 'plugin') for _ in robot.iter(tag))
    report(extras == 0, 'no <gazebo>, <sensor> or <plugin> elements (REQ-M1-09)', f'{extras} found')


# ---------------------------------------------------------------- (b) SDF level
def check_sdf(path):
    print(f'== (b) SDF level after fixed-joint lumping: {path}')
    model = ET.parse(path).getroot().find('model')
    links = {l.get('name'): l for l in model.findall('link')}
    report(set(links) == {'base_footprint', 'left_wheel_link', 'right_wheel_link'},
           f'3 links: base_footprint (lumped) + 2 wheels (found {sorted(links)})')

    lump = links['base_footprint'].find('inertial')
    m = float(lump.find('mass').text)
    pose = vec(lump.find('pose').text)
    report(abs(m - 8.4) <= 1e-9, 'lumped base_footprint mass 8.4 kg (CALC-M1-15)', f'{m:.6g} kg')
    report([sig4(v) for v in pose[:3]] == [-0.1021, 0.0, 0.1098] and close(pose[3:], [0, 0, 0]),
           'lumped CoM (-0.1021, 0, +0.1098) m in base_footprint, 4 s.f.; no rotation', f'pose {pose}')
    total = m + sum(float(links[w].find('inertial').find('mass').text) for w in ('left_wheel_link', 'right_wheel_link'))
    report(abs(total - 9.4) <= 1e-9, 'SDF total mass 9.4 kg', f'{total:.6g} kg')

    # Parallel-axis combination of CALC-M1-07, -09, -10 about the lumped CoM, recomputed here.
    # Bodies: (mass, CoM in base_footprint, principal moments about own CoM, link-aligned axes)
    bodies = [
        (8.0, (-0.100, 0, 0.110), (8.0 * (0.350**2 + 0.120**2) / 12, 8.0 * (0.450**2 + 0.120**2) / 12,
                                   8.0 * (0.450**2 + 0.350**2) / 12)),
        (0.2, (-0.360, 0, 0.025), (0.4 * 0.2 * 0.025**2,) * 3),
        (0.2, (0.070, 0, 0.185), (0.2 * (0.080**2 + 0.030**2) / 12, 0.2 * (0.080**2 + 0.030**2) / 12,
                                  0.2 * (0.080**2 + 0.080**2) / 12)),
    ]
    mL = sum(b[0] for b in bodies)
    c = [sum(b[0] * b[1][k] for b in bodies) / mL for k in range(3)]
    expected = dict.fromkeys(('ixx', 'iyy', 'izz', 'ixy', 'ixz', 'iyz'), 0.0)
    for mi, ri, (a, b_, cc) in bodies:
        d = [ri[k] - c[k] for k in range(3)]
        expected['ixx'] += a + mi * (d[1]**2 + d[2]**2)
        expected['iyy'] += b_ + mi * (d[0]**2 + d[2]**2)
        expected['izz'] += cc + mi * (d[0]**2 + d[1]**2)
        expected['ixy'] -= mi * d[0] * d[1]
        expected['ixz'] -= mi * d[0] * d[2]
        expected['iyz'] -= mi * d[1] * d[2]
    tensor = lump.find('inertia')
    for k, e in expected.items():
        got = float(tensor.find(k).text)
        ok = sig4(got) == sig4(e) if abs(e) > 1e-12 else abs(got) <= 1e-12
        report(ok, f'lumped {k} = parallel-axis combination {sig4(e):.4g} kg m^2 (4 s.f.)', f'{got:.6g}')

    collisions = [c_.get('name') for c_ in links['base_footprint'].findall('collision')]
    report(len(collisions) == 3 and sum('fixed_joint_lump' in n for n in collisions) == 3,
           'base_footprint holds the 3 lumped collisions (chassis, caster, bracket)', ', '.join(collisions))
    frames = {f.get('name') for f in model.iter('frame')}
    report({'base_link', 'caster_link', 'lidar_mount_link'} <= frames,
           'lumped links survive as <frame> elements', ', '.join(sorted(frames)))
    joints = {j.get('name'): j.get('type') for j in model.findall('joint')}
    report(joints == {'left_wheel_joint': 'revolute', 'right_wheel_joint': 'revolute'},
           'only the 2 wheel joints remain, converted to revolute', str(joints))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    check_urdf(sys.argv[1])
    check_sdf(sys.argv[2])
    print(f'== {"ALL CHECKS PASSED" if failures == 0 else f"{failures} CHECK(S) FAILED"}')
    sys.exit(1 if failures else 0)
