#!/usr/bin/env bash
# Demonstration gallery capture (2026-11-13): re-creates a tested scene with the Gazebo GUI and RViz
# visible, records both windows to video (tools/sim_record.sh) and saves still screenshots (tools/sim_capture.py)
# into docs/gallery/_pending/<M>/<TEST-ID>/<scene>_demo_* (git-ignored; moved to docs/gallery/<M>/<TEST-ID>/ and
# committed only after I review them, docs/gallery/README.md). These are demonstrations of what a test covers, re-created on the
# current revision; they are NOT test evidence (the evidence is the logs under docs/evidence/).
# Run from the repository root after sourcing /opt/ros/jazzy/setup.bash and amr_ws/install/setup.bash.
# Usage: bash tools/demo_capture.sh <scene>      scenes: see the case statement below
# Rules learned while building it (2026-11-13):
#  - set -m: without job control, background jobs of a non-interactive shell ignore SIGINT and survive the teardown
#    (TS-011). A surviving robot_state_publisher on the same ROS domain corrupted the next scenes (two robot
#    descriptions, wall-clock joint states: RViz RobotModel/TF errors), so the script refuses to start while any
#    ROS/Gazebo process from an earlier run exists, and checks again at the end (exit 1 if anything is left).
#  - Windows must not overlap: xwd and ximagesrc capture visible pixels only. RViz is started after the Gazebo window
#    exists and is 860 px wide, so the window manager places it beside Gazebo; a requested X/Y position is ignored.
#  - The M1 scene uses joint_state_publisher (no GUI) instead of display.launch.py's slider window, which covered RViz.
set -u
set -m
SCENE=${1:?scene}
export QT_QPA_PLATFORM=xcb ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-90} GZ_PARTITION="amr_demo_$$"
PROCS='gz sim|robot_state_publisher|joint_state_publisher|rviz2|parameter_bridge|ros2 launch|controller_manager|controller_manager/spawner'
others() { pgrep -af "$PROCS" | grep -v -E "pgrep|demo_capture" ; }
if [ -n "$(others)" ]; then echo "# refused: ROS/Gazebo processes already running:"; others; exit 1; fi
BR=$(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz
DS=$(ros2 pkg prefix amr_description)/share/amr_description
TMP=$(mktemp -d)
LAUNCH="ros2 launch amr_bringup sim.launch.py headless:=false"; RVIZ=$BR/odometry.rviz; DRIVE=; VIEW=; WAIT=0; NOGZ=0
case $SCENE in
  m1_rviz_model)   DIR=M1/TEST-M1-04; NOGZ=1; WAIT=6; RVIZ=$DS/rviz/display.rviz
                   LAUNCH="ros2 run robot_state_publisher robot_state_publisher --ros-args --params-file $TMP/rsp.yaml" ;;
  m1_gazebo_spawn) DIR=M1/TEST-M1-06; LAUNCH="ros2 launch amr_description gazebo.launch.py"; RVIZ=; WAIT=12
                   VIEW="1.2 -1.2 0.8 0 0 0.15" ;;
  m2_linear)  DIR=M2/TEST-M2-05; DRIVE="0.2 0 5 0 0 3 -0.2 0 5"; VIEW="0.5 -1.8 1.1 0.5 0 0" ;;
  m2_rotate)  DIR=M2/TEST-M2-06; DRIVE="0 0.5 6.283 0 0 3 0 -0.5 6.283"; VIEW="-0.9 -0.9 0.9 0 0 0" ;;
  m3_lidar)   DIR=M3/TEST-M3-10; LAUNCH="$LAUNCH sensors:=true world:=sensor_test.sdf"; RVIZ=$BR/sensors.rviz
              DRIVE="0 0.4 7.854 0 0 2"; VIEW="-4.0 -4.5 5.0 -1.0 0 0" ;;
  m4_square)  DIR=M4/TEST-M4-06; Q="0.2 0 5 0 0 1 0 0.5 3.1416 0 0 1"; DRIVE="$Q $Q $Q $Q"
              VIEW="-1.0 -1.4 2.4 0.5 0.5 0" ;;
  m4_circle)  DIR=M4/TEST-M4-07; DRIVE="0.2 0.2 31.416"; VIEW="0 -1.3 2.0 0 0.9 0" ;;
  *) echo "unknown scene $SCENE"; exit 2 ;;
esac
OUT=docs/gallery/_pending/$DIR; mkdir -p "$OUT"; P=$OUT/${SCENE}_demo
rm -f "${P}"_*
win() { xwininfo -root -tree | grep -E "$1" | head -1 | awk '{print $1}'; }
wait_gone() { for _ in $(seq "$1"); do [ -z "$(others)" ] && return 0; timeout 1 tail -f /dev/null; done; return 1; }
echo "# demo $SCENE, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD), domain $ROS_DOMAIN_ID"

JPID=
if [ "$SCENE" = m1_rviz_model ]; then
  # The M1 model (default expansion, as display.launch.py); the description goes in through a params file.
  xacro "$DS/urdf/amr.urdf.xacro" > "$TMP/amr.urdf"
  python3 - "$TMP/amr.urdf" "$TMP/rsp.yaml" <<'EOF'
import sys, yaml
yaml.safe_dump({'robot_state_publisher': {'ros__parameters': {'robot_description': open(sys.argv[1]).read()}}},
               open(sys.argv[2], 'w'))
EOF
  ros2 run joint_state_publisher joint_state_publisher > "$TMP/jsp.log" 2>&1 &
  JPID=$!
fi
$LAUNCH > "$TMP/launch.log" 2>&1 &
LPID=$!
GW=
if [ $NOGZ = 0 ]; then
  for _ in $(seq 60); do GW=$(win '\("gz-sim-gui" "Gazebo GUI"\)'); [ -n "$GW" ] && break; timeout 1 tail -f /dev/null; done
  [ -z "$GW" ] && echo "# no Gazebo window"
fi
RPID=
if [ -n "$RVIZ" ]; then
  # Copy of the RViz config for the capture: no Views panel (more room for the 3D view), 860 x 845 window.
  python3 - "$RVIZ" "$TMP/view.rviz" <<'EOF'
import re, sys
t = open(sys.argv[1]).read()
t = t.replace('  - Class: rviz_common/Views\n    Name: Views\n', '')
geo = 'Window Geometry:\n  Displays:\n    collapsed: false\n  Height: 845\n  Width: 860\n  Hide Left Dock: false\n  Hide Right Dock: true\n'
t = re.sub(r'^Window Geometry:\n(?:[ ].*\n?)*', '', t, flags=re.M).rstrip('\n') + '\n' + geo
open(sys.argv[2], 'w').write(t)
EOF
  if [ $NOGZ = 1 ]; then rviz2 -d "$TMP/view.rviz" > "$TMP/rviz.log" 2>&1 &
  else rviz2 -d "$TMP/view.rviz" --ros-args -p use_sim_time:=true > "$TMP/rviz.log" 2>&1 & fi
  RPID=$!
  for _ in $(seq 30); do [ -n "$(win ' - RViz": \("rviz2" "rviz2"\)')" ] && break; timeout 1 tail -f /dev/null; done
fi
timeout 8 tail -f /dev/null
[ -n "$VIEW" ] && python3 tools/sim_capture.py view $VIEW && timeout 3 tail -f /dev/null   # camera move animation
if [ -n "$DRIVE" ]; then
  bash tools/sim_record.sh start "$P"
  timeout 3 tail -f /dev/null   # the first ~2 s of a recording are stale frames, cut by sim_record.sh stop
  python3 tools/demo_drive.py $DRIVE
  timeout 2 tail -f /dev/null
  bash tools/sim_record.sh stop "$P"
else
  timeout $WAIT tail -f /dev/null
fi
python3 tools/sim_capture.py shot "$P"
[ -z "$RVIZ" ] && rm -f "${P}_rviz.png"      # no RViz in this scene
[ $NOGZ = 1 ] && rm -f "${P}_gazebo.png"
# Teardown: SIGINT to each process group (job control gives every job its own group), then escalate.
for pid in $RPID $LPID $JPID; do kill -INT -- -"$pid" 2>/dev/null; done
wait_gone 20 || { pkill -INT -f '^gz sim'; wait_gone 10; } \
  || { for pid in $RPID $LPID $JPID; do kill -TERM -- -"$pid" 2>/dev/null; done; pkill -TERM -f '^gz sim'; wait_gone 10; }
LEFT=$(others)
echo "# leftover ROS/Gazebo processes: $( [ -z "$LEFT" ] && echo 0 || echo "$LEFT" | wc -l)"
[ -n "$LEFT" ] && echo "$LEFT"
ls -la "$OUT" | grep "$SCENE"
rm -rf "$TMP"
[ -z "$LEFT" ]
