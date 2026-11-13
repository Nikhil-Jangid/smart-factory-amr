#!/usr/bin/env bash
# TEST-M3-13: unit tests of the DEC-038 IMU block averager (REQ-M3-15; docs/testing/test_plan.md §7.3).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash`, after TEST-M3-01 (the package is built).
# Writes docs/evidence/M3/TEST-M3-13${TAG}_unit.log (TAG empty for the first run).
# Steps: `colcon test` for amr_gazebo_plugins (gtest test_imu_block_averager), `colcon test-result --verbose`, and
# the gtest binary once more with its per-case listing for the record.
# Pass: colcon test exit 0, test-result exit 0 with 0 failures and 0 errors, every gtest case OK, 13 cases.
set -u
TAG=${1:-}
LOG=docs/evidence/M3/TEST-M3-13${TAG}_unit.log
TMP=$(mktemp -d); FAIL=0
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
{
echo "# TEST-M3-13 unit tests, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# $(gcc --version | head -1), gtest from ament_cmake_gtest $(dpkg-query -W -f='${Version}' ros-jazzy-ament-cmake-gtest)"
echo; echo '$ cd amr_ws && colcon test --packages-select amr_gazebo_plugins --event-handlers console_direct+'
(cd amr_ws && colcon test --packages-select amr_gazebo_plugins --event-handlers console_direct+) > "$TMP/test.txt" 2>&1
RC=$?; grep -E '^\s*[0-9]+/[0-9]+ Test|tests passed|tests failed|Total Test time' "$TMP/test.txt"; rc $RC
echo; echo '$ cd amr_ws && colcon test-result --verbose --test-result-base build/amr_gazebo_plugins'
(cd amr_ws && colcon test-result --verbose --test-result-base build/amr_gazebo_plugins); rc $?
echo; echo '$ amr_ws/build/amr_gazebo_plugins/test_imu_block_averager'
amr_ws/build/amr_gazebo_plugins/test_imu_block_averager > "$TMP/gtest.txt" 2>&1; RG=$?
grep -E '^\[ +(OK|FAILED|PASSED) +\]|^\[==========\]' "$TMP/gtest.txt"
grep -E -B2 -A6 'Failure' "$TMP/gtest.txt"
rc $RG
N=$(grep -c -E '^\[ +OK \]' "$TMP/gtest.txt"); F=$(grep -c -E '^\[ +FAILED +\] [A-Za-z]' "$TMP/gtest.txt")
echo "# gtest cases OK: $N, failed: $F (expected 13 OK, 0 failed)"
[ "$N" = 13 ] && [ "$F" = 0 ]; rc $?
echo; echo "# overall: $([ $FAIL = 0 ] && echo PASS || echo FAIL)"
} 2>&1 | sed -e "s|$HOME|<home>|g" > "$LOG"
rm -rf "$TMP"
grep -q '# overall: PASS' "$LOG"
