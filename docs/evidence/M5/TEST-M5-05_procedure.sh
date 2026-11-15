#!/usr/bin/env bash
# TEST-M5-05 save and reload (REQ-M5-06; M5 Task C; DEC-051, DEC-054, DEC-055). No simulation.
# Run from the repository root after `source /opt/ros/jazzy/setup.bash`:
#   bash docs/evidence/M5/TEST-M5-05_procedure.sh <output log> [<pose-graph source prefix>]
# The reference map amr_ws/src/amr_bringup/maps/mapping_arena.* was made once from TEST-M5-03 attempt 1 (rule fixed
# before that run, M5 plan §12):
#   cp docs/evidence/M5/TEST-M5-03_a1_map.pgm maps/mapping_arena.pgm
#   sed 's/^image: .*/image: mapping_arena.pgm/' docs/evidence/M5/TEST-M5-03_a1_map.yaml > maps/mapping_arena.yaml
#   then the origin line moved by half a cell, -0.025 m in x and y (DEC-055, TS-041): [-2.046, -4.055, 0] -> [-2.071, -4.080, 0]
#   gzip -9 -n -c <PG_DIR>/TEST-M5-03_a1_posegraph.posegraph > maps/mapping_arena.posegraph.gz   (and .data -> .data.gz)
# Steps:
#   1. the reference map is the TEST-M5-03 attempt 1 map: .pgm byte-identical; .yaml identical except the image name
#      and the origin, which is the attempt 1 origin minus half a cell (0.025 m) in x and y, yaw unchanged (DEC-055);
#   2. the compressed pose graph is intact (gzip -t) and decompresses to the serialized pose graph of that attempt
#      (byte comparison, when the source prefix is given; its SHA-256 is printed either way);
#   3. Nav2 map_server (lifecycle node) loads maps/mapping_arena.yaml, is configured and activated, and the grid it
#      serves on /map equals the file cell by cell, with the same size, resolution, origin and frame
#      (TEST-M5-05_reload_check.py); map_server stops cleanly (exit 0) on SIGINT to its process group;
#   4. negative control: map_server serves a copy with one occupied cell turned free; the same check must FAIL.
# Own ROS_DOMAIN_ID 140. Job control (set -m; TS-011); launches outside any pipeline (TS-017).
set -u
set -m
OUT=$1; SRC=${2:-}
EV=docs/evidence/M5
M=amr_ws/src/amr_bringup/maps
TMP=$(mktemp -d); FAIL=0
export ROS_DOMAIN_ID=140
rc() { echo "# exit $1"; [ "$1" = 0 ] || FAIL=1; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
serve() {   # serve <yaml> <label>: start map_server, configure, activate; sets MPID
  ros2 run nav2_map_server map_server --ros-args -p yaml_filename:="$(realpath "$1")" > "$TMP/ms_$2.log" 2>&1 &
  MPID=$!
  for _ in $(seq 30); do ros2 node list 2>/dev/null | grep -q '^/map_server$' && break; pause 1; done
  timeout --foreground 20 ros2 lifecycle set /map_server configure | tail -1
  timeout --foreground 20 ros2 lifecycle set /map_server activate | tail -1
  echo "# lifecycle state: $(timeout --foreground 10 ros2 lifecycle get /map_server)"
}
unserve() {   # stop map_server with SIGINT to its process group, as Ctrl-C does (`ros2 run` does not pass a SIGINT sent
              # to itself alone on to the map_server child); exit code
  kill -INT -- -"$MPID" 2>/dev/null
  for _ in $(seq 15); do kill -0 "$MPID" 2>/dev/null || break; pause 1; done
  kill -0 "$MPID" 2>/dev/null && { kill -TERM -- -"$MPID" 2>/dev/null; echo "# map_server did not stop on SIGINT in 15 s"; }
  wait "$MPID"; MS=$?
  echo "# map_server ($1) exit $MS; log: $(grep -c -E '\[ERROR\]' "$TMP/ms_$1.log") [ERROR] lines"
  grep -E 'Loading|Read map|\[ERROR\]|\[WARN\]' "$TMP/ms_$1.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sed "s|$PWD/||g" | sed 's/^/#   /'
}
{
echo "# TEST-M5-05 save and reload, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)$(git diff --quiet HEAD -- amr_ws/src && echo ' (amr_ws/src clean)' || echo ' (amr_ws/src has uncommitted changes)')"
echo "# nav2_map_server $(dpkg-query -W -f='${Version}' ros-jazzy-nav2-map-server); $(gzip --version | head -1)"
ls -l $M | awk 'NR > 1 {print "#   " $5 " bytes  " $NF}'

echo; echo "## 1. reference map = TEST-M5-03 attempt 1"
cmp $M/mapping_arena.pgm $EV/TEST-M5-03_a1_map.pgm && echo ".pgm byte-identical to TEST-M5-03_a1_map.pgm"; rc $?
diff <(grep -v -E '^(image|origin):' $M/mapping_arena.yaml) <(grep -v -E '^(image|origin):' $EV/TEST-M5-03_a1_map.yaml) && echo ".yaml identical except the image and origin lines"; rc $?
python3 - $M/mapping_arena.yaml $EV/TEST-M5-03_a1_map.yaml <<'PYEOF'
import sys, yaml
ref, run = (yaml.safe_load(open(f))['origin'] for f in sys.argv[1:])
d = [round(a - b, 6) for a, b in zip(ref, run)]
print(f'origin {ref} = attempt 1 origin {run} + {d} (DEC-055: half a cell, -0.025, -0.025, 0)')
sys.exit(0 if d == [-0.025, -0.025, 0] else 1)
PYEOF
rc $?
[ "$(grep '^image:' $M/mapping_arena.yaml)" = 'image: mapping_arena.pgm' ]; rc $?
sed 's/^/#   /' $M/mapping_arena.yaml; echo

echo; echo "## 2. compressed pose graph (DEC-054)"
for K in posegraph data; do
  gzip -t "$M/mapping_arena.$K.gz" && echo "mapping_arena.$K.gz: gzip -t OK"; rc $?
  echo "#   decompressed $(gzip -dc "$M/mapping_arena.$K.gz" | wc -c) bytes, SHA-256 $(gzip -dc "$M/mapping_arena.$K.gz" | sha256sum | cut -c1-64)"
  if [ -n "$SRC" ]; then
    gzip -dc "$M/mapping_arena.$K.gz" | cmp - "$SRC.$K" && echo "decompressed .$K byte-identical to the TEST-M5-03 attempt 1 serialization"; rc $?
  else
    echo "# source not given: byte comparison skipped"
  fi
done

echo; echo "## 3. map_server reload"
serve $M/mapping_arena.yaml ref
echo '$ python3 TEST-M5-05_reload_check.py amr_ws/src/amr_bringup/maps/mapping_arena.yaml'
python3 "$EV/TEST-M5-05_reload_check.py" $M/mapping_arena.yaml; rc $?
unserve ref; [ "$MS" = 0 ]; rc $?

echo; echo "## 4. negative control: one occupied cell turned free in a served copy"
python3 - "$M/mapping_arena.pgm" "$TMP/neg.pgm" <<'EOF'
import sys
d = bytearray(open(sys.argv[1], 'rb').read())
i = d.rindex(b'\x00')            # the last occupied pixel (value 0)
d[i] = 254                       # free
open(sys.argv[2], 'wb').write(d)
print(f'# pixel at byte offset {i} changed from 0 (occupied) to 254 (free)')
EOF
sed 's/^image: .*/image: neg.pgm/' $M/mapping_arena.yaml > "$TMP/neg.yaml"
serve "$TMP/neg.yaml" neg
python3 "$EV/TEST-M5-05_reload_check.py" $M/mapping_arena.yaml; NEG=$?
echo "# negative control checker exit $NEG (expected 1)"; [ "$NEG" = 1 ]; rc $?
unserve neg

LEFT=$(pgrep -af 'map_server' | grep -v -E 'pgrep|TEST-M5-05' | wc -l); echo "# leftover map_server processes: $LEFT"; [ "$LEFT" = 0 ]; rc $?
echo; echo "# overall: $([ $FAIL = 0 ] && echo 'ALL CHECKS PASSED' || echo 'AT LEAST ONE CHECK FAILED')"
} > "$TMP/raw.log" 2>&1
sed -e "s|$TMP|<tmp>|g" -e "s|$HOME|<home>|g" -e "s|$PWD/||g" "$TMP/raw.log" > "$OUT"
rm -rf "$TMP"
grep -q '^# overall: ALL CHECKS PASSED' "$OUT"
