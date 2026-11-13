#!/usr/bin/env bash
# Scratch rig: shutdown timing of sim.launch.py with the Gazebo GUI (TEST-M4-10 investigation, 2026-11-13).
# Usage: bash gui_shutdown_rig.sh <variant A|B|C> <runs> <outdir>
#   A: headless:=false sensors:=true world:=sensor_test.sdf y:=-20.0   (failing case)
#   B: headless:=false (no sensors, empty world)
#   C: headless:=true  sensors:=true world:=sensor_test.sdf y:=-20.0   (baseline)
set -u; set -m
V=$1; N=$2; OUT=$3; mkdir -p "$OUT"
case $V in
  A) ARGS="headless:=false sensors:=true world:=sensor_test.sdf y:=-20.0" ;;
  B) ARGS="headless:=false" ;;
  C) ARGS="headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0" ;;
esac
for i in $(seq 1 "$N"); do
  export ROS_DOMAIN_ID=$((60 + i)) GZ_PARTITION="rig_${V}_$$_$i"
  L=$OUT/${V}_$i.launch.log
  ros2 launch amr_bringup sim.launch.py $ARGS > "$L" 2>&1 &
  LPID=$!
  # ready: controller active (odom published) or 60 s
  for _ in $(seq 60); do timeout 2 ros2 topic echo --once /diff_drive_controller/odom > /dev/null 2>&1 && break; done
  timeout 5 tail -f /dev/null
  T0=$(date +%s.%N)
  kill -INT "$LPID"
  timeout 4 tail -f /dev/null
  AT4=$(pgrep -a -g "$LPID" | grep -E 'gz sim' | sed -E 's/^([0-9]+) gz sim (server|gui|-r).*/\2/' | tr '\n' ' ')
  for _ in $(seq 300); do pgrep -g "$LPID" > /dev/null || break; timeout 0.1 tail -f /dev/null; done
  T1=$(date +%s.%N)
  wait "$LPID" 2>/dev/null
  E=$(grep -c '\[ERROR\]' "$L")
  printf '%s run %d: stop %.1f s; gz alive at +4 s: [%s]; [ERROR] lines %d; %s\n' "$V" "$i" "$(echo "$T1 - $T0" | bc)" "$AT4" "$E" \
    "$(grep -m1 -o 'process has died \[pid [0-9]*, exit code [-0-9]*' "$L" | sed 's/pid [0-9]*, //')"
done
