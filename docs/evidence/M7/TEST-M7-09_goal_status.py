#!/usr/bin/env python3
"""TEST-M7-09 supporting record: final status of every NavigateToPose goal (2026-11-23).

Usage: python3 -I docs/evidence/M7/TEST-M7-09_goal_status.py <echo file>
<echo file> is the output of `ros2 topic echo /navigate_to_pose/_action/status action_msgs/msg/GoalStatusArray`
during the session. Prints the last status seen for each goal id (4 SUCCEEDED, 5 CANCELED, 6 ABORTED) and a count.
Supporting record only: TEST-M7-09's result is the user's observation. Exit 0.
"""
import re, sys
text = open(sys.argv[1]).read()
final = {}
for uuid, status in re.findall(r'uuid:\s*\n((?:\s*- \d+\n)+).*?status: (\d+)', text, re.S):
    final[tuple(re.findall(r'\d+', uuid))] = int(status)   # last status seen per goal id
names = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}
done = [s for s in final.values() if s in names]
for i, s in enumerate(done, 1):
    print(f'goal {i}: {names[s]}')
print(f'# goals with a final status: {len(done)}; SUCCEEDED {done.count(4)}, ABORTED {done.count(6)}, CANCELED {done.count(5)}')
