"""Task D clearance check for the motion-test spawn point (0, -20) m in sensor_test.sdf (test_plan.md §7.1).

Usage: python3 -I TEST-M3-D_clearance_check.py <world.sdf> <amr_properties.xacro>
Static (before any motion run): the swept area of every Task D profile must stay clear of every model in the
world and inside the ground plane with a margin.
  Robot bounding radius R: the largest distance from base_footprint to any point of the chassis, wheels and
  caster footprints, from the amr_properties.xacro values (plus 0.05 m).
  Swept area: the robot's centre moves only along +-x from the spawn point (linear legs) or not at all
  (in-place rotation). Envelope of the profiles, from their commanded speeds and durations with the speed limit
  0.5 m/s and an allowance of +50 %: forward 0.5 m/s x 3 s + braking (stop profile) and 0.2 m/s x 5 s (linear);
  reverse 0.2 m/s x 5 s. The centre path is the segment x in [x_min, x_max], y = -20; the swept area is that
  segment dilated by R.
  Required: distance from the swept area to every model box >= 5.0 m (no LiDAR target or other model can be hit
  or interact), and to the ground-plane edge >= 5.0 m.
The harness additionally prints the measured ground-truth excursion of every run.
Exit 0 if every requirement holds.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET  # trusted repository files only

SPAWN = (0.0, -20.0)
MARGIN = 5.0


def props(path):
    text = open(path).read()
    return {m.group(1): m.group(2) for m in re.finditer(r'<xacro:property name="([^"]+)" value="([^"]+)"', text)}


def num(p, key):
    v = p[key]
    return float(v) if not v.startswith('$') else None


def main(world, xacro):
    p = props(xacro)
    need = ('chassis_length', 'chassis_width', 'wheel_radius', 'wheel_track', 'caster_x')
    vals = {k: num(p, k) for k in need}
    print('# amr_properties.xacro: ' + ', '.join(f'{k} {v}' for k, v in vals.items()))
    # Conservative footprint: chassis rectangle centred anywhere within +-caster_x of base_footprint, wheels at
    # +-track/2 with radius as half-width allowance, caster at caster_x.
    reach_x = max(vals['chassis_length'] / 2 + abs(vals['caster_x']), abs(vals['caster_x']) + vals['wheel_radius'])
    reach_y = max(vals['chassis_width'] / 2, vals['wheel_track'] / 2 + vals['wheel_radius'])
    R = math.hypot(reach_x, reach_y) + 0.05
    print(f'# robot bounding radius R = hypot({reach_x:.3f}, {reach_y:.3f}) + 0.05 = {R:.3f} m (conservative)')
    fwd = 1.5 * max(0.5 * 3.0 + 0.5 ** 2 / (2 * 0.5), 0.2 * 5.0)
    rev = 1.5 * 0.2 * 5.0
    x_min, x_max = SPAWN[0] - rev, SPAWN[0] + fwd
    print(f'# centre path: x {x_min:+.3f} .. {x_max:+.3f} m at y {SPAWN[1]:+.1f} m (profiles +50 %); swept area = path dilated by R')
    ok = True
    root = ET.parse(world).getroot()
    for model in root.iter('model'):
        name = model.get('name')
        box = model.find('link/collision/geometry/box/size')
        plane = model.find('link/collision/geometry/plane/size')
        pose = [float(v) for v in (model.find('pose').text.split() if model.find('pose') is not None else [0] * 6)]
        if box is not None:
            sx, sy, _ = (float(v) for v in box.text.split())
            # distance from segment to axis-aligned rectangle (2D)
            bx0, bx1, by0, by1 = pose[0] - sx / 2, pose[0] + sx / 2, pose[1] - sy / 2, pose[1] + sy / 2
            dx = max(bx0 - x_max, x_min - bx1, 0.0)
            dy = max(by0 - SPAWN[1], SPAWN[1] - by1, 0.0)
            d = math.hypot(dx, dy) - R
            good = d >= MARGIN
            print(f'{"PASS" if good else "FAIL"}  {name}: box x {bx0:+.3f}..{bx1:+.3f}, y {by0:+.3f}..{by1:+.3f}; '
                  f'clearance from the swept area {d:.3f} m >= {MARGIN} m')
            ok &= good
        elif plane is not None:
            px, py = (float(v) for v in plane.text.split())
            d = min(px / 2 - max(abs(x_min), abs(x_max)), py / 2 - abs(SPAWN[1])) - R
            good = d >= MARGIN
            print(f'{"PASS" if good else "FAIL"}  {name}: plane {px:g} x {py:g} m centred at the origin; '
                  f'distance from the swept area to its edge {d:.3f} m >= {MARGIN} m')
            ok &= good
    print('== CLEARANCE OK' if ok else '== CLEARANCE INSUFFICIENT')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
