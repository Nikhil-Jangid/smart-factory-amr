#!/usr/bin/env bash
# TEST-M2-04: simulation time, joint states, odometry frames and TF tree (test_plan.md §6.2).
# Run from the repository root after sourcing /opt/ros/jazzy/setup.bash and amr_ws/install/setup.bash.
# Usage: bash docs/evidence/M2/TEST-M2-04_procedure.sh <log> <frames basename>
# Writes the log and <frames basename>.pdf/.gv (view_frames output). Exit 0 only if every check passed.
# The TF-vs-odometry identity is checked by the harness (mode tfcheck) in the same session.
set -u
# SHOW=1 (option added 2026-11-13 for TEST-M4-10, my choice): Gazebo GUI instead of headless (headless:=false) and the
# GUI camera aimed at the robot (tools/sim_capture.py view). Physics, harness and criteria unchanged; default = headless.
HL=true; [ "${SHOW:-0}" = 1 ] && HL=false
GZPAT="gz sim -r -s empty.sdf"; [ "$HL" = false ] && GZPAT="gz sim -r empty.sdf"
show_view() { [ "${SHOW:-0}" = 1 ] && (sleep 12; python3 tools/sim_capture.py view -1.5 -1.5 1.8 0.3 0 0 > /dev/null 2>&1) & }
set -m  # background jobs keep default SIGINT handling (TS-011)
OUT=$1; FRAMES=$2; TMP=$(mktemp -d); FAIL=0
export ROS_DOMAIN_ID=81 GZ_PARTITION="amr_m2_t04_$$"
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
# The launch is started and stopped OUTSIDE the logging block: inside a pipeline there is no job
# control, so it would ignore SIGINT and never stop (TS-017). The block writes to a raw file,
# which is sanitized at the end.
ros2 launch amr_bringup sim.launch.py headless:=$HL > "$TMP/launch.log" 2>&1 &
LPID=$!
show_view
{
echo "# TEST-M2-04, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src DIRTY)'), headless:=$HL"
for _ in $(seq 1 90); do timeout 5 ros2 control list_controllers 2>/dev/null | grep -q 'diff_drive_controller.*active' && break; timeout 1 tail -f /dev/null; done
echo; echo '$ ros2 topic echo --once /clock   (twice, about 2 s apart)'
# first purely numeric line: the echo output ends with a '---' separator (TS-017), and under load `ros2 topic echo`
# prints 'A message was lost!!!' on stdout before the value (TS-048); stderr dropped (broken-pipe trace after grep -m1)
C1=$(timeout 10 ros2 topic echo --once /clock --field clock.sec 2>/dev/null | grep -m1 -E '^[0-9]+$'); timeout 2 tail -f /dev/null; C2=$(timeout 10 ros2 topic echo --once /clock --field clock.sec 2>/dev/null | grep -m1 -E '^[0-9]+$')
echo "clock.sec: $C1 then $C2"; [ -n "$C1" ] && [ -n "$C2" ] && [ "$C2" -gt "$C1" ]; rc $?
echo; echo '$ ros2 param get <node> use_sim_time   (every M2 runtime node)'
NODES=$(timeout 10 ros2 node list 2>/dev/null | grep -v -E '_ros2cli|/m2_' | sort)
echo "nodes: $(echo $NODES)"
ALL=0
for n in $NODES; do V=$(timeout 10 ros2 param get "$n" use_sim_time 2>&1 | tail -1); echo "$n: $V"; echo "$V" | grep -q 'True' || ALL=1; done
[ -n "$NODES" ] && [ $ALL = 0 ]; rc $?
echo; echo '$ ros2 topic echo --once /joint_states'
JS=$(timeout 10 ros2 topic echo --once /joint_states); echo "$JS" | grep -A3 -E '^(name|position|velocity):'
echo "$JS" | grep -q left_wheel_joint && echo "$JS" | grep -q right_wheel_joint && [ "$(echo "$JS" | grep -c -E '^(position|velocity):')" = 2 ]; rc $?
echo; echo '$ ros2 topic echo --once /diff_drive_controller/odom   (header and child frame)'
OD=$(timeout 10 ros2 topic echo --once /diff_drive_controller/odom); echo "$OD" | grep -E 'frame_id'
echo "$OD" | grep -q "frame_id: odom" && echo "$OD" | grep -q "child_frame_id: base_footprint"; rc $?
echo; echo '$ ros2 run tf2_ros tf2_echo odom base_footprint   (first transform)'
TE=$(timeout 8 ros2 run tf2_ros tf2_echo odom base_footprint 2>&1); echo "$TE" | grep -m3 -E 'At time|Translation|Rotation: in Quaternion'
echo "$TE" | grep -q 'Translation'; rc $?
echo; echo '$ ros2 run tf2_tools view_frames   (TF tree)'
(cd "$TMP" && timeout 30 ros2 run tf2_tools view_frames > view_frames.log 2>&1); grep -v -E 'frame_id|^$' "$TMP/view_frames.log" | head -3
GV=$(ls "$TMP"/frames_*.gv 2>/dev/null | head -1)
[ -n "$GV" ] && cp "$GV" "$FRAMES.gv" && cp "${GV%.gv}.pdf" "$FRAMES.pdf"
python3 -I - "$FRAMES.gv" <<'PY'
import re, sys
edges = re.findall(r'"([^"]+)" -> "([^"]+)"', open(sys.argv[1]).read())
print('edges:', sorted(edges))
expected = {('odom', 'base_footprint'), ('base_footprint', 'base_link'), ('base_link', 'left_wheel_link'),
            ('base_link', 'right_wheel_link'), ('base_link', 'caster_link'), ('base_link', 'lidar_mount_link')}
parents = {}
for p, c in edges:
    parents.setdefault(c, []).append(p)
ok = set(edges) == expected and all(len(v) == 1 for v in parents.values())
print('tree == odom -> base_footprint -> M1 tree, one parent per frame:', ok)
sys.exit(0 if ok else 1)
PY
rc $?
echo; echo '$ python3 TEST-M2_motion_measure.py tfcheck   (TF odom->base_footprint vs odometry at the same stamp)'
python3 docs/evidence/M2/TEST-M2_motion_measure.py tfcheck; rc $?
echo "FAIL=$FAIL"
} > "$TMP/raw.log" 2>&1
kill -INT $LPID; wait $LPID 2>/dev/null
for _ in $(seq 1 30); do pgrep -f "$GZPAT" > /dev/null || break; timeout 1 tail -f /dev/null; done
FAIL=$(sed -n 's/^FAIL=//p' "$TMP/raw.log")
{ grep -v '^FAIL=' "$TMP/raw.log"
  echo; echo "# launch log: $(grep -c '\[ERROR\]' "$TMP/launch.log") [ERROR] lines; leftover gz processes: $(pgrep -f "$GZPAT" | wc -l)"
  echo "# overall: $([ "$FAIL" = 0 ] && echo 'ALL CHECKS PASSED' || echo 'AT LEAST ONE CHECK FAILED')"
} | sed -e "s|$HOME|<home>|g" > "$OUT"
rm -rf "$TMP"
grep -q 'ALL CHECKS PASSED' "$OUT"
