#!/usr/bin/env bash
# TS-044 reproduction: how often does diff_drive_controller fail to load at start-up after the 2026-11-18 apt upgrade
# (ros2_control 4.50.0, diff_drive_controller 4.43.1)? Diagnostic, not a formal test.
# Each launch is the default M2 launch, started and stopped exactly as in TEST-M2_procedure.sh (isolated ROS_DOMAIN_ID
# and GZ_PARTITION, job control, SIGINT then SIGTERM to the process group, leftover check). Nothing calls the controller
# manager during start-up: the spawner's own launch-log lines are watched, so the probe does not change the timing.
# Outcome per launch:
#   OK       both spawners report "Configured and activated" and /diff_drive_controller/odom delivers a message
#   LOADFAIL the diff_drive_controller spawner reports a load_controller timeout or dies
#   TIMEOUT  neither within 90 s wall time
# The full sanitized launch log of every non-OK launch is appended to the output log.
# Usage, from the repository root after sourcing /opt/ros/jazzy/setup.bash and amr_ws/install/setup.bash:
#   SHOW=1 bash docs/evidence/M2/TS-044_startup_loop.sh <launches> <output log>
set -u
HL=true; [ "${SHOW:-0}" = 1 ] && HL=false
GZPAT="gz sim -r -s empty.sdf"; [ "$HL" = false ] && GZPAT="gz sim -r empty.sdf"
set -m
N=$1; OUT=$2
TMP=$(mktemp -d); NOK=0; NLOAD=0; NTO=0
sanitize() { sed -e "s|$HOME|<home>|g" -e "s|$(hostname)|<host>|g"; }
{
echo "# TS-044 start-up loop: $N launches, headless:=$HL, $(date '+%F %T %Z')"
echo "# revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src DIRTY)')"
echo "# ros2_control $(dpkg-query -W -f='${Version}' ros-jazzy-ros2-control), diff_drive_controller $(dpkg-query -W -f='${Version}' ros-jazzy-diff-drive-controller), gz_ros2_control $(dpkg-query -W -f='${Version}' ros-jazzy-gz-ros2-control), rclcpp $(dpkg-query -W -f='${Version}' ros-jazzy-rclcpp)"
echo "# columns: launch, outcome, wall seconds from launch to both controllers active (or to the failure), odom message received"
} > "$OUT"
for i in $(seq 1 "$N"); do
  export ROS_DOMAIN_ID=$((150 + i % 80)) GZ_PARTITION="amr_ts044_$$_$i"
  LOG="$TMP/launch_$i.log"
  T0=$(date +%s.%N)
  ros2 launch amr_bringup sim.launch.py headless:=$HL > "$LOG" 2>&1 &
  LPID=$!
  RES=TIMEOUT; T=""
  for _ in $(seq 1 900); do
    if grep -q -E "Failed getting a result from calling /controller_manager/load_controller.*Attempt 3 of 3|\[spawner-[0-9]+\]: process has died" "$LOG"; then
      RES=LOADFAIL; T=$(printf '%.2f' "$(echo "$(date +%s.%N) - $T0" | bc)"); break
    fi
    if [ "$(grep -c 'Configured and activated' "$LOG")" -ge 2 ]; then
      RES=OK; T=$(printf '%.2f' "$(echo "$(date +%s.%N) - $T0" | bc)"); break
    fi
    timeout 0.1 tail -f /dev/null
  done
  ODOM=no
  [ "$RES" = OK ] && timeout 15 ros2 topic echo --once /diff_drive_controller/odom > /dev/null 2>&1 && ODOM=yes
  [ "$RES" = OK ] && [ "$ODOM" = no ] && RES=NOODOM
  kill -INT "$LPID" 2>/dev/null
  for _ in $(seq 1 30); do kill -0 "$LPID" 2>/dev/null || pgrep -f "$GZPAT" > /dev/null || break; timeout 1 tail -f /dev/null; done
  STOP=SIGINT
  if kill -0 "$LPID" 2>/dev/null; then kill -TERM -"$LPID" 2>/dev/null; STOP=SIGTERM; fi
  wait "$LPID" 2>/dev/null
  LEFT=$(pgrep -af "$GZPAT" | grep -v pgrep | wc -l)
  [ "$LEFT" -ne 0 ] && pkill -TERM -f "$GZPAT"
  printf '%3d %-8s %6s s  odom=%-3s  stop=%s  leftover=%s\n' "$i" "$RES" "${T:-90+}" "$ODOM" "$STOP" "$LEFT" >> "$OUT"
  case $RES in
    OK) NOK=$((NOK + 1)) ;;
    LOADFAIL|NOODOM) NLOAD=$((NLOAD + 1)) ;;
    *) NTO=$((NTO + 1)) ;;
  esac
  if [ "$RES" != OK ]; then
    { echo "#   --- launch $i log (sanitized) ---"; sanitize < "$LOG" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sed 's/^/#   /'; } >> "$OUT"
  fi
done
echo -e "\n# summary: OK $NOK, LOADFAIL/NOODOM $NLOAD, TIMEOUT $NTO of $N launches" >> "$OUT"
rm -rf "$TMP"
[ "$NOK" -eq "$N" ]
