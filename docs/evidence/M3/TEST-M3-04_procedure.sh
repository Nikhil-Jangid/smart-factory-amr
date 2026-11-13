#!/usr/bin/env bash
# TEST-M3-04: sensor topics, rates, frames, stamps (REQ-M3-04 to -06; DEC-036 D1-D4) and the unchanged
# default launch (DEC-034; Task B acceptance criterion 2). docs/testing/test_plan.md §7.2.
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Writes docs/evidence/M3/TEST-M3-04${TAG}_review.log (TAG empty for the first run, -R1 for re-test 1, ...).
#
# Part 1 (sensors on): sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf; robot at the origin.
#   Gazebo command line and world name recorded and checked; TEST-M3-04_topics_check.py (D1-D4) once both
#   controllers are active. An invalid run (RTF < 0.5, checker exit 2) is repeated, at most 3 attempts.
# Part 2 (defaults): sim.launch.py headless:=true, no other argument. The Gazebo command line must be exactly
#   `gz sim -r -s empty.sdf` (the M2 command, which the M2 harness also looks for), the world `empty` (its
#   /world/empty/pose/info is the M2 ground truth), the published robot_description byte-identical to the
#   M2 expansion (xacro ... use_ros2_control:=true controllers_file:=<ctrl>), and no /scan, /imu or
#   sensor_bridge (TEST-M3-04_default_check.py).
# Both parts: fresh launch, own ROS_DOMAIN_ID and GZ_PARTITION, both controllers active within 90 s,
# SIGINT to the launch process only (as the M2 procedures), and afterwards 0 [ERROR] lines in the launch
# log and 0 leftover processes in the launch's process group. Job control (set -m; TS-011, TS-021) and
# timeout --foreground (TS-025); the launches run outside any pipeline (TS-017). The gz_ros2_control "IMU sensor ... skipping" warning is expected.
# DEC-039 (added 2026-11-04, before any run under it): the launch-log condition is judged by
# TEST-M3_launch_shutdown_classify.py. In Part 1 (sensor launch), an attempt whose only defect is the exact TS-029
# shutdown signature (upstream gz shutdown deadlock; only gz escalates after SIGINT, every other process finishes
# cleanly, 0 leftovers) is INVALID if its checks passed: recorded, not counted, repeated within the 3 attempts.
# Part 2 (default launch, no rendering sensor) keeps the strict 0-[ERROR] rule.
set -u
set -m
TAG=${1:-}
EV=docs/evidence/M3
OUT=$EV/TEST-M3-04${TAG}_review.log
TMP=$(mktemp -d); FAIL=0; TS029=0; SHUT_TS029=0
SHARE_D="$(ros2 pkg prefix amr_description)/share/amr_description"
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
CTRL="$SHARE_B/config/controllers.yaml"
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }

start_launch() {  # $1 = label; remaining arguments go to the launch
  local label=$1; shift
  echo "\$ ros2 launch amr_bringup sim.launch.py $*   (ROS_DOMAIN_ID=$ROS_DOMAIN_ID, GZ_PARTITION=<label>_<pid>)"
  ros2 launch amr_bringup sim.launch.py "$@" > "$TMP/launch_$label.log" 2>&1 &
  LPID=$!
  local active=0
  for _ in $(seq 1 90); do
    active=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')
    [ "$active" = 2 ] && break
    pause 1
  done
  timeout --foreground 10 ros2 control list_controllers 2>&1 | grep -v 'waiting for service'
  [ "$active" = 2 ] && echo "both controllers active"; rc $([ "$active" = 2 ] && echo 0 || echo 1)
  GZCMD=$(pgrep -a -g "$LPID" | grep -m1 -E '^[0-9]+ gz sim ' | cut -d' ' -f2-)   # the launch's process group (set -m)
  echo "# Gazebo command line: $GZCMD"
}

stop_launch() {  # $1 = label; $2 = dec039 to apply the DEC-039 TS-029 rule (sensor launch only)
  local label=$1
  kill -INT "$LPID" 2>/dev/null
  for _ in $(seq 1 30); do kill -0 "$LPID" 2>/dev/null || break; pause 1; done
  if kill -0 "$LPID" 2>/dev/null; then kill -TERM -- -"$LPID" 2>/dev/null; echo "# launch did not stop on SIGINT within 30 s; SIGTERM sent to its process group"; fi
  wait "$LPID" 2>/dev/null
  for _ in $(seq 1 10); do pgrep -g "$LPID" > /dev/null || break; pause 1; done
  local left nerr
  left=$(pgrep -g "$LPID" | wc -l)
  nerr=$(grep -c '\[ERROR\]' "$TMP/launch_$label.log")
  echo "# launch log: $nerr [ERROR] lines; leftover processes in the launch process group: $left"
  grep -E '\[ERROR\]|\[WARN\]' "$TMP/launch_$label.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//; s/\[(pid|[a-z_]+-)[0-9]+\]?//g' | sort | uniq -c | sed 's/^/#   /'
  python3 -I "$EV/TEST-M3_launch_shutdown_classify.py" "$TMP/launch_$label.log"; local sh=$?
  SHUT_TS029=0
  if [ "${2:-}" = dec039 ] && [ "$left" = 0 ] && [ "$sh" = 3 ]; then
    SHUT_TS029=1; TS029=$((TS029 + 1)); echo "# DEC-039: TS-029 shutdown signature only; launch-log condition not counted for this attempt"
  else
    [ "$sh" = 0 ] && [ "$left" = 0 ]; rc $?
  fi
  if [ "$left" != 0 ]; then pkill -TERM -g "$LPID"; echo "# leftover processes stopped with SIGTERM"; fi
}

{
echo "# TEST-M3-04 topics and default launch, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted Task B changes)')"
echo "# $(gz sim --version | head -1); ros_gz_bridge $(dpkg-query -W -f='${Version}' ros-jazzy-ros-gz-bridge); <share_b> = <install>/share/amr_bringup"

echo; echo "## Part 1: sensors on (sensor_test.sdf), D1-D4"
ATTEMPT=0; RC1=2
while [ "$RC1" = 2 ] && [ "$ATTEMPT" -lt 3 ]; do
  ATTEMPT=$((ATTEMPT + 1))
  export ROS_DOMAIN_ID=$((88 + ATTEMPT)) GZ_PARTITION="amr_m3_04_s_$$_$ATTEMPT"
  echo; echo "### attempt $ATTEMPT"
  start_launch sensors_$ATTEMPT headless:=true sensors:=true world:=sensor_test.sdf
  EXP="gz sim -r -s --headless-rendering $SHARE_B/worlds/sensor_test.sdf"
  [ "$GZCMD" = "$EXP" ] && echo "Gazebo command == gz sim -r -s --headless-rendering <share_b>/worlds/sensor_test.sdf"; rc $?
  echo '$ gz topic -l | grep /world/sensor_test/pose/info   (world name sensor_test, from the world file)'
  timeout --foreground 10 gz topic -l | grep -x '/world/sensor_test/pose/info'; rc $?
  echo; echo '$ python3 docs/evidence/M3/TEST-M3-04_topics_check.py'
  timeout --foreground 120 python3 "$EV/TEST-M3-04_topics_check.py"; RC1=$?
  echo "# checker exit $RC1"
  stop_launch sensors_$ATTEMPT dec039
  [ "$SHUT_TS029" = 1 ] && [ "$RC1" = 0 ] && RC1=2 && echo "# attempt $ATTEMPT INVALID under DEC-039 (measurement checks passed; not counted, repeated)"
done
[ "$RC1" = 0 ] || FAIL=1
[ "$RC1" = 2 ] && echo "# no valid run in 3 attempts"

echo; echo "## Part 2: default launch (no sensors, no world argument) == M2"
export ROS_DOMAIN_ID=92 GZ_PARTITION="amr_m3_04_d_$$"
start_launch default headless:=true
[ "$GZCMD" = "gz sim -r -s empty.sdf" ] && echo "Gazebo command == gz sim -r -s empty.sdf (M2)"; rc $?
echo '$ gz topic -l | grep /world/empty/pose/info   (world empty: the M2 ground-truth topic)'
timeout --foreground 10 gz topic -l | grep -x '/world/empty/pose/info'; rc $?
echo; echo '$ python3 docs/evidence/M3/TEST-M3-04_default_check.py <tmp>/published.urdf'
timeout --foreground 60 python3 "$EV/TEST-M3-04_default_check.py" "$TMP/published.urdf"; rc $?
echo '$ xacro <share_d>/urdf/amr.urdf.xacro use_ros2_control:=true controllers_file:=<ctrl> > <tmp>/m2.urdf   (the M2 launch command); cmp'
xacro "$SHARE_D/urdf/amr.urdf.xacro" use_ros2_control:=true controllers_file:="$CTRL" > "$TMP/m2.urdf"
cmp "$TMP/published.urdf" "$TMP/m2.urdf" && echo "published robot_description byte-identical to the M2 expansion"; rc $?
sha256sum "$TMP/published.urdf" "$TMP/m2.urdf"
stop_launch default

echo "# TS-029 attempts declared invalid under DEC-039: $TS029"
echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL CHECKS PASSED' || echo 'AT LEAST ONE CHECK FAILED')"
} > "$TMP/raw.log" 2>&1   # not a pipeline: launches started inside a pipeline ignore SIGINT (TS-017)
sed -e "s|$TMP|<tmp>|g" -e "s|$CTRL|<ctrl>|g" -e "s|$SHARE_B|<share_b>|g" -e "s|$SHARE_D|<share_d>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g; s|_$$\b|_<pid>|g" "$TMP/raw.log" > "$OUT"
rm -rf "$TMP"
# Exit status from this procedure's own verdict line only (the checker also prints 'ALL CHECKS PASSED';
# anchored 2026-11-03 after TEST-M3-04 R1 exited 0 with a failed launch-log step).
grep -q '^# overall: ALL CHECKS PASSED' "$OUT"
