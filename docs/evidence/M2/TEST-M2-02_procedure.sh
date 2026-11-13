#!/usr/bin/env bash
# TEST-M2-02: model regression (default variant) and control description (enabled variant).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Writes docs/evidence/M2/TEST-M2-02${TAG}_review.log (TAG empty for the first run, -R1 for re-test 1, ...).
# xacro runs in amr_ws/ (TS-010). No M1 evidence file is written.
set -u
TAG=${1:-}
EV1=docs/evidence/M1; EV=docs/evidence/M2
LOG=$EV/TEST-M2-02${TAG}_review.log
TMP=$(mktemp -d); FAIL=0
CTRL="$(ros2 pkg prefix amr_bringup)/share/amr_bringup/config/controllers.yaml"
step() { echo; echo "\$ $1"; }
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
mesh() { python3 -I - "$@" <<'PY'
import sys, xml.etree.ElementTree as ET
bad = 0
for p in sys.argv[1:]:
    n = len(list(ET.parse(p).getroot().iter('mesh'))); bad += n; print(f'{p.split("/")[-1]}: {n} <mesh> elements')
sys.exit(1 if bad else 0)
PY
}
{
echo "# TEST-M2-02 review, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src DIRTY)')"
echo "# xacro $(dpkg-query -W -f='${Version}' ros-jazzy-xacro), sdformat $(gz sdf --versions 2>/dev/null | tail -1); controllers file <install>/share/amr_bringup/config/controllers.yaml"
echo; echo "## Default variant (use_ros2_control unset): M1 baseline must be unchanged"
step "(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro) > <tmp>/off.urdf; cmp with $EV1/TEST-M1-02_amr.urdf"
(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro) > "$TMP/off.urdf" && cmp "$TMP/off.urdf" "$EV1/TEST-M1-02_amr.urdf" && echo identical; rc $?
step "gz sdf -p <tmp>/off.urdf > <tmp>/off.sdf; cmp with $EV1/TEST-M1-03_amr.sdf"
gz sdf -p "$TMP/off.urdf" > "$TMP/off.sdf" && cmp "$TMP/off.sdf" "$EV1/TEST-M1-03_amr.sdf" && echo identical; rc $?
step "check_urdf <tmp>/off.urdf"; check_urdf "$TMP/off.urdf"; rc $?
step "python3 -I $EV1/TEST-M1-03_check.py <tmp>/off.urdf <tmp>/off.sdf"; python3 -I "$EV1/TEST-M1-03_check.py" "$TMP/off.urdf" "$TMP/off.sdf"; rc $?
step "python3 -I $EV1/TEST-M1-08_consistency_check.py <tmp>/off.urdf   # expected: only the M1-scope source-file assertion for amr.ros2_control.xacro fails (TS-016)"
python3 -I "$EV1/TEST-M1-08_consistency_check.py" "$TMP/off.urdf" > "$TMP/m108.txt"; cat "$TMP/m108.txt"
N=$(grep -c '^FAIL' "$TMP/m108.txt"); M=$(grep '^FAIL' "$TMP/m108.txt" | grep -c 'amr.ros2_control.xacro: no mesh, gazebo, sensor, plugin, transmission, ros2_control elements')
[ "$N" = 1 ] && [ "$M" = 1 ] && echo "only the expected M1-scope assertion for the M2 file fails"; rc $?
step "mesh check: source Xacro files and <tmp>/off.urdf"; mesh amr_ws/src/amr_description/urdf/*.xacro "$TMP/off.urdf"; rc $?
echo; echo "## Enabled variant (use_ros2_control:=true controllers_file:=<installed controllers.yaml>)"
step "(cd amr_ws && xacro ... use_ros2_control:=true controllers_file:=<ctrl>) > <tmp>/on.urdf; check_urdf"
(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro use_ros2_control:=true controllers_file:="$CTRL") > "$TMP/on.urdf" && check_urdf "$TMP/on.urdf"; rc $?
step "gz sdf -p <tmp>/on.urdf > <tmp>/on.sdf"; gz sdf -p "$TMP/on.urdf" > "$TMP/on.sdf"; rc $?
step "python3 -I $EV1/TEST-M1-03_check.py <tmp>/on.urdf <tmp>/on.sdf   # expected: only the REQ-M1-09/-10 scope assertions and the two M1 cylinder wheel-collision assertions (replaced by DEC-028, TS-019) fail"
python3 -I "$EV1/TEST-M1-03_check.py" "$TMP/on.urdf" "$TMP/on.sdf" > "$TMP/m103.txt"; cat "$TMP/m103.txt"
N=$(grep -c '^FAIL' "$TMP/m103.txt"); M=$(grep '^FAIL' "$TMP/m103.txt" | grep -c -E 'REQ-M1-09|REQ-M1-10|^FAIL  (left|right)_wheel_link collision: cylinder ')
[ "$N" = 4 ] && [ "$M" = 4 ] && echo "only the four expected assertions fail (M1 scope; DEC-028 collision, verified by the M2 control check)"; rc $?
step "python3 -I $EV/TEST-M2-02_control_check.py <tmp>/on.urdf <tmp>/on.sdf <ctrl>"
python3 -I "$EV/TEST-M2-02_control_check.py" "$TMP/on.urdf" "$TMP/on.sdf" "$CTRL"; rc $?
echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL STEPS PASSED' || echo 'AT LEAST ONE STEP FAILED')"
} 2>&1 | sed -e "s|$TMP|<tmp>|g" -e "s|$CTRL|<ctrl>|g" -e "s|$HOME|<home>|g" > "$LOG"
rm -rf "$TMP"
grep -q 'ALL STEPS PASSED' "$LOG"
