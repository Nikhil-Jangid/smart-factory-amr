#!/usr/bin/env bash
# TEST-M5-02: SLAM interface (REQ-M5-02, -03; docs/testing/test_plan.md §10; M5 Task A).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M5/TEST-M5-02_procedure.sh <valid runs> <output log>
# Each attempt: fresh `sim.launch.py sensors:=true world:=mapping_arena.sdf` (headless unless SHOW=1), both
# controllers active, checker step `pre` (SLAM not running), then `slam.launch.py` (DEC-050), checker step `main`
# (TEST-M5-02_interface_check.py: criteria in its header), then teardown: SIGINT to RViz, the SLAM launch, then the
# simulation launch. Own ROS_DOMAIN_ID (111-119) and GZ_PARTITION per attempt; never two Gazebo runs at once.
# Shutdown (test_plan §7.1 rules, as M3): the SLAM launch must stop CLEAN (classifier exit 0) with 0 leftovers; the
# simulation launch CLEAN, or under DEC-039 the exact TS-029 signature (gz only, sensors on) with 0 leftovers: then the
# attempt is INVALID if its checks passed (recorded, not counted, repeated). Attempt limit: runs + 3.
# Dropped scans (INFO): lines of the SLAM log with "dropping" (tf2 message filter) or "queue" are counted.
# Job control (set -m; TS-011), launches outside any pipeline (TS-017), timeout --foreground (TS-025).
# Options (environment):
#   SHOW=1          Gazebo GUI and RViz (rviz/mapping.rviz) on screen (simulation tests are shown).
#                   Attempt 1 is recorded (tools/sim_record.sh) and photographed after the drive (tools/sim_capture.py)
#                   into docs/gallery/_pending/M5/TEST-M5-02/ (git-ignored until accepted).
#   LAYOUT_FLAG=<f> with SHOW=1: attempt 1 waits (at most 15 min) until file <f> exists before the camera is set and
#                   the recording starts, so the two windows can be placed side by side first (window positions
#                   cannot be set from a script under Wayland). The test checks do not depend on the wait.
#                   If the file is not empty, its first line replaces the Gazebo camera VIEW (x y z tx ty tz), so the
#                   view can be chosen for the window shape that was set (added after the first formal run).
# Changed after the first formal run (2026-11-15, TS-039), before any re-run:
#  - the full launch logs (simulation and SLAM) of an attempt whose shutdown is not CLEAN are kept beside the review
#    log as <log name>_a<N>_{sim,slam}_launch.log (sanitized); the first run kept only the [ERROR]/[WARN] summary;
#  - leftover processes are also counted by name (`gz sim`, `slam_toolbox`, `parameter_bridge`,
#    `robot_state_publisher`, `rviz2`): with the GUI, `gz sim` starts its server and GUI in their own process groups
#    (cmdsim8.rb: Process.setpgid), so the process-group count alone cannot see them;
#  - the default camera view looks along +x from the west, for the portrait 3D view of a half-screen window.
set -u
set -m
RUNS=$1; OUT=$2
EV=docs/evidence/M5
TMP=$(mktemp -d); FAIL=0; TS029=0; VALID=0; ATTEMPT=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
HL="headless:=true"; [ "${SHOW:-0}" = 1 ] && HL="headless:=false"
B=$(basename "$OUT"); B=${B%_review.log}; B=${B%.log}
SHOTS=docs/gallery/_pending/M5/TEST-M5-02/$B
VIEW="-7.5 0.0 10.0 3.2 0.0 0"   # Gazebo camera: whole 10 x 8 m arena from the west, above (portrait view)
NAMES='gz sim|async_slam_toolbox|parameter_bridge|robot_state_publisher|rviz2 -d'
byname() { pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M5-02_procedure" | wc -l; }
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
stop_job() {  # SIGINT to a launch job, wait up to $2 s, then SIGTERM to its process group
  kill -INT "$1" 2>/dev/null
  for _ in $(seq 1 "$2"); do kill -0 "$1" 2>/dev/null || break; pause 1; done
  if kill -0 "$1" 2>/dev/null; then kill -TERM -- -"$1" 2>/dev/null; echo "# $3 did not stop on SIGINT within $2 s; SIGTERM sent to its process group"; fi
  wait "$1" 2>/dev/null
  for _ in $(seq 1 10); do pgrep -g "$1" > /dev/null || break; pause 1; done
}
{
echo "# TEST-M5-02 procedure, valid runs required=$RUNS, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); slam_toolbox $(dpkg-query -W -f='${Version}' ros-jazzy-slam-toolbox); launch: sim.launch.py $HL sensors:=true world:=mapping_arena.sdf + slam.launch.py"
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1)); RC=1
  export ROS_DOMAIN_ID=$((110 + ATTEMPT)) GZ_PARTITION="amr_m5_02_$$_$ATTEMPT"
  echo; echo "## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID)"
  ros2 launch amr_bringup sim.launch.py $HL sensors:=true world:=mapping_arena.sdf > "$TMP/sim_$ATTEMPT.log" 2>&1 &
  LPID=$!; SPID=; RPID=
  ACTIVE=0
  for _ in $(seq 1 90); do
    ACTIVE=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')
    [ "$ACTIVE" = 2 ] && break
    pause 1
  done
  [ "$ACTIVE" = 2 ] && echo "both controllers active"; rc $([ "$ACTIVE" = 2 ] && echo 0 || echo 1)
  if [ "${SHOW:-0}" = 1 ]; then
    for _ in $(seq 60); do xwininfo -root -tree | grep -q '("gz-sim-gui" "Gazebo GUI")' && break; pause 1; done
    QT_QPA_PLATFORM=xcb rviz2 -d "$SHARE_B/rviz/mapping.rviz" --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
    RPID=$!
  fi
  echo; echo "\$ python3 $EV/TEST-M5-02_interface_check.py pre <state>"
  timeout --foreground 120 python3 "$EV/TEST-M5-02_interface_check.py" pre "$TMP/state.json"; RCP=$?
  echo "# checker (pre) exit $RCP"
  echo; echo '$ ros2 launch amr_bringup slam.launch.py'
  ros2 launch amr_bringup slam.launch.py > "$TMP/slam_$ATTEMPT.log" 2>&1 &
  SPID=$!
  REC=0
  if [ -n "$RPID" ] && [ "$ATTEMPT" = 1 ]; then
    if [ -n "${LAYOUT_FLAG:-}" ]; then
      for _ in $(seq 900); do [ -e "$LAYOUT_FLAG" ] && break; pause 1; done
      echo "# window layout confirmed: $([ -e "$LAYOUT_FLAG" ] && echo yes || echo 'no (15 min timeout)')"
      [ -s "${LAYOUT_FLAG}" ] && VIEW=$(head -1 "$LAYOUT_FLAG") && echo "# camera view from the layout file: $VIEW"
    else
      pause 8
    fi
    mkdir -p "$(dirname "$SHOTS")"
    python3 tools/sim_capture.py view $VIEW > /dev/null 2>&1; pause 3
    bash tools/sim_record.sh start "${SHOTS}_a1" | sed "s|$PWD/||g"; pause 3   # stale-frame window (TS-036)
    REC=1
  elif [ -n "$RPID" ]; then
    (sleep 10; python3 tools/sim_capture.py view $VIEW > /dev/null 2>&1) &
  fi
  echo; echo "\$ python3 $EV/TEST-M5-02_interface_check.py main <state>"
  timeout --foreground 240 python3 "$EV/TEST-M5-02_interface_check.py" main "$TMP/state.json"; RC=$?
  echo "# checker (main) exit $RC"
  [ "$RCP" = 0 ] || { [ "$RCP" = 2 ] && RC=2 || RC=1; }
  if [ "$REC" = 1 ]; then
    pause 2
    bash tools/sim_record.sh stop "${SHOTS}_a1" | sed "s|$PWD/||g"
    python3 tools/sim_capture.py shot "${SHOTS}_a1" 2>&1 | sed "s|$PWD/||g"
  fi
  [ -n "$RPID" ] && { kill -INT "$RPID" 2>/dev/null; wait "$RPID" 2>/dev/null; }
  stop_job "$SPID" 20 "SLAM launch"
  stop_job "$LPID" 30 "simulation launch"
  DROP=$(grep -c -i -E 'dropping|queue' "$TMP/slam_$ATTEMPT.log")
  echo "# SLAM log: $(grep -c '\[ERROR\]' "$TMP/slam_$ATTEMPT.log") [ERROR] lines; lines with 'dropping' or 'queue' (dropped scans, INFO): $DROP"
  grep -E '\[ERROR\]|\[WARN\]|dropping|queue' "$TMP/slam_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sort | uniq -c | sed 's/^/#   /'
  python3 -I "docs/evidence/M3/TEST-M3_launch_shutdown_classify.py" "$TMP/slam_$ATTEMPT.log"; SHS=$?
  LEFTS=$(pgrep -g "$SPID" | wc -l)
  echo "# SLAM launch leftover processes: $LEFTS"
  [ "$SHS" = 0 ] && [ "$LEFTS" = 0 ]; rc $?
  echo "# simulation log: $(grep -c '\[ERROR\]' "$TMP/sim_$ATTEMPT.log") [ERROR] lines"
  grep -E '\[ERROR\]|\[WARN\]' "$TMP/sim_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sort | uniq -c | sed 's/^/#   /'
  python3 -I "docs/evidence/M3/TEST-M3_launch_shutdown_classify.py" "$TMP/sim_$ATTEMPT.log"; SH=$?
  LEFT=$(pgrep -g "$LPID" | wc -l)
  echo "# simulation launch leftover processes: $LEFT"
  if [ "$LEFT" = 0 ] && [ "$SH" = 3 ]; then
    TS029=$((TS029 + 1)); echo "# DEC-039: TS-029 shutdown signature only; launch-log condition not counted for this attempt"
    [ "$RC" = 0 ] && RC=2 && echo "# attempt $ATTEMPT INVALID under DEC-039 (checks passed; not counted, repeated)"
  else
    [ "$SH" = 0 ] && [ "$LEFT" = 0 ]; rc $?
  fi
  for _ in $(seq 1 10); do [ "$(byname)" = 0 ] && break; pause 1; done
  LEFTN=$(byname)
  echo "# leftover processes by name (gz sim, SLAM, bridge, robot_state_publisher, RViz): $LEFTN"
  pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M5-02_procedure" | sed 's/^/#   /'
  [ "$LEFTN" = 0 ]; rc $?
  if [ "$SH" != 0 ] || [ "$SHS" != 0 ]; then
    for K in sim slam; do
      sed -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/${K}_$ATTEMPT.log" > "$(dirname "$OUT")/${B}_a${ATTEMPT}_${K}_launch.log"
    done
    echo "# full launch logs kept: ${B}_a${ATTEMPT}_sim_launch.log, ${B}_a${ATTEMPT}_slam_launch.log"
  fi
  for G in "$LPID" "$SPID"; do [ "$(pgrep -g "$G" | wc -l)" = 0 ] || { pkill -TERM -g "$G"; echo "# leftover processes stopped with SIGTERM"; }; done
  [ "$LEFTN" = 0 ] || { pkill -TERM -f "$NAMES"; echo "# leftover processes (by name) stopped with SIGTERM"; }
  case $RC in
    0) VALID=$((VALID + 1)) ;;
    2) echo "# attempt $ATTEMPT INVALID (not counted)" ;;
    *) VALID=$((VALID + 1)); FAIL=1 ;;
  esac
done
[ "$VALID" -lt "$RUNS" ] && FAIL=1 && echo "# only $VALID valid runs of $RUNS"
echo "# TS-029 attempts declared invalid under DEC-039: $TS029"
echo; echo "# overall: $([ $FAIL = 0 ] && echo "ALL $RUNS VALID RUNS PASSED" || echo 'AT LEAST ONE CHECK FAILED')"
} > "$TMP/raw.log" 2>&1   # not a pipeline: launches started inside a pipeline ignore SIGINT (TS-017)
sed -e "s|$TMP|<tmp>|g" -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/raw.log" > "$OUT"
rm -rf "$TMP"
grep -q '^# overall: ALL .* VALID RUNS PASSED' "$OUT"
