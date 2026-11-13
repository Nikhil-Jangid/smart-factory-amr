#!/usr/bin/env bash
# TEST-M4-01: build and configuration regression (REQ-M4-09; docs/testing/test_plan.md §9; M4 Task B).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Usage: bash docs/evidence/M4/TEST-M4-01_procedure.sh [TAG]   -> docs/evidence/M4/TEST-M4-01${TAG}_review.log
# BASE = 30d737f, the last revision before the DEC-042 covariance change (written 2026-11-13 before its formal run).
# Steps:
#  1. colcon build of the three project packages: exit 0, no line matching 'warning'.
#  2. Default model expansion byte-identical to docs/evidence/M1/TEST-M1-02_amr.urdf (M1 baseline).
#  3. M2 enabled expansion (use_ros2_control:=true) byte-identical to the BASE expansion (model unchanged).
#  4. controllers.yaml differs from BASE only by added comment lines and the two covariance keys; nothing removed.
#  5. The two covariance keys equal the accepted CALC-M4-04 values (typed here from the M4 plan §3.3a).
set -u
TAG=${1:-}
BASE=${BASE:-docs/evidence/M4/M4_baseline}   # model package and controllers.yaml as they were before M4
PKGS="amr_description amr_bringup amr_gazebo_plugins"
CFG=amr_ws/src/amr_bringup/config/controllers.yaml
LOG=docs/evidence/M4/TEST-M4-01${TAG}_review.log
X=src/amr_description/urdf/amr.urdf.xacro
TMP=$(mktemp -d); FAIL=0
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
{
echo "# TEST-M4-01 review, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)'); baseline $BASE"

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

echo; echo "## 3. M2 enabled expansion vs $BASE"
mkdir -p "$TMP/base" && cp -r "$BASE/amr_ws" "$TMP/base/"
(cd "$TMP/base/amr_ws" && xacro $X use_ros2_control:=true controllers_file:="$CTRL") > "$TMP/base.urdf"
(cd amr_ws && xacro $X use_ros2_control:=true controllers_file:="$CTRL") > "$TMP/now.urdf"
cmp "$TMP/base.urdf" "$TMP/now.urdf" && echo identical; rc $?

echo; echo "## 4. controllers.yaml vs $BASE"
diff -U0 "$BASE/controllers.yaml" "$CFG" | tee "$TMP/d.txt"
REMOVED=$(grep -c '^-[^-]' "$TMP/d.txt")
OTHER=$(grep '^+[^+]' "$TMP/d.txt" | grep -v -E '^\+\s*#|^\+\s*(pose|twist)_covariance_diagonal:' | wc -l)
ADDED_KEYS=$(grep -c -E '^\+\s*(pose|twist)_covariance_diagonal:' "$TMP/d.txt")
echo "# removed lines: $REMOVED; added non-comment lines other than the covariance keys: $OTHER; covariance keys added: $ADDED_KEYS"
[ "$REMOVED" = 0 ] && [ "$OTHER" = 0 ] && [ "$ADDED_KEYS" = 2 ]; rc $?

echo; echo "## 5. Covariance values vs CALC-M4-04"
python3 - "$CFG" <<'EOF'
import re, sys
txt = open(sys.argv[1]).read()
exp = {'pose_covariance_diagonal': [0.01, 0.01, 1.0e3, 1.0e3, 1.0e3, 0.0158],
       'twist_covariance_diagonal': [2.5e-5, 2.5e-5, 1.0e3, 1.0e3, 1.0e3, 4.0e-4]}
ok = True
for k, v in exp.items():
    m = re.search(rf'^\s*{k}:\s*\[([^\]]*)\]', txt, re.M)
    got = [float(x) for x in m.group(1).split(',')] if m else None
    good = got is not None and len(got) == 6 and all(abs(a - b) <= 1e-12 * max(1.0, abs(b)) for a, b in zip(got, v))
    print(f'{"PASS" if good else "FAIL"}  {k} = {got}, expected {v}')
    ok &= good
sys.exit(0 if ok else 1)
EOF
rc $?

echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL STEPS PASSED' || echo 'AT LEAST ONE STEP FAILED')"
} 2>&1 | sed -e "s|$HOME|<home>|g" -e "s|$TMP|<tmp>|g" > "$LOG"
rm -rf "$TMP"
grep -q '# overall: ALL STEPS PASSED' "$LOG"
