#!/usr/bin/env bash
# TS-029 rig (informal). Usage: TS-029_shutdown_rig.sh <label> <runs> [<overlay ws>]; run from inside the repository.
# scratch: launch/SIGINT cycles; $1 = variant label, $2 = runs, $3 = optional overlay ws
set -m
cd "$(git rev-parse --show-toplevel)"
source /opt/ros/jazzy/setup.bash; source amr_ws/install/setup.bash; [ -n "${3:-}" ] && source "$3/install/setup.bash"
for i in $(seq 1 $2); do
  export ROS_DOMAIN_ID=$((140 + i)) GZ_PARTITION=rig_$1_$$_$i
  L=$(mktemp)
  ros2 launch amr_bringup sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0 > $L 2>&1 &
  LPID=$!
  for _ in $(seq 1 90); do A=$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E ' active'); [ "$A" = 2 ] && break; timeout --foreground 1 tail -f /dev/null; done
  timeout --foreground 5 tail -f /dev/null
  GZ=$(pgrep -g $LPID -f "gz sim -r -s" | head -1)
  T0=$(date +%s.%N); kill -INT $LPID
  SNAP=""
  for k in $(seq 1 300); do kill -0 $GZ 2>/dev/null || break
    if [ $k = 30 ] && [ -z "$SNAP" ]; then SNAP=$(for t in /proc/$GZ/task/*; do echo "$(cat $t/comm 2>/dev/null):$(cat $t/wchan 2>/dev/null)"; done | sort | uniq -c | tr '\n' ';'); fi
    timeout --foreground 0.1 tail -f /dev/null; done
  T1=$(date +%s.%N)
  wait $LPID 2>/dev/null; pkill -TERM -g $LPID 2>/dev/null
  printf "%s run %d: gz exit after %.1f s; ERROR lines %d; plugin shutdown line %d; %s\n" $1 $i $(echo "$T1 - $T0" | bc) $(grep -c '\[ERROR\]' $L) $(grep -c 'ImuDecimator\] shutdown' $L) "${SNAP:+threads@3s: $SNAP}"
  rm -f $L
done
