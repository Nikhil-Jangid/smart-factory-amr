#!/usr/bin/env python3
"""Serial runner for the formal test procedures (DEC-040 (a), REQ-TA-03; plan docs/milestones/M3-M4_test_automation.md §5).

Usage, from the repository root after `source /opt/ros/jazzy/setup.bash` and `source amr_ws/install/setup.bash`:
    python3 tools/run_suite.py <suite> <tag> [--dry-run] [--from <label>]
    python3 tools/run_suite.py --list
    python3 tools/run_suite.py --self-test
<tag> names this execution, e.g. TA03. It goes into every log name (TEST-M3-13-TA03_unit.log) and into the summary
docs/evidence/TA/<suite>-<tag>_summary.md.

What it does, per entry, strictly one at a time:
  1. Refuse if a simulation process is still running (gz sim, ros2 launch, bridge, controller manager, ...). At the start
     this is exit 3 and nothing runs; between entries it stops the suite (exit 1).
  2. Refuse an entry whose log already exists (evidence is never overwritten).
  3. Run the exact procedure command of docs/testing/test_plan.md (nothing is re-implemented here).
  4. Read the log: the last `# overall:` line (or a checker's `== ALL CHECKS PASSED` / `== n CHECK(S) FAILED`), and the
     DEC-039 count `# TS-029 attempts declared invalid under DEC-039: n`.
  5. Classify: PASS-candidate (exit 0 and a passing overall line), FAIL (exit != 0 and a failing overall line),
     MISMATCH (exit and overall line disagree: the TEST-M3-04 R1 defect class) or NO-OVERALL.
The runner never records a result. PASS-candidate means "ready for human log review"; only after that review is
TEST_RESULTS.md changed (DEC-040 item 5). Exit 0 = every entry PASS-candidate; 1 = otherwise; 3 = refused at start.
"""
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time

EV = 'docs/evidence'
MAP = 'amr_ws/src/amr_bringup/maps/mapping_arena.yaml'   # M5 reference map (DEC-051, DEC-055)
PROC_RE = re.compile(r'(^|/)gz sim |ros2 launch|parameter_bridge|ros2_control_node|robot_state_publisher'
                     r'|controller_manager|/spawner |ruby .*gz sim')
OVERALL_RE = re.compile(r'^(# overall: .*|== (ALL CHECKS PASSED|\d+ CHECK\(S\) FAILED).*)$')
TS029_RE = re.compile(r'TS-029 attempts declared invalid under DEC-039: (\d+)')


def E(label, cmd, log, stdout_log=False):
    """Suite entry: label, procedure command (str, may use {log} and {tag}), log path (may use {tag}).
    stdout_log: the command prints its result (consistency checkers) and the runner writes stdout+stderr to the log."""
    return {'label': label, 'cmd': cmd, 'log': log, 'stdout_log': stdout_log}


def m2(test, mode, runs):
    return E(f'{test}-{mode}', f'bash {EV}/M2/TEST-M2_procedure.sh {mode} {runs} {{log}}', f'{EV}/M2/{test}-{{tag}}_{mode}.log')


def m3d(test, mode, runs):
    return E(test, f'bash {EV}/M3/TEST-M3-D_procedure.sh {mode} {runs} {{log}}', f'{EV}/M3/{test}-{{tag}}_review.log')


def m4(test, mode):
    return E(f'{test}-{mode}', f'bash {EV}/M4/TEST-M4_procedure.sh {mode} 3 {{log}}', f'{EV}/M4/{test}-{{tag}}_{mode}_review.log')


def m6(label, env, suffix=''):
    """M6 localization run (TEST-M6_procedure.sh, test_plan.md §11): options passed through `env`."""
    return E(label, f'env {env} bash {EV}/M6/TEST-M6_procedure.sh 3 {{log}}',
             f'{EV}/M6/{label[:10]}-{{tag}}{suffix}_review.log')


def m311(mode):
    return E(f'TEST-M3-11-{mode}', f'bash {EV}/M3/TEST-M3-11_procedure.sh {mode} 3 {{log}}',
             f'{EV}/M3/TEST-M3-11-{{tag}}_{mode}_review.log')


SUITES = {
    # TEST-TA-03: the GPU-free checks (build, unit tests, model regression, odometry recomputation).
    # Standalone TEST-M1-08 is deliberately absent (TS-033): its M1-scope source-file assertion fails by design on
    # the M2/M3 Xacro files (TS-016, TS-023). TEST-M3-02 runs the same checker and requires exactly those failures.
    'static': [
        E('TEST-M3-01', f'bash {EV}/M3/TEST-M3-01_procedure.sh -{{tag}}', f'{EV}/M3/TEST-M3-01-{{tag}}_build.log'),
        E('TEST-M3-13', f'bash {EV}/M3/TEST-M3-13_procedure.sh -{{tag}}', f'{EV}/M3/TEST-M3-13-{{tag}}_unit.log'),
        E('TEST-M3-02', f'bash {EV}/M3/TEST-M3-02_procedure.sh -{{tag}}', f'{EV}/M3/TEST-M3-02-{{tag}}_review.log'),
        E('TEST-M4-03', f'python3 -I {EV}/M4/TEST-M4-03_recompute.py', f'{EV}/M4/TEST-M4-03-{{tag}}_recompute.log', True),
        E('TEST-M5-07', f'python3 -I {EV}/M5/TEST-M5-07_distort.py {MAP}', f'{EV}/M5/TEST-M5-07-{{tag}}_review.log', True),
        E('TEST-M6-08', f'python3 -I {EV}/M6/TEST-M6-08_distort.py {EV}/M6/TEST-M6-08_recorded',
          f'{EV}/M6/TEST-M6-08-{{tag}}_review.log', True),
    ],
    # TEST-TA-04: every formal test whose harness uses M2.Spinner (plan §6). Run counts as
    # in the last formal runs (M2 re-test 1, M3 §7.3 re-run, Task E).
    'regression': [
        m2('TEST-M2-03', 'startup', 3), m2('TEST-M2-03', 'fault', 1),
        E('TEST-M2-04', f'bash {EV}/M2/TEST-M2-04_procedure.sh {{log}} {EV}/M2/TEST-M2-04-{{tag}}_frames',
          f'{EV}/M2/TEST-M2-04-{{tag}}_review.log'),
        m2('TEST-M2-05', 'linear', 3), m2('TEST-M2-06', 'rotate', 3),
        m2('TEST-M2-07', 'stop', 3), m2('TEST-M2-07', 'timeout', 3), m2('TEST-M2-07', 'stale', 3),
        m2('TEST-M2-07', 'wallclock', 3), m2('TEST-M2-07', 'domainswitch', 3),
        m2('TEST-M2-08', 'limits', 3), m2('TEST-M2-10', 'rest', 3),
        m3d('TEST-M3-07', 'imu_rest', 2), m3d('TEST-M3-08', 'imu_motion', 3), m3d('TEST-M3-09', 'encoders', 3),
        m311('linear'), m311('rotate'), m311('stop'), m311('timeout'),
        E('TEST-M3-14', f'bash {EV}/M3/TEST-M3-14_procedure.sh 3 {{log}}', f'{EV}/M3/TEST-M3-14-{{tag}}_review.log'),
    ],
    # REQ-M4-11: every automatable M4 test with the commands of test_plan.md §9 and TEST_RESULTS.md § M4.
    # Not here: TEST-M4-10 (the static and regression suites themselves) and TEST-M4-11 (observed in RViz).
    # TEST-M4-09 writes one log per case plus TEST-M4-09-<tag>_check.log, whose overall line the runner reads.
    'm4': [
        E('TEST-M4-01', f'bash {EV}/M4/TEST-M4-01_procedure.sh -{{tag}}', f'{EV}/M4/TEST-M4-01-{{tag}}_review.log'),
        E('TEST-M4-03', f'python3 -I {EV}/M4/TEST-M4-03_recompute.py', f'{EV}/M4/TEST-M4-03-{{tag}}_recompute.log', True),
        m4('TEST-M4-02', 'interface'), m4('TEST-M4-04', 'straight'), m4('TEST-M4-05', 'rotate'),
        m4('TEST-M4-06', 'square_ccw'), m4('TEST-M4-06', 'square_cw'), m4('TEST-M4-07', 'circle'), m4('TEST-M4-08', 'twist'),
        E('TEST-M4-09', f'bash {EV}/M4/TEST-M4-09_procedure.sh -{{tag}} 3', f'{EV}/M4/TEST-M4-09-{{tag}}_check.log'),
    ],
    # REQ-M5-10: every automatable M5 test with the commands of test_plan.md §10 and TEST_RESULTS.md § M5.
    # Not here: TEST-M5-04 (checked inside the TEST-M5-03 runs), TEST-M5-08 (the static, regression and m4 suites
    # themselves) and TEST-M5-09 (observed in RViz).
    # With SHOW=1 add NOREC=1: otherwise attempt 1 of each mapping procedure records into docs/gallery/_pending/.
    'm5': [
        E('TEST-M5-01', f'bash {EV}/M5/TEST-M5-01_procedure.sh -{{tag}}', f'{EV}/M5/TEST-M5-01-{{tag}}_review.log'),
        E('TEST-M5-07', f'python3 -I {EV}/M5/TEST-M5-07_distort.py {MAP}', f'{EV}/M5/TEST-M5-07-{{tag}}_review.log', True),
        E('TEST-M5-02', f'bash {EV}/M5/TEST-M5-02_procedure.sh 3 {{log}}', f'{EV}/M5/TEST-M5-02-{{tag}}_review.log'),
        E('TEST-M5-03', f'bash {EV}/M5/TEST-M5_procedure.sh 3 {{log}}', f'{EV}/M5/TEST-M5-03-{{tag}}_review.log'),
        E('TEST-M5-05', f'bash {EV}/M5/TEST-M5-05_procedure.sh {{log}}', f'{EV}/M5/TEST-M5-05-{{tag}}_review.log'),
        E('TEST-M5-06', f'bash {EV}/M5/TEST-M5-06_procedure.sh 3 {{log}}', f'{EV}/M5/TEST-M5-06-{{tag}}_review.log'),
    ],
    # REQ-M6-13: every automatable M6 test with the commands of test_plan.md §11. Not here: TEST-M6-09 (the static,
    # regression, m4 and m5 suites themselves) and TEST-M6-10 (observed in RViz). With SHOW=1 add NOREC=1: otherwise
    # attempt 1 of each Gazebo procedure records into docs/gallery/_pending/.
    'm6': [
        E('TEST-M6-01', f'bash {EV}/M6/TEST-M6-01_procedure.sh -{{tag}}', f'{EV}/M6/TEST-M6-01-{{tag}}_review.log'),
        E('TEST-M6-08', f'python3 -I {EV}/M6/TEST-M6-08_distort.py {EV}/M6/TEST-M6-08_recorded',
          f'{EV}/M6/TEST-M6-08-{{tag}}_review.log', True),
        E('TEST-M6-02', f'bash {EV}/M6/TEST-M6-02_procedure.sh 3 {{log}}', f'{EV}/M6/TEST-M6-02-{{tag}}_review.log'),
        m6('TEST-M6-03-forward', 'ROUTE=forward', '-forward'), m6('TEST-M6-03-reverse', 'ROUTE=reverse', '-reverse'),
        m6('TEST-M6-04', 'WRONG=1'),
        m6('TEST-M6-05-forward', 'INJECT=1 ROUTE=forward', '-forward'),
        m6('TEST-M6-05-reverse', 'INJECT=1 ROUTE=reverse', '-reverse'),
        m6('TEST-M6-06-forward', f'WORLD={EV}/M6/TEST-M6_unmapped_arena.sdf ROUTE=forward', '-forward'),
        m6('TEST-M6-06-reverse', f'WORLD={EV}/M6/TEST-M6_unmapped_arena.sdf ROUTE=reverse', '-reverse'),
        m6('TEST-M6-07', 'FUSION=1 INJECT=sep'),
    ],
}
# TEST-TA-05 (CI, .github/workflows/ci.yml; plan §7): the same entries as `static`.
# TEST-M5-10 (2026-11-15): TEST-M5-07 (map-checker sensitivity) joins the static and ci suites.
# 2026-11-20: TEST-M6-08 (pose-checker sensitivity) joins the static and ci suites.
SUITES['ci'] = SUITES['static'][:]


def running_sim_processes():
    """Simulation-related processes still alive (excluding this process and its parent shell)."""
    out = subprocess.run(['ps', '-eo', 'pid=,args='], capture_output=True, text=True).stdout
    mine = {os.getpid(), os.getppid()}
    hits = []
    for line in out.splitlines():
        pid, _, args = line.strip().partition(' ')
        if pid.isdigit() and int(pid) not in mine and PROC_RE.search(args) and 'run_suite.py' not in args:
            hits.append(f'{pid} {args[:100]}')
    return hits


def read_result(log):
    """(overall line or None, passing bool, DEC-039 TS-029 count) from a log."""
    try:
        text = open(log, encoding='utf-8', errors='replace').read()
    except FileNotFoundError:
        return None, False, 0
    lines = [ln for ln in text.splitlines() if OVERALL_RE.match(ln.strip())]
    overall = lines[-1].strip() if lines else None
    passing = overall is not None and 'PASS' in overall and 'FAIL' not in overall
    return overall, passing, sum(int(n) for n in TS029_RE.findall(text))


def classify(code, overall, passing):
    if overall is None:
        return 'NO-OVERALL'
    if (code == 0) != passing:
        return 'MISMATCH'
    return 'PASS-candidate' if code == 0 else 'FAIL'


def run_entry(e, tag, env=None):
    log = e['log'].format(tag=tag)
    if os.path.exists(log):
        return {'label': e['label'], 'cmd': e['cmd'].format(log=log, tag=tag), 'log': log, 'code': None,
                'overall': None, 'ts029': 0, 'verdict': 'REFUSED (log exists)', 'seconds': 0.0}
    cmd = e['cmd'].format(log=log, tag=tag)
    t0 = time.monotonic()
    if e['stdout_log']:
        with open(log, 'w', encoding='utf-8') as f:
            code = subprocess.run(shlex.split(cmd), stdout=f, stderr=subprocess.STDOUT, env=env).returncode
    else:
        code = subprocess.run(shlex.split(cmd), env=env).returncode
    seconds = time.monotonic() - t0
    overall, passing, ts029 = read_result(log)
    return {'label': e['label'], 'cmd': cmd, 'log': log, 'code': code, 'overall': overall, 'ts029': ts029,
            'verdict': classify(code, overall, passing), 'seconds': seconds}


def summary_table(results):
    rows = ['| # | Entry | Exit | Overall line | Runner classification | TS-029 invalid (DEC-039) | Duration | Log |',
            '|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(results, 1):
        rows.append(f'| {i} | {r["label"]} | {"—" if r["code"] is None else r["code"]} | {r["overall"] or "—"} | '
                    f'{r["verdict"]} | {r["ts029"]} | {r["seconds"]:.0f} s | `{r["log"]}` |')
    return '\n'.join(rows)


def run_suite(name, entries, tag, check=running_sim_processes, summary_dir=f'{EV}/TA', header=True):
    """Run entries serially; returns (exit code, results). Writes <summary_dir>/<name>-<tag>_summary.md."""
    busy = check()
    if busy:
        print('# refused: simulation processes are running; nothing was started:\n#   ' + '\n#   '.join(busy))
        return 3, []
    summary = os.path.join(summary_dir, f'{name}-{tag}_summary.md')
    if os.path.exists(summary):
        print(f'# refused: {summary} exists (choose a new tag)')
        return 3, []
    results, stopped = [], None
    started = time.strftime('%F %T %Z')
    # Revision and cleanliness at the start: commits made while a long suite runs must not appear as its revision
    # (the M508 regression and m4 headers showed the revision at the finish).
    rev = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', 'amr_ws/src', 'docs/evidence', 'tools']).returncode
    for e in entries:
        if results:
            busy = check()
            if busy:
                stopped = f'simulation processes left after "{results[-1]["label"]}": ' + '; '.join(busy)
                print(f'# suite stopped: {stopped}')
                break
        print(f'## {e["label"]}: {e["cmd"].format(log=e["log"].format(tag=tag), tag=tag)}', flush=True)
        r = run_entry(e, tag)
        print(f'# {r["label"]}: exit {r["code"]}, {r["verdict"]}, {r["seconds"]:.0f} s; {r["overall"]}', flush=True)
        results.append(r)
    ok = not stopped and len(results) == len(entries) and all(r['verdict'] == 'PASS-candidate' for r in results)
    if header:
        end_rev = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
        head = (f'# Suite {name}, tag {tag}: started {started}, finished {time.strftime("%F %T %Z")}, revision {rev}'
                f'{" (amr_ws/src, docs/evidence or tools with uncommitted changes)" if dirty else " (clean)"} at the start'
                f'{"" if end_rev == rev else f"; HEAD {end_rev} at the finish"}\n\n'
                'Runner classification only. **Not a test result**: every log is reviewed by a human before '
                '`TEST_RESULTS.md` changes (DEC-040 item 5).\n\n')
    else:
        head = ''
    tail = (f'\n\n{"Suite stopped: " + stopped if stopped else ""}\n'
            f'# overall: {"ALL ENTRIES PASS-candidate" if ok else "AT LEAST ONE ENTRY NOT PASS-candidate"}\n')
    with open(summary, 'w', encoding='utf-8') as f:
        f.write(head + summary_table(results) + tail)
    print(summary_table(results))
    print(f'# summary: {summary}\n# overall: {"ALL ENTRIES PASS-candidate" if ok else "AT LEAST ONE ENTRY NOT PASS-candidate"}')
    return (0 if ok else 1), results


def self_test():
    """TEST-TA-02: synthetic entries for every classification and refusal; no ROS, no Gazebo."""
    fails = 0

    def expect(ok, text):
        nonlocal fails
        fails += 0 if ok else 1
        print(f'{"PASS" if ok else "FAIL"}  {text}')

    with tempfile.TemporaryDirectory() as d:
        def sh(label, body, stdout_log=False):
            body = body.replace('LOG', '"$1"')
            return E(label, f'bash -c {shlex.quote(body)} x {{log}}' if not stdout_log else f'bash -c {shlex.quote(body)}',
                     os.path.join(d, f'{label}-{{tag}}.log'), stdout_log)
        entries = [
            sh('pass', 'echo "# overall: ALL STEPS PASSED" > LOG; exit 0'),
            sh('fail', 'echo "# overall: AT LEAST ONE STEP FAILED" > LOG; exit 1'),
            sh('mismatch-exit0', 'echo "# overall: AT LEAST ONE STEP FAILED" > LOG; exit 0'),
            sh('mismatch-exit1', 'echo "# overall: ALL 3 VALID RUNS PASSED" > LOG; exit 1'),
            sh('no-overall', 'echo "nothing" > LOG; exit 0'),
            sh('checker', 'echo "PASS  a"; echo "== ALL CHECKS PASSED"; exit 0', stdout_log=True),
            sh('checker-fail', 'echo "FAIL  a"; echo "== 1 CHECK(S) FAILED"; exit 1', stdout_log=True),
            sh('ts029', 'printf "# TS-029 attempts declared invalid under DEC-039: 1\\n# TS-029 attempts declared invalid '
                        'under DEC-039: 2\\n# overall: ALL 3 VALID RUNS PASSED\\n" > LOG; exit 0'),
            sh('exists', f'touch {d}/exists-ran; echo "# overall: PASS" > LOG; exit 0'),
        ]
        open(os.path.join(d, 'exists-T1.log'), 'w').close()
        code, res = run_suite('selftest', entries, 'T1', check=lambda: [], summary_dir=d, header=False)
        got = {r['label']: r for r in res}
        want = {'pass': 'PASS-candidate', 'fail': 'FAIL', 'mismatch-exit0': 'MISMATCH', 'mismatch-exit1': 'MISMATCH',
                'no-overall': 'NO-OVERALL', 'checker': 'PASS-candidate', 'checker-fail': 'FAIL', 'ts029': 'PASS-candidate',
                'exists': 'REFUSED (log exists)'}
        for label, verdict in want.items():
            expect(got.get(label, {}).get('verdict') == verdict, f'{label}: classified {verdict} (got {got.get(label, {}).get("verdict")})')
        expect(got['ts029']['ts029'] == 3, f'TS-029 lines summed to 3 (got {got["ts029"]["ts029"]})')
        expect(not os.path.exists(f'{d}/exists-ran'), 'an entry whose log exists is not executed')
        expect(code == 1, f'mixed suite exits 1 (got {code})')
        expect(os.path.exists(os.path.join(d, 'selftest-T1_summary.md')), 'summary file written')
        code2, _ = run_suite('selftest', entries, 'T1', check=lambda: [], summary_dir=d, header=False)
        expect(code2 == 3, f'existing summary (reused tag) refused with exit 3 (got {code2})')
        code3, res3 = run_suite('allpass', entries[:1], 'T2', check=lambda: [], summary_dir=d, header=False)
        expect(code3 == 0 and len(res3) == 1, f'all-PASS suite exits 0 (got {code3})')
        code4, res4 = run_suite('busy', entries[:1], 'T3', check=lambda: ['123 gz sim -r'], summary_dir=d, header=False)
        expect(code4 == 3 and res4 == [] and not os.path.exists(os.path.join(d, 'pass-T3.log')),
               f'a running simulation refuses the start, exit 3, nothing run (got {code4})')
        calls = iter([[], ['456 ros2 launch amr_bringup sim.launch.py']])
        code5, res5 = run_suite('leftover', entries[:2], 'T4', check=lambda: next(calls), summary_dir=d, header=False)
        expect(code5 == 1 and len(res5) == 1, f'a leftover process between entries stops the suite, exit 1 (got {code5}, {len(res5)} run)')
        expect(bool(PROC_RE.search('gz sim -r -s --headless-rendering w.sdf')) and bool(PROC_RE.search('/usr/bin/python3 /opt/ros/jazzy/bin/ros2 launch x'))
               and not PROC_RE.search('vim notes.txt'), 'process pattern matches gz sim and ros2 launch, not unrelated processes')
    print(f'# overall: {"PASS" if fails == 0 else f"FAIL ({fails})"}')
    return 0 if fails == 0 else 1


def main(argv):
    if argv[1:2] == ['--self-test']:
        return self_test()
    if argv[1:2] == ['--list']:
        for name, entries in SUITES.items():
            print(f'{name}: ' + ', '.join(e['label'] for e in entries))
        return 0
    if len(argv) < 3 or argv[1] not in SUITES or not re.fullmatch(r'[A-Za-z0-9]+', argv[2]):
        print(__doc__)
        return 2
    name, tag, rest = argv[1], argv[2], argv[3:]
    entries = SUITES[name]
    if '--from' in rest:
        start = rest[rest.index('--from') + 1]
        idx = [e['label'] for e in entries].index(start)
        entries = entries[idx:]
    if '--dry-run' in rest:
        for e in entries:
            log = e['log'].format(tag=tag)
            print(f'{e["label"]}: {e["cmd"].format(log=log, tag=tag)}{"  > " + log if e["stdout_log"] else ""}'
                  f'{"   [log exists]" if os.path.exists(log) else ""}')
        return 0
    if 'amr_ws/install' not in os.environ.get('AMENT_PREFIX_PATH', ''):
        print('# refused: source /opt/ros/jazzy/setup.bash and amr_ws/install/setup.bash first')
        return 3
    return run_suite(name, entries, tag)[0]


if __name__ == '__main__':
    sys.exit(main(sys.argv))
