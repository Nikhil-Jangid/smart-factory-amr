#!/usr/bin/env bash
# TEST-M3-11: M2 motion regression with the sensors on (REQ-M3-13; docs/testing/test_plan.md §7.2).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M3/TEST-M3-11_procedure.sh <mode> <valid runs> <output log>
#   <mode>: linear (TEST-M2-05), rotate (TEST-M2-06), stop, timeout (TEST-M2-07); 3 valid runs each (DEC-027).
# Copy of TEST-M3-D_procedure.sh (left unchanged), with only these differences: the harness is
# TEST-M3-11_m2_regression.py (the M2 mode functions and criteria unchanged, sensors on), the ROS_DOMAIN_ID
# bases are 140/150/160/170 per mode, and the GZ_PARTITION prefix is amr_m3_11.
# Launch per attempt: `sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0` (the stock
# empty.sdf has no Sensors or IMU system). The static clearance check covers these profiles: its forward envelope
# (2.625 m) exceeds the timeout profile (0.2 m/s x 3 s plus <= 0.9 s to rest, about 0.78 m) and the stop and
# linear profiles it was written for; every run also prints its measured excursion.
# Invalid runs (harness exit 2, e.g. RTF < 0.5) are repeated and not counted, at most <valid runs> + 3 attempts.
# Each attempt: own ROS_DOMAIN_ID and GZ_PARTITION; SIGINT to the launch process only; job control (set -m);
# launches outside any pipeline (TS-017); timeout --foreground (TS-025). Never two Gazebo runs at once.
# DEC-039 (written into this procedure before its first run): the launch-log condition is judged by
# TEST-M3_launch_shutdown_classify.py. An attempt whose only defect is the exact TS-029 shutdown signature (upstream
# gz shutdown deadlock; only gz escalates after SIGINT, every other process finishes cleanly, 0 leftovers) is INVALID
# if its measurement checks passed: it is recorded, not counted, and repeated within the existing attempt limit.
# Any other [ERROR] line or leftover process still fails the attempt.
set -u
set -m
MODE=$1; RUNS=$2; OUT=$3
EV=docs/evidence/M3
TMP=$(mktemp -d); FAIL=0; TS029=0; VALID=0; ATTEMPT=0
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
WORLD="$SHARE_B/worlds/sensor_test.sdf"
case $MODE in linear) BASE=140 ;; rotate) BASE=150 ;; stop) BASE=160 ;; *) BASE=170 ;; esac
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
{
echo "# TEST-M3-11 procedure mode=$MODE, valid runs required=$RUNS, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); world <share_b>/worlds/sensor_test.sdf sha256 $(sha256sum "$WORLD" | cut -c1-16)…"
echo; echo '$ python3 -I docs/evidence/M3/TEST-M3-D_clearance_check.py <share_b>/worlds/sensor_test.sdf amr_ws/src/amr_description/urdf/amr_properties.xacro'
python3 -I "$EV/TEST-M3-D_clearance_check.py" "$WORLD" amr_ws/src/amr_description/urdf/amr_properties.xacro; CL=$?; rc $CL
while [ "$CL" = 0 ] && [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1))
  export ROS_DOMAIN_ID=$((BASE + ATTEMPT)) GZ_PARTITION="amr_m3_11_${MODE}_$$_$ATTEMPT"
  echo; echo "## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID)"
  echo '$ ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0'
  ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0 > "$TMP/launch_$ATTEMPT.log" 2>&1 &
  LPID=$!
  echo "\$ python3 $EV/TEST-M3-11_m2_regression.py $MODE"
  timeout --foreground 300 python3 "$EV/TEST-M3-11_m2_regression.py" "$MODE"; RC=$?
  echo "# Gazebo command line: $(pgrep -a -g "$LPID" | grep -m1 -E '^[0-9]+ gz sim ' | cut -d' ' -f2-)"
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
