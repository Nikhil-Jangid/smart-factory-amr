#!/usr/bin/env bash
# DEC-080 supporting evidence (2026-11-23): the sim.launch.py allowance in TEST-M5-01 and TEST-M6-01 step 4.
# Usage, from the repository root: bash docs/evidence/M7/DEC-080_scope_check.sh > docs/evidence/M7/DEC-080_scope_check.log
# Loads dec075_only() from each procedure and runs it on the working-tree sim.launch.py (must be allowed against the
# M4 and M5 closeouts) and on three tampered copies (must be rejected): a changed spawn default, an extra comment line,
# one gui_config line missing. Copies are checked with git --work-tree=<temp dir>; the repository is not modified.
# Exit 0 = every case as expected.
set -u
F=amr_ws/src/amr_bringup/launch/sim.launch.py
S=$(mktemp -d); trap 'rm -rf "$S"' EXIT
FAIL=0
echo "# DEC-080 scope check, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)"
for PROC in docs/evidence/M5/TEST-M5-01_procedure.sh docs/evidence/M6/TEST-M6-01_procedure.sh; do
  echo; echo "## $PROC"
  unset -f dec075_only
  eval "$(sed -n '/^dec075_only() {/,/^}/p' "$PROC")"
  declare -F dec075_only > /dev/null || { echo "FAIL  dec075_only not found"; FAIL=1; continue; }
  BASE=$(sed -n 's/^BASE=\${BASE:-\([0-9a-f]*\)}$/\1/p' "$PROC")
  echo "# BASE $BASE"
  mkdir -p "$S/w/${F%/*}" "$S/t"; TMP=$S/t
  if dec075_only "$F"; then echo "PASS  working tree: allowed"; else echo "FAIL  working tree: rejected"; FAIL=1; fi
  for CASE in spawn comment missing; do
    cp "$F" "$S/w/$F"
    case $CASE in
      spawn) sed -i "s/default_value='0.0'/default_value='0.1'/" "$S/w/$F"; D='spawn pose default 0.0 -> 0.1' ;;
      comment) echo '# extra' >> "$S/w/$F"; D='one extra comment line' ;;
      missing) sed -i '/--gui-config., packaged/d' "$S/w/$F"; D='one gui_config line removed' ;;
    esac
    if cmp -s "$F" "$S/w/$F"; then echo "FAIL  $D: tampering had no effect"; FAIL=1; continue; fi
    git() { command git --work-tree="$S/w" "$@"; }
    if dec075_only "$F"; then R=allowed; else R=rejected; fi
    unset -f git
    [ "$R" = rejected ] && echo "PASS  $D: rejected" || { echo "FAIL  $D: allowed"; FAIL=1; }
  done
done
echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL CASES AS EXPECTED' || echo 'AT LEAST ONE CASE WRONG')"
exit $FAIL
