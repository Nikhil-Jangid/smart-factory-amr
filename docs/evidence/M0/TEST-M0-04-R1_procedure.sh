#!/usr/bin/env bash
# TEST-M0-04 re-test 1: headless Gazebo -> ROS 2 /clock bridge, isolated from other simulators.
W=$1; cd "$W"
export GZ_PARTITION="amr_m0_retest_$$" ROS_DOMAIN_ID=73
say() { echo "$*"; }
run() { echo "\$ $*"; bash -c "$*"; local r=$?; echo "[exit=$r]"; echo; return $r; }
say "TEST-M0-04 re-test 1 (headless /clock bridge)"; say "date: $(date -Iseconds)"
say "repo HEAD: $(git -C ~/Projects/smart-factory-amr rev-parse HEAD)"
say "isolation: GZ_PARTITION=$GZ_PARTITION ROS_DOMAIN_ID=$ROS_DOMAIN_ID (a pre-existing 'gz sim server' on the default partition was left untouched)"; echo
say "## Pre-check: no /clock in the isolated partition/domain"
run "timeout 5 gz topic -l | grep -x /clock || echo 'no gz /clock'"
run "timeout 10 ros2 topic list | grep -x /clock || echo 'no ROS /clock'"
say "## Start headless Gazebo server"
say "\$ gz sim -s -r -v 2 shapes.sdf   (background, own process group)"
setsid gz sim -s -r -v 2 shapes.sdf > gz_server.out 2>&1 & GZPID=$!
say "gz pid/pgid=$GZPID"
for i in $(seq 1 30); do timeout 3 gz topic -l 2>/dev/null | grep -qx /clock && break; sleep 1; done
say "gz /clock advertised after ~${i}s"; run "timeout 5 gz topic -l | grep -E '^/clock$|^/world/shapes/clock$'"
say "## Start bridge"
say "\$ ros2 run ros_gz_bridge parameter_bridge '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'   (background, own process group)"
setsid ros2 run ros_gz_bridge parameter_bridge '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock' > bridge.out 2>&1 & BPID=$!
say "bridge pid/pgid=$BPID"; sleep 4
run "timeout 10 ros2 topic info /clock"
say "## Sample /clock twice"
run "timeout 15 ros2 topic echo --once /clock > clock1.txt; r=\$?; cat clock1.txt; exit \$r"; R1=$?
sleep 2
run "timeout 15 ros2 topic echo --once /clock > clock2.txt; r=\$?; cat clock2.txt; exit \$r"; R2=$?
t() { awk '/sec:/ && !/nanosec/{s=$2} /nanosec:/{n=$2} END{if(s=="")print "NA"; else printf "%.9f\n", s+n/1e9}' "$1"; }
T1=$(t clock1.txt); T2=$(t clock2.txt)
say "## Evaluation"; say "t1=$T1 s  t2=$T2 s  (echo exits: $R1, $R2)"
if [ "$R1" = 0 ] && [ "$R2" = 0 ] && [ "$T1" != NA ] && [ "$T2" != NA ] && awk -v a="$T1" -v b="$T2" 'BEGIN{exit !(b>a)}'; then
  say "delta=$(awk -v a="$T1" -v b="$T2" 'BEGIN{printf "%.3f", b-a}') s -> /clock ADVANCED"; VERDICT=PASS
else say "/clock did NOT advance or could not be read"; VERDICT=FAIL; fi
say "## Cleanup (only processes started by this test)"
kill -INT -- -$BPID 2>/dev/null; kill -INT -- -$GZPID 2>/dev/null; sleep 3
for g in $BPID $GZPID; do pgrep -g $g >/dev/null && { say "pgid $g still alive -> SIGTERM"; kill -TERM -- -$g; sleep 2; }; done
for g in $BPID $GZPID; do pgrep -g $g >/dev/null && { say "pgid $g still alive -> SIGKILL"; kill -KILL -- -$g; sleep 1; }; done
for g in $BPID $GZPID; do pgrep -g $g >/dev/null && say "pgid $g REMAINS" || say "pgid $g: no processes remain"; done
say "pre-existing server 34793: $(ps -o pid=,cmd= -p 34793 || echo 'not running')"
say "## Server output (tail)"; tail -n 15 gz_server.out
say "## Bridge output (tail)"; tail -n 15 bridge.out
say "VERDICT: $VERDICT"
