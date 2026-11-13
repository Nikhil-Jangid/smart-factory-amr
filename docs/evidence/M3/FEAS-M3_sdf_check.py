"""FEAS-M3 G6: sensors-on SDF: links, masses, inertia, sensor poses (DEC-034 conditions)."""
import sys, xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
model = root.find('model')
fails = 0
def rep(ok, msg):
    global fails
    fails += 0 if ok else 1
    print(('PASS  ' if ok else 'FAIL  ') + msg)
total = 0.0
links = model.findall('link')
print('links:', [l.get('name') for l in links])
for l in links:
    inert = l.find('inertial')
    if inert is None:
        rep(False, f"link {l.get('name')}: no <inertial> (would be massless in SDF)")
        continue
    m = float(inert.find('mass').text); total += m
    I = inert.find('inertia')
    diag = [float(I.find(k).text) for k in ('ixx', 'iyy', 'izz')]
    rep(m > 0 and all(d > 0 for d in diag), f"link {l.get('name')}: mass {m:.6f} kg, Ixx/Iyy/Izz {diag[0]:.6g}/{diag[1]:.6g}/{diag[2]:.6g} (all > 0)")
rep(abs(total - 9.4) < 1e-9, f'total mass {total:.6f} kg == 9.4 kg')
rep(not any(l.get('name') in ('laser_frame', 'imu_link') for l in links), 'laser_frame and imu_link are lumped (not separate SDF links)')
for s in model.iter('sensor'):
    parent = next(l.get('name') for l in links if s in list(l))
    pose = s.find('pose'); fid = s.find('gz_frame_id')
    print(f"sensor {s.get('name')} type={s.get('type')} parent_link={parent} pose=[{pose.text.strip() if pose is not None else 'none'}] "
          f"relative_to={pose.get('relative_to') if pose is not None else '-'} gz_frame_id={fid.text if fid is not None else 'MISSING'}")
# expected sensor poses in base_footprint: laser = (0.070, 0, 0.075+0.125+0.030=0.230); imu = (0, 0, 0.075)
exp = {'lidar': (0.070, 0.0, 0.230), 'imu': (0.0, 0.0, 0.075)}
for s in model.iter('sensor'):
    v = [float(x) for x in s.find('pose').text.split()[:3]]
    e = exp[s.get('name')]
    rep(all(abs(a - b) < 1e-9 for a, b in zip(v, e)), f"sensor {s.get('name')} position {v} == expected {e} in base_footprint (merged link frame)")
print('== ALL CHECKS PASSED' if fails == 0 else f'== {fails} CHECK(S) FAILED')
sys.exit(1 if fails else 0)
