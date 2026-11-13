#!/usr/bin/env bash
# TS-029 rig 2 (scratch, informal): one launch / SIGINT cycle. Usage: runone.sh <label> <i> <hold s> <outdir> [<overlay ws>] [extra launch args...]
# This shell is the parent of the launch, so it is an ancestor of `gz sim`. On a hang it exec's gdb (same PID, still an
# ancestor), which kernel.yama.ptrace_scope=1 allows without any system change.
set -m
LABEL=$1; I=$2; HOLD=$3; OUT=$4; OV=${5:-}; shift 5 2>/dev/null || shift $#
R=<home>/Projects/smart-factory-amr
cd "$R"
source /opt/ros/jazzy/setup.bash; source amr_ws/install/setup.bash; [ -n "$OV" ] && [ "$OV" != - ] && source "$OV/install/setup.bash"
export ROS_DOMAIN_ID=$((160 + I % 30)) GZ_PARTITION=rig2_${LABEL}_$$_$I
L=$OUT/${LABEL}_run${I}_launch.log
ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0 "$@" > "$L" 2>&1 &
LPID=$!
echo $LPID > "$OUT/${LABEL}_run${I}.lpid"
ok=0
for _ in $(seq 1 90); do A=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E ' active'); [ "$A" = 2 ] && ok=1 && break; timeout --foreground 1 tail -f /dev/null; done
# external subscribers during the hold, as in the formal harnesses (ROS /scan /imu /joint_states; gz pose/info and,
# when present, gz /imu_raw); they all exit before SIGINT
SUBT=$(( HOLD > 5 ? HOLD - 5 : 1 ))
timeout --foreground $SUBT ros2 topic echo /scan --no-arr > /dev/null 2>&1 &
timeout --foreground $SUBT ros2 topic echo /imu > /dev/null 2>&1 &
timeout --foreground $SUBT ros2 topic echo /joint_states > /dev/null 2>&1 &
timeout --foreground $SUBT gz topic -e -t /world/sensor_test/pose/info > /dev/null 2>&1 &
timeout --foreground $SUBT gz topic -e -t /imu_raw > /dev/null 2>&1 &
wait $(jobs -p | grep -v "^$LPID$") 2>/dev/null
timeout --foreground 5 tail -f /dev/null
GZ=$(pgrep -g $LPID -f "gz sim -r -s" | head -1)
echo "$GZ" > "$OUT/${LABEL}_run${I}.gzpid"
echo "controllers_active=$ok gz=$GZ" > "$OUT/${LABEL}_run${I}.meta"
date +%s.%N > "$OUT/${LABEL}_run${I}.t0"
kill -INT $LPID
for k in $(seq 1 35); do kill -0 "$GZ" 2>/dev/null || exit 0; timeout --foreground 0.1 tail -f /dev/null; done
# still alive 3.5 s after SIGINT: thread snapshot (state + kernel wait channel), then stack traces
{ echo "# alive 3.5 s after SIGINT; per-thread comm state wchan"
  for t in /proc/$GZ/task/*; do echo "$(cat $t/comm 2>/dev/null) $(awk '{print $3}' $t/stat 2>/dev/null) $(cat $t/wchan 2>/dev/null)"; done | sort | uniq -c
} > "$OUT/${LABEL}_run${I}_threads.txt"
exec gdb -q -batch -p "$GZ" -ex "set debuginfod enabled off" -ex "set pagination off" -ex "info threads" \
  -ex "thread apply all bt" -ex detach > "$OUT/${LABEL}_run${I}_gdb.txt" 2>&1
