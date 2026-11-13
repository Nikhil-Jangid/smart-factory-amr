#!/usr/bin/env bash
# TS-029 rig 2 (scratch, informal). Usage: rig2.sh <label> <runs> <hold s> <overlay ws or -> [extra launch args...]
D=$(cd "$(dirname "$0")" && pwd)
LABEL=$1; N=$2; HOLD=$3; OV=$4; shift 4
OUT=$D/out; mkdir -p "$OUT"
SUM=$OUT/summary.log
for i in $(seq ${START:-1} $(( ${START:-1} + N - 1 ))); do
  pre=$(pgrep -c -x 'ruby|gz|parameter_bridg|robot_state_pub|cmd_vel_guard|ros2|spawner|create' 2>/dev/null)
  [ "$pre" != 0 ] && { echo "$LABEL run $i: ABORT, $pre leftover processes before launch: $(pgrep -a -x 'ruby|gz|parameter_bridg|robot_state_pub|cmd_vel_guard|ros2|spawner|create' | tr '\n' ';')" >> "$SUM"; exit 1; }
  bash "$D/${RUNONE:-TS-029_rig2_runone.sh}" "$LABEL" "$i" "$HOLD" "$OUT" "$OV" "$@"
  P=$OUT/${LABEL}_run$i
  GZ=$(cat $P.gzpid); LPID=$(cat $P.lpid)
  while kill -0 "$GZ" 2>/dev/null; do timeout --foreground 0.1 tail -f /dev/null; done
  T1=$(date +%s.%N)
  while kill -0 "$LPID" 2>/dev/null; do timeout --foreground 0.2 tail -f /dev/null; done
  timeout --foreground 1 tail -f /dev/null
  left=$(pgrep -g "$LPID" 2>/dev/null | wc -l); pkill -KILL -g "$LPID" 2>/dev/null
  L=${P}_launch.log
  dt=$(echo "$T1 - $(cat $P.t0)" | bc)
  printf "%s run %d: hold %ss; %s; gz exit after %.1f s; ERROR lines %d; plugin shutdown line %d; leftover %d; %s\n" \
    "$LABEL" "$i" "$HOLD" "$(cat $P.meta)" "$dt" "$(grep -c '\[ERROR\]' $L)" "$(grep -c 'ImuDecimator\] shutdown' $L)" "$left" \
    "$([ -f ${P}_gdb.txt ] && echo 'HANG: threads+gdb captured' || echo clean)" >> "$SUM"
  # keep full launch logs only for hangs
  [ -f ${P}_gdb.txt ] || rm -f "$L"
done
