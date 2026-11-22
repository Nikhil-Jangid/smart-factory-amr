#!/usr/bin/env bash
# M7 Task B dry runs of TEST-M7_nav_run.py (GUI shown; scratch, not a formal test). Usage, from the repository root:
#   bash docs/evidence/M7/TaskB_dryrun.sh <out dir> [modes ...]   (default modes: sequence invalid route cancel)
# Dry run 1: default order. 2: invalid route. 3: invalid route with NAV2_PARAMS=<copy with allow_unknown false>.
# 4: invalid sequence route cancel (DEC-077 and DEC-078 in nav2.yaml and TEST-M7_goals.py). Consoles: TaskB-dry<n>_console.log.
set -m

source /opt/ros/jazzy/setup.bash; source amr_ws/install/setup.bash
set -u
OUT=$1; shift; MODES="${*:-sequence invalid route cancel}"
mkdir -p "$OUT"
export ROS_DOMAIN_ID=181 GZ_PARTITION="amr_m7_dry_$$"
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
pause() { timeout --foreground "$1" tail -f /dev/null; }
stop_job() {
  kill -INT "$1" 2>/dev/null
  for _ in $(seq 1 "$2"); do kill -0 "$1" 2>/dev/null || break; pause 1; done
  kill -0 "$1" 2>/dev/null && { kill -TERM -- -"$1" 2>/dev/null; echo "# $3: SIGTERM to group"; }
  wait "$1" 2>/dev/null
}
echo "# dry run $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)"
ros2 launch amr_bringup sim.launch.py headless:=false sensors:=true world:=mapping_arena.sdf > "$OUT/sim.log" 2>&1 &
LPID=$!; echo "$LPID" > "$OUT/pids"
for _ in $(seq 1 90); do
  [ "$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')" = 2 ] && break; pause 1
done
echo "# controllers active"
ros2 launch amr_bringup localization.launch.py > "$OUT/loc.log" 2>&1 &
SPID=$!; echo "$SPID" >> "$OUT/pids"
for _ in $(seq 60); do timeout --foreground 5 ros2 lifecycle get /amcl 2>/dev/null | grep -q active && break; pause 1; done
echo "# amcl active"
QT_QPA_PLATFORM=xcb rviz2 -d "$SHARE_B/rviz/navigation.rviz" --ros-args -p use_sim_time:=true > "$OUT/rviz.log" 2>&1 &
RPID=$!; echo "$RPID" >> "$OUT/pids"
ros2 launch amr_bringup navigation.launch.py ${NAV2_PARAMS:+nav2_params_file:=$NAV2_PARAMS} > "$OUT/nav.log" 2>&1 &
NPID=$!; echo "$NPID" >> "$OUT/pids"
pause 10
for MODE in $MODES; do
  echo; echo "## mode $MODE"
  python3 docs/evidence/M7/TEST-M7_nav_run.py "$OUT/dry_$MODE" --mode "$MODE"
  echo "# exit $?"
done
kill -INT "$RPID" 2>/dev/null; wait "$RPID" 2>/dev/null
stop_job "$NPID" 20 navigation
stop_job "$SPID" 20 localization
stop_job "$LPID" 30 simulation
pause 3
echo "# leftovers: $(ps -eo comm,args | awk '$1 ~ /^(gz|ruby|parameter_bridg|robot_state_pub|rviz2|amcl|map_server|planner_server|controller_serv|behavior_serve|bt_navigator|velocity_smoot|lifecycle_mana|cmd_vel_guard)/' | wc -l)"
echo "# done $(date '+%T')"
