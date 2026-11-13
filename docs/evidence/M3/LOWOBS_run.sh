#!/usr/bin/env bash
# LOWOBS investigation runner (throwaway; FEAS-M3 gate harness with the TS-021 fixes).
# Usage: bash lowobs_run.sh <dir> <A|B> <log>
L=$1; MODE=$2; LOG=$3
source /opt/ros/jazzy/setup.bash
source <home>/Projects/smart-factory-amr/amr_ws/install/setup.bash
export BEARING_DUMP=${BEARING_DUMP:-} ROS_DOMAIN_ID=84 GZ_PARTITION=lowobs_m3 GATE_URDF=$L/$MODE.urdf GATE_WORLD=$L/lowobs_world.sdf GATE_HEADLESS=render MODE
if [ "$MODE" = A ]; then export LX=0.070 LZ=0.230 GATE_BRIDGE_EXTRA='/depth/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked'
else export LX=0.160 LZ=0.120 GATE_BRIDGE_EXTRA=''; fi
{ echo "# LOWOBS run $MODE, $(date '+%Y-%m-%d %H:%M:%S %Z'), GPU: $(lspci | grep -i vga | cut -d: -f3-)"
  echo "# gz sim $(gz sim --version | head -1 | awk '{print $NF}'), -s --headless-rendering, ROS_DOMAIN_ID=$ROS_DOMAIN_ID GZ_PARTITION=$GZ_PARTITION"; } > "$LOG"
set -m
ros2 launch "$L/lowobs_launch.py" > "$L/launch_$MODE.log" 2>&1 &
LPID=$!
echo "# launch SigIgn: $(grep SigIgn /proc/$LPID/status | awk '{print $2}')" >> "$LOG"
python3 "$L/lowobs_measure.py" >> "$LOG" 2>&1; MRC=$?
echo "# gz topics: $(gz topic -l | grep -E 'scan|depth|imu' | tr '\n' ' ')" >> "$LOG"
echo "# measure exit code: $MRC" >> "$LOG"
kill -INT $LPID 2>/dev/null; for i in $(seq 1 30); do kill -0 $LPID 2>/dev/null || break; sleep 1; done
kill -0 $LPID 2>/dev/null && { echo "# launch did not exit after SIGINT; sending TERM" >> "$LOG"; kill -TERM -$LPID; sleep 3; }
echo "# leftover processes: $(pgrep -af 'gz sim|parameter_bridge|robot_state_publisher' | grep -v '^11466 ' | grep -v pgrep || echo none) (PID 11466, a pre-existing user gz sim server, excluded)" >> "$LOG"
echo "# launch log: errors/warnings (excluding the diff_drive_controller command-timeout messages)" >> "$LOG"
grep -iE "error|fatal|failed|segmentation|warn" "$L/launch_$MODE.log" | grep -v "Velocity command timed out" | head -20 >> "$LOG"
exit $MRC
