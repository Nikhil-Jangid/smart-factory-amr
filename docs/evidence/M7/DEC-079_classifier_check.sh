#!/usr/bin/env bash
# DEC-079 classifier check (TS-039): run from the repository root, `bash docs/evidence/M7/DEC-079_classifier_check.sh`.
# 1. Every launch log kept in the repository gets the same class from the classifier before DEC-079 (revision b8fc601)
#    and after it, except the TEST-M7-05 attempt-3 log the change was made for.
# 2. That log (TS-039, GUI front end) classifies as TS-039 (exit 4).
# 3. Six near-miss copies of it classify as OTHER (exit 1): no front-end marks, server-only `gz sim -s`, exit code 2,
#    an added SIGTERM -> SIGKILL escalation, an [ERROR] from another process, the marks printed by another process.
# Exit 0 if all hold.
set -u
C=docs/evidence/M3/TEST-M3_launch_shutdown_classify.py
L=docs/evidence/M7/TEST-M7-05_a3_sim_launch.log
T=$(mktemp -d); FAIL=0
git show b8fc601:$C > "$T/old.py"
echo "# DEC-079 classifier check, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)"
echo "## 1. kept launch logs: class before DEC-079 -> after"
for f in $(git ls-files 'docs/evidence/*launch*.log' | grep -v 'TEST-M7-05_a3_'); do
  python3 -I "$T/old.py" "$f" > /dev/null; o=$?
  python3 -I "$C" "$f" > /dev/null; n=$?
  [ "$o" = "$n" ] && r=PASS || { r=FAIL; FAIL=1; }
  echo "$r  $o -> $n  $f"
done
echo "## 2. the TS-039 log"
python3 -I "$C" "$L"; n=$?
[ "$n" = 4 ] && echo "PASS  exit 4 (TS-039)" || { echo "FAIL  exit $n (expected 4)"; FAIL=1; }
echo "## 3. near-miss copies (expected OTHER, exit 1)"
sed '/Escalating to SIGKILL on \[Gazebo Sim GUI\]/d; /Errno::ESRCH/d' "$L" > "$T/no_marks.log"
sed "s|cmd 'gz sim -r|cmd 'gz sim -s -r|" "$L" > "$T/server_only.log"
sed 's/exit code 1,/exit code 2,/' "$L" > "$T/exit2.log"
sed "/process has died \[pid 34329/i [ERROR] [gz-5]: process[gz-5] failed to terminate '10.0' seconds after receiving 'SIGTERM', escalating to 'SIGKILL'" "$L" > "$T/sigkill.log"
sed 's/^\[INFO\] \[parameter_bridge-2\]: process has finished cleanly.*$/[ERROR] [parameter_bridge-2]: process has died [pid 1, exit code 1, cmd x]./' "$L" > "$T/other_err.log"
sed 's/^\[gz-5\] Escalating to SIGKILL/[bridge-9] Escalating to SIGKILL/; /Errno::ESRCH/d' "$L" > "$T/mark_other_proc.log"
for k in no_marks server_only exit2 sigkill other_err mark_other_proc; do
  out=$(python3 -I "$C" "$T/$k.log"); n=$?
  [ "$n" = 1 ] && r=PASS || { r=FAIL; FAIL=1; }
  echo "$r  $k: exit $n; ${out:0:150}"
done
rm -rf "$T"
echo "# result: $([ $FAIL = 0 ] && echo PASS || echo FAIL)"
exit $FAIL
