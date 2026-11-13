#!/usr/bin/env bash
# gz sim SIGINT shutdown-hang loop. Usage: sigint_loop.sh <runs> <hold seconds> <outdir>
# Starts `gz sim -r -s --headless-rendering gpu_lidar_sigint.sdf`, waits until /scan is published, holds,
# sends SIGINT to the gz process, and waits 5 s. A process still alive then counts as a hang: its threads
# are dumped with gdb (this shell is its parent, so ptrace_scope=1 allows it), then it is killed.
WORLD="$(cd "$(dirname "$0")" && pwd)/TS-029_minimal_gpu_lidar_sigint.sdf"; RUNS=$1; HOLD=$2; OUT=$3; mkdir -p "$OUT"
hangs=0
for i in $(seq 1 "$RUNS"); do
  export GZ_PARTITION=sigint_$$_$i
  gz sim -r -s --headless-rendering "$WORLD" > "$OUT/run$i.log" 2>&1 &
  GZ=$!
  for _ in $(seq 1 100); do timeout 1 gz topic -e -n 1 -t /scan >/dev/null 2>&1 && break; done
  sleep "$HOLD"
  kill -INT "$GZ"
  for _ in $(seq 1 50); do kill -0 "$GZ" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$GZ" 2>/dev/null; then
    hangs=$((hangs + 1))
    gdb -q -batch -p "$GZ" -ex "set debuginfod enabled off" -ex "set pagination off" -ex "thread apply all bt" > "$OUT/run${i}_gdb.txt" 2>&1
    kill -KILL "$GZ"; wait "$GZ" 2>/dev/null
    echo "run $i: HANG (alive 5 s after SIGINT; gdb in run${i}_gdb.txt)"
  else
    wait "$GZ"; echo "run $i: exit $? "; rm -f "$OUT/run$i.log"
  fi
done
echo "summary: $hangs hang(s) in $RUNS runs, hold $HOLD s"
