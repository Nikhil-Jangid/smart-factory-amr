#!/usr/bin/env bash
# FEAS-M3 runtime gate (throwaway): launch headless with rendering, measure, shut down, check leftovers.
# Usage: bash gate_run.sh <gate_dir> <log>
# (no set -u: ROS setup.bash uses unset variables)
G=$1; LOG=$2
source /opt/ros/jazzy/setup.bash
source <home>/Projects/smart-factory-amr/amr_ws/install/setup.bash   # amr_bringup controllers.yaml, gz_ros2_control
export ROS_DOMAIN_ID=83 GZ_PARTITION=feas_m3_gate GATE_URDF=$G/on.urdf GATE_WORLD=$G/gate_world.sdf GATE_HEADLESS=render
{
echo "# FEAS-M3 runtime gate, $(date '+%Y-%m-%d %H:%M:%S %Z'), host GPU: $(lspci | grep -i vga | cut -d: -f3-)"
echo "# gz sim $(gz sim --version | head -1 | awk '{print $NF}'), mode: -s --headless-rendering, render engine ogre2, ROS_DOMAIN_ID=$ROS_DOMAIN_ID GZ_PARTITION=$GZ_PARTITION"
echo "# EGL/GL env: DISPLAY=${DISPLAY:-unset} WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-unset}"
} > "$LOG"
set -m   # TS-011/TS-021: job control so the background launch does not ignore SIGINT
ros2 launch "$G/gate_launch.py" > "$G/launch.log" 2>&1 &
LPID=$!
echo "# launch SigIgn: $(grep SigIgn /proc/$LPID/status | awk '{print $2}')" >> "$LOG"
python3 "$G/gate_measure.py" >> "$LOG" 2>&1; MRC=$?
echo "# measure exit code: $MRC" >> "$LOG"
kill -INT $LPID 2>/dev/null; for i in $(seq 1 30); do kill -0 $LPID 2>/dev/null || break; sleep 1; done
kill -0 $LPID 2>/dev/null && { echo "# launch did not exit after SIGINT; sending TERM" >> "$LOG"; kill -TERM $LPID; sleep 3; }
LEFT=$(pgrep -af "gz sim" | grep -v pgrep | grep gate_world || true)
echo "# leftover gz sim processes: ${LEFT:-none}" >> "$LOG"
echo "# launch log: rendering/sensor lines" >> "$LOG"
grep -iE "ogre|render|egl|sensor|gpu|error|fatal|failed|segmentation" "$G/launch.log" | grep -v "^\s*$" | head -40 >> "$LOG"
exit $MRC
