#!/usr/bin/env python3
"""Classify the shutdown of one `ros2 launch` sensor run from its launch log (DEC-039, TS-029).

Usage: python3 -I TEST-M3_launch_shutdown_classify.py <launch.log>
Prints one line `# shutdown: <CLASS> (<details>)` and exits with:
  0  CLEAN   no [ERROR] line in the log, every started process finished cleanly or was a finished one-shot.
  3  TS-029  the exact TS-029 signature and nothing else (DEC-039):
             - the launch received the user's SIGINT ("user interrupted with ctrl-c (SIGINT)");
             - the only [ERROR] lines belong to the single `gz sim` process and are its shutdown escalation:
               "failed to terminate '5' seconds after receiving 'SIGINT', escalating to 'SIGTERM'" (required),
               optionally "failed to terminate ... after receiving 'SIGTERM', escalating to 'SIGKILL'", and
               optionally "process has died [pid N, exit code -9 or -15, cmd 'gz sim ...']";
             - every other started process logged "process has finished cleanly".
  4  TS-039  the GUI form of the same stall (DEC-079; only meaningful for `gz sim` without `-s`, i.e. the Ruby front end
             that forks the server and the GUI): exactly
             - the user's SIGINT, and the single `gz sim` process's "failed to terminate '5' seconds after receiving
               'SIGINT', escalating to 'SIGTERM'" (required);
             - "process has died [pid N, exit code 1, cmd 'gz sim ...']" (required; cmd without ` -s `);
             - in that process's output after the SIGINT: "Escalating to SIGKILL on [Gazebo Sim GUI]" and/or the front
               end's "cmdsim8.rb:...:in `kill': No such process (Errno::ESRCH)" traceback (at least one required);
             - no other [ERROR] line (no SIGTERM -> SIGKILL escalation) and every other process finished cleanly.
             Callers that predate DEC-079 treat 4 like 1 (they accept only 0 and 3).
  1  OTHER   anything else (any other [ERROR] line, another process that did not finish cleanly, a gz process
             that died before SIGINT, more than one gz process, or no SIGINT in the log).
The caller still checks for leftover processes itself; DEC-039 requires 0 leftovers for both CLEAN and TS-029.
Root cause of TS-029 (docs/troubleshooting.md): gz-common's signal handler stops the server on the interrupted
main thread while the Sensors system's render thread destroys the gpu_lidar sensor; an upstream deadlock/stall.
TS-039 (docs/troubleshooting.md, DEC-079): with the GUI, `gz sim` is a Ruby front end (gz-sim 8 cmdsim8.rb) whose INT
trap stops the GUI and then the server, waiting up to 5 s for each; when a child is slow, ros2 launch's own 5 s SIGINT
grace ends first, the SIGTERM trap runs the same kill sequence again (ESRCH on the child already gone), the front end
SIGKILLs the slow child and exits 1.
"""
import re
import sys

STARTED = re.compile(r'^\[INFO\] \[([\w.-]+-\d+)\]: process started with pid \[(\d+)\]')
CLEAN = re.compile(r'^\[INFO\] \[([\w.-]+-\d+)\]: process has finished cleanly \[pid (\d+)\]')
ERROR = re.compile(r'^\[ERROR\] \[([\w.-]+)\]: (.*)$')
SIGINT_ESC = re.compile(r"^process\[(gz-\d+)\] failed to terminate '5(\.0)?' seconds after receiving 'SIGINT', "
                        r"escalating to 'SIGTERM'$")
SIGTERM_ESC = re.compile(r"^process\[(gz-\d+)\] failed to terminate '[\d.]+' seconds after receiving 'SIGTERM', "
                         r"escalating to 'SIGKILL'$")
DIED = re.compile(r"^process has died \[pid \d+, exit code (-9|-15), cmd 'gz sim .*'\]\.?$")
DIED_GUI = re.compile(r"^process has died \[pid \d+, exit code 1, cmd '(gz sim .*)'\]\.?$")
GUI_KILL = 'Escalating to SIGKILL on [Gazebo Sim GUI]'
GUI_ESRCH = re.compile(r"cmdsim8\.rb:\d+:in `kill': No such process \(Errno::ESRCH\)")


def classify(lines):
    started = {}
    clean = set()
    errors = []
    sigint_line = None
    gui_marks = []
    for n, raw in enumerate(lines):
        line = raw.rstrip('\n')
        m = STARTED.match(line)
        if m:
            started[m.group(1)] = n
        m = CLEAN.match(line)
        if m:
            clean.add(m.group(1))
        m = ERROR.match(line)
        if m:
            errors.append((n, m.group(1), m.group(2)))
        if sigint_line is None and 'user interrupted with ctrl-c (SIGINT)' in line:
            sigint_line = n
        if line.startswith('[gz-') and (GUI_KILL in line or GUI_ESRCH.search(line)):
            gui_marks.append((n, line.split(']', 1)[0][1:], 'SIGKILL GUI' if GUI_KILL in line else 'ESRCH'))
    gz = [name for name in started if name.startswith('gz-')]
    not_clean = sorted(name for name in started if name not in clean)
    if not errors:
        if not_clean:
            return 1, 'OTHER', f'no [ERROR] line, but not finished cleanly: {", ".join(not_clean)}'
        return 0, 'CLEAN', f'0 [ERROR] lines; {len(started)} processes finished cleanly'
    if len(gz) != 1:
        return 1, 'OTHER', f'{len(errors)} [ERROR] lines and {len(gz)} gz processes (expected 1)'
    g = gz[0]
    if sigint_line is None:
        return 1, 'OTHER', f'{len(errors)} [ERROR] lines but no SIGINT from the user in the log'
    kinds = []
    for n, proc, text in errors:
        if proc != g or n < sigint_line:
            return 1, 'OTHER', f'[ERROR] not part of the gz shutdown escalation: [{proc}] {text[:120]}'
        if SIGINT_ESC.match(text) and SIGINT_ESC.match(text).group(1) == g:
            kinds.append('SIGINT->SIGTERM')
        elif SIGTERM_ESC.match(text) and SIGTERM_ESC.match(text).group(1) == g:
            kinds.append('SIGTERM->SIGKILL')
        elif DIED.match(text):
            kinds.append('died ' + DIED.match(text).group(1))
        elif DIED_GUI.match(text) and ' -s ' not in DIED_GUI.match(text).group(1) + ' ':
            kinds.append('died 1 (GUI front end)')
        else:
            return 1, 'OTHER', f'[ERROR] [{proc}] not in the TS-029 signature: {text[:120]}'
    if kinds.count('SIGINT->SIGTERM') != 1 or len(kinds) != len(set(kinds)):
        return 1, 'OTHER', f'gz escalation lines not in the TS-029 pattern: {kinds}'
    others = [name for name in not_clean if name != g]
    if others:
        return 1, 'OTHER', f'gz escalation, but other processes did not finish cleanly: {", ".join(others)}'
    if 'died 1 (GUI front end)' in kinds:
        marks = sorted({k for n, proc, k in gui_marks if proc == g and n > sigint_line})
        if 'SIGTERM->SIGKILL' in kinds or not marks:
            return 1, 'OTHER', f'gz exit code 1 not in the TS-039 pattern: {kinds}, front-end marks {marks}'
        return 4, 'TS-039', (f'only {g} (GUI front end) escalated after SIGINT ({", ".join(kinds)}; {", ".join(marks)}); '
                             'all other processes finished cleanly')
    return 3, 'TS-029', f'only {g} escalated after SIGINT ({", ".join(kinds)}); all other processes finished cleanly'


def main():
    with open(sys.argv[1], errors='replace') as f:
        code, cls, details = classify(f.readlines())
    print(f'# shutdown: {cls} ({details})')
    sys.exit(code)


if __name__ == '__main__':
    main()
