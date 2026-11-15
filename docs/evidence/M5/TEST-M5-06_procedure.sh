#!/usr/bin/env bash
# TEST-M5-06 robustness to odometry error (REQ-M5-07; M5 Task D). Gazebo.
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   [SHOW=1 LAYOUT_FLAG=<f>] bash docs/evidence/M5/TEST-M5-06_procedure.sh <valid runs> <output log>
# TEST-M5-03/-04 repeated with the TEST-M4-09 odometry errors injected (DEC-043 test-only overrides): the product
# controllers.yaml is copied to a temporary file with three lines added under diff_drive_controller/ros__parameters,
#   wheel_separation_multiplier: 1.02, left_wheel_radius_multiplier: 1.01, right_wheel_radius_multiplier: 1.01,
# and the mapping procedure TEST-M5_procedure.sh runs with CONTROLLERS=<that file> (its log shows the diff). The
# product file is not changed (checked before and after). The route follower steers on ground truth, so the robot
# drives the same route as in TEST-M5-03 while the odometry drifts.
# Criteria per valid attempt: the map and SLAM-pose criteria of TEST-M5-03/-04 (in the mapping procedure), and the
# odometry drift at the end > 3 x the pose bound and within +/- 25 % of CALC-M5-04 (TEST-M5-06_drift_check.py).
# The drift check is appended to the mapping log; its last line is the overall line the runner reads. Exit 0 only if
# both pass.
set -u
RUNS=$1; OUT=$2
EV=docs/evidence/M5
CFG=amr_ws/src/amr_bringup/config/controllers.yaml
TMP=$(mktemp -d)
SUM0=$(sha256sum "$CFG" | cut -c1-64)
python3 - "$CFG" "$TMP/controllers_m5-06.yaml" <<'EOF'
import sys
src, dst = sys.argv[1:]
lines = ['wheel_separation_multiplier: 1.02', 'left_wheel_radius_multiplier: 1.01', 'right_wheel_radius_multiplier: 1.01']
out, state = [], 0
for l in open(src).read().split('\n'):
    out.append(l)
    if l == 'diff_drive_controller:':
        state = 1
    elif state == 1 and l.strip() == 'ros__parameters:':
        out += [f'    {x}  # TEST-M5-06 test-only override (TEST-M4-09 values, DEC-043)' for x in lines]
        state = 2
assert state == 2, 'diff_drive_controller/ros__parameters not found'
open(dst, 'w').write('\n'.join(out))
EOF
CONTROLLERS="$TMP/controllers_m5-06.yaml" bash "$EV/TEST-M5_procedure.sh" "$RUNS" "$OUT"; MAP=$?
{
  echo
  echo "# mapping procedure exit $MAP"
  echo "\$ python3 -I $EV/TEST-M5-06_drift_check.py $OUT"
  python3 -I "$EV/TEST-M5-06_drift_check.py" "$OUT"; DR=$?
  echo "# drift check exit $DR"
  [ "$(sha256sum "$CFG" | cut -c1-64)" = "$SUM0" ] && echo "# product controllers.yaml unchanged" || { echo "# product controllers.yaml CHANGED"; DR=1; }
  echo "# overall: TEST-M5-06 $([ "$MAP" = 0 ] && [ "$DR" = 0 ] && echo 'MAPPING AND DRIFT CHECKS PASSED' || echo 'AT LEAST ONE CHECK FAILED')"
} >> "$OUT" 2>&1
sed -i -e "s|$TMP|<tmp>|g" "$OUT"
rm -rf "$TMP"
grep -q '^# overall: TEST-M5-06 MAPPING AND DRIFT CHECKS PASSED' "$OUT"
