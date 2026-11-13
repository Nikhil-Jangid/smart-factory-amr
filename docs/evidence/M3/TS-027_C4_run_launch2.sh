#!/usr/bin/env bash
# scratch: real launch + probe; $1 = output log, $2 = domain id, extra launch args after
set -m
OUT=$1; DOM=$2; shift 2
cd <home>/Projects/smart-factory-amr
source /opt/ros/jazzy/setup.bash; source amr_ws/install/setup.bash; [ -n "${OVERLAY:-}" ] && source "$OVERLAY/install/setup.bash"; echo "# amr_bringup prefix: $(ros2 pkg prefix amr_bringup)"
export ROS_DOMAIN_ID=$DOM GZ_PARTITION=ts027_probe_$$
D=$(dirname "$OUT")
{
echo "# launch: sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0 $*"
ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0 "$@" > "$OUT.launch" 2>&1 &
LPID=$!
for _ in $(seq 1 90); do A=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active'); [ "$A" = 2 ] && break; timeout --foreground 1 tail -f /dev/null; done
echo "# controllers active: $A"
timeout --foreground 120 python3 <scratch>/${PROBE:-probe.py}; echo "# probe exit $?"
kill -INT $LPID; for _ in $(seq 1 30); do kill -0 $LPID 2>/dev/null || break; timeout --foreground 1 tail -f /dev/null; done
wait $LPID 2>/dev/null; sleep 2; echo "# leftovers: $(pgrep -g $LPID | wc -l)"; pkill -TERM -g $LPID 2>/dev/null
} > "$OUT" 2>&1
