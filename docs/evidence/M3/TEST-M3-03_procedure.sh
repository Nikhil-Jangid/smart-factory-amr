#!/usr/bin/env bash
# TEST-M3-03: sensor frames (REQ-M3-03; DEC-036 D5; docs/testing/test_plan.md §7.2).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Writes docs/evidence/M3/TEST-M3-03${TAG}_review.log and TEST-M3-03${TAG}_frames.gv/.pdf (view_frames).
# Model: the M3 simulation model (use_ros2_control:=true use_sensors:=true), published by robot_state_publisher;
# joint_state_publisher publishes zero wheel positions so that the whole tree exists. No Gazebo is needed:
# both sensor transforms are fixed joints of the URDF (frames_and_tf.md §5).
# Isolation: own ROS_DOMAIN_ID; job control (set -m) so SIGINT reaches the background nodes (TS-011, TS-021).
# Fixed after attempt 1 (TS-025): robot_description goes through a params file (rcl rejected the URDF as an
# inline -p override), and every timeout uses --foreground (under set -m, a plain timeout also signalled this script).
set -u
set -m
TAG=${1:-}
EV=docs/evidence/M3
OUT=$EV/TEST-M3-03${TAG}_review.log; FRAMES=$EV/TEST-M3-03${TAG}_frames
export ROS_DOMAIN_ID=${ROS_DOMAIN_ID_TEST:-87}
TMP=$(mktemp -d); FAIL=0
CTRL="$(ros2 pkg prefix amr_bringup)/share/amr_bringup/config/controllers.yaml"
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro use_ros2_control:=true controllers_file:="$CTRL" use_sensors:=true) > "$TMP/s2.urdf"
python3 -I - "$TMP/s2.urdf" "$TMP/rsp_params.yaml" <<'PY'
import sys, yaml
text = open(sys.argv[1]).read()
yaml.safe_dump({'robot_state_publisher': {'ros__parameters': {'robot_description': text}}}, open(sys.argv[2], 'w'))
PY
ros2 run robot_state_publisher robot_state_publisher --ros-args --params-file "$TMP/rsp_params.yaml" > "$TMP/rsp.log" 2>&1 &
RSP=$!
ros2 run joint_state_publisher joint_state_publisher > "$TMP/jsp.log" 2>&1 &
JSP=$!
for _ in $(seq 1 50); do ros2 topic list 2>/dev/null | grep -q '^/tf_static$' && break; timeout --foreground 0.2 tail -f /dev/null; done
{
echo "# TEST-M3-03 sensor frames, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted Task A changes)')"
echo "# model: xacro amr.urdf.xacro use_ros2_control:=true controllers_file:=<ctrl> use_sensors:=true; ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
for pair in "lidar_mount_link laser_frame" "base_link imu_link"; do
  echo; echo "\$ timeout --foreground -s INT 4 ros2 run tf2_ros tf2_echo $pair   (record; tf2_echo prints 3 decimals)"
  timeout --foreground -s INT 4 ros2 run tf2_ros tf2_echo $pair 2>&1 | grep -E 'At time|Translation|Rotation: in Quaternion|Rotation: in RPY \(radian\)' | head -4
done
echo; echo '$ python3 docs/evidence/M3/TEST-M3-03_tf_check.py   (D5 at full precision; single tree)'
python3 "$EV/TEST-M3-03_tf_check.py"; rc $?
echo; echo '$ ros2 run tf2_tools view_frames   (TF tree diagram)'
(cd "$TMP" && timeout --foreground 30 ros2 run tf2_tools view_frames > view_frames.log 2>&1); echo "# view_frames exit $?"
GV=$(ls "$TMP"/frames_*.gv 2>/dev/null | head -1)
if [ -n "$GV" ]; then cp "$GV" "$FRAMES.gv" && cp "${GV%.gv}.pdf" "$FRAMES.pdf"; fi
python3 -I - "$FRAMES.gv" <<'PY'
import re, sys
edges = sorted(set(re.findall(r'"([^"]+)" -> "([^"]+)"', open(sys.argv[1]).read())))
print('edges:', edges)
expected = sorted({('base_footprint', 'base_link'), ('base_link', 'left_wheel_link'), ('base_link', 'right_wheel_link'),
                   ('base_link', 'caster_link'), ('base_link', 'lidar_mount_link'), ('lidar_mount_link', 'laser_frame'),
                   ('base_link', 'imu_link')})
children = [c for _, c in edges]
ok = edges == expected and len(children) == len(set(children))
print(('PASS' if ok else 'FAIL') + '  view_frames tree == M1 tree + lidar_mount_link -> laser_frame + base_link -> imu_link; one parent per frame')
sys.exit(0 if ok else 1)
PY
rc $?
echo "FAIL=$FAIL"
} > "$TMP/raw.log" 2>&1
kill -INT -- -$JSP -$RSP 2>/dev/null; wait $JSP $RSP 2>/dev/null
for _ in $(seq 1 20); do pgrep -g $RSP,$JSP > /dev/null || break; timeout --foreground 0.25 tail -f /dev/null; done
LEFT=$(pgrep -g $RSP,$JSP | wc -l)   # processes left in the two test process groups (set -m: one group per job)
FAIL=$(sed -n 's/^FAIL=//p' "$TMP/raw.log")
{ grep -v '^FAIL=' "$TMP/raw.log"
  echo; echo "# node logs: $(cat "$TMP/rsp.log" "$TMP/jsp.log" | grep -c -E '\[(ERROR|FATAL)\]') [ERROR]/[FATAL] lines; leftover test processes: $LEFT"
  [ "$LEFT" = 0 ] || FAIL=1
  echo "# overall: $([ "$FAIL" = 0 ] && echo 'ALL CHECKS PASSED' || echo 'AT LEAST ONE CHECK FAILED')"
} | sed -e "s|$TMP|<tmp>|g" -e "s|$CTRL|<ctrl>|g" -e "s|$HOME|<home>|g" > "$OUT"
rm -rf "$TMP"
# Exit status from this procedure's own verdict line only (the checker also prints 'ALL CHECKS PASSED';
# anchored 2026-11-03 after TEST-M3-04 R1 exited 0 with a failed launch-log step).
grep -q '^# overall: ALL CHECKS PASSED' "$OUT"
