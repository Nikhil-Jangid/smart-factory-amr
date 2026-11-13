#!/usr/bin/env bash
# TS-014 diagnostic (not a test; the repository model is NOT changed): copies amr_description and
# amr_bringup into a temporary workspace, replaces ONLY the wheel <collision> geometry (cylinder
# r = wheel_radius, length = wheel_width, rpy pi/2) by a sphere of the same radius (visual, inertia,
# joints, friction, controller unchanged), builds it there, and runs the TEST-M2-06 rotate mode once.
# Run from the repository root after `source /opt/ros/jazzy/setup.bash`. Writes the given log.
# Result 2026-10-22: TS-014_rotate_sphere_wheels.log (+180.18 / -179.87 deg) against
# TS-014_rotate_cylinder_wheels.log (+196.34 / -196.39 deg, same harness, repository model).
set -u
OUT=$1; WS=$(mktemp -d)
mkdir -p "$WS/src" && cp -r amr_ws/src/amr_description amr_ws/src/amr_bringup "$WS/src/"
python3 -I - "$WS/src/amr_description/urdf/amr.urdf.xacro" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
a = '''      <collision>
        <origin xyz="0 0 0" rpy="${pi / 2} 0 0"/>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>'''
b = '''      <collision>
        <origin xyz="0 0 0" rpy="0 0 0"/>
        <geometry>
          <sphere radius="${wheel_radius}"/>
        </geometry>
      </collision>'''
assert s.count(a) == 1
open(p, 'w').write(s.replace(a, b))
PY
(cd "$WS" && colcon build --packages-select amr_description amr_bringup > /dev/null 2>&1) || { echo "scratch build failed"; exit 1; }
source "$WS/install/setup.bash"
bash docs/evidence/M2/TEST-M2_procedure.sh rotate 1 "$OUT"
RC=$?
rm -rf "$WS"
exit $RC
