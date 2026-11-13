#!/usr/bin/env bash
# V1 (production configuration) with external subscribers during the hold, 20 runs, 25 s hold
D=$(cd "$(dirname "$0")" && pwd)
echo "# batch2 start $(date +%T)" >> $D/out/summary.log
RUNONE=TS-029_rig2_runone_subs.sh bash $D/TS-029_rig2.sh V1S 20 25 -
echo "batch2 done $(date +%T)" >> $D/out/summary.log
