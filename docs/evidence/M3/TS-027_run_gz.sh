#!/usr/bin/env bash
# scratch: gz sim server with sensor_test.sdf, runtime spawn of $2 (SDF file), probe2; $1 = log
set -m
OUT=$1; MODEL=$2
source /opt/ros/jazzy/setup.bash; source <home>/Projects/smart-factory-amr/amr_ws/install/setup.bash
export GZ_PARTITION=ts027_gz_$$
W=$(ros2 pkg prefix amr_bringup)/share/amr_bringup/worlds/sensor_test.sdf
D=${SCRATCH:?set SCRATCH to a scratch directory}   # archived investigation script; the original scratch path is not kept
{
echo "# gz sim -r -s --headless-rendering sensor_test.sdf; spawn $(basename $MODEL) at (0,-20,0)"
gz sim -r -s --headless-rendering "$W" > "$OUT.server" 2>&1 &
GPID=$!
timeout --foreground 5 tail -f /dev/null
gz service -s /world/sensor_test/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 5000 --req "sdf_filename: \"$MODEL\", name: \"amr\", pose: {position: {y: -20}}"
timeout --foreground 60 python3 $D/probe2.py; echo "# probe exit $?"
kill -INT $GPID; wait $GPID 2>/dev/null; sleep 1; echo "# leftovers $(pgrep -g $GPID | wc -l)"; pkill -TERM -g $GPID 2>/dev/null
} > "$OUT" 2>&1
