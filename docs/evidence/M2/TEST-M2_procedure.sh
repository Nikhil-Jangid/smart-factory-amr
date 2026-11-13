#!/usr/bin/env bash
# M2 motion-test procedure (docs/testing/test_plan.md §6.1): fresh headless launch per run,
# isolated ROS_DOMAIN_ID / GZ_PARTITION, harness TEST-M2_motion_measure.py <mode>, clean shutdown,
# leftover-process check, launch-log scan. Invalid runs (harness exit 2, e.g. RTF < 0.5) are repeated.
# Usage, from the repository root after sourcing /opt/ros/jazzy/setup.bash and amr_ws/install/setup.bash:
#   bash docs/evidence/M2/TEST-M2_procedure.sh <mode> <valid runs> <output log>
# Exit 0 only if every valid run passed all criteria.
# Job control (set -m): without it, background jobs of a non-interactive shell start with SIGINT
# ignored, so ros2 launch and its children could not be stopped by SIGINT (TS-011).
# The harness runs with plain python3: python3 -I would drop the ROS PYTHONPATH (TS-011).
set -u
# SHOW=1 (option added 2026-11-13 for TEST-M4-10, my choice): Gazebo GUI instead of headless (headless:=false) and the
# GUI camera aimed at the robot (tools/sim_capture.py view). Physics, harness and criteria unchanged; default = headless.
HL=true; [ "${SHOW:-0}" = 1 ] && HL=false
GZPAT="gz sim -r -s empty.sdf"; [ "$HL" = false ] && GZPAT="gz sim -r empty.sdf"
show_view() { [ "${SHOW:-0}" = 1 ] && (sleep 12; python3 tools/sim_capture.py view -1.5 -1.5 1.8 0.3 0 0 > /dev/null 2>&1) & }
set -m
MODE=$1; RUNS=$2; OUT=$3
HARNESS=docs/evidence/M2/TEST-M2_motion_measure.py
TMP=$(mktemp -d); FAIL=0; VALID=0; ATTEMPT=0
sanitize() { sed -e "s|$HOME|<home>|g" -e "s|$(hostname)|<host>|g"; }
{
echo "# TEST-M2 procedure: mode=$MODE, valid runs required=$RUNS, $(date '+%F %T %Z')"
echo "# revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src DIRTY)')"
echo "# ros2_control $(dpkg-query -W -f='${Version}' ros-jazzy-ros2-control), diff_drive_controller $(dpkg-query -W -f='${Version}' ros-jazzy-diff-drive-controller), gz_ros2_control $(dpkg-query -W -f='${Version}' ros-jazzy-gz-ros2-control)"
} > "$OUT"
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1))
  export ROS_DOMAIN_ID=$((70 + ATTEMPT)) GZ_PARTITION="amr_m2_${MODE}_$$_${ATTEMPT}"
  echo -e "\n## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID, GZ_PARTITION=amr_m2_${MODE}_<pid>_${ATTEMPT}, headless:=$HL)" >> "$OUT"
  ros2 launch amr_bringup sim.launch.py headless:=$HL > "$TMP/launch_$ATTEMPT.log" 2>&1 &
  LPID=$!
  show_view
  timeout 240 python3 "$HARNESS" "$MODE" >> "$OUT" 2>&1
  RC=$?
  if [ "$MODE" = startup ]; then
    { echo '$ ros2 control list_controllers'; timeout 20 ros2 control list_controllers 2>&1 | grep -v 'waiting for service'
      echo '$ ros2 control list_hardware_interfaces'; timeout 20 ros2 control list_hardware_interfaces 2>&1 | grep -v 'waiting for service'; } >> "$OUT"
  fi
  kill -INT "$LPID" 2>/dev/null
  for _ in $(seq 1 30); do kill -0 "$LPID" 2>/dev/null || pgrep -f "$GZPAT" > /dev/null || break; timeout 1 tail -f /dev/null; done
  if kill -0 "$LPID" 2>/dev/null; then kill -TERM -"$LPID" 2>/dev/null; echo "# launch did not stop on SIGINT within 30 s; SIGTERM sent to its process group" >> "$OUT"; fi
  wait "$LPID" 2>/dev/null
  LEFT=$(pgrep -af "$GZPAT" | grep -v pgrep | wc -l)
  NERR=$(grep -c '\[ERROR\]' "$TMP/launch_$ATTEMPT.log")
  { echo "# harness exit $RC; launch log: $NERR [ERROR] lines; leftover gz processes: $LEFT"
    grep -E '\[ERROR\]|\[WARN\]' "$TMP/launch_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sanitize | sort | uniq -c | sed 's/^/#   /'; } >> "$OUT"
  if [ "$LEFT" -ne 0 ]; then pkill -TERM -f "$GZPAT"; echo "# leftover gz process stopped with SIGTERM" >> "$OUT"; fi
  case $RC in
    0) VALID=$((VALID + 1)) ;;
    2) echo "# attempt $ATTEMPT INVALID (not counted)" >> "$OUT" ;;
    *) VALID=$((VALID + 1)); FAIL=1 ;;
  esac
done
[ "$VALID" -lt "$RUNS" ] && FAIL=1 && echo "# only $VALID valid runs of $RUNS" >> "$OUT"
echo -e "\n# overall: $([ $FAIL = 0 ] && echo "ALL $RUNS VALID RUNS PASSED" || echo 'AT LEAST ONE RUN FAILED OR TOO FEW VALID RUNS')" >> "$OUT"
rm -rf "$TMP"
exit $FAIL
