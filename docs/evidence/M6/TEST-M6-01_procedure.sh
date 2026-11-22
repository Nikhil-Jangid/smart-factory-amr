#!/usr/bin/env bash
# TEST-M6-01: build and regression identity (REQ-M6-11; docs/testing/test_plan.md §11; M6 Task A).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Usage: bash docs/evidence/M6/TEST-M6-01_procedure.sh [TAG]   -> docs/evidence/M6/TEST-M6-01${TAG}_review.log
# BASE = 9b85171, the M5 closeout commit (M5 complete; finalized -11-15).
# Steps:
#  1. colcon build of the three project packages: exit 0, no line matching 'warning'.
#  2. Default model expansion byte-identical to docs/evidence/M1/TEST-M1-02_amr.urdf (M1 baseline).
#  3. Expansions with use_ros2_control:=true and with use_ros2_control:=true use_sensors:=true (the M2 and M3-M5
#     launch models) byte-identical to the BASE expansions: M6 does not change the robot.
#  4. sim.launch.py, controllers.yaml, amr.sensors.xacro, amr_properties.xacro, slam_toolbox.yaml, slam.launch.py and
#     the four M5 reference map files unchanged since BASE (git diff empty); sim.launch.py may add exactly the
#     DEC-075 gui_config lines listed in TEST-M7-01 step 7 (DEC-080, 2026-11-23).
#  5. Existing files changed in amr_ws/src from BASE to END: only amr_bringup/package.xml (exactly the five added
#     exec_depend lines: nav2_map_server, nav2_amcl, nav2_lifecycle_manager, robot_localization (Task D, DEC-057;
#     added to this list 2026-11-20, TS-049), nav2_rviz_plugins) and
#     amr_bringup/CMakeLists.txt (comment lines and the install rule gaining the maps folder). Every other change is a
#     new file (M6 plan §6: localization runs beside the unchanged simulation, DEC-060).
#  6. maps/mapping_arena_amcl.yaml differs from maps/mapping_arena.yaml only in its comment lines and an origin
#     exactly +0.025 m (half a 0.05 m cell) in x and y (DEC-062, TS-045).
set -u
TAG=${1:-}
BASE=${BASE:-9b85171}
# END = 9777615, the M6 closeout commit (M6 complete; finalized -11-21): step 5 checks only M6's own
# increment (DEC-064); later milestones' changes are checked by their own identity tests.
END=${END:-9777615}
PKGS="amr_description amr_bringup amr_gazebo_plugins"
LOG=docs/evidence/M6/TEST-M6-01${TAG}_review.log
X=src/amr_description/urdf/amr.urdf.xacro
B=amr_ws/src/amr_bringup
TMP=$(mktemp -d); FAIL=0
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
{
echo "# TEST-M6-01 review, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)'); baseline $BASE"

echo; echo "## 1. Build"
echo "\$ cd amr_ws && colcon build --symlink-install --packages-select $PKGS"
(cd amr_ws && colcon build --symlink-install --packages-select $PKGS --event-handlers console_direct+) > "$TMP/build.txt" 2>&1
BR=$?
tail -5 "$TMP/build.txt"
W=$(grep -i -c -E 'warning|warn:' "$TMP/build.txt")
echo "# colcon exit $BR; lines matching 'warning': $W"
[ "$BR" = 0 ] && [ "$W" = 0 ]; rc $?
CTRL="$(ros2 pkg prefix amr_bringup)/share/amr_bringup/config/controllers.yaml"

echo; echo "## 2. Default expansion vs the M1 baseline"
(cd amr_ws && xacro $X) > "$TMP/off.urdf" && cmp "$TMP/off.urdf" docs/evidence/M1/TEST-M1-02_amr.urdf && echo identical; rc $?

echo; echo "## 3. Launch-model expansions vs $BASE"
mkdir -p "$TMP/base" && git archive "$BASE" amr_ws/src/amr_description | tar -x -C "$TMP/base"
for ARGS in "use_ros2_control:=true" "use_ros2_control:=true use_sensors:=true"; do
  (cd "$TMP/base/amr_ws" && xacro $X $ARGS controllers_file:="$CTRL") > "$TMP/base.urdf"
  (cd amr_ws && xacro $X $ARGS controllers_file:="$CTRL") > "$TMP/now.urdf"
  echo "\$ xacro amr.urdf.xacro $ARGS ($(wc -c < "$TMP/now.urdf") bytes)"
  cmp "$TMP/base.urdf" "$TMP/now.urdf" && echo identical; rc $?
done

# DEC-080 (2026-11-23): sim.launch.py may differ from BASE only by the DEC-075 gui_config option, exactly the lines
# TEST-M7-01 step 7 allows (read from its SIM_EXPECTED block: one list, kept in TEST-M7-01). Any other change fails.
dec075_only() {
  git diff -U0 "$BASE" -- "$1" | grep -E '^-[^-]' > "$TMP/s_rm.txt"
  git diff -U0 "$BASE" -- "$1" | grep -E '^\+[^+]' > "$TMP/s_add.txt"
  sed -n "/<<'SIM_EXPECTED'/,/^SIM_EXPECTED\$/p" docs/evidence/M7/TEST-M7-01_procedure.sh | sed '1d;$d' > "$TMP/s_exp.txt"
  [ -s "$TMP/s_exp.txt" ] && [ ! -s "$TMP/s_rm.txt" ] && cmp -s "$TMP/s_exp.txt" "$TMP/s_add.txt"
}
echo; echo "## 4. Simulation, controller, sensor, SLAM and reference-map files vs $BASE"
FILES="$B/launch/sim.launch.py $B/config/controllers.yaml amr_ws/src/amr_description/urdf/amr.sensors.xacro
amr_ws/src/amr_description/urdf/amr_properties.xacro $B/config/slam_toolbox.yaml $B/launch/slam.launch.py
$B/maps/mapping_arena.yaml $B/maps/mapping_arena.pgm $B/maps/mapping_arena.data.gz $B/maps/mapping_arena.posegraph.gz"
for F in $FILES; do
  if [ -e "$F" ] && git diff --quiet "$BASE" -- "$F"; then echo "unchanged  $F"
  elif [ "${F##*/}" = sim.launch.py ] && dec075_only "$F"; then echo "DEC-075    $F: only the gui_config option added (DEC-080)"
  else echo "CHANGED    $F"; git diff --stat "$BASE" -- "$F"; false; fi; rc $?
done

echo; echo "## 5. Existing files changed in amr_ws/src from $BASE to ${END:-the working tree} (M6 increment, DEC-064)"
git diff --name-status "$BASE" "$END" -- amr_ws/src | tee "$TMP/ns.txt"
MOD=$(grep -v '^A' "$TMP/ns.txt" | awk '{print $2}' | sort | tr '\n' ' ')
echo "# modified or removed (not new): ${MOD:-none}"
[ "$MOD" = "$B/CMakeLists.txt $B/package.xml " ]; rc $?
git diff -U0 "$BASE" "$END" -- $B/package.xml | grep -E '^[+-][^+-]' | tee "$TMP/p.txt"
printf '%s\n' "+  <exec_depend>nav2_map_server</exec_depend>" "+  <exec_depend>nav2_amcl</exec_depend>" \
  "+  <exec_depend>nav2_lifecycle_manager</exec_depend>" "+  <exec_depend>robot_localization</exec_depend>" \
  "+  <exec_depend>nav2_rviz_plugins</exec_depend>" > "$TMP/p_exp.txt"
cmp -s "$TMP/p.txt" "$TMP/p_exp.txt" && echo "package.xml: only the five M6 exec_depend lines added"; rc $?
git diff -U0 "$BASE" "$END" -- $B/CMakeLists.txt | grep -E '^[+-][^+-]' > "$TMP/c.txt"
grep -v -E '^[+-]\s*#' "$TMP/c.txt" > "$TMP/c_code.txt"
cat "$TMP/c_code.txt"
printf '%s\n' "-  DIRECTORY config launch rviz worlds" "+  DIRECTORY config launch maps rviz worlds" > "$TMP/c_exp.txt"
echo "# CMakeLists.txt changed lines: $(wc -l < "$TMP/c.txt"), of which not comments: $(wc -l < "$TMP/c_code.txt")"
cmp -s "$TMP/c_code.txt" "$TMP/c_exp.txt" && echo "CMakeLists.txt: only comments and the maps folder added to the install rule"; rc $?

echo; echo "## 6. AMCL map copy vs the reference map (DEC-062)"
python3 -I - "$B/maps/mapping_arena.yaml" "$B/maps/mapping_arena_amcl.yaml" <<'PY'
import sys, yaml
ref_t, amcl_t = (open(p).read() for p in sys.argv[1:])
ref, amcl = yaml.safe_load(ref_t), yaml.safe_load(amcl_t)
d = [round(a - b, 6) for a, b in zip(amcl['origin'], ref['origin'])]
others = {k: (ref.get(k), amcl.get(k)) for k in set(ref) | set(amcl) if k != 'origin' and ref.get(k) != amcl.get(k)}
body = '\n'.join(l for l in amcl_t.split('\n') if not l.startswith('#'))
textual = body.replace(f"origin: {amcl_t.split('origin: ')[1].split(chr(10))[0]}", f"origin: {ref_t.split('origin: ')[1].split(chr(10))[0]}") == ref_t
print(f'origin reference {ref["origin"]}, AMCL copy {amcl["origin"]}, difference {d}')
print(f'other keys differing: {others or "none"}; text identical apart from comments and origin: {textual}')
sys.exit(0 if d == [0.025, 0.025, 0.0] and not others and textual else 1)
PY
rc $?

echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL STEPS PASSED' || echo 'AT LEAST ONE STEP FAILED')"
} 2>&1 | sed -e "s|$HOME|<home>|g" -e "s|$TMP|<tmp>|g" > "$LOG"
rm -rf "$TMP"
grep -q '# overall: ALL STEPS PASSED' "$LOG"
