#!/usr/bin/env bash
# OPEN-08 validation (DEC-023): conditional ros2_control option in the AMR Xacro, checked on a TEMPORARY copy.
# Nothing in amr_ws/ is modified. Run from the repository root after `source /opt/ros/jazzy/setup.bash`.
# Checks: (1) default expansion byte-identical to the M1 evidence URDF; (2) explicit false identical;
# (3) enabled expansion valid (check_urdf, 6 links / 5 joints, one ros2_control system on the two wheel
# joints, plugin parameters path passed through); (4) gz sdf conversion keeps the plugin; (5) M1 property
# check on both variants. The ros2_control content below is a validation PROTOTYPE, not the implementation.
set -u
REPO=$(pwd); TMP=$(mktemp -d); FAIL=0
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
echo "# OPEN-08 Xacro option check, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)"
mkdir -p "$TMP/amr_ws/src" && cp -r amr_ws/src/amr_description "$TMP/amr_ws/src/"
U="$TMP/amr_ws/src/amr_description/urdf"
python3 -I - "$U/amr.urdf.xacro" <<'EOF'
import sys
p = sys.argv[1]; s = open(p).read()
head = '<robot name="amr" xmlns:xacro="http://www.ros.org/wiki/xacro">'
s = s.replace(head, head + '\n  <xacro:arg name="use_ros2_control" default="false"/>\n  <xacro:arg name="controllers_file" default=""/>', 1)
s = s.replace('\n</robot>', '\n  <xacro:if value="$(arg use_ros2_control)">\n    <!-- comment inside the conditional: dropped when false -->\n    <xacro:include filename="amr.ros2_control.xacro"/>\n  </xacro:if>\n\n</robot>', 1)
open(p, 'w').write(s)
EOF
cat > "$U/amr.ros2_control.xacro" <<'EOF'
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
  <ros2_control name="AmrGazeboSystem" type="system">
    <hardware><plugin>gz_ros2_control/GazeboSimSystem</plugin></hardware>
    <joint name="left_wheel_joint"><command_interface name="velocity"/><state_interface name="position"/><state_interface name="velocity"/></joint>
    <joint name="right_wheel_joint"><command_interface name="velocity"/><state_interface name="position"/><state_interface name="velocity"/></joint>
  </ros2_control>
  <gazebo>
    <plugin filename="gz_ros2_control-system" name="gz_ros2_control::GazeboSimROS2ControlPlugin">
      <parameters>$(arg controllers_file)</parameters>
    </plugin>
  </gazebo>
</robot>
EOF
cd "$TMP/amr_ws"
echo; echo '$ xacro src/amr_description/urdf/amr.urdf.xacro > off.urdf; cmp off.urdf <repo>/docs/evidence/M1/TEST-M1-02_amr.urdf'
xacro src/amr_description/urdf/amr.urdf.xacro > ../off.urdf && cmp ../off.urdf "$REPO/docs/evidence/M1/TEST-M1-02_amr.urdf" && echo "identical"; rc $?
echo; echo '$ xacro ... use_ros2_control:=false; cmp with default'
xacro src/amr_description/urdf/amr.urdf.xacro use_ros2_control:=false > ../off2.urdf && cmp ../off.urdf ../off2.urdf && echo "identical"; rc $?
echo; echo '$ xacro ... use_ros2_control:=true controllers_file:=/path/controllers.yaml > on.urdf; check_urdf on.urdf'
xacro src/amr_description/urdf/amr.urdf.xacro use_ros2_control:=true controllers_file:=/path/controllers.yaml > ../on.urdf && check_urdf ../on.urdf | grep -E 'Successfully|root Link'; rc ${PIPESTATUS[0]}
echo; echo '$ structure of on.urdf'
python3 -I - ../on.urdf <<'EOF'
import sys, xml.etree.ElementTree as ET
r = ET.parse(sys.argv[1]).getroot(); rc = r.findall('ros2_control')
ok = len(r.findall('link')) == 6 and len(r.findall('joint')) == 5 and len(rc) == 1 \
     and [j.get('name') for j in rc[0].findall('joint')] == ['left_wheel_joint', 'right_wheel_joint'] \
     and r.find('gazebo/plugin/parameters').text == '/path/controllers.yaml'
print('links', len(r.findall('link')), 'joints', len(r.findall('joint')), 'ros2_control systems', len(rc),
      'joints', [j.get('name') for j in rc[0].findall('joint')], 'parameters', r.find('gazebo/plugin/parameters').text)
sys.exit(0 if ok else 1)
EOF
rc $?
echo; echo '$ gz sdf -p on.urdf > on.sdf; grep plugin'
gz sdf -p ../on.urdf > ../on.sdf && grep -c 'gz_ros2_control-system' ../on.sdf; rc $?
gz sdf -p ../off.urdf > ../off.sdf
echo; echo '$ TEST-M1-03_check.py off.urdf off.sdf   # default variant: all M1 checks expected to pass'
python3 -I "$REPO/docs/evidence/M1/TEST-M1-03_check.py" ../off.urdf ../off.sdf | tail -1; rc ${PIPESTATUS[0]}
echo; echo '$ TEST-M1-03_check.py on.urdf on.sdf    # enabled variant: only the two M1-scope checks (REQ-M1-09, -10) expected to fail'
python3 -I "$REPO/docs/evidence/M1/TEST-M1-03_check.py" ../on.urdf ../on.sdf | grep -E '^FAIL|CHECK'
N=$(python3 -I "$REPO/docs/evidence/M1/TEST-M1-03_check.py" ../on.urdf ../on.sdf | grep -c '^FAIL')
M=$(python3 -I "$REPO/docs/evidence/M1/TEST-M1-03_check.py" ../on.urdf ../on.sdf | grep '^FAIL' | grep -c -E 'REQ-M1-09|REQ-M1-10')
[ "$N" = 2 ] && [ "$M" = 2 ] && echo "only the expected M1-scope checks fail"; rc $?
cd "$REPO"; rm -rf "$TMP"
echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL CHECKS PASSED' || echo 'AT LEAST ONE CHECK FAILED')"
exit $FAIL
