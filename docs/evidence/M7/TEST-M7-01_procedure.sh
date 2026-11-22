#!/usr/bin/env bash
# TEST-M7-01: build and regression identity (REQ-M7-11; docs/testing/test_plan.md §12; M7 Task A).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Usage: bash docs/evidence/M7/TEST-M7-01_procedure.sh [TAG]   -> docs/evidence/M7/TEST-M7-01${TAG}_review.log
# BASE = 9777615, the M6 closeout commit (M6 complete; finalized -11-21; DEC-064).
# Steps:
#  1. colcon build of the three project packages: exit 0, no line matching 'warning'.
#  2. Default model expansion byte-identical to docs/evidence/M1/TEST-M1-02_amr.urdf (M1 baseline).
#  3. Expansions with use_ros2_control:=true and with use_ros2_control:=true use_sensors:=true (the M2 and M3-M6
#     launch models) byte-identical to the BASE expansions: M7 does not change the robot.
#  4. The simulation, controller, sensor, SLAM, localization and map files unchanged since BASE (git diff empty):
#     cmd_vel_guard.cpp (DEC-029), sensor_bridge.yaml, controllers.yaml, controllers_ekf.yaml,
#     amr.sensors.xacro, amr_properties.xacro, mapping_arena.sdf, slam_toolbox.yaml, slam.launch.py,
#     localization.launch.py, amcl.yaml, ekf.yaml and the five map files.
#  5. Existing files changed in amr_ws/src from BASE to END: only amr_bringup/package.xml (exactly the seven added
#     exec_depend lines of M7 plan §6), amr_bringup/CMakeLists.txt (comment lines and the install rule gaining the
#     behavior_trees folder) and launch/sim.launch.py (step 7). Every other change is a new file (M7 plan §6: navigation runs beside the unchanged
#     simulation and localization, DEC-066).
#  6. The two behavior trees equal the installed Nav2 trees they copy, apart from their header comment and the removed
#     Spin and BackUp lines (DEC-071).
#  7. sim.launch.py (DEC-075, 2026-11-21; was in step 4 until then): its diff from BASE removes no line and adds exactly
#     the 12 lines of the optional gui_config argument (docstring, argument, and the --gui-config branch, which is
#     taken only when the argument is set), so with the default the gz sim command is the M2-M6 one.
set -u
TAG=${1:-}
BASE=${BASE:-9777615}
# END: empty = the working tree (M7 in progress). At M7 closeout it is pinned to the closeout commit (DEC-064), so
# step 5 checks only M7's own increment.
END=${END:-}
PKGS="amr_description amr_bringup amr_gazebo_plugins"
LOG=docs/evidence/M7/TEST-M7-01${TAG}_review.log
X=src/amr_description/urdf/amr.urdf.xacro
B=amr_ws/src/amr_bringup
BT_SRC=/opt/ros/jazzy/share/nav2_bt_navigator/behavior_trees
TMP=$(mktemp -d); FAIL=0
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
{
echo "# TEST-M7-01 review, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)'); baseline $BASE"
echo "# nav2_bt_navigator $(dpkg-query -W -f='${Version}' ros-jazzy-nav2-bt-navigator)"

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

echo; echo "## 4. Simulation, controller, sensor, SLAM, localization and map files vs $BASE"
FILES="$B/src/cmd_vel_guard.cpp $B/config/sensor_bridge.yaml $B/config/controllers.yaml
$B/config/controllers_ekf.yaml $B/worlds/mapping_arena.sdf
amr_ws/src/amr_description/urdf/amr.sensors.xacro amr_ws/src/amr_description/urdf/amr_properties.xacro
$B/config/slam_toolbox.yaml $B/launch/slam.launch.py $B/launch/localization.launch.py $B/config/amcl.yaml
$B/config/ekf.yaml $B/maps/mapping_arena.yaml $B/maps/mapping_arena.pgm $B/maps/mapping_arena.data.gz
$B/maps/mapping_arena.posegraph.gz $B/maps/mapping_arena_amcl.yaml"
for F in $FILES; do
  if [ -e "$F" ] && git diff --quiet "$BASE" -- "$F"; then echo "unchanged  $F"; else echo "CHANGED    $F"; git diff --stat "$BASE" -- "$F"; false; fi; rc $?
done

echo; echo "## 5. Existing files changed in amr_ws/src from $BASE to ${END:-the working tree} (M7 increment, DEC-064)"
git diff --name-status "$BASE" $END -- amr_ws/src | tee "$TMP/ns.txt"
[ -z "$END" ] && git ls-files --others --exclude-standard amr_ws/src | sed 's/^/?\t/' | tee -a "$TMP/ns.txt"
MOD=$(grep -v -E '^(A|\?)' "$TMP/ns.txt" | awk '{print $2}' | sort | tr '\n' ' ')
echo "# modified or removed (not new): ${MOD:-none}"
[ "$MOD" = "$B/CMakeLists.txt $B/launch/sim.launch.py $B/package.xml " ]; rc $?
git diff -U0 "$BASE" $END -- $B/package.xml | grep -E '^[+-][^+-]' | tee "$TMP/p.txt"
for D in nav2_planner nav2_controller nav2_behaviors nav2_bt_navigator nav2_velocity_smoother nav2_navfn_planner \
  nav2_regulated_pure_pursuit_controller; do echo "+  <exec_depend>$D</exec_depend>"; done > "$TMP/p_exp.txt"
cmp -s "$TMP/p.txt" "$TMP/p_exp.txt" && echo "package.xml: only the seven M7 exec_depend lines added"; rc $?
git diff -U0 "$BASE" $END -- $B/CMakeLists.txt | grep -E '^[+-][^+-]' > "$TMP/c.txt"
grep -v -E '^[+-]\s*#' "$TMP/c.txt" > "$TMP/c_code.txt"
cat "$TMP/c_code.txt"
printf '%s\n' "-  DIRECTORY config launch maps rviz worlds" "+  DIRECTORY behavior_trees config launch maps rviz worlds" > "$TMP/c_exp.txt"
echo "# CMakeLists.txt changed lines: $(wc -l < "$TMP/c.txt"), of which not comments: $(wc -l < "$TMP/c_code.txt")"
cmp -s "$TMP/c_code.txt" "$TMP/c_exp.txt" && echo "CMakeLists.txt: only comments and the behavior_trees folder added to the install rule"; rc $?

echo; echo "## 6. Behavior trees vs the installed Nav2 trees (DEC-071)"
for N in navigate_to_pose navigate_through_poses; do
  S="$BT_SRC/${N}_w_replanning_and_recovery.xml"
  REMOVED=$(grep -c -E '<(Spin|BackUp) ' "$S")
  echo "\$ diff <(installed $N tree without its comment, Spin and BackUp lines) <($N.xml without its comment)"
  diff <(grep -v -e '<Spin ' -e '<BackUp ' "$S" | sed '1,/-->/d') <(sed '1,/-->/d' "$B/behavior_trees/$N.xml") \
    && ! sed '1,/-->/d' "$B/behavior_trees/$N.xml" | grep -q -E '<(Spin|BackUp) ' \
    && echo "identical apart from the comment; installed lines removed: $REMOVED (Spin, BackUp)"
  rc $?
done

echo; echo "## 7. sim.launch.py vs $BASE: only the DEC-075 gui_config option added"
git diff -U0 "$BASE" $END -- $B/launch/sim.launch.py | grep -E '^-[^-]' > "$TMP/s_rm.txt"
git diff -U0 "$BASE" $END -- $B/launch/sim.launch.py | grep -E '^\+[^+]' > "$TMP/s_add.txt"
cat > "$TMP/s_exp.txt" <<'SIM_EXPECTED'
+M7 option (DEC-075; screen recordings only): gui_config:=<file> starts the Gazebo GUI with that layout
+(`gz sim --gui-config`). A bare name is resolved in this package's config/ directory, e.g.
+gui_config:=gazebo_gui_capture.config (no side panels, 960 x 1000 px). Default empty: the command is unchanged
+(`gz sim -r [-s] <world>`) and Gazebo loads the user's own GUI layout. Ignored with headless:=true.
+    gui_config = LaunchConfiguration('gui_config').perform(context)
+    if gui_config and not is_true(context, 'headless'):  # DEC-075: recordings only; default leaves cmd unchanged
+        packaged = os.path.join(get_package_share_directory('amr_bringup'), 'config', gui_config)
+        cmd += ['--gui-config', packaged if os.path.isfile(packaged) else gui_config]
+    args += [DeclareLaunchArgument('gui_config', default_value='',
+                                   description='Gazebo GUI layout file for screen recordings (DEC-075): a file in '
+                                               'amr_bringup/config (e.g. gazebo_gui_capture.config) or a path; '
+                                               'default empty = the user\'s own layout, command unchanged')]
SIM_EXPECTED
echo "# lines removed: $(wc -l < "$TMP/s_rm.txt"); lines added: $(wc -l < "$TMP/s_add.txt") (expected 0 and $(wc -l < "$TMP/s_exp.txt"))"
diff "$TMP/s_exp.txt" "$TMP/s_add.txt" && [ ! -s "$TMP/s_rm.txt" ] && echo "sim.launch.py: only the gui_config option added"; rc $?

echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL STEPS PASSED' || echo 'AT LEAST ONE STEP FAILED')"
} 2>&1 | sed -e "s|$HOME|<home>|g" -e "s|$TMP|<tmp>|g" > "$LOG"
rm -rf "$TMP"
grep -q '# overall: ALL STEPS PASSED' "$LOG"
