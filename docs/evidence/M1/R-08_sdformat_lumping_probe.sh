#!/usr/bin/env bash
# Review finding R-08 / R-02 evidence: generic SDFormat fixed-joint lumping probe.
# This is NOT the AMR model. It shows how the installed sdformat converts a URDF
# with fixed joints, and what the installed SDFormat spec says about self-collision.
# Usage (repository root, after `source /opt/ros/jazzy/setup.bash`):
#   bash docs/evidence/M1/R-08_sdformat_lumping_probe.sh 2>&1 | tee docs/evidence/M1/R-08_sdformat_lumping_probe.log
set -u
EV="$(cd "$(dirname "$0")" && pwd)"
IN=R-08_sdformat_lumping_probe.urdf
OUT=R-08_sdformat_lumping_probe.sdf
echo "date: $(date -Iseconds)"
echo "gz: $(command -v gz)"
echo "gz sdf --versions: $(gz sdf --versions 2>&1 | tr '\n' ' ')"
echo "input: $IN sha256 $(sha256sum "$EV/$IN" | cut -d' ' -f1)"
echo "command: gz sdf -p $IN > $OUT"
( cd "$EV" && gz sdf -p "$IN" > "$OUT" )
echo "exit code: $?"
echo "output: $OUT sha256 $(sha256sum "$EV/$OUT" | cut -d' ' -f1)"
echo "--- output <link> elements:"
grep -n "<link " "$EV/$OUT"
echo "--- output <inertial> of the merged root link:"
sed -n '/<link name=.root.>/,/<\/inertial>/p' "$EV/$OUT"
echo "--- output joint type:"
grep -n "<joint " "$EV/$OUT"
echo "--- self_collide elements in output: $(grep -c self_collide "$EV/$OUT")"
echo "--- installed SDFormat 1.11 spec, model-level self_collide (gz sdf -d 1.11):"
gz sdf -d 1.11 | grep -m1 -A1 "element name ='self_collide'"
echo "--- spec exit code: ${PIPESTATUS[0]}"
