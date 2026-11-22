#!/usr/bin/env bash
# TEST-M7-09 (REQ-M7-12): RViz navigation session for the user's observation (2026-11-23).
# SUPERSEDED, do not use (TS-057): written outside the shared procedure, it lacked `set -m` (TS-011) and the
# recording. Kept only because it produced TEST-M7-09_session.log. TEST-M7-09 runs through TEST-M7_procedure.sh.
# Usage, from the repository root, after sourcing ROS and amr_ws/install:
#   bash docs/evidence/M7/TEST-M7-09_session.sh <log> <done-flag-file>
# Starts, as TEST-M7_procedure.sh does: sim.launch.py sensors:=true world:=mapping_arena.sdf (GUI shown, default
# layout), localization.launch.py, RViz navigation.rviz, navigation.launch.py. The user sends goals with the Nav2
# goal tool. Supporting record (not the result): every NavigateToPose goal's final status from
# /navigate_to_pose/_action/status, [ERROR] counts and shutdown class of each launch, leftover processes.
# Stops everything when <done-flag-file> exists (created when the user reports the observation).
set -u
OUT=$1; FLAG=$2
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
SHARE_B=$(ros2 pkg prefix amr_bringup)/share/amr_bringup
export ROS_DOMAIN_ID=179 GZ_PARTITION="amr_m7_09_$$"
pause() { timeout --foreground "$1" tail -f /dev/null; }
stop_job() {  # pid, seconds, name: SIGINT, wait, then SIGTERM
  [ -n "$1" ] || return 0
  kill -INT "$1" 2>/dev/null
  for _ in $(seq "$2"); do kill -0 "$1" 2>/dev/null || break; pause 1; done
  kill -0 "$1" 2>/dev/null && { echo "# $3 still running after ${2} s: SIGTERM"; kill -TERM "$1"; }
  wait "$1" 2>/dev/null
}
{
echo "# TEST-M7-09 session, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gz sim --version | head -1); navigation2 $(dpkg-query -W -f='${Version}' ros-jazzy-navigation2)"
echo; echo '$ ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf'
ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf > "$TMP/sim.log" 2>&1 &
LPID=$!
for _ in $(seq 90); do
  [ "$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')" = 2 ] && break
  pause 1
done
echo "controllers: $(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c active) active"
echo; echo '$ ros2 launch amr_bringup localization.launch.py'
ros2 launch amr_bringup localization.launch.py > "$TMP/loc.log" 2>&1 &
SPID=$!
for _ in $(seq 60); do timeout --foreground 5 ros2 lifecycle get /amcl 2>/dev/null | grep -q active && break; pause 1; done
echo "amcl: $(timeout --foreground 5 ros2 lifecycle get /amcl 2>&1)"
QT_QPA_PLATFORM=xcb rviz2 -d "$SHARE_B/rviz/navigation.rviz" --ros-args -p use_sim_time:=true > /dev/null 2>&1 &
RPID=$!
echo; echo '$ ros2 launch amr_bringup navigation.launch.py'
ros2 launch amr_bringup navigation.launch.py > "$TMP/nav.log" 2>&1 &
NPID=$!
for _ in $(seq 60); do timeout --foreground 5 ros2 lifecycle get /bt_navigator 2>/dev/null | grep -q active && break; pause 1; done
echo "bt_navigator: $(timeout --foreground 5 ros2 lifecycle get /bt_navigator 2>&1)"
ros2 topic echo /navigate_to_pose/_action/status action_msgs/msg/GoalStatusArray > "$TMP/status.txt" 2>/dev/null &
EPID=$!
echo "# ready for goals: $(date '+%T')"
while [ ! -e "$FLAG" ]; do pause 2; done
echo "# user done: $(date '+%T')"
kill -INT "$EPID" 2>/dev/null; wait "$EPID" 2>/dev/null
echo; echo '## goal results (NavigateToPose action status; 4 = SUCCEEDED, 5 = CANCELED, 6 = ABORTED)'
python3 -I - "$TMP/status.txt" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
final = {}
for uuid, status in re.findall(r'uuid:\s*\n((?:\s*- \d+\n)+).*?status: (\d+)', text, re.S):
    final[tuple(re.findall(r'\d+', uuid))] = int(status)   # last status seen per goal id
names = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}
done = [s for s in final.values() if s in names]
for i, s in enumerate(done, 1):
    print(f'goal {i}: {names[s]}')
print(f'# goals with a final status: {len(done)}; SUCCEEDED {done.count(4)}, ABORTED {done.count(6)}, CANCELED {done.count(5)}')
PY
echo; echo '## shutdown'
kill -INT "$RPID" 2>/dev/null; wait "$RPID" 2>/dev/null
stop_job "$NPID" 30 "navigation launch"
stop_job "$SPID" 20 "localization launch"
stop_job "$LPID" 30 "simulation launch"
for K in nav loc sim; do
  echo "# $K log: $(grep -c '\[ERROR\]' "$TMP/$K.log") [ERROR] lines"
  python3 -I docs/evidence/M3/TEST-M3_launch_shutdown_classify.py "$TMP/$K.log"; echo "# classifier exit $?"
done
NAMES='gz sim|map_server|amcl|lifecycle_manager|planner_server|controller_server|behavior_server|bt_navigator|velocity_smoother|parameter_bridge|robot_state_publisher|rviz2 -d'
for _ in $(seq 10); do [ "$(pgrep -fc "$NAMES")" = 0 ] && break; pause 1; done
echo "# leftover processes by name: $(pgrep -fc "$NAMES")"
} > "$OUT" 2>&1
