#!/usr/bin/env bash
# TEST-M3-02: model regression with the use_sensors option (REQ-M3-02, DEC-034; docs/testing/test_plan.md §7.2).
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`.
# Writes docs/evidence/M3/TEST-M3-02${TAG}_review.log (TAG empty for the first run, -R1 for re-test 1, ...).
# xacro always runs inside a workspace with the relative path (TS-010). No older evidence file is written.
# BASE is the last revision before M3 Task A; its M2 expansion is the "M2 enabled expansion unchanged" reference.
#
# Expected M1/M2-scope assertion failures, declared before the formal run (TS-016 precedent; TS-023):
#  - TEST-M1-08 checker on the default URDF: only the source-file assertion "no mesh, gazebo, sensor, plugin,
#    transmission, ros2_control elements" for amr.ros2_control.xacro (TS-016) and amr.sensors.xacro (TS-023).
#  - TEST-M2-02 control check on the sensors-on M2 URDF: only "6 links / 5 joints" and "no <sensor> elements".
#    The same check must pass completely on the sensors-off M2 URDF.
set -u
TAG=${1:-}
BASE=${BASE:-docs/evidence/M2/M2_baseline}   # the M2 model package as it was at the M2 closeout
EV1=docs/evidence/M1; EV2=docs/evidence/M2; EV=docs/evidence/M3
LOG=$EV/TEST-M3-02${TAG}_review.log
TMP=$(mktemp -d); FAIL=0
CTRL="$(ros2 pkg prefix amr_bringup)/share/amr_bringup/config/controllers.yaml"
X=src/amr_description/urdf/amr.urdf.xacro
step() { echo; echo "\$ $1"; }
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
{
echo "# TEST-M3-02 review, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)'); baseline revision $BASE"
echo "# xacro $(dpkg-query -W -f='${Version}' ros-jazzy-xacro), $(gz sim --version | head -1); controllers file <ctrl> = <install>/share/amr_bringup/config/controllers.yaml"

echo; echo "## 1. Default variant (use_sensors and use_ros2_control unset): M1 baseline unchanged"
step "(cd amr_ws && xacro $X) > <tmp>/off.urdf; cmp with $EV1/TEST-M1-02_amr.urdf"
(cd amr_ws && xacro $X) > "$TMP/off.urdf" && cmp "$TMP/off.urdf" "$EV1/TEST-M1-02_amr.urdf" && echo identical; rc $?
sha256sum "$TMP/off.urdf" "$EV1/TEST-M1-02_amr.urdf"
step "(cd amr_ws && xacro $X use_sensors:=false) > <tmp>/off_explicit.urdf; cmp with $EV1/TEST-M1-02_amr.urdf"
(cd amr_ws && xacro $X use_sensors:=false) > "$TMP/off_explicit.urdf" && cmp "$TMP/off_explicit.urdf" "$EV1/TEST-M1-02_amr.urdf" && echo identical; rc $?
step "gz sdf -p <tmp>/off.urdf > <tmp>/off.sdf; cmp with $EV1/TEST-M1-03_amr.sdf"
gz sdf -p "$TMP/off.urdf" > "$TMP/off.sdf" && cmp "$TMP/off.sdf" "$EV1/TEST-M1-03_amr.sdf" && echo identical; rc $?
step "check_urdf <tmp>/off.urdf"; check_urdf "$TMP/off.urdf"; rc $?
step "python3 -I $EV1/TEST-M1-03_check.py <tmp>/off.urdf <tmp>/off.sdf"; python3 -I "$EV1/TEST-M1-03_check.py" "$TMP/off.urdf" "$TMP/off.sdf"; rc $?
step "python3 -I $EV1/TEST-M1-08_consistency_check.py <tmp>/off.urdf   # expected: only the M1-scope source-file assertion fails, for amr.ros2_control.xacro (TS-016) and amr.sensors.xacro (TS-023)"
python3 -I "$EV1/TEST-M1-08_consistency_check.py" "$TMP/off.urdf" > "$TMP/m108.txt"; cat "$TMP/m108.txt"
N=$(grep -c '^FAIL' "$TMP/m108.txt")
M=$(grep '^FAIL' "$TMP/m108.txt" | grep -c -E 'urdf/amr\.(ros2_control|sensors)\.xacro: no mesh, gazebo, sensor, plugin, transmission, ros2_control elements')
[ "$N" = 2 ] && [ "$M" = 2 ] && echo "only the two expected M1-scope source-file assertions fail"; rc $?

echo; echo "## 2. M2 enabled variant (use_ros2_control:=true), sensors off: unchanged from baseline $BASE"
step "cp -r $BASE/amr_ws <tmp>/base/; xacro there and here with use_ros2_control:=true controllers_file:=<ctrl>; cmp"
mkdir -p "$TMP/base" && cp -r "$BASE/amr_ws" "$TMP/base/"
(cd "$TMP/base/amr_ws" && xacro $X use_ros2_control:=true controllers_file:="$CTRL") > "$TMP/m2_base.urdf"
(cd amr_ws && xacro $X use_ros2_control:=true controllers_file:="$CTRL") > "$TMP/m2.urdf" && cmp "$TMP/m2.urdf" "$TMP/m2_base.urdf" && echo identical; rc $?
sha256sum "$TMP/m2.urdf" "$TMP/m2_base.urdf"
step "check_urdf <tmp>/m2.urdf; gz sdf -p <tmp>/m2.urdf > <tmp>/m2.sdf"
check_urdf "$TMP/m2.urdf" && gz sdf -p "$TMP/m2.urdf" > "$TMP/m2.sdf"; rc $?
step "python3 -I $EV2/TEST-M2-02_control_check.py <tmp>/m2.urdf <tmp>/m2.sdf <ctrl>   # must pass completely"
python3 -I "$EV2/TEST-M2-02_control_check.py" "$TMP/m2.urdf" "$TMP/m2.sdf" "$CTRL"; rc $?

echo; echo "## 3. Sensors on: use_sensors:=true (s1) and use_ros2_control:=true use_sensors:=true (s2, the M3 simulation model)"
step "(cd amr_ws && xacro $X use_sensors:=true) > <tmp>/s1.urdf; check_urdf"
(cd amr_ws && xacro $X use_sensors:=true) > "$TMP/s1.urdf" && check_urdf "$TMP/s1.urdf"; rc $?
step "(cd amr_ws && xacro $X use_ros2_control:=true controllers_file:=<ctrl> use_sensors:=true) > <tmp>/s2.urdf; check_urdf"
(cd amr_ws && xacro $X use_ros2_control:=true controllers_file:="$CTRL" use_sensors:=true) > "$TMP/s2.urdf" && check_urdf "$TMP/s2.urdf"; rc $?
for v in s1 s2; do
  step "gz sdf -p <tmp>/$v.urdf > <tmp>/$v.sdf   # stderr shown; the <gz_frame_id> warnings are expected (sensors.md §6.1)"
  gz sdf -p "$TMP/$v.urdf" > "$TMP/$v.sdf" 2> "$TMP/$v.err"; R=$?; sed 's/\x1b\[[0-9;]*m//g' "$TMP/$v.err"
  U=$(sed 's/\x1b\[[0-9;]*m//g' "$TMP/$v.err" | grep -v -c 'XML Element\[gz_frame_id\], child of element\[sensor\], not defined in SDF')
  echo "# stderr lines other than the expected gz_frame_id warnings: $U"
  [ "$R" = 0 ] && [ "$U" = 0 ]; rc $?
done
step "python3 -I $EV2/TEST-M2-02_control_check.py <tmp>/s2.urdf <tmp>/s2.sdf <ctrl>   # expected: only '6 links / 5 joints' and 'no <sensor> elements' fail (M2 scope; TS-023)"
python3 -I "$EV2/TEST-M2-02_control_check.py" "$TMP/s2.urdf" "$TMP/s2.sdf" "$CTRL" > "$TMP/m202.txt"; cat "$TMP/m202.txt"
N=$(grep -c '^FAIL' "$TMP/m202.txt")
M=$(grep '^FAIL' "$TMP/m202.txt" | grep -c -E '^FAIL  (6 links / 5 joints \(M1 tree unchanged\)|no <sensor> elements \(no active sensors in M2\))')
[ "$N" = 2 ] && [ "$M" = 2 ] && echo "only the two expected M2-scope assertions fail"; rc $?
step "python3 -I $EV/TEST-M3-02_model_check.py <tmp>/off.urdf <tmp>/s1.urdf <tmp>/m2.urdf <tmp>/s2.urdf <tmp>/s1.sdf <tmp>/s2.sdf <tmp>/m2.sdf"
python3 -I "$EV/TEST-M3-02_model_check.py" "$TMP/off.urdf" "$TMP/s1.urdf" "$TMP/m2.urdf" "$TMP/s2.urdf" "$TMP/s1.sdf" "$TMP/s2.sdf" "$TMP/m2.sdf"; rc $?

echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL STEPS PASSED' || echo 'AT LEAST ONE STEP FAILED')"
} 2>&1 | sed -e "s|$TMP|<tmp>|g" -e "s|$CTRL|<ctrl>|g" -e "s|$HOME|<home>|g" > "$LOG"
rm -rf "$TMP"
grep -q 'ALL STEPS PASSED' "$LOG"
