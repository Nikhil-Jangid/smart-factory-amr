#!/usr/bin/env bash
# M6 localization-run procedure (docs/testing/test_plan.md §11; M6 Tasks B-C): TEST-M6-03 to -06 (and -07 in Task D).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M6/TEST-M6_procedure.sh <valid runs> <output log>
# Each attempt: fresh `sim.launch.py sensors:=true world:=<world>` (headless unless SHOW=1), both controllers active,
# `localization.launch.py` (DEC-060), then TEST-M6_run.py (drives the route, records the rest points and the 10 Hz
# track), then teardown (SIGINT to RViz, the localization launch, the simulation launch) and the offline checker
# TEST-M6_pose_check.py on the recorded files. Outputs beside the log: <log name>_a<N>_{rest,track}.csv, _a<N>_check.json.
# Own ROS_DOMAIN_ID (141-149) and GZ_PARTITION per attempt; never two Gazebo runs at once.
# Shutdown rules as TEST-M6-02 (test_plan §7.1, DEC-039): localization launch CLEAN; simulation launch CLEAN or the exact
# TS-029 signature (then the attempt is INVALID if its checks passed); 0 leftover processes by process group and by
# name; the full launch logs of an attempt that does not stop CLEAN are kept (<log name>_a<N>_{sim,loc}_launch.log).
# Attempt result: harness exit (0 recorded / 1 safety stop / 2 INVALID), checker exit, shutdown. Limit: runs + 3.
# Job control (set -m; TS-011), launches outside any pipeline (TS-017), timeout --foreground (TS-025).
# Options (environment):
#   SHOW=1, LAYOUT_FLAG=<f>   as TEST-M6-02_procedure.sh (GUI + RViz localization.rviz; attempt 1 recorded into
#                             docs/gallery/_pending/M6/<test ID>/)
#   NOREC=1                   with SHOW=1: no recording or screenshots (dry runs)
#   ROUTE=forward|reverse     route direction (default forward; TEST-M6_route.py)
#   WRONG=1                   wrong start (TEST-M6-04): harness --wrong-start, checker --recovery
#   GLOBAL=1                  global-localization demonstration (TEST-M6-10, DEC-058: not an acceptance criterion):
#                             after AMCL is active, `ros2 service call /reinitialize_global_localization` spreads the
#                             particles over the whole map; 5 s pause; then the route; checker --recovery (INFO for
#                             the demonstration: whether and where the estimate converged)
#   WORLD=<file>              world (default mapping_arena.sdf; TEST-M6-06: docs/evidence/M6/TEST-M6_unmapped_arena.sdf,
#                             passed as an absolute path)
#   AMCL=<file>               localization.launch.py amcl_params_file:=<file> (diagnosis runs only; formal runs use
#                             the product amcl.yaml; the log records the difference)
#   CONTROLLERS=<file>        launch with controllers_file:=<file> (TEST-M6-05: TEST-M4-09 overrides); the checker
#                             then also judges the odometry drift (--drift <route>)
#   INJECT=1                  TEST-M6-05: write the TEST-M4-09 overrides (wheel_separation_multiplier 1.02, both
#                             wheel radius multipliers 1.01; DEC-043) into a temporary copy of the installed
#                             controllers.yaml, exactly as TEST-M5-06_procedure.sh does, and use it as CONTROLLERS
#   INJECT=sep                TEST-M6-07: wheel_separation_multiplier 1.02 alone (M6 plan §3.4), same method
#   FUSION=1                  TEST-M6-07 (DEC-057): the base controllers file is controllers_ekf.yaml (also for INJECT),
#                             localization.launch.py ekf:=true, TEST-M6-07_fusion_check.py pre (before the localization
#                             launch) and main (after it) in every attempt, and the checker judges --fusion <route>
#                             instead of --drift
set -u
set -m
RUNS=$1; OUT=$2
EV=docs/evidence/M6
ROUTE=${ROUTE:-forward}
EKFARG=""; [ "${FUSION:-0}" = 1 ] && EKFARG="ekf:=true"
WORLD=${WORLD:-mapping_arena.sdf}
case $WORLD in /*|mapping_arena.sdf) ;; *) WORLD=$(realpath "$WORLD") ;; esac
HARG="--route $ROUTE"; CARG=""
[ "${WRONG:-0}" = 1 ] && HARG="$HARG --wrong-start" && CARG="--recovery"
[ "${GLOBAL:-0}" = 1 ] && CARG="--recovery"
TMP=$(mktemp -d); FAIL=0; TS029=0; VALID=0; ATTEMPT=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
BASE_C="$SHARE_B/config/controllers.yaml"; [ "${FUSION:-0}" = 1 ] && BASE_C="$SHARE_B/config/controllers_ekf.yaml"
[ "${FUSION:-0}" = 1 ] && [ -z "${CONTROLLERS:-}" ] && [ "${INJECT:-0}" = 0 ] && CONTROLLERS=$BASE_C
if [ "${INJECT:-0}" != 0 ]; then
  CONTROLLERS="$TMP/controllers_m6-inject.yaml"
  python3 - "$BASE_C" "$CONTROLLERS" "$INJECT" <<'PY'
import sys
src, dst, mode = sys.argv[1:]
lines = ['wheel_separation_multiplier: 1.02']
if mode == '1':
    lines += ['left_wheel_radius_multiplier: 1.01', 'right_wheel_radius_multiplier: 1.01']
out, state = [], 0
for l in open(src).read().split('\n'):
    out.append(l)
    if l == 'diff_drive_controller:':
        state = 1
    elif state == 1 and l.strip() == 'ros__parameters:':
        out += [f'    {x}  # TEST-M6-05/-07 test-only override (TEST-M4-09 values, DEC-043)' for x in lines]
        state = 2
assert state == 2, 'diff_drive_controller ros__parameters not found'
open(dst, 'w').write('\n'.join(out))
PY
fi
if [ "${FUSION:-0}" = 1 ]; then CARG="$CARG --fusion $ROUTE"; elif [ -n "${CONTROLLERS:-}" ]; then CARG="$CARG --drift $ROUTE"; fi
LARGS="headless:=true"; [ "${SHOW:-0}" = 1 ] && LARGS="headless:=false"
[ -n "${CONTROLLERS:-}" ] && LARGS="$LARGS controllers_file:=$CONTROLLERS"
D=$(dirname "$OUT"); B=$(basename "$OUT"); B=${B%_review.log}; B=${B%.log}
ID=$(printf '%s' "$B" | grep -oE '^TEST-M6-[0-9]{2}' || echo dry)
SHOTS=docs/gallery/_pending/M6/$ID/$B
VIEW="0.8 0.0 8.0 3.0 0.0 0"   # Gazebo camera chosen for TEST-M5-02 R1 (portrait half-screen window)
NAMES='gz sim|map_server|amcl|lifecycle_manager|ekf_node|parameter_bridge|robot_state_publisher|rviz2 -d'
byname() { pgrep -af "$NAMES" | grep -v -E "pgrep|TEST-M6_procedure" | wc -l; }
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
echo "# TEST-M6 localization procedure, valid runs required=$RUNS, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); nav2_amcl $(dpkg-query -W -f='${Version}' ros-jazzy-nav2-amcl); route $ROUTE; wrong start ${WRONG:-0}; global ${GLOBAL:-0}"
echo "# launch: sim.launch.py $LARGS sensors:=true world:=$WORLD + localization.launch.py $EKFARG" | sed "s|$PWD/||g"
[ -n "${AMCL:-}" ] && { echo "# AMCL parameter file differs from the product file by:"; diff "$SHARE_B/config/amcl.yaml" "$AMCL" | sed 's/^/#   /'; }
[ -n "${CONTROLLERS:-}" ] && { echo "# controllers file differs from the product controllers.yaml by:"; diff "$SHARE_B/config/controllers.yaml" "$CONTROLLERS" | sed 's/^/#   /'; }
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1)); RC=1; P="$D/${B}_a${ATTEMPT}"
  export ROS_DOMAIN_ID=$((140 + ATTEMPT)) GZ_PARTITION="amr_m6_loc_$$_$ATTEMPT"
  echo; echo "## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID)"
  ros2 launch amr_bringup sim.launch.py $LARGS sensors:=true world:="$WORLD" > "$TMP/sim_$ATTEMPT.log" 2>&1 &
  LPID=$!; RPID=
  ACTIVE=0
  for _ in $(seq 1 90); do
    ACTIVE=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')
    [ "$ACTIVE" = 2 ] && break
    pause 1
  done
  [ "$ACTIVE" = 2 ] && echo "both controllers active"; rc $([ "$ACTIVE" = 2 ] && echo 0 || echo 1)
  if [ "${FUSION:-0}" = 1 ]; then
    echo; echo "\$ python3 $EV/TEST-M6-07_fusion_check.py pre <state>"
    python3 "$EV/TEST-M6-07_fusion_check.py" pre "$TMP/fusion_$ATTEMPT.json"; rc $?
  fi
  ros2 launch amr_bringup localization.launch.py ${AMCL:+amcl_params_file:=$AMCL} $EKFARG > "$TMP/loc_$ATTEMPT.log" 2>&1 &
  SPID=$!
  if [ "${FUSION:-0}" = 1 ]; then
    echo; echo "\$ python3 $EV/TEST-M6-07_fusion_check.py main <state>"
    python3 "$EV/TEST-M6-07_fusion_check.py" main "$TMP/fusion_$ATTEMPT.json"; rc $?
  fi
  REC=0
  if [ "${SHOW:-0}" = 1 ]; then
    for _ in $(seq 60); do xwininfo -root -tree | grep -q '("gz-sim-gui" "Gazebo GUI")' && break; pause 1; done
    QT_QPA_PLATFORM=xcb rviz2 -d "$SHARE_B/rviz/localization.rviz" --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
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
  if [ "${GLOBAL:-0}" = 1 ]; then
    echo; echo '$ ros2 service call /reinitialize_global_localization std_srvs/srv/Empty   (GLOBAL=1, DEC-058)'
    for _ in $(seq 60); do timeout 5 ros2 lifecycle get /amcl 2>/dev/null | grep -q active && break; pause 1; done
    pause 3
    GOUT=$(timeout 20 ros2 service call /reinitialize_global_localization std_srvs/srv/Empty 2>&1); GRC=$?
    printf '%s\n' "$GOUT" | tail -1; rc $GRC
    pause 5
  fi
  echo; echo "\$ python3 $EV/TEST-M6_run.py <prefix> $HARG"
  timeout --foreground 900 python3 "$EV/TEST-M6_run.py" "$P" $HARG; RC=$?
  echo "# harness exit $RC"
  if [ "$REC" = 1 ]; then
    bash tools/sim_record.sh stop "${SHOTS}_a1" | sed "s|$PWD/||g"
    python3 tools/sim_capture.py shot "${SHOTS}_a1" 2>&1 | sed "s|$PWD/||g"
  fi
  [ -n "$RPID" ] && { kill -INT "$RPID" 2>/dev/null; wait "$RPID" 2>/dev/null; }
  stop_job "$SPID" 20 "localization launch"
  stop_job "$LPID" 30 "simulation launch"
  echo "# localization log: $(grep -c '\[ERROR\]' "$TMP/loc_$ATTEMPT.log") [ERROR] lines"
  grep -E '\[ERROR\]|\[WARN\]' "$TMP/loc_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sort | uniq -c | sed 's/^/#   /'
  python3 -I docs/evidence/M3/TEST-M3_launch_shutdown_classify.py "$TMP/loc_$ATTEMPT.log"; SHS=$?
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
    for K in sim loc; do sed -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/${K}_$ATTEMPT.log" > "${P}_${K}_launch.log"; done
    echo "# full launch logs kept: $(basename "${P}")_{sim,loc}_launch.log"
  fi
  [ "$LEFTN" = 0 ] || { pkill -TERM -f "$NAMES"; echo "# leftover processes stopped with SIGTERM"; }
  if [ -s "${P}_rest.csv" ] && [ -s "${P}_track.csv" ]; then
    echo; echo "\$ python3 -I $EV/TEST-M6_pose_check.py <prefix> $CARG --json <prefix>_check.json"
    python3 -I "$EV/TEST-M6_pose_check.py" "$P" $CARG --json "${P}_check.json"; PC=$?
    echo "# pose checker exit $PC"; [ "$PC" = 0 ] || { [ "$RC" = 2 ] || RC=1; }
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
