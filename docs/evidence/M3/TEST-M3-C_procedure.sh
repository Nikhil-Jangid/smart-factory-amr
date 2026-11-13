#!/usr/bin/env bash
# Task C procedure: TEST-M3-05 (mode range) and TEST-M3-06 (mode fov); docs/testing/test_plan.md §7.2.
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M3/TEST-M3-C_procedure.sh <range|fov> <output log>
# Fresh launch `sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf` (robot at the origin, yaw 0),
# both controllers active, then TEST-M3-C_lidar_check.py <mode> <installed world file>. An invalid run (checker
# exit 2, e.g. RTF < 0.5) is repeated, at most 3 attempts (sensors.md §7.5). Each attempt: own ROS_DOMAIN_ID
# (101-109) and GZ_PARTITION; SIGINT to the launch process only; 0 [ERROR] lines and 0 leftover processes in the
# launch's process group are required. Job control (set -m; TS-011), launches outside any pipeline (TS-017),
# timeout --foreground (TS-025). Task C and Task D runs are serialized (never two Gazebo runs at once).
# DEC-039 (added 2026-11-04, before any run under it): the launch-log condition is judged by
# TEST-M3_launch_shutdown_classify.py. An attempt whose only defect is the exact TS-029 shutdown signature (upstream
# gz shutdown deadlock; only gz escalates after SIGINT, every other process finishes cleanly, 0 leftovers) is INVALID
# if its measurement checks passed: it is recorded, not counted, and repeated within the existing attempt limit.
# Any other [ERROR] line or leftover process still fails the attempt.
set -u
set -m
MODE=$1; OUT=$2
EV=docs/evidence/M3
TMP=$(mktemp -d); FAIL=0; TS029=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
WORLD="$SHARE_B/worlds/sensor_test.sdf"
BASE=$([ "$MODE" = range ] && echo 100 || echo 104)
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
{
echo "# Task C procedure mode=$MODE, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); world <share_b>/worlds/sensor_test.sdf sha256 $(sha256sum "$WORLD" | cut -c1-16)…"
ATTEMPT=0; RC=2
while [ "$RC" = 2 ] && [ "$ATTEMPT" -lt 3 ]; do
  ATTEMPT=$((ATTEMPT + 1))
  export ROS_DOMAIN_ID=$((BASE + ATTEMPT)) GZ_PARTITION="amr_m3_c_${MODE}_$$_$ATTEMPT"
  echo; echo "## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID)"
  echo '$ ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf'
  ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf > "$TMP/launch_$ATTEMPT.log" 2>&1 &
  LPID=$!
  ACTIVE=0
  for _ in $(seq 1 90); do
    ACTIVE=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')
    [ "$ACTIVE" = 2 ] && break
    pause 1
  done
  [ "$ACTIVE" = 2 ] && echo "both controllers active"; rc $([ "$ACTIVE" = 2 ] && echo 0 || echo 1)
  echo "# Gazebo command line: $(pgrep -a -g "$LPID" | grep -m1 -E '^[0-9]+ gz sim ' | cut -d' ' -f2-)"
  echo; echo "\$ python3 $EV/TEST-M3-C_lidar_check.py $MODE <share_b>/worlds/sensor_test.sdf"
  timeout --foreground 180 python3 "$EV/TEST-M3-C_lidar_check.py" "$MODE" "$WORLD"; RC=$?
  echo "# checker exit $RC"
  kill -INT "$LPID" 2>/dev/null
  for _ in $(seq 1 30); do kill -0 "$LPID" 2>/dev/null || break; pause 1; done
  if kill -0 "$LPID" 2>/dev/null; then kill -TERM -- -"$LPID" 2>/dev/null; echo "# launch did not stop on SIGINT within 30 s; SIGTERM sent to its process group"; fi
  wait "$LPID" 2>/dev/null
  for _ in $(seq 1 10); do pgrep -g "$LPID" > /dev/null || break; pause 1; done
  LEFT=$(pgrep -g "$LPID" | wc -l); NERR=$(grep -c '\[ERROR\]' "$TMP/launch_$ATTEMPT.log")
  echo "# launch log: $NERR [ERROR] lines; leftover processes in the launch process group: $LEFT"
  grep -E '\[ERROR\]|\[WARN\]' "$TMP/launch_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sort | uniq -c | sed 's/^/#   /'
  python3 -I "$EV/TEST-M3_launch_shutdown_classify.py" "$TMP/launch_$ATTEMPT.log"; SH=$?
  if [ "$LEFT" = 0 ] && [ "$SH" = 3 ]; then
    TS029=$((TS029 + 1)); echo "# DEC-039: TS-029 shutdown signature only; launch-log condition not counted for this attempt"
    [ "$RC" = 0 ] && RC=2 && echo "# attempt $ATTEMPT INVALID under DEC-039 (measurement checks passed; not counted, repeated)"
  else
    [ "$SH" = 0 ] && [ "$LEFT" = 0 ]; rc $?
  fi
  if [ "$LEFT" != 0 ]; then pkill -TERM -g "$LPID"; echo "# leftover processes stopped with SIGTERM"; fi
  [ "$RC" = 2 ] && echo "# attempt $ATTEMPT INVALID (not counted)"
done
[ "$RC" = 0 ] || FAIL=1
[ "$RC" = 2 ] && echo "# no valid run in 3 attempts"
echo "# TS-029 attempts declared invalid under DEC-039: $TS029"
echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL CHECKS PASSED' || echo 'AT LEAST ONE CHECK FAILED')"
} > "$TMP/raw.log" 2>&1   # not a pipeline: launches started inside a pipeline ignore SIGINT (TS-017)
sed -e "s|$TMP|<tmp>|g" -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/raw.log" > "$OUT"
rm -rf "$TMP"
# Exit status from this procedure's own verdict line only (the checker also prints 'ALL CHECKS PASSED';
# anchored 2026-11-03 after TEST-M3-04 R1 exited 0 with a failed launch-log step).
grep -q '^# overall: ALL CHECKS PASSED' "$OUT"
