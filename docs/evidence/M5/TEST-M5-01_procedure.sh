#!/usr/bin/env bash
# TEST-M5-01: build and regression identity (REQ-M5-09; docs/testing/test_plan.md §10; M5 Task A).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Usage: bash docs/evidence/M5/TEST-M5-01_procedure.sh [TAG]   -> docs/evidence/M5/TEST-M5-01${TAG}_review.log
# BASE = 517608f, the M4 closeout commit (M4 complete, finalized 2026-11-13).
# Steps:
#  1. colcon build of the three project packages: exit 0, no line matching 'warning'.
#  2. Default model expansion byte-identical to docs/evidence/M1/TEST-M1-02_amr.urdf (M1 baseline).
#  3. Expansions with use_ros2_control:=true and with use_ros2_control:=true use_sensors:=true (the M2 and M3/M5
#     launch models) byte-identical to the BASE expansions: M5 does not change the robot.
#  4. sim.launch.py, controllers.yaml, amr.sensors.xacro and amr_properties.xacro unchanged since BASE (git diff empty);
#     sim.launch.py may add exactly the DEC-075 gui_config lines listed in TEST-M7-01 step 7 (DEC-080, 2026-11-23).
#  5. Existing files changed in amr_ws/src since BASE: only amr_bringup/package.xml (exactly one added line,
#     <exec_depend>slam_toolbox</exec_depend>) and amr_bringup/CMakeLists.txt (comment lines only). Every other change
#     is a new file (M5 plan §12: "only new files" read as "no behavioural change to existing files").
#     Compared BASE -> END, END = 9b85171, the M5 closeout commit (DEC-064, 2026-11-20): this step checks M5's own
#     increment; later milestones' changes are checked by their own identity tests (TEST-M6-01 from 9b85171). Before
#     DEC-064 the step compared BASE with the working tree and failed on M6's approved additions (TS-049).
set -u
TAG=${1:-}
BASE=${BASE:-517608f}
END=${END:-9b85171}
PKGS="amr_description amr_bringup amr_gazebo_plugins"
LOG=docs/evidence/M5/TEST-M5-01${TAG}_review.log
X=src/amr_description/urdf/amr.urdf.xacro
TMP=$(mktemp -d); FAIL=0
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
{
echo "# TEST-M5-01 review, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)'); baseline $BASE"

echo; echo "## 1. Build"
echo "\$ cd amr_ws && colcon build --symlink-install --packages-select $PKGS"
(cd amr_ws && colcon build --symlink-install --packages-select $PKGS --event-handlers console_direct+) > "$TMP/build.txt" 2>&1
B=$?
tail -5 "$TMP/build.txt"
W=$(grep -i -c -E 'warning|warn:' "$TMP/build.txt")
echo "# colcon exit $B; lines matching 'warning': $W"
[ "$B" = 0 ] && [ "$W" = 0 ]; rc $?
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
echo; echo "## 4. Simulation, controller and sensor files vs $BASE"
FILES="amr_ws/src/amr_bringup/launch/sim.launch.py amr_ws/src/amr_bringup/config/controllers.yaml
amr_ws/src/amr_description/urdf/amr.sensors.xacro amr_ws/src/amr_description/urdf/amr_properties.xacro"
for F in $FILES; do
  if git diff --quiet "$BASE" -- "$F"; then echo "unchanged  $F"
  elif [ "${F##*/}" = sim.launch.py ] && dec075_only "$F"; then echo "DEC-075    $F: only the gui_config option added (DEC-080)"
  else echo "CHANGED    $F"; git diff "$BASE" -- "$F"; false; fi; rc $?
done

echo; echo "## 5. Existing files changed in amr_ws/src from $BASE to $END (M5 increment, DEC-064)"
git diff --name-status "$BASE" "$END" -- amr_ws/src | tee "$TMP/ns.txt"
MOD=$(grep -v '^A' "$TMP/ns.txt" | awk '{print $2}' | sort | tr '\n' ' ')
echo "# modified or removed (not new): ${MOD:-none}"
[ "$MOD" = "amr_ws/src/amr_bringup/CMakeLists.txt amr_ws/src/amr_bringup/package.xml " ]; rc $?
git diff -U0 "$BASE" "$END" -- amr_ws/src/amr_bringup/package.xml | grep -E '^[+-][^+-]' | tee "$TMP/p.txt"
[ "$(cat "$TMP/p.txt")" = "+  <exec_depend>slam_toolbox</exec_depend>" ] && echo "package.xml: only the slam_toolbox exec_depend added"; rc $?
git diff -U0 "$BASE" "$END" -- amr_ws/src/amr_bringup/CMakeLists.txt | grep -E '^[+-][^+-]' > "$TMP/c.txt"
NONCOMMENT=$(grep -v -E '^[+-]\s*#' "$TMP/c.txt" | wc -l)
echo "# CMakeLists.txt changed lines: $(wc -l < "$TMP/c.txt"), of which not comments: $NONCOMMENT"
[ "$NONCOMMENT" = 0 ]; rc $?

echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL STEPS PASSED' || echo 'AT LEAST ONE STEP FAILED')"
} 2>&1 | sed -e "s|$HOME|<home>|g" -e "s|$TMP|<tmp>|g" > "$LOG"
rm -rf "$TMP"
grep -q '# overall: ALL STEPS PASSED' "$LOG"
