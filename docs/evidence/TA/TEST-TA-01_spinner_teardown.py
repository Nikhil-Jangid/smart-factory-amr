#!/usr/bin/env python3
"""TEST-TA-01: teardown of the shared harness spin thread (REQ-TA-01; DEC-040 (c); TS-030).

Usage, from the repository root with ROS sourced (plain python3, TS-011):
    python3 docs/evidence/TA/TEST-TA-01_spinner_teardown.py <teardowns> > <log>
No Gazebo. Imports the real M2.Spinner from docs/evidence/M2/TEST-M2_motion_measure.py, and per teardown:
  - rclpy.init;
  - a node under load (4 timers at 2 kHz publishing, 4 subscriptions doing busy work);
  - Spinner(ex).start();
  - a random 0-50 ms hold;
  - Spinner.stop(node).
This is the TS-030 scratch reproduction of 2026-11-04, with the helper in place of the old teardown order.
Pass: 0 thread exceptions (Spinner state and threading.excepthook) and 0 threads left alive.
Exit 0 = PASS, 1 = FAIL. Uses ROS_DOMAIN_ID 77 unless set.
"""
import contextlib
import importlib.util
import io
import os
import random
import subprocess
import sys
import threading
import time

os.environ.setdefault('ROS_DOMAIN_ID', '77')
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    'test_m2', os.path.join(HERE, '..', 'M2', 'TEST-M2_motion_measure.py'))
M2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M2)
from std_msgs.msg import Empty  # noqa: E402  (after the ROS environment is confirmed by the import above)

n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
other = []
threading.excepthook = lambda a: other.append(f'{a.thread.name}: {a.exc_type.__name__}: {a.exc_value}')
rev = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
dirty = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', 'docs/evidence/M2', 'docs/evidence/M3', 'docs/evidence/TA']).returncode
rev += ' (harness files with uncommitted changes)' if dirty else ' (harness files clean)'
print(f'# TEST-TA-01 spinner teardown, {n} teardowns, {time.strftime("%F %T %Z")}, revision {rev}, '
      f'ROS_DOMAIN_ID {os.environ["ROS_DOMAIN_ID"]}')
states = {}
alive = 0
t_start = time.monotonic()
for i in range(n):
    M2.rclpy.init()
    node = M2.rclpy.create_node('ta01')
    pub = node.create_publisher(Empty, 'ta01', 10)
    for _ in range(4):
        node.create_timer(0.0005, lambda: pub.publish(Empty()))
        node.create_subscription(Empty, 'ta01', lambda m: sum(range(2000)), 50)
    ex = M2.SingleThreadedExecutor()
    ex.add_node(node)
    sp = M2.Spinner(ex).start()
    time.sleep(random.uniform(0.0, 0.05))
    with contextlib.redirect_stdout(io.StringIO()):  # Spinner.stop prints one line per teardown
        state = sp.stop(node)
    states[state] = states.get(state, 0) + 1
    alive += sp.thread.is_alive()
print(f'# duration {time.monotonic() - t_start:.1f} s')
for state, count in sorted(states.items()):
    print(f'# spin thread {state}: {count}')
print(f'# other thread exceptions: {len(other)}' + (f' (first: {other[0]})' if other else ''))
ok = states.get('ended cleanly', 0) == n and not other and alive == 0
print(f'{"PASS" if ok else "FAIL"}  {states.get("ended cleanly", 0)} of {n} teardowns ended cleanly; '
      f'threads alive {alive}; other exceptions {len(other)}')
print(f'# overall: {"PASS" if ok else "FAIL"}')
sys.stdout.flush()
os._exit(0 if ok else 1)  # as the harnesses: the gz-transport node of the imported module aborts at teardown
