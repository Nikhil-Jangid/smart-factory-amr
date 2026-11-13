#!/usr/bin/env python3
"""TEST-M1-08: test-record and evidence consistency for M1.

Usage, from the repository root:  python3 -I docs/evidence/M1/TEST-M1-08_records_check.py

Checks that:
  * every executed M1 test (status other than PLANNED in the TEST_RESULTS.md summary) has a
    record heading in TEST_RESULTS.md and at least one evidence link in its summary row;
  * the summary status, the test_plan.md §4 status and the requirements.md traceability agree
    (the test plan cell must start with the same verdict as the summary; a test that the summary
    lists as PLANNED must not be called PASS or FAIL anywhere);
  * every relative link in TEST_RESULTS.md, test_plan.md, requirements.md and the evidence
    README resolves to an existing file;
  * every file in docs/evidence/M1/ is listed in docs/evidence/README.md, and every TEST-M1
    evidence file is also referenced from TEST_RESULTS.md (the R-08 probe files are referenced
    from frames_and_tf.md instead, as the evidence README states).
TEST-M1-08's own evidence is excluded from the "referenced" check while its record is being written.
Exits 0 only if every check passes.
"""
import os
import re
import sys

failures = 0
EV = 'docs/evidence/M1'
SELF_PREFIX = 'TEST-M1-08'  # TEST-M1-08_* and TEST-M1-08-R1_* (the test's own evidence)


def report(ok, label, detail=''):
    global failures
    failures += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'}  {label}{'  [' + detail + ']' if detail else ''}")


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def verdict(text):
    m = re.match(r'\s*(PASS|FAIL|PLANNED|BLOCKED|NOT RUN)', text)
    return m.group(1) if m else None


results = read('TEST_RESULTS.md')
plan = read('docs/testing/test_plan.md')
reqs = read('docs/requirements.md')
readme = read(f'{EV}/../README.md')

print('== 1. Summary table vs records and test plan')
summary = {}
for line in results.splitlines():
    m = re.match(r'\| (TEST-M1-0\d)( \(re-test (\d+)[^)]*\))? \| M1 \| ([^|]+)\| ([^|]*)\|', line)
    if m:
        summary[(m.group(1), m.group(3))] = (m.group(4).strip(), m.group(5).strip())
    m = re.match(r'\| TEST-M1-0(\d) to TEST-M1-0(\d) \| M1 \| ([^|]+)\|', line)
    if m:
        for n in range(int(m.group(1)), int(m.group(2)) + 1):
            summary[(f'TEST-M1-0{n}', None)] = (m.group(3).strip(), '—')
tests = sorted({t for t, _ in summary})
report(tests == [f'TEST-M1-0{n}' for n in range(1, 9)], 'summary covers TEST-M1-01 to -08', ', '.join(tests))
plan_status = {}
for line in plan.splitlines():
    m = re.match(r'\| (TEST-M1-0\d) [^|]*\|.*\| ([^|]+) \|$', line)
    if m:
        plan_status[m.group(1)] = m.group(2)
for (test, retest), (status, evidence) in sorted(summary.items(), key=lambda kv: (kv[0][0], kv[0][1] or '')):
    label = test + (f' re-test {retest}' if retest else '')
    v = verdict(status)
    if v == 'PLANNED':
        report(not re.search(rf'^### {test}\b', results, re.M), f'{label}: PLANNED and has no execution record')
        report(verdict(plan_status.get(test, '')) == 'PLANNED', f'{label}: test plan also PLANNED', plan_status.get(test, '?')[:40])
        continue
    heading = rf'^### {test} \(re-test {retest}\)' if retest else rf'^### {test} — '
    report(bool(re.search(heading, results, re.M)), f'{label}: summary {v}, record heading present')
    report('](' in evidence, f'{label}: summary row links evidence', evidence[:60])
    if not retest:
        report(verdict(plan_status.get(test, '')) == v, f'{label}: test plan status starts with {v}', plan_status.get(test, '?')[:50])

print('== 2. Requirements traceability (requirements.md) vs executed tests')
for line in reqs.splitlines():
    m = re.match(r'\| (REQ-M1-\d\d) \|.*\| ([^|]*TEST-M1-[^|]*) \| ([^|]+) \|$', line)
    if not m:
        continue
    req, cell = m.group(1), m.group(3)
    planned_tests = [t for t in re.findall(r'TEST-M1-0\d', m.group(2)) if verdict(summary.get((t, None), ('',))[0]) == 'PLANNED']
    done_tests = [t for t in re.findall(r'TEST-M1-0\d', m.group(2)) if t not in planned_tests]
    claims_pass_for_planned = any(re.search(rf'{t} PASS', cell) for t in planned_tests)
    ok = not claims_pass_for_planned and (('PASS' in cell) if done_tests else verdict(cell) == 'PLANNED')
    report(ok, f'{req}: result cell consistent with its tests ({", ".join(done_tests) or "none"} executed)', cell[:70])

print('== 3. Relative links resolve')
for doc in ('TEST_RESULTS.md', 'docs/testing/test_plan.md', 'docs/requirements.md', 'docs/evidence/README.md'):
    base = os.path.dirname(doc)
    links = [t for t in re.findall(r'\]\(([^)#\s]+)', read(doc)) if not t.startswith('http')]
    missing = [t for t in links if not os.path.exists(os.path.normpath(os.path.join(base, t)))]
    report(not missing, f'{doc}: {len(links)} relative links resolve', ', '.join(missing))

print('== 4. Evidence files are indexed and referenced')
for name in sorted(os.listdir(EV)):
    if name.startswith(SELF_PREFIX):
        continue
    report(f'M1/{name}' in readme, f'{name}: listed in docs/evidence/README.md')
    if name.startswith('TEST-M1'):
        report(f'{EV}/{name}' in results, f'{name}: referenced from TEST_RESULTS.md')

print(f'== {"ALL CHECKS PASSED" if failures == 0 else f"{failures} CHECK(S) FAILED"}')
sys.exit(1 if failures else 0)
