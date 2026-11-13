#!/usr/bin/env bash
# TEST-M1-08: documentation / code consistency review.
# Run from the repository root after `source /opt/ros/jazzy/setup.bash`. Writes:
#   docs/evidence/M1/TEST-M1-08${TAG}_mesh_check.log  element-level <mesh> check (test_plan.md §4 procedure)
#   docs/evidence/M1/TEST-M1-08${TAG}_review.log      regeneration, byte comparison with the committed
#                                                     TEST-M1-02/03 evidence, TEST-M1-03 property check,
#                                                     design-document consistency check, record check
# TAG is empty for the first run and "-R1" for re-test 1 (pass it as the first argument).
# xacro runs in amr_ws/, the shell context assumed by test_plan.md §4 and used by TEST-M1-02:
# xacro writes the invoked path into the URDF header comment, so another working directory gives
# a URDF that differs from the evidence in that comment only (TS-010).
# Exit code: 0 only if every step passed.
set -u
TAG=${1:-}
EV=docs/evidence/M1
LOG=$EV/TEST-M1-08${TAG}_review.log
MESHLOG=TEST-M1-08${TAG}_mesh_check.log
TMP=$(mktemp -d)
FAIL=0
step() { echo; echo "\$ $1"; }
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }

{
echo "# TEST-M1-08 review, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src DIRTY)')"
echo "# xacro $(dpkg-query -W -f='${Version}' ros-jazzy-xacro 2>/dev/null), sdformat $(gz sdf --versions 2>/dev/null | tail -1)"

step "(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro) > <tmp>/amr.urdf"
(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro) > "$TMP/amr.urdf"; rc $?
step "cmp <tmp>/amr.urdf $EV/TEST-M1-02_amr.urdf    # committed generated-URDF evidence is current"
cmp "$TMP/amr.urdf" "$EV/TEST-M1-02_amr.urdf" && echo "identical"; rc $?
step "gz sdf -p <tmp>/amr.urdf > <tmp>/amr.sdf"
gz sdf -p "$TMP/amr.urdf" > "$TMP/amr.sdf"; rc $?
step "cmp <tmp>/amr.sdf $EV/TEST-M1-03_amr.sdf      # committed generated-SDF evidence is current"
cmp "$TMP/amr.sdf" "$EV/TEST-M1-03_amr.sdf" && echo "identical"; rc $?
step "check_urdf <tmp>/amr.urdf"
check_urdf "$TMP/amr.urdf"; rc $?

step "python3 -I $EV/TEST-M1-03_check.py <tmp>/amr.urdf <tmp>/amr.sdf    # per-link inertials (CALC-M1-07 to -10) and lumped SDF (CALC-M1-15)"
python3 -I "$EV/TEST-M1-03_check.py" "$TMP/amr.urdf" "$TMP/amr.sdf"; rc $?
step "python3 -I $EV/TEST-M1-08_consistency_check.py <tmp>/amr.urdf    # design documents vs amr_properties.xacro and the generated URDF"
python3 -I "$EV/TEST-M1-08_consistency_check.py" "$TMP/amr.urdf"; rc $?
step "python3 -I $EV/TEST-M1-08_records_check.py    # test records, statuses, traceability, links, evidence index"
python3 -I "$EV/TEST-M1-08_records_check.py"; rc $?
} > "$LOG" 2>&1

# Element-level mesh check, exactly as specified in docs/testing/test_plan.md §4 (run from amr_ws/).
cp "$TMP/amr.urdf" /tmp/amr.urdf
( cd amr_ws && EV=../docs/evidence/M1 && python3 -I - src/amr_description/urdf/*.xacro /tmp/amr.urdf <<'EOF' | tee $EV/$MESHLOG
import sys, xml.etree.ElementTree as ET
bad = 0
for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    meshes = [m.get('filename') for m in root.iter('mesh')]
    bad += len(meshes)
    print(f'{path}: {len(meshes)} <mesh> elements {meshes}')
sys.exit(1 if bad else 0)
EOF
exit ${PIPESTATUS[0]} ) > /dev/null
MESH=$?
{ echo; echo "\$ <test_plan.md §4 element-level mesh check> -> $EV/$MESHLOG"; cat "$EV/$MESHLOG"; rc $MESH
  echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL STEPS PASSED' || echo 'AT LEAST ONE STEP FAILED')"; } >> "$LOG"
rm -rf "$TMP"
exit $FAIL
