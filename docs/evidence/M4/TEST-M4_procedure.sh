#!/usr/bin/env bash
# M4 odometry-test procedure (docs/testing/test_plan.md §9; copied from TEST-M2_procedure.sh, same launch, teardown and checks): fresh headless launch per run,
# isolated ROS_DOMAIN_ID / GZ_PARTITION, harness TEST-M2_motion_measure.py <mode>, clean shutdown,
# leftover-process check, launch-log scan. Invalid runs (harness exit 2, e.g. RTF < 0.5) are repeated.
# Usage, from the repository root after sourcing /opt/ros/jazzy/setup.bash and amr_ws/install/setup.bash:
#   bash docs/evidence/M4/TEST-M4_procedure.sh <mode> <valid runs> <output log> [csv, mode record only]
# Exit 0 only if every valid run passed all criteria.
# Job control (set -m): without it, background jobs of a non-interactive shell start with SIGINT
# ignored, so ros2 launch and its children could not be stopped by SIGINT (TS-011).
# The harness runs with plain python3: python3 -I would drop the ROS PYTHONPATH (TS-011).
set -u
set -m
MODE=$1; RUNS=$2; OUT=$3; CSV=${4:-}
# Options (environment, added 2026-11-13 for M4 Task D, before their first formal use):
#   SHOW=1             Gazebo GUI instead of headless, plus RViz with rviz/odometry.rviz (so the simulation tests
#                      can be watched). Physics and criteria are unchanged; the RTF rule still applies.
#   CONTROLLERS=<file> launch with controllers_file:=<file> (TEST-M4-09 test-only calibration overrides, DEC-043).
LARGS="headless:=true"; [ "${SHOW:-0}" = 1 ] && LARGS="headless:=false"
[ -n "${CONTROLLERS:-}" ] && LARGS="$LARGS controllers_file:=$CONTROLLERS"
PAT='gz sim -r( -s)? empty.sdf'
# With SHOW=1, attempt 1 also records both windows (tools/sim_record.sh, WebM) and saves screenshots after its motion
# (tools/sim_capture.py; added 2026-11-13) into docs/gallery/_pending/M4/<test ID>/, git-ignored until I have
# reviewed them (then moved to docs/gallery/M4/<test ID>/). Changed 2026-11-13 after TEST-M4-09 and its R1 re-run:
# <log name without _review.log>_a1_gazebo.png / _a1_rviz.png / _a1_gazebo.webm / _a1_rviz.webm.
# RViz is started only after the Gazebo window exists, so the window manager places it beside Gazebo.
B=$(basename "$OUT"); B=${B%_review.log}; B=${B%.log}
ID=$(printf '%s' "$B" | grep -oE '^TEST-M4-[0-9]{2}')   # test ID without a re-run or suite tag: TEST-M4-09-R1, TEST-M4-04-M412 -> TEST-M4-0x
SHOTS=docs/gallery/_pending/M4/$ID/$B   # git-ignored until reviewed (docs/gallery/README.md)
case $MODE in
  straight)   VIEW="1.0 -2.6 2.2 1.0 0 0" ;;
  rotate)     VIEW="-0.9 -0.9 0.9 0 0 0" ;;
  square_ccw) VIEW="-1.0 -1.4 2.4 0.5 0.5 0" ;;
  square_cw)  VIEW="-1.0 1.4 2.4 0.5 -0.5 0" ;;
  circle)     VIEW="0 -2.2 3.0 0 1.0 0" ;;
  *)          VIEW="-1.5 -1.5 1.8 0.3 0 0" ;;
esac
HARNESS=docs/evidence/M4/TEST-M4_odom_measure.py
TMP=$(mktemp -d); FAIL=0; VALID=0; ATTEMPT=0
sanitize() { sed -e "s|$HOME|<home>|g" -e "s|$(hostname)|<host>|g"; }
{
echo "# TEST-M4 procedure: mode=$MODE, valid runs required=$RUNS, $(date '+%F %T %Z')"
echo "# revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src DIRTY)')"
echo "# launch arguments: $LARGS" | sed "s|$PWD/||g"
echo "# ros2_control $(dpkg-query -W -f='${Version}' ros-jazzy-ros2-control), diff_drive_controller $(dpkg-query -W -f='${Version}' ros-jazzy-diff-drive-controller), gz_ros2_control $(dpkg-query -W -f='${Version}' ros-jazzy-gz-ros2-control)"
} > "$OUT"
while [ "$VALID" -lt "$RUNS" ] && [ "$ATTEMPT" -lt $((RUNS + 3)) ]; do
  ATTEMPT=$((ATTEMPT + 1))
  export ROS_DOMAIN_ID=$((80 + ATTEMPT)) GZ_PARTITION="amr_m4_${MODE}_$$_${ATTEMPT}"
  echo -e "\n## attempt $ATTEMPT (ROS_DOMAIN_ID=$ROS_DOMAIN_ID, GZ_PARTITION=amr_m4_${MODE}_<pid>_${ATTEMPT})" >> "$OUT"
  ros2 launch amr_bringup sim.launch.py $LARGS > "$TMP/launch_$ATTEMPT.log" 2>&1 &
  LPID=$!
  RPID=
  if [ "${SHOW:-0}" = 1 ]; then
    for _ in $(seq 60); do xwininfo -root -tree | grep -q '("gz-sim-gui" "Gazebo GUI")' && break; timeout 1 tail -f /dev/null; done
    QT_QPA_PLATFORM=xcb rviz2 -d "$(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz/odometry.rviz" --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
    RPID=$!
    if [ "$ATTEMPT" = 1 ]; then  # camera first (move animation ~1 s), then record, so the video starts on the set view
      mkdir -p "$(dirname "$SHOTS")"; timeout 8 tail -f /dev/null
      python3 tools/sim_capture.py view $VIEW > /dev/null 2>&1; timeout 3 tail -f /dev/null
      bash tools/sim_record.sh start "${SHOTS}_a1" >> "$OUT"; timeout 3 tail -f /dev/null   # stale-frame window (TS-036)
    else
      (sleep 12; python3 tools/sim_capture.py view $VIEW > /dev/null 2>&1) &
    fi
  fi
  timeout 300 python3 "$HARNESS" "$MODE" $CSV >> "$OUT" 2>&1
  RC=$?
  [ -n "$RPID" ] && [ "$ATTEMPT" = 1 ] && bash tools/sim_record.sh stop "${SHOTS}_a1" >> "$OUT"
  if [ -n "$RPID" ] && [ "$ATTEMPT" = 1 ]; then python3 tools/sim_capture.py shot "${SHOTS}_a1" 2>&1 | sed "s|$PWD/||g" >> "$OUT"; fi
  [ -n "$RPID" ] && kill -INT "$RPID" 2>/dev/null
  kill -INT "$LPID" 2>/dev/null
  for _ in $(seq 1 30); do kill -0 "$LPID" 2>/dev/null || pgrep -f "$PAT" > /dev/null || break; timeout 1 tail -f /dev/null; done
  if kill -0 "$LPID" 2>/dev/null; then kill -TERM -"$LPID" 2>/dev/null; echo "# launch did not stop on SIGINT within 30 s; SIGTERM sent to its process group" >> "$OUT"; fi
  wait "$LPID" 2>/dev/null
  LEFT=$(pgrep -af "$PAT" | grep -v pgrep | wc -l)
  NERR=$(grep -c '\[ERROR\]' "$TMP/launch_$ATTEMPT.log")
  { echo "# harness exit $RC; launch log: $NERR [ERROR] lines; leftover gz processes: $LEFT"
    grep -E '\[ERROR\]|\[WARN\]' "$TMP/launch_$ATTEMPT.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sanitize | sort | uniq -c | sed 's/^/#   /'; } >> "$OUT"
  if [ "$LEFT" -ne 0 ]; then pkill -TERM -f "$PAT"; echo "# leftover gz process stopped with SIGTERM" >> "$OUT"; fi
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
