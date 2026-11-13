#!/usr/bin/env bash
# TEST-M4-09: sensitivity of the odometry accuracy tests to injected calibration errors
# (REQ-M4-08; DEC-043; predictions CALC-M4-05 in the M4 plan §3.3b; test_plan.md §9). Written 2026-11-13 before its run.
# Run from the repository root after sourcing /opt/ros/jazzy/setup.bash and amr_ws/install/setup.bash.
# Usage: [SHOW=1] bash docs/evidence/M4/TEST-M4-09_procedure.sh [TAG] [RUNS]
#   -> docs/evidence/M4/TEST-M4-09${TAG}_<case>_review.log per case and TEST-M4-09${TAG}_check.log
# Test-only overrides: each case copies the product controllers.yaml to a temporary file and inserts one or two
# multiplier lines under diff_drive_controller/ros__parameters; the launch loads it with controllers_file:=.
# The product file is never edited; its unchanged state is checked at the end. The exact inserted lines are logged.
#   R: left and right wheel radius multipliers 1.01 -> straight   (TEST-M4-04 profile)
#   B: wheel separation multiplier 1.02            -> rotate     (TEST-M4-05 profile)
#   L: left wheel radius multiplier 1.005          -> square_ccw and square_cw (TEST-M4-06 profiles)
# The accuracy runs are expected to FAIL; TEST-M4-09_check.py decides the test result.
set -u
TAG=${1:-}; RUNS=${2:-3}
EV=docs/evidence/M4
CFG=amr_ws/src/amr_bringup/config/controllers.yaml
TMP=$(mktemp -d)
mk() {  # mk <name> <lines...>: override file with the given parameter lines inserted
  local name=$1; shift
  python3 - "$CFG" "$TMP/$name.yaml" "$@" <<'EOF'
import sys
src, dst, *lines = sys.argv[1:]
out, state = [], 0
for l in open(src).read().split('\n'):
    out.append(l)
    if l == 'diff_drive_controller:':
        state = 1
    elif state == 1 and l.strip() == 'ros__parameters:':
        out += [f'    {x}  # TEST-M4-09 test-only override (DEC-043)' for x in lines]
        state = 2
assert state == 2, 'diff_drive_controller/ros__parameters not found'
open(dst, 'w').write('\n'.join(out))
EOF
}
mk R 'left_wheel_radius_multiplier: 1.01' 'right_wheel_radius_multiplier: 1.01'
mk B 'wheel_separation_multiplier: 1.02'
mk L 'left_wheel_radius_multiplier: 1.005'
for spec in "R straight" "B rotate" "L square_ccw" "L square_cw"; do
  set -- $spec
  LOG=$EV/TEST-M4-09${TAG}_$1_$2_review.log
  CONTROLLERS="$TMP/$1.yaml" bash $EV/TEST-M4_procedure.sh "$2" "$RUNS" "$LOG"
  { echo; echo "# TEST-M4-09 case $1 ($2): override lines inserted into a copy of controllers.yaml:"
    diff "$CFG" "$TMP/$1.yaml" | sed 's/^/#   /'; } >> "$LOG"
  sed -i "s|$TMP|<tmp>|g" "$LOG"
done
{ echo "# product controllers.yaml unchanged by the test: $(git diff --quiet HEAD -- "$CFG" && echo yes || echo NO)"; } \
  > "$TMP/product.txt"
python3 -I $EV/TEST-M4-09_check.py "$TAG" "$(cat "$TMP/product.txt")" > "$EV/TEST-M4-09${TAG}_check.log" 2>&1
RC=$?
cat "$EV/TEST-M4-09${TAG}_check.log"
rm -rf "$TMP"
exit $RC
