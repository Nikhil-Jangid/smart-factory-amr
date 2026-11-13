#!/usr/bin/env bash
# TEST-M3-01: build of the M3 packages (REQ-M3-01; docs/testing/test_plan.md §7.2).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash`.
# Writes docs/evidence/M3/TEST-M3-01${TAG}_build.log (TAG empty for the first run, -R1 for re-test 1, ...).
# Pass: colcon exits 0 and its output contains no warning for amr_description or amr_bringup.
# Changed for re-test 2 (DEC-038), before that run: the build also selects amr_gazebo_plugins, and
# the pass condition adds the installed plugin library and its GZ_SIM_SYSTEM_PLUGIN_PATH environment hook.
# CLEAN=1 first removes amr_ws/build and amr_ws/install (generated, git-ignored), for a build from scratch.
# The unit tests of amr_gazebo_plugins are TEST-M3-13 (TEST-M3-13_procedure.sh).
set -u
TAG=${1:-}
PKGS="amr_description amr_bringup amr_gazebo_plugins"
PLUGIN=amr_ws/install/amr_gazebo_plugins/lib/libamr_imu_decimator_system.so
HOOK=amr_ws/install/amr_gazebo_plugins/share/amr_gazebo_plugins/environment/amr_gazebo_plugins.dsv
LOG=docs/evidence/M3/TEST-M3-01${TAG}_build.log
TMP=$(mktemp -d)
{
echo "# TEST-M3-01 build, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
# The installed colcon-core version is read locally (TS-037: `colcon version-check` queries PyPI and hung on a
# stalled connection, 10 min and then 30 s with a timeout, 2026-11-13). Informational only; no criterion reads it.
echo "# colcon-core $(python3 -c 'import colcon_core; print(colcon_core.__version__)' 2>/dev/null), ROS_DISTRO=$ROS_DISTRO"
if [ "${CLEAN:-0}" = 1 ]; then echo; echo '$ rm -rf amr_ws/build amr_ws/install   # CLEAN=1: build from scratch'; rm -rf amr_ws/build amr_ws/install; fi
echo
echo "\$ cd amr_ws && colcon build --symlink-install --packages-select $PKGS --event-handlers console_direct+"
(cd amr_ws && colcon build --symlink-install --packages-select $PKGS --event-handlers console_direct+) > "$TMP/build.txt" 2>&1
RC=$?
cat "$TMP/build.txt"
echo "# colcon exit $RC"
W=$(grep -i -c -E 'warning|warn:' "$TMP/build.txt")
echo "# lines matching 'warning' (case-insensitive): $W"
[ "$W" = 0 ] || grep -i -n -E 'warning|warn:' "$TMP/build.txt"
echo "# installed sensors file: $(ls amr_ws/install/amr_description/share/amr_description/urdf/amr.sensors.xacro 2>/dev/null || echo MISSING)"
echo "# installed plugin: $(ls "$PLUGIN" 2>/dev/null || echo MISSING); environment hook: $(cat "$HOOK" 2>/dev/null || echo MISSING)"
[ "$RC" = 0 ] && [ "$W" = 0 ] && [ -e amr_ws/install/amr_description/share/amr_description/urdf/amr.sensors.xacro ] \
  && [ -e "$PLUGIN" ] && grep -q '^prepend-non-duplicate;GZ_SIM_SYSTEM_PLUGIN_PATH;lib$' "$HOOK" 2>/dev/null \
  && echo "# overall: PASS (exit 0, no warnings, amr.sensors.xacro, plugin and environment hook installed)" || echo "# overall: FAIL"
} 2>&1 | sed -e "s|$HOME|<home>|g" > "$LOG"
rm -rf "$TMP"
grep -q '# overall: PASS' "$LOG"
