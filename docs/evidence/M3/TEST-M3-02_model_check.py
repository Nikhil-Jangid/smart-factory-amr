"""TEST-M3-02 model checks for the sensors-on variants (REQ-M3-02, DEC-034; DEC-030 to DEC-032 values).

Usage: python3 -I TEST-M3-02_model_check.py <off.urdf> <s1.urdf> <m2.urdf> <s2.urdf> <s1.sdf> <s2.sdf> <m2.sdf>
  off = default expansion (M1); s1 = use_sensors:=true only;
  m2  = use_ros2_control:=true (M2); s2 = use_ros2_control:=true use_sensors:=true (the M3 simulation model).
Checks:
  A. URDF: every link and joint of the sensors-off variant is element-for-element identical in the
     sensors-on variant (geometry, inertials, joints unchanged); the only additions are laser_frame and
     imu_link (no inertial, visual or collision) and their fixed joints at the DEC-030 / DEC-032 offsets.
  B. SDF (s1 and s2): every link has mass > 0 and Ixx, Iyy, Izz > 0; total mass 9.4 kg; laser_frame and
     imu_link are lumped; the inertial blocks of s2 equal those of m2; sensor poses in base_footprint
     equal (0.070, 0, 0.230) for the LiDAR and (0, 0, 0.075) for the IMU, with zero rotation.
  C. Sensor configuration in the SDF equals DEC-031 (LiDAR) and DEC-032 as amended by DEC-038 (IMU); exactly two
     sensors (no camera or depth sensor, DEC-037).
Exit 0 only if every check passes.
History: updated for TEST-M3-02 re-test 2, before that run (DEC-038). The IMU now samples at 1000 Hz on
/imu_raw, with raw noise = DEC-032 value x sqrt(10). The model gains one model-level <gazebo> element holding the
ImuDecimator plugin (/imu_raw -> /imu, block 10, 1000 -> 100 Hz), checked in C. Earlier runs used the DEC-032
expectations (100 Hz, /imu, 0.001 / 0.01, six added elements); their logs are unchanged.
"""
import math
import sys
import xml.etree.ElementTree as ET

TOL = 1e-9
failures = 0


def report(ok, msg):
    global failures
    failures += 0 if ok else 1
    print(('PASS  ' if ok else 'FAIL  ') + msg)


def canon(elem):
    """Serialization of an element without its tail. ET.tostring() appends the tail (the whitespace after the
    closing tag), which xacro sets differently for the last element before </robot> when more elements follow.
    Fixed after the first formal run (TS-024); the element content is still compared byte for byte."""
    tail, elem.tail = elem.tail, None
    try:
        return ET.tostring(elem)
    finally:
        elem.tail = tail


def close(a, b, tol=TOL):
    return all(abs(x - y) <= tol for x, y in zip(a, b)) and len(a) == len(b)


def floats(text):
    return [float(v) for v in text.split()]


def urdf_parts(path):
    root = ET.parse(path).getroot()
    links = {l.get('name'): l for l in root.findall('link')}
    joints = {j.get('name'): j for j in root.findall('joint')}
    return links, joints


def check_urdf_pair(off_path, on_path, label):
    print(f'== A. URDF {label}')
    off_links, off_joints = urdf_parts(off_path)
    on_links, on_joints = urdf_parts(on_path)
    for name, link in off_links.items():
        same = name in on_links and canon(link) == canon(on_links[name])
        report(same, f'{label}: link {name} identical with sensors on (visual, collision, inertial)')
    for name, joint in off_joints.items():
        same = name in on_joints and canon(joint) == canon(on_joints[name])
        report(same, f'{label}: joint {name} identical with sensors on')
    # Whole-document check: every top-level element of the sensors-off variant (links, joints, <gazebo>,
    # <ros2_control>) appears unchanged with sensors on; the only additions are the six sensor elements.
    off_top = [canon(e) for e in ET.parse(off_path).getroot()]
    on_root = ET.parse(on_path).getroot()
    remaining = [canon(e) for e in on_root]
    missing = 0
    for e in off_top:
        if e in remaining:
            remaining.remove(e)
        else:
            missing += 1
    report(missing == 0, f'{label}: all {len(off_top)} top-level elements of the sensors-off variant unchanged with sensors on')
    extra = sorted((e.tag, e.get('name') or e.get('reference') or '') for e in on_root if canon(e) in remaining)
    expected_extra = sorted([('joint', 'laser_joint'), ('link', 'laser_frame'), ('joint', 'imu_joint'), ('link', 'imu_link'),
                             ('gazebo', 'laser_frame'), ('gazebo', 'imu_link'), ('gazebo', '')])
    report(extra == expected_extra, f'{label}: added top-level elements {extra} == the six sensor elements and the '
                                    f'model-level <gazebo> of the DEC-038 decimator plugin')
    added_links = sorted(set(on_links) - set(off_links))
    added_joints = sorted(set(on_joints) - set(off_joints))
    report(added_links == ['imu_link', 'laser_frame'], f'{label}: added links {added_links} == [imu_link, laser_frame]')
    report(added_joints == ['imu_joint', 'laser_joint'], f'{label}: added joints {added_joints} == [imu_joint, laser_joint]')
    for name in ('laser_frame', 'imu_link'):
        link = on_links.get(name)
        empty = link is not None and len(list(link)) == 0
        report(empty, f'{label}: {name} has no inertial, visual or collision (massless frame, DEC-034)')
    expect = {'laser_joint': ('lidar_mount_link', 'laser_frame', [0.0, 0.0, 0.030]),   # DEC-030
              'imu_joint': ('base_link', 'imu_link', [0.0, 0.0, 0.0])}                 # DEC-032
    for name, (parent, child, xyz) in expect.items():
        j = on_joints.get(name)
        if j is None:
            report(False, f'{label}: joint {name} missing')
            continue
        o = j.find('origin')
        got_xyz = floats(o.get('xyz')) if o is not None else []
        got_rpy = floats(o.get('rpy', '0 0 0')) if o is not None else []
        ok = (j.get('type') == 'fixed' and j.find('parent').get('link') == parent
              and j.find('child').get('link') == child and close(got_xyz, xyz) and close(got_rpy, [0, 0, 0]))
        report(ok, f'{label}: {name} fixed, {parent} -> {child}, xyz {got_xyz} == {xyz}, rpy {got_rpy} == [0, 0, 0]')


def sdf_model(path):
    return ET.parse(path).getroot().find('model')


def inertials(model):
    return {l.get('name'): canon(l.find('inertial')) for l in model.findall('link')}


def check_sdf(path, label):
    print(f'== B. SDF {label}')
    model = sdf_model(path)
    links = model.findall('link')
    print(f'{label}: links {[l.get("name") for l in links]}')
    total = 0.0
    for l in links:
        inert = l.find('inertial')
        if inert is None:
            report(False, f'{label}: link {l.get("name")} has no <inertial> (massless in SDF)')
            continue
        m = float(inert.find('mass').text)
        total += m
        i = inert.find('inertia')
        diag = [float(i.find(k).text) for k in ('ixx', 'iyy', 'izz')]
        report(m > 0 and all(d > 0 for d in diag),
               f'{label}: link {l.get("name")} mass {m:.6f} kg, Ixx/Iyy/Izz {diag[0]:.6g}/{diag[1]:.6g}/{diag[2]:.6g} (all > 0)')
    report(abs(total - 9.4) < TOL, f'{label}: total mass {total:.9f} kg == 9.4 kg')
    names = {l.get('name') for l in links}
    report(not names & {'laser_frame', 'imu_link'}, f'{label}: laser_frame and imu_link lumped (not separate SDF links)')
    expected_pose = {'lidar': [0.070, 0.0, 0.230, 0.0, 0.0, 0.0], 'imu': [0.0, 0.0, 0.075, 0.0, 0.0, 0.0]}
    sensors = list(model.iter('sensor'))
    for s in sensors:
        parent = next(l.get('name') for l in links if s in list(l))
        pose = s.find('pose')
        got = floats(pose.text) if pose is not None else []
        rel = pose.get('relative_to') if pose is not None else None
        exp = expected_pose.get(s.get('name'))
        report(exp is not None and parent == 'base_footprint' and rel in (None, '__model__', 'base_footprint') and close(got, exp),
               f'{label}: sensor {s.get("name")} on link {parent}, pose {got} (relative_to {rel}) == {exp} in base_footprint')
    return model


def text(elem, path):
    found = elem.find(path)
    return None if found is None else found.text.strip()


def check_config(model, label):
    print(f'== C. Sensor configuration {label} (DEC-031, DEC-032)')
    sensors = {s.get('name'): s for s in model.iter('sensor')}
    types = sorted((n, s.get('type')) for n, s in sensors.items())
    report(types == [('imu', 'imu'), ('lidar', 'gpu_lidar')],
           f'{label}: sensors {types} == [(imu, imu), (lidar, gpu_lidar)]; no camera or depth sensor (DEC-037)')
    lid = sensors.get('lidar')
    if lid is not None:
        h = lid.find('lidar/scan/horizontal')
        mn, mx, n = float(text(h, 'min_angle')), float(text(h, 'max_angle')), int(text(h, 'samples'))
        step = (mx - mn) / (n - 1)
        report(abs(mn + math.pi) < 1e-12, f'{label}: lidar min_angle {mn!r} == -pi')
        report(abs(mx - 3.12413936106985) < 1e-12, f'{label}: lidar max_angle {mx!r} == 3.12413936106985 (sensors.md §6.1)')
        report(n == 360 and abs(step - math.pi / 180) < 1e-12, f'{label}: lidar 360 samples, step {math.degrees(step)!r} deg == 1 deg')
        v = lid.find('lidar/scan/vertical')
        report(int(text(v, 'samples')) == 1, f'{label}: lidar 1 vertical ray')
        report(float(text(lid, 'update_rate')) == 10.0, f'{label}: lidar update_rate {text(lid, "update_rate")} == 10 Hz')
        rmin, rmax = float(text(lid, 'lidar/range/min')), float(text(lid, 'lidar/range/max'))
        report(rmin == 0.12 and rmax == 12.0, f'{label}: lidar range {rmin}..{rmax} m == 0.12..12.0 m')
        report(text(lid, 'lidar/noise/type') == 'gaussian' and float(text(lid, 'lidar/noise/mean')) == 0.0
               and float(text(lid, 'lidar/noise/stddev')) == 0.01, f'{label}: lidar noise gaussian, mean 0, stddev 0.01 m')
        report(text(lid, 'topic') == '/scan' and text(lid, 'gz_frame_id') == 'laser_frame',
               f'{label}: lidar topic {text(lid, "topic")} == /scan, gz_frame_id {text(lid, "gz_frame_id")} == laser_frame')
    imu = sensors.get('imu')
    if imu is not None:
        report(float(text(imu, 'update_rate')) == 1000.0,
               f'{label}: imu update_rate {text(imu, "update_rate")} == 1000 Hz (raw sampling, DEC-038)')
        report(text(imu, 'topic') == '/imu_raw' and text(imu, 'gz_frame_id') == 'imu_link',
               f'{label}: imu topic {text(imu, "topic")} == /imu_raw (Gazebo-internal), gz_frame_id '
               f'{text(imu, "gz_frame_id")} == imu_link')
        # DEC-032 output values; raw = output x sqrt(10) (DEC-038 item 4, derived, Calculated)
        for group, sd_out in (('angular_velocity', 0.001), ('linear_acceleration', 0.01)):
            sd = sd_out * math.sqrt(10)
            for axis in ('x', 'y', 'z'):
                noise = imu.find(f'imu/{group}/{axis}/noise')
                ok = (noise is not None and noise.get('type') == 'gaussian' and float(text(noise, 'mean')) == 0.0
                      and abs(float(text(noise, 'stddev')) - sd) <= 1e-12 * sd
                      and noise.find('bias_mean') is None and noise.find('bias_stddev') is None)
                report(ok, f'{label}: imu {group} {axis}: gaussian, mean 0, raw stddev {text(noise, "stddev") if noise is not None else None} '
                           f'== {sd_out} x sqrt(10), no bias terms')
    plugins = [pl for pl in model.findall('plugin') if pl.get('name') == 'amr_gazebo_plugins::ImuDecimator']
    report(len(plugins) == 1, f'{label}: model-level ImuDecimator plugin elements: {len(plugins)} == 1 (DEC-038)')
    if plugins:
        pl = plugins[0]
        got = {k: text(pl, k) for k in ('input_topic', 'output_topic', 'block_size', 'raw_rate', 'output_rate')}
        exp = {'input_topic': '/imu_raw', 'output_topic': '/imu', 'block_size': '10', 'raw_rate': '1000',
               'output_rate': '100'}
        report(pl.get('filename') == 'amr_imu_decimator_system' and got == exp,
               f'{label}: ImuDecimator filename {pl.get("filename")} == amr_imu_decimator_system, parameters {got} == {exp}')


def main(argv):
    if len(argv) != 8:
        print(__doc__)
        return 2
    off, s1, m2, s2, s1_sdf, s2_sdf, m2_sdf = argv[1:]
    check_urdf_pair(off, s1, 'default vs use_sensors')
    check_urdf_pair(m2, s2, 'M2 vs M2 + use_sensors')
    check_sdf(s1_sdf, 'sdf(use_sensors)')
    model = check_sdf(s2_sdf, 'sdf(M2 + use_sensors)')
    same = inertials(model) == inertials(sdf_model(m2_sdf))
    report(same, 'sdf: inertial blocks of M2 + use_sensors identical to M2 (links %s)' % sorted(inertials(model)))
    check_config(model, 'sdf(M2 + use_sensors)')
    print('== ALL CHECKS PASSED' if failures == 0 else f'== {failures} CHECK(S) FAILED')
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
