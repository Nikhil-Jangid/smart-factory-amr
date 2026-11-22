#!/usr/bin/env bash
# TEST-M7-02: navigation interface (REQ-M7-01, -02, -03; docs/testing/test_plan.md §12; M7 Task A).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M7/TEST-M7-02_procedure.sh <valid runs> <output log>
# Each attempt: fresh `sim.launch.py sensors:=true world:=mapping_arena.sdf` (headless unless SHOW=1), both
# controllers active, `localization.launch.py` (M6, unchanged) until amcl is active, then `navigation.launch.py`
# (DEC-066), then TEST-M7-02_interface_check.py (criteria in its header), then teardown: SIGINT to RViz, the
# navigation launch, the localization launch, then the simulation launch. Own ROS_DOMAIN_ID (171-179) and
# GZ_PARTITION per attempt; never two Gazebo runs at once. Structure, shutdown rules and options as
# docs/evidence/M6/TEST-M6-02_procedure.sh (TS-011, TS-017, TS-025, TS-029/DEC-039, TS-036, TS-039):
#  - the navigation and localization launches must stop CLEAN (classifier exit 0) with 0 leftovers; the simulation
#    launch CLEAN, or under DEC-039 the exact TS-029 signature with 0 leftovers: then the attempt is INVALID if its
#    checks passed (recorded, not counted, repeated). Attempt limit: runs + 3;
#  - the full launch logs of an attempt whose shutdown is not CLEAN are kept beside the review log as
#    <log name>_a<N>_{sim,loc,nav}_launch.log (sanitized); leftovers are also counted by process name.
# Options (environment):
#   SHOW=1          Gazebo GUI and RViz (rviz/navigation.rviz) on screen (user preference: current-milestone
#                   simulation tests are shown). Attempt 1 is recorded (tools/sim_record.sh) and photographed after
#                   the goal (tools/sim_capture.py) into docs/gallery/_pending/M7/TEST-M7-02/ (git-ignored until
#                   approved).
#   LAYOUT_FLAG=<f> with SHOW=1: attempt 1 waits (at most 15 min) until file <f> exists before the camera is set and
#                   the recording starts; a non-empty first line replaces the Gazebo camera VIEW (x y z tx ty tz).
set -u
set -m
RUNS=$1; OUT=$2
EV=docs/evidence/M7
TMP=$(mktemp -d); FAIL=0; TS029=0; VALID=0; ATTEMPT=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
HL="headless:=true"; [ "${SHOW:-0}" = 1 ] && HL="headless:=false"
B=$(basename "$OUT"); B=${B%_review.log}; B=${B%.log}
SHOTS=docs/gallery/_pending/M7/TEST-M7-02/$B
VIEW="0.8 0.0 8.0 3.0 0.0 0"   # Gazebo camera: the M5 overhead view (TEST-M5_procedure.sh; user choice 2026-11-21, replaces the far TEST-M6-02 view)
NAMES='gz sim|map_server|amcl|lifecycle_manager|planner_server|controller_server|behavior_server|bt_navigator|velocity_smoother|parameter_bridge|robot_state_publisher|rviz2 -d'
byname() { pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M7-02_procedure" | wc -l; }
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
stop_job() {  # SIGINT to a launch job, wait up to $2 s, then SIGTERM to its process group
  kill -INT "$1" 2>/dev/null
  for _ in $(seq 1 "$2"); do kill -0 "$1" 2>/dev/null || break; pause 1; done
  if kill -0 "$1" 2>/dev/null; then kill -TERM -- -"$1" 2>/dev/null; echo "# $3 did not stop on SIGINT within $2 s; SIGTERM sent to its process group"; fi
  wait "$1" 2>/dev/null
  for _ in $(seq 1 10); do pgrep -g "$1" > /dev/null || break; pause 1; done
}
check_launch() {  # $1 log key, $2 job pid, $3 label: CLEAN shutdown and no leftovers in its process group
  echo "# $3 log: $(grep -c '\[ERROR\]' "$TMP/$1_$ATTEMPT.log") [ERROR] lines"
  grep -E '\[ERROR\]|\[WARN\]' "$TMP/$1_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sort | uniq -c | sed 's/^/#   /'
  python3 -I "docs/evidence/M3/TEST-M3_launch_shutdown_classify.py" "$TMP/$1_$ATTEMPT.log"; LSH=$?
  LLEFT=$(pgrep -g "$2" | wc -l)
  echo "# $3 leftover processes: $LLEFT"
}
{
echo "# TEST-M7-02 procedure, valid runs required=$RUNS, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); navigation2 $(dpkg-query -W -f='${Version}' ros-jazzy-navigation2); launch: sim.launch.py $HL sensors:=true world:=mapping_arena.sdf + localization.launch.py + navigation.launch.py"
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1)); RC=1
  export ROS_DOMAIN_ID=$((170 + ATTEMPT)) GZ_PARTITION="amr_m7_02_$$_$ATTEMPT"
  echo; echo "## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID)"
  ros2 launch amr_bringup sim.launch.py $HL sensors:=true world:=mapping_arena.sdf > "$TMP/sim_$ATTEMPT.log" 2>&1 &
  LPID=$!; SPID=; NPID=; RPID=
  ACTIVE=0
  for _ in $(seq 1 90); do
    ACTIVE=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')
    [ "$ACTIVE" = 2 ] && break
    pause 1
  done
  [ "$ACTIVE" = 2 ] && echo "both controllers active"; rc $([ "$ACTIVE" = 2 ] && echo 0 || echo 1)
  echo; echo '$ ros2 launch amr_bringup localization.launch.py'
  ros2 launch amr_bringup localization.launch.py > "$TMP/loc_$ATTEMPT.log" 2>&1 &
  SPID=$!
  for _ in $(seq 60); do timeout --foreground 5 ros2 lifecycle get /amcl 2>/dev/null | grep -q active && break; pause 1; done
  echo "amcl: $(timeout --foreground 5 ros2 lifecycle get /amcl 2>&1)"
  if [ "${SHOW:-0}" = 1 ]; then
    for _ in $(seq 60); do xwininfo -root -tree | grep -q '("gz-sim-gui" "Gazebo GUI")' && break; pause 1; done
    QT_QPA_PLATFORM=xcb rviz2 -d "$SHARE_B/rviz/navigation.rviz" --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
    RPID=$!
  fi
  echo; echo '$ ros2 launch amr_bringup navigation.launch.py'
  ros2 launch amr_bringup navigation.launch.py > "$TMP/nav_$ATTEMPT.log" 2>&1 &
  NPID=$!
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
  echo; echo "\$ python3 $EV/TEST-M7-02_interface_check.py"
  timeout --foreground 420 python3 "$EV/TEST-M7-02_interface_check.py"; RC=$?
  echo "# checker exit $RC"
  if [ "$REC" = 1 ]; then
    pause 2
    bash tools/sim_record.sh stop "${SHOTS}_a1" | sed "s|$PWD/||g"
    python3 tools/sim_capture.py shot "${SHOTS}_a1" 2>&1 | sed "s|$PWD/||g"
  fi
  [ -n "$RPID" ] && { kill -INT "$RPID" 2>/dev/null; wait "$RPID" 2>/dev/null; }
  stop_job "$NPID" 20 "navigation launch"
  stop_job "$SPID" 20 "localization launch"
  stop_job "$LPID" 30 "simulation launch"
  SHB=0
  check_launch nav "$NPID" "navigation launch"; [ "$LSH" = 0 ] || SHB=1
  [ "$LSH" = 0 ] && [ "$LLEFT" = 0 ]; rc $?
  check_launch loc "$SPID" "localization launch"; [ "$LSH" = 0 ] || SHB=1
  [ "$LSH" = 0 ] && [ "$LLEFT" = 0 ]; rc $?
  check_launch sim "$LPID" "simulation launch"; [ "$LSH" = 0 ] || SHB=1
  if [ "$LLEFT" = 0 ] && [ "$LSH" = 3 ]; then
    TS029=$((TS029 + 1)); echo "# DEC-039: TS-029 shutdown signature only; launch-log condition not counted for this attempt"
    [ "$RC" = 0 ] && RC=2 && echo "# attempt $ATTEMPT INVALID under DEC-039 (checks passed; not counted, repeated)"
  else
    [ "$LSH" = 0 ] && [ "$LLEFT" = 0 ]; rc $?
  fi
  for _ in $(seq 1 10); do [ "$(byname)" = 0 ] && break; pause 1; done
  LEFTN=$(byname)
  echo "# leftover processes by name (gz sim, map servers, AMCL, Nav2 servers, lifecycle managers, bridge, robot_state_publisher, RViz): $LEFTN"
  pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M7-02_procedure" | sed 's/^/#   /'
  [ "$LEFTN" = 0 ]; rc $?
  if [ "$SHB" = 1 ]; then
    for K in sim loc nav; do
      sed -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/${K}_$ATTEMPT.log" > "$(dirname "$OUT")/${B}_a${ATTEMPT}_${K}_launch.log"
    done
    echo "# full launch logs kept: ${B}_a${ATTEMPT}_{sim,loc,nav}_launch.log"
  fi
  for G in "$LPID" "$SPID" "$NPID"; do [ "$(pgrep -g "$G" | wc -l)" = 0 ] || { pkill -TERM -g "$G"; echo "# leftover processes stopped with SIGTERM"; }; done
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
