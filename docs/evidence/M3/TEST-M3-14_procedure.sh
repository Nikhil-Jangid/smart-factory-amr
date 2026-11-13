#!/usr/bin/env bash
# TEST-M3-14: DEC-038 IMU decimation, integration (REQ-M3-15; docs/testing/test_plan.md §7.3).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M3/TEST-M3-14_procedure.sh <valid runs> <output log>
# Modelled on TEST-M3-D_procedure.sh (left unchanged).
# 1. Static (f): TEST-M3-14_static_rate_check.py on the installed controllers.yaml, the simulation model expanded
#    with use_ros2_control:=true use_sensors:=true, the M3 test world and the stock empty.sdf (the default world).
# 2. Per run: a fresh `sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0`, both controllers
#    active, the harness TEST-M3-14_imu_decimation_check.py ((a)-(e) and INFO). Invalid runs (harness exit 2) are
#    repeated and not counted, at most <valid runs> + 3 attempts. After SIGINT, the launch log must contain the
#    plugin's "active" line once and its shutdown counters with dropped_incomplete, missing_samples, duplicates,
#    off_grid and resets all 0, discarded_partial 1 or 2 (the startup block and at most one partial block at
#    shutdown), and raw samples - 10 x published <= 18 (only those partial blocks unpublished): (b) startup and
#    missing-sample behaviour in the real launch. As every launch procedure: own ROS_DOMAIN_ID (132-139) and
#    GZ_PARTITION, SIGINT to the launch process only, 0 [ERROR] lines, 0 leftover processes, job control (set -m),
#    no pipeline around the launch (TS-017), timeout --foreground (TS-025).
# DEC-039 (added 2026-11-04, before any run under it): the launch-log condition is judged by
# TEST-M3_launch_shutdown_classify.py. An attempt whose only defect is the exact TS-029 shutdown signature (upstream
# gz shutdown deadlock; only gz escalates after SIGINT, every other process finishes cleanly, 0 leftovers) is INVALID
# if its measurement checks passed: it is recorded, not counted, and repeated within the existing attempt limit.
# Any other [ERROR] line or leftover process still fails the attempt.
set -u
set -m
RUNS=$1; OUT=$2
EV=docs/evidence/M3
TMP=$(mktemp -d); FAIL=0; TS029=0; VALID=0; ATTEMPT=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
CTRL="$SHARE_B/config/controllers.yaml"
WORLD="$SHARE_B/worlds/sensor_test.sdf"
EMPTY=/opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/worlds/empty.sdf
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
{
echo "# TEST-M3-14 procedure, valid runs required=$RUNS, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); plugin $(ls "$(ros2 pkg prefix amr_gazebo_plugins)/lib/libamr_imu_decimator_system.so" | sed "s|$HOME|<home>|")"
echo; echo '## 1. Static rate consistency (f)'
(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro use_ros2_control:=true controllers_file:="$CTRL" use_sensors:=true) > "$TMP/s2.urdf"
echo '$ python3 -I docs/evidence/M3/TEST-M3-14_static_rate_check.py <share_b>/config/controllers.yaml <tmp>/s2.urdf <share_b>/worlds/sensor_test.sdf <gz_sim_vendor>/worlds/empty.sdf'
python3 -I "$EV/TEST-M3-14_static_rate_check.py" "$CTRL" "$TMP/s2.urdf" "$WORLD" "$EMPTY"; rc $?
echo; echo '## 2. Launch runs'
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1))
  export ROS_DOMAIN_ID=$((131 + ATTEMPT)) GZ_PARTITION="amr_m3_14_$$_$ATTEMPT"
  echo; echo "## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID)"
  echo '$ ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0'
  ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0 > "$TMP/launch_$ATTEMPT.log" 2>&1 &
  LPID=$!
  echo "\$ python3 $EV/TEST-M3-14_imu_decimation_check.py"
  timeout --foreground 300 python3 "$EV/TEST-M3-14_imu_decimation_check.py"; RC=$?
  echo "# harness exit $RC"
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
  echo '# plugin lines in the launch log:'
  grep -E 'amr_gazebo_plugins::ImuDecimator' "$TMP/launch_$ATTEMPT.log" | sed 's/^/#   /'
  python3 -I - "$TMP/launch_$ATTEMPT.log" <<'PY'; PC=$?
import re, sys
log = open(sys.argv[1]).read()
active = len(re.findall(r'ImuDecimator\] active: /imu_raw \(1000 Hz\) -> /imu \(100 Hz\), block 10', log))
m = re.findall(r'ImuDecimator\] shutdown: raw samples (\d+), published (\d+), dropped_incomplete (\d+), discarded_partial (\d+), '
               r'missing_samples (\d+), duplicates (\d+), off_grid (\d+), resets (\d+)', log)
err = len(re.findall(r'ImuDecimator\].*(invalid configuration|NOT active)', log))
if len(m) != 1:
    print(f'FAIL  (b) plugin shutdown counter line found {len(m)} times (expected 1); active lines {active}')
    sys.exit(1)
raw, pub, drop, part, miss, dup, off, res = map(int, m[0])
ok = (active == 1 and err == 0 and pub > 0 and drop == miss == dup == off == res == 0 and part in (1, 2)
      and 0 <= raw - 10 * pub <= 18)
print(f'{"PASS" if ok else "FAIL"}  (b) plugin: active line {active} (== 1), configuration errors {err}; shutdown counters: '
      f'raw {raw}, published {pub}, dropped_incomplete {drop}, missing_samples {miss}, duplicates {dup}, off_grid {off}, '
      f'resets {res} (all 0); discarded_partial {part} (1 or 2: startup, shutdown); raw - 10 x published = {raw - 10 * pub} '
      f'(<= 18: only partial blocks unpublished; first output only after a complete block)')
sys.exit(0 if ok else 1)
PY
  if [ "$SH" = 3 ] && [ "$LEFT" = 0 ]; then echo "# (b) plugin shutdown-line check not counted: TS-029 attempt (DEC-039)"; else rc $PC; fi
  case $RC in
    0) VALID=$((VALID + 1)) ;;
    2) echo "# attempt $ATTEMPT INVALID (not counted)" ;;
    *) VALID=$((VALID + 1)); FAIL=1 ;;
  esac
done
[ "$VALID" -lt "$RUNS" ] && FAIL=1 && echo "# only $VALID valid runs of $RUNS"
echo "# TS-029 attempts declared invalid under DEC-039: $TS029"
echo; echo "# overall: $([ $FAIL = 0 ] && echo "ALL $RUNS VALID RUNS PASSED" || echo 'AT LEAST ONE RUN FAILED OR TOO FEW VALID RUNS')"
} > "$TMP/raw.log" 2>&1   # not a pipeline: launches started inside a pipeline ignore SIGINT (TS-017)
sed -e "s|$TMP|<tmp>|g" -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/raw.log" > "$OUT"
rm -rf "$TMP"
grep -q "ALL $RUNS VALID RUNS PASSED" "$OUT"
