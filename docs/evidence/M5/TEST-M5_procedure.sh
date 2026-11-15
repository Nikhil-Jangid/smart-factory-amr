#!/usr/bin/env bash
# M5 mapping-run procedure (docs/testing/test_plan.md §10; M5 Tasks B-D): TEST-M5-03/-04 (and -06 with CONTROLLERS).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M5/TEST-M5_procedure.sh <valid runs> <output log>
# Each attempt: fresh `sim.launch.py sensors:=true world:=mapping_arena.sdf` (headless unless SHOW=1), both
# controllers active, `slam.launch.py`, then TEST-M5_map_run.py (drives the Selected route, rest-point poses), then the
# map is saved while SLAM still runs:
#   ros2 run nav2_map_server map_saver_cli -f <prefix>_map --ros-args -p use_sim_time:=true   (.pgm + .yaml, DEC-051)
#   ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '<abs prefix>_posegraph'}"
# then teardown (SIGINT to RViz, the SLAM launch, the simulation launch) and the offline checker TEST-M5_map_check.py on
# the saved map. Outputs beside the log: <log name>_a<N>_rest.csv, _a<N>_map.{pgm,yaml}, _a<N>_check.json. The pose graph
# (about 8 MB, not evidence) goes to PG_DIR as <log name>_a<N>_posegraph.{posegraph,data}; the log records its raw and
# gzip -9 sizes (OPEN-27, DEC-051). PG_DIR unset: a temporary folder, deleted at the end. Own ROS_DOMAIN_ID (131-139) and GZ_PARTITION per attempt; never two Gazebo runs at once.
# Shutdown rules as TEST-M5-02 (test_plan §7.1, DEC-039): SLAM launch CLEAN; simulation launch CLEAN or the exact TS-029
# signature (then the attempt is INVALID if its checks passed); 0 leftover processes by process group and by name; the
# full launch logs of an attempt that does not stop CLEAN are kept (<log name>_a<N>_{sim,slam}_launch.log).
# Attempt result: harness exit (0 PASS / 1 FAIL / 2 INVALID), map checker exit, map save, shutdown. Limit: runs + 3.
# Job control (set -m; TS-011), launches outside any pipeline (TS-017), timeout --foreground (TS-025).
# Options (environment):
#   SHOW=1, LAYOUT_FLAG=<f>   as TEST-M5-02_procedure.sh (GUI + RViz mapping.rviz; attempt 1 recorded into
#                             docs/gallery/_pending/M5/<test ID>/, after the window layout is confirmed)
#   NOREC=1                   with SHOW=1: no recording or screenshots (dry runs)
#   CONTROLLERS=<file>        launch with controllers_file:=<file> (TEST-M5-06: TEST-M4-09 calibration overrides)
#   PG_DIR=<dir>              keep the serialized pose graphs there (Task C: the reference map's pose graph)
set -u
set -m
RUNS=$1; OUT=$2
EV=docs/evidence/M5
TMP=$(mktemp -d); FAIL=0; TS029=0; VALID=0; ATTEMPT=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
LARGS="headless:=true"; [ "${SHOW:-0}" = 1 ] && LARGS="headless:=false"
[ -n "${CONTROLLERS:-}" ] && LARGS="$LARGS controllers_file:=$CONTROLLERS"
D=$(dirname "$OUT"); B=$(basename "$OUT"); B=${B%_review.log}; B=${B%.log}
ID=$(printf '%s' "$B" | grep -oE '^TEST-M5-[0-9]{2}' || echo dry)
SHOTS=docs/gallery/_pending/M5/$ID/$B
VIEW="0.8 0.0 8.0 3.0 0.0 0"   # Gazebo camera chosen for TEST-M5-02 R1 (portrait half-screen window)
NAMES='gz sim|async_slam_toolbox|parameter_bridge|robot_state_publisher|rviz2 -d|map_saver_cli'
byname() { pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M5_procedure" | wc -l; }
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
stop_job() {
  kill -INT "$1" 2>/dev/null
  for _ in $(seq 1 "$2"); do kill -0 "$1" 2>/dev/null || break; pause 1; done
  if kill -0 "$1" 2>/dev/null; then kill -TERM -- -"$1" 2>/dev/null; echo "# $3 did not stop on SIGINT within $2 s; SIGTERM sent to its process group"; fi
  wait "$1" 2>/dev/null
  for _ in $(seq 1 10); do pgrep -g "$1" > /dev/null || break; pause 1; done
}
{
echo "# TEST-M5 mapping procedure, valid runs required=$RUNS, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); slam_toolbox $(dpkg-query -W -f='${Version}' ros-jazzy-slam-toolbox); nav2_map_server $(dpkg-query -W -f='${Version}' ros-jazzy-nav2-map-server)"
mkdir -p "${PG_DIR:-$TMP}"
echo "# launch: sim.launch.py $LARGS sensors:=true world:=mapping_arena.sdf + slam.launch.py" | sed "s|$PWD/||g"
[ -n "${CONTROLLERS:-}" ] && { echo "# controllers file differs from the product file by:"; diff "$SHARE_B/config/controllers.yaml" "$CONTROLLERS" | sed 's/^/#   /'; }
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1)); RC=1; P="$D/${B}_a${ATTEMPT}"; PG="${PG_DIR:-$TMP}/${B}_a${ATTEMPT}_posegraph"
  export ROS_DOMAIN_ID=$((130 + ATTEMPT)) GZ_PARTITION="amr_m5_map_$$_$ATTEMPT"
  echo; echo "## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID)"
  ros2 launch amr_bringup sim.launch.py $LARGS sensors:=true world:=mapping_arena.sdf > "$TMP/sim_$ATTEMPT.log" 2>&1 &
  LPID=$!; RPID=
  ACTIVE=0
  for _ in $(seq 1 90); do
    ACTIVE=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')
    [ "$ACTIVE" = 2 ] && break
    pause 1
  done
  [ "$ACTIVE" = 2 ] && echo "both controllers active"; rc $([ "$ACTIVE" = 2 ] && echo 0 || echo 1)
  ros2 launch amr_bringup slam.launch.py > "$TMP/slam_$ATTEMPT.log" 2>&1 &
  SPID=$!
  REC=0
  if [ "${SHOW:-0}" = 1 ]; then
    for _ in $(seq 60); do xwininfo -root -tree | grep -q '("gz-sim-gui" "Gazebo GUI")' && break; pause 1; done
    QT_QPA_PLATFORM=xcb rviz2 -d "$SHARE_B/rviz/mapping.rviz" --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
    RPID=$!
    if [ "$ATTEMPT" = 1 ] && [ "${NOREC:-0}" != 1 ]; then
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
    else
      (sleep 10; python3 tools/sim_capture.py view $VIEW > /dev/null 2>&1) &
    fi
  fi
  echo; echo "\$ python3 $EV/TEST-M5_map_run.py <prefix>_rest.csv"
  timeout --foreground 900 python3 "$EV/TEST-M5_map_run.py" "${P}_rest.csv"; RC=$?
  echo "# harness exit $RC"
  echo; echo '$ ros2 run nav2_map_server map_saver_cli -f <prefix>_map --ros-args -p use_sim_time:=true'
  timeout --foreground 60 ros2 run nav2_map_server map_saver_cli -f "${P}_map" --ros-args -p use_sim_time:=true > "$TMP/saver.log" 2>&1
  MS=$?
  if [ "$MS" = 0 ]; then G='Saving|saved|error|Error|fail'; else G='.'; echo "# map_saver_cli exit $MS: full output"; fi
  grep -E "$G" "$TMP/saver.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sed "s|$PWD/||g" | sed 's/^/#   /'
  [ "$MS" = 0 ] && [ -s "${P}_map.pgm" ] && [ -s "${P}_map.yaml" ]; rc $?
  echo '$ ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: <prefix>_posegraph}"'
  timeout --foreground 60 ros2 service call /slam_toolbox/serialize_map slam_toolbox/srv/SerializePoseGraph "{filename: '$(realpath -m "$PG")'}" 2>&1 | tail -2 | sed 's/^/#   /'
  for F in "$PG".posegraph "$PG".data; do
    [ -s "$F" ] && echo "#   $(basename "$F"): $(stat -c %s "$F") bytes, gzip -9 $(gzip -9 -c "$F" | wc -c) bytes"
  done
  [ -s "$PG.posegraph" ] && [ -s "$PG.data" ]; rc $?
  if [ "$REC" = 1 ]; then
    bash tools/sim_record.sh stop "${SHOTS}_a1" | sed "s|$PWD/||g"
    python3 tools/sim_capture.py shot "${SHOTS}_a1" 2>&1 | sed "s|$PWD/||g"
  fi
  [ -n "$RPID" ] && { kill -INT "$RPID" 2>/dev/null; wait "$RPID" 2>/dev/null; }
  stop_job "$SPID" 20 "SLAM launch"
  stop_job "$LPID" 30 "simulation launch"
  echo "# SLAM log: $(grep -c '\[ERROR\]' "$TMP/slam_$ATTEMPT.log") [ERROR] lines; lines with 'dropping' or 'queue' (dropped scans, INFO): $(grep -c -i -E 'dropping|queue' "$TMP/slam_$ATTEMPT.log")"
  grep -E '\[ERROR\]|\[WARN\]|dropping|queue' "$TMP/slam_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sort | uniq -c | sed 's/^/#   /'
  python3 -I docs/evidence/M3/TEST-M3_launch_shutdown_classify.py "$TMP/slam_$ATTEMPT.log"; SHS=$?
  [ "$SHS" = 0 ] && [ "$(pgrep -g "$SPID" | wc -l)" = 0 ]; rc $?
  echo "# simulation log: $(grep -c '\[ERROR\]' "$TMP/sim_$ATTEMPT.log") [ERROR] lines"
  grep -E '\[ERROR\]' "$TMP/sim_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sort | uniq -c | sed 's/^/#   /'
  python3 -I docs/evidence/M3/TEST-M3_launch_shutdown_classify.py "$TMP/sim_$ATTEMPT.log"; SH=$?
  LEFT=$(pgrep -g "$LPID" | wc -l)
  if [ "$LEFT" = 0 ] && [ "$SH" = 3 ]; then
    TS029=$((TS029 + 1)); echo "# DEC-039: TS-029 shutdown signature only; launch-log condition not counted for this attempt"
    [ "$RC" = 0 ] && RC=2 && echo "# attempt $ATTEMPT INVALID under DEC-039 (checks passed; not counted, repeated)"
  else
    [ "$SH" = 0 ] && [ "$LEFT" = 0 ]; rc $?
  fi
  for _ in $(seq 1 10); do [ "$(byname)" = 0 ] && break; pause 1; done
  LEFTN=$(byname); echo "# leftover processes by name: $LEFTN"; [ "$LEFTN" = 0 ]; rc $?
  if [ "$SH" != 0 ] || [ "$SHS" != 0 ]; then
    for K in sim slam; do sed -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/${K}_$ATTEMPT.log" > "${P}_${K}_launch.log"; done
    echo "# full launch logs kept: $(basename "${P}")_{sim,slam}_launch.log"
  fi
  [ "$LEFTN" = 0 ] || { pkill -TERM -f "$NAMES"; echo "# leftover processes stopped with SIGTERM"; }
  if [ -s "${P}_map.yaml" ]; then
    echo; echo "\$ python3 -I $EV/TEST-M5_map_check.py <prefix>_map.yaml --json <prefix>_check.json"
    python3 -I "$EV/TEST-M5_map_check.py" "${P}_map.yaml" --json "${P}_check.json"; MC=$?
    echo "# map checker exit $MC"; [ "$MC" = 0 ] || { [ "$RC" = 2 ] || RC=1; }
  else
    [ "$RC" = 2 ] || RC=1
  fi
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
sed -e "s|$TMP|<tmp>|g" -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" -e "s|$PWD/||g" "$TMP/raw.log" > "$OUT"
rm -rf "$TMP"
grep -q '^# overall: ALL .* VALID RUNS PASSED' "$OUT"
