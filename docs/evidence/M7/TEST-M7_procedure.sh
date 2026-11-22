#!/usr/bin/env bash
# TEST-M7-03 to -06: formal navigation runs (REQ-M7-04 to -09; docs/testing/test_plan.md §12; M7 Task C).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M7/TEST-M7_procedure.sh <TEST-M7-03|04|05|06|09> <valid runs> <output log>
# TEST-M7-09 (REQ-M7-12, observed by me; added 2026-11-23, TS-057): SHOW=1 DONE_FLAG=<file> ... TEST-M7-09 1 <log>.
# Same launches, layout, camera, recording, screenshots and teardown as the other tests; instead of the harness the
# user sends goals with the RViz Nav2 goal tool until <file> exists. Supporting record: every NavigateToPose goal's
# final status (TEST-M7-09_goal_status.py). The attempt passes when the launches stop CLEAN with 0 leftovers; the
# test result is the user's observation, recorded in TEST_RESULTS.md.
# Test -> harness mode (TEST-M7_nav_run.py; goals TEST-M7_goals.py): 03 sequence (G1..G6, NavigateToPose), 04 route
# (G1 -> G3 -> G5, NavigateThroughPoses, DEC-078), 05 invalid (inside P1, outside the map), 06 cancel (G1, after 1.0 m).
# Each attempt: fresh `sim.launch.py sensors:=true world:=mapping_arena.sdf` (headless unless SHOW=1), both
# controllers active, `localization.launch.py` until amcl is active, then `navigation.launch.py`, then the harness
# (recording into <log dir>/<log name>_a<N>_{track,cmd,goals,plans}.csv and _meta.json) and the offline checker
# TEST-M7_nav_check.py --test <TEST-ID> on that recording (criteria DEC-073, in the checker's header), then teardown:
# SIGINT to RViz, the navigation launch, the localization launch, then the simulation launch. The robot starts at the
# spawn pose in every attempt (DEC-058). Own ROS_DOMAIN_ID and GZ_PARTITION per attempt; never two Gazebo runs at once.
# Attempt classification: harness exit 2 (invalid run: RTF < 0.5, missing samples, no result) -> INVALID, not counted,
# repeated; checker exit 0 -> PASS; otherwise FAIL. Structure, shutdown rules and options as TEST-M7-02_procedure.sh
# (TS-011, TS-017, TS-025, TS-029/DEC-039, TS-036, TS-039):
#  - the navigation and localization launches must stop CLEAN (classifier exit 0) with 0 leftovers; the simulation
#    launch CLEAN, or under DEC-039 the exact TS-029 signature with 0 leftovers: then the attempt is INVALID if its
#    checks passed (recorded, not counted, repeated); with SHOW=1 the same holds for the TS-039 GUI front-end
#    signature (classifier exit 4, DEC-079). Attempt limit: runs + 3;
#  - the full launch logs of an attempt whose shutdown is not CLEAN are kept beside the review log as
#    <log name>_a<N>_{sim,loc,nav}_launch.log (sanitized); leftovers are also counted by process name.
# Options (environment):
#   SHOW=1          Gazebo GUI (capture layout gui_config:=gazebo_gui_capture.config, DEC-075) and RViz
#                   (rviz/navigation.rviz) on screen. The Gazebo camera is the fixed M5 overhead view for the whole run
#                   (DEC-075 amendment). Attempt 1 is recorded (tools/sim_record.sh) and photographed after the run
#                   (tools/sim_capture.py) into docs/gallery/_pending/M7/<TEST-ID>/ (git-ignored until approved).
#   LAYOUT_FLAG=<f> with SHOW=1: attempt 1 waits (at most 15 min) until file <f> exists before the camera is set and
#                   the recording starts; a non-empty first line replaces the Gazebo camera VIEW (x y z tx ty tz).
set -u
set -m
TEST=$1; RUNS=$2; OUT=$3
case $TEST in
  TEST-M7-03) MODE=sequence; DOM=150 ;;
  TEST-M7-04) MODE=route; DOM=155 ;;
  TEST-M7-05) MODE=invalid; DOM=160 ;;
  TEST-M7-06) MODE=cancel; DOM=165 ;;
  TEST-M7-09) MODE=observe; DOM=170
    { [ "${SHOW:-0}" = 1 ] && [ -n "${DONE_FLAG:-}" ]; } || { echo "TEST-M7-09 needs SHOW=1 and DONE_FLAG=<file>"; exit 2; } ;;
  *) echo "usage: $0 <TEST-M7-03|04|05|06|09> <valid runs> <output log>"; exit 2 ;;
esac
EV=docs/evidence/M7
TMP=$(mktemp -d); FAIL=0; TS029=0; TS039=0; VALID=0; ATTEMPT=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
HL="headless:=true"; [ "${SHOW:-0}" = 1 ] && HL="headless:=false gui_config:=gazebo_gui_capture.config"
B=$(basename "$OUT"); B=${B%_review.log}; B=${B%.log}
SHOTS=docs/gallery/_pending/M7/$TEST/$B
DATA=$(dirname "$OUT")/$B
VIEW="0.8 0.0 8.0 3.0 0.0 0"   # Gazebo camera: the M5 overhead view (TEST-M5_procedure.sh; user choice 2026-11-21, replaces the far TEST-M6-02 view)
NAMES='gz sim|map_server|amcl|lifecycle_manager|planner_server|controller_server|behavior_server|bt_navigator|velocity_smoother|parameter_bridge|robot_state_publisher|rviz2 -d'
byname() { pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M7_procedure" | wc -l; }
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
echo "# $TEST procedure (mode $MODE), valid runs required=$RUNS, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); navigation2 $(dpkg-query -W -f='${Version}' ros-jazzy-navigation2); launch: sim.launch.py $HL sensors:=true world:=mapping_arena.sdf + localization.launch.py + navigation.launch.py"
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1)); RC=1
  export ROS_DOMAIN_ID=$((DOM + ATTEMPT)) GZ_PARTITION="amr_m7_${MODE}_$$_$ATTEMPT"
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
  if [ "$MODE" = observe ]; then   # TEST-M7-09: the user sends goals in RViz until DONE_FLAG exists
    ros2 topic echo /navigate_to_pose/_action/status action_msgs/msg/GoalStatusArray > "$TMP/status_$ATTEMPT.txt" 2>/dev/null &
    EPID=$!
    echo "# ready for the user's goals: $(date '+%T')"
    while [ ! -e "$DONE_FLAG" ]; do pause 2; done
    echo "# user done: $(date '+%T')"
    rm -f "$DONE_FLAG"   # a repeated attempt (INVALID) waits for the user again
    kill -INT "$EPID" 2>/dev/null; wait "$EPID" 2>/dev/null
    echo; echo "\$ python3 -I $EV/TEST-M7-09_goal_status.py <status echo>"
    python3 -I "$EV/TEST-M7-09_goal_status.py" "$TMP/status_$ATTEMPT.txt"; RC=$?
    cp "$TMP/status_$ATTEMPT.txt" "${DATA}_a${ATTEMPT}_status.txt"
    HRC=0
  else
  echo; echo "\$ python3 $EV/TEST-M7_nav_run.py ${B}_a$ATTEMPT --mode $MODE"
  timeout --foreground 900 python3 "$EV/TEST-M7_nav_run.py" "${DATA}_a$ATTEMPT" --mode "$MODE"; HRC=$?
  echo "# harness exit $HRC"
  fi
  if [ "$MODE" = observe ]; then
    :
  elif [ "$HRC" = 2 ]; then
    RC=2; echo "# attempt $ATTEMPT INVALID: harness reported an invalid run (not counted, repeated)"
  else
    echo; echo "\$ python3 -I $EV/TEST-M7_nav_check.py ${B}_a$ATTEMPT --test $TEST"
    python3 -I "$EV/TEST-M7_nav_check.py" "${DATA}_a$ATTEMPT" --test "$TEST"; RC=$?
    echo "# checker exit $RC"
    [ "$RC" = 2 ] && { RC=1; echo "# checker found the recording unusable: attempt FAIL"; }
    [ "$HRC" = 0 ] || { RC=1; echo "# harness exit $HRC: attempt FAIL"; }
  fi
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
  elif [ "$LLEFT" = 0 ] && [ "$LSH" = 4 ] && [ "${SHOW:-0}" = 1 ]; then
    TS039=$((TS039 + 1)); echo "# DEC-079: TS-039 (GUI front end) shutdown signature only; launch-log condition not counted for this attempt"
    [ "$RC" = 0 ] && RC=2 && echo "# attempt $ATTEMPT INVALID under DEC-079 (checks passed; not counted, repeated)"
  else
    [ "$LSH" = 0 ] && [ "$LLEFT" = 0 ]; rc $?
  fi
  for _ in $(seq 1 10); do [ "$(byname)" = 0 ] && break; pause 1; done
  LEFTN=$(byname)
  echo "# leftover processes by name (gz sim, map servers, AMCL, Nav2 servers, lifecycle managers, bridge, robot_state_publisher, RViz): $LEFTN"
  pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M7_procedure" | sed 's/^/#   /'
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
echo "# TS-029 attempts declared invalid under DEC-039: $TS029; TS-039 attempts declared invalid under DEC-079: $TS039"
echo; echo "# overall: $([ $FAIL = 0 ] && echo "ALL $RUNS VALID RUNS PASSED" || echo 'AT LEAST ONE CHECK FAILED')"
} > "$TMP/raw.log" 2>&1   # not a pipeline: launches started inside a pipeline ignore SIGINT (TS-017)
sed -e "s|$TMP|<tmp>|g" -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/raw.log" > "$OUT"
rm -rf "$TMP"
grep -q '^# overall: ALL .* VALID RUNS PASSED' "$OUT"
