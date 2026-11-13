#!/usr/bin/env bash
# Interleaved V0 / V1 / V2, 25 s hold, 20 rounds
D=$(cd "$(dirname "$0")" && pwd)
for r in $(seq 1 20); do
  START=$r bash $D/TS-029_rig2.sh V0 1 25 <rig>/ov_v0 || exit 1
  START=$r bash $D/TS-029_rig2.sh V1 1 25 - || exit 1
  START=$r bash $D/TS-029_rig2.sh V2 1 25 <rig>/ov_v2 || exit 1
done
echo "batch1 done $(date +%T)" >> $D/out/summary.log
