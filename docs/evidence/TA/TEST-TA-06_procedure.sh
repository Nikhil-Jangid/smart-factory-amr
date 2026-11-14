#!/usr/bin/env bash
# TEST-TA-06: the geometry-drawing check (tools/geometry_drawing.py --check) passes on the repository
# and fails on a stale drawing and on a parameter-table mismatch. The two negative cases run on a scratch copy
# of only the files the checker reads, so the repository is never modified.
# Usage: bash docs/evidence/TA/TEST-TA-06_procedure.sh   (from the repository root; exit 0 = every case as expected)
set -u
cd "$(git rev-parse --show-toplevel)"
echo "# TEST-TA-06 drawing check; revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- tools docs/design amr_ws/src/amr_description/urdf || echo ' (modified)'); $(date -u +%FT%TZ)"
fails=0
expect() {  # expect <label> <wanted exit code> <dir>
    local out code
    out=$(cd "$3" && python3 -I tools/geometry_drawing.py --check 2>&1); code=$?
    echo "## $1 (expected exit $2)"; echo "$out" | sed 's/^/    /'
    if [ "$code" -eq "$2" ]; then echo "PASS  $1: exit $code"; else echo "FAIL  $1: exit $code, expected $2"; fails=$((fails + 1)); fi
}
expect "repository as committed" 0 .
scratch=$(mktemp -d); trap 'rm -rf "$scratch"' EXIT
copy() { mkdir -p "$scratch/tools" "$scratch/docs/design" "$scratch/amr_ws/src/amr_description/urdf"
         cp tools/geometry_drawing.py "$scratch/tools/"
         cp docs/design/mechanical_geometry.md docs/design/amr_geometry_drawing.svg "$scratch/docs/design/"
         cp amr_ws/src/amr_description/urdf/amr_properties.xacro amr_ws/src/amr_description/urdf/amr.sensors.xacro \
            "$scratch/amr_ws/src/amr_description/urdf/"; }
copy; echo '<!-- hand edit -->' >> "$scratch/docs/design/amr_geometry_drawing.svg"
expect "negative: drawing edited by hand (stale)" 1 "$scratch"
rm -rf "$scratch"/*; copy
sed -i 's/| `wheel_track` | 0.400 m/| `wheel_track` | 0.404 m/' "$scratch/docs/design/mechanical_geometry.md"
expect "negative: section 2 table disagrees with the Xacro (wheel_track 0.404)" 1 "$scratch"
echo "# overall: $([ "$fails" -eq 0 ] && echo PASS || echo FAIL) ($fails unexpected)"
exit $((fails > 0))
