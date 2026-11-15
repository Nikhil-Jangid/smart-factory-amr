#!/usr/bin/env bash
# TS-039 diagnosis rig (docs/troubleshooting.md TS-039): how does the GUI simulation launch shut down?
# Run from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
#   bash docs/evidence/M5/TS-039_gui_shutdown_rig.sh <cycles> <summary log>
# Each cycle reproduces the TEST-M5-02 launch and teardown without the checks: `sim.launch.py headless:=false
# sensors:=true world:=mapping_arena.sdf`, both controllers active, `slam.launch.py`, 15 s of running (SLAM maps from
# the scans), then SIGINT to the SLAM launch (20 s grace), SIGINT to the simulation launch (30 s grace). Recorded
# per cycle: time from SIGINT to the end of the simulation launch, the DEC-039 classifier verdict, the gz exit-code
# line, the `gz sim` front end's own lines ("Escalating to SIGKILL on [...]"), and leftover processes by name.
# The full simulation launch log of every cycle that is not CLEAN is kept as <summary>_c<N>_sim_launch.log.
# Hypothesis under test (from cmdsim8.rb, gz-sim 8): with the GUI, `gz sim` is a Ruby front end whose INT/TERM traps
# stop the GUI and then the server (5 s each, then SIGKILL) and end with `return 1`; when that takes longer than the
# launch's 5 s SIGINT grace, the launch sends SIGTERM and the front end exits with code 1.
# Job control (set -m; TS-011); launches outside any pipeline (TS-017); own ROS_DOMAIN_ID (121-) and GZ_PARTITION.
set -u
set -m
N=$1; OUT=$2
TMP=$(mktemp -d)
SHARE_B="$(ros2 pkg prefix amr_bringup)/share/amr_bringup"
NAMES='gz sim|async_slam_toolbox|parameter_bridge|robot_state_publisher'
byname() { pgrep -af "$NAMES" | grep -v -E 'pgrep|TS-039_gui_shutdown_rig' | wc -l; }
pause() { timeout --foreground "$1" tail -f /dev/null; }
D=$(dirname "$OUT"); B=$(basename "$OUT" .log)
{
echo "# TS-039 GUI shutdown rig, $N cycles, $(date '+%F %T %Z'), revision $(git rev-parse --short HEAD)"
echo "# $(gz sim --version | head -1); launch: sim.launch.py headless:=false sensors:=true world:=mapping_arena.sdf + slam.launch.py"
for C in $(seq 1 "$N"); do
  export ROS_DOMAIN_ID=$((120 + C)) GZ_PARTITION="ts039_$$_$C"
  [ "$(byname)" = 0 ] || { echo "# cycle $C: processes left from before, stopped"; pkill -TERM -f "$NAMES"; pause 5; }
  ros2 launch amr_bringup sim.launch.py headless:=false sensors:=true world:=mapping_arena.sdf > "$TMP/sim_$C.log" 2>&1 &
  LPID=$!
  for _ in $(seq 1 90); do
    [ "$(timeout --foreground 5 ros2 control list_controllers 2>/dev/null | grep -c -E '^(joint_state_broadcaster|diff_drive_controller) .* active')" = 2 ] && break
    pause 1
  done
  ros2 launch amr_bringup slam.launch.py > "$TMP/slam_$C.log" 2>&1 &
  SPID=$!
  pause 15
  kill -INT "$SPID"; for _ in $(seq 1 20); do kill -0 "$SPID" 2>/dev/null || break; pause 1; done
  kill -0 "$SPID" 2>/dev/null && { kill -TERM -- -"$SPID"; echo "# cycle $C: SLAM launch needed SIGTERM"; }
  wait "$SPID" 2>/dev/null
  T0=$(date +%s.%N)
  kill -INT "$LPID"; for _ in $(seq 1 300); do kill -0 "$LPID" 2>/dev/null || break; timeout --foreground 0.1 tail -f /dev/null; done
  T1=$(date +%s.%N)
  kill -0 "$LPID" 2>/dev/null && { kill -TERM -- -"$LPID"; echo "# cycle $C: simulation launch alive 30 s after SIGINT, SIGTERM to its group"; }
  wait "$LPID" 2>/dev/null
  for _ in $(seq 1 10); do [ "$(byname)" = 0 ] && break; pause 1; done
  LEFT=$(byname)
  CLS=$(python3 -I docs/evidence/M3/TEST-M3_launch_shutdown_classify.py "$TMP/sim_$C.log"); SH=$?
  SCLS=$(python3 -I docs/evidence/M3/TEST-M3_launch_shutdown_classify.py "$TMP/slam_$C.log")
  GZEXIT=$(grep -o -E "\[gz-[0-9]+\]: process (has finished cleanly|has died \[pid [0-9]+, exit code -?[0-9]+)" "$TMP/sim_$C.log" | sed -E 's/\[pid [0-9]+, //' | head -1)
  FRONT=$(grep -c 'Escalating to SIGKILL on' "$TMP/sim_$C.log")
  echo "cycle $C: stop $(awk "BEGIN{printf \"%.1f\", $T1 - $T0}") s; sim ${CLS#\# shutdown: }; gz: ${GZEXIT:-none}; front-end SIGKILL lines: $FRONT; SLAM ${SCLS#\# shutdown: }; leftovers by name: $LEFT"
  grep -E 'Escalating to SIGKILL on|failed to terminate|process has died' "$TMP/sim_$C.log" | sed -E 's/\[[0-9]+\.[0-9]+\]//' | sed 's/^/#   /'
  if [ "$SH" != 0 ]; then
    sed -e "s|$SHARE_B|<share_b>|g" -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" "$TMP/sim_$C.log" > "$D/${B}_c${C}_sim_launch.log"
    echo "#   full log kept: ${B}_c${C}_sim_launch.log"
  fi
  [ "$LEFT" = 0 ] || { pgrep -af "$NAMES" | grep -v -E 'pgrep|TS-039' | sed 's/^/#   left: /'; pkill -TERM -f "$NAMES"; }
done
} > "$TMP/raw.log" 2>&1
{ grep -v '^# summary' "$TMP/raw.log"
  echo "# summary: CLEAN $(grep -c '; sim CLEAN' "$TMP/raw.log"), TS-029 $(grep -c '; sim TS-029' "$TMP/raw.log"), OTHER $(grep -c '; sim OTHER' "$TMP/raw.log") of $N cycles"
} | sed -e "s|$HOME|<home>|g" -e "s|_$$_|_<pid>_|g" > "$OUT"
rm -rf "$TMP"
