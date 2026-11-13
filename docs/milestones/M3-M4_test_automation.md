# Between M3 and M4 — Test Automation (DEC-040): Plan and Record


**Status:** **Complete** (2026-11-04). In progress since 2026-11-04.
- The detailed scope below was finalized on 2026-11-04, with three choices:
  - re-run every formal test whose harness uses the changed teardown helper;
  - CI in the official `ros:jazzy-ros-base` container;
  - the runner at `tools/run_suite.py`.
- M4 does not start until this step is closed (DEC-040 item 1).

## 1. Purpose
Every formal procedure is started, tracked and cross-checked by hand. This step makes three things cheaper and harder to get wrong:
- running a milestone's suite;
- catching breakage of `main`;
- closing two known harness defects found in M3 (TS-030 and the stop-measurement timing).

It changes **no robot, controller or sensor configuration**. It also changes **no pass criterion**.

## 2. Scope
**In scope (DEC-040 item 2 and the 2026-11-04 scope additions):**
| Item | DEC-040 ref | Requirement |
|---|---|---|
| TS-030: one teardown-safe spin helper used by every formal harness | (c) | REQ-TA-01 |
| Stop-measurement timing INFO in the M2 stop mode | (d) | REQ-TA-02 |
| Local suite runner `tools/run_suite.py` | (a) | REQ-TA-03 |
| Formal regression re-run of every harness user, through the runner | (c), (a) | REQ-TA-04 |
| GitHub Actions CI for GPU-free checks, minutes-budgeted | (b), item 3 | REQ-TA-05 |

**Out of scope:**
- Gazebo sensor tests in CI: hosted runners have no GPU (DEC-040 item 4).
- Automatic PASS recording (item 5).
- Any change to the DEC-027/DEC-036/DEC-038 criteria.
- The `/server_control` stop for TS-029, which is deferred (DEC-039 amendment).

## 3. Requirements and acceptance criteria (Proposed with the plan; accepted 2026-11-04)
| ID | Requirement | Acceptance criterion | Test |
|---|---|---|---|
| REQ-TA-01 | Harness threads stop before ROS shuts down (TS-030) | One helper in `TEST-M2_motion_measure.py` is used by the four formal harnesses (M2 motion, M3 Task D, TEST-M3-11, TEST-M3-14). It stops the spin loop with a flag, joins the thread, and only then shuts the executor, the node and the context down. Every harness prints the thread-end state. The Gazebo-free reproduction script runs the new helper with 0 thread exceptions in 1000 teardowns. | TEST-TA-01, TEST-TA-04 |
| REQ-TA-02 | Stop distance reported with known timing (DEC-040 (d)) | The stop mode adds two INFO lines: (1) the latency from the zero command to the first decrease of `/diff_drive_controller/cmd_vel_out`; (2) the stop distance with the ground truth linearly interpolated at that instant. Pass criteria and their lines are unchanged. | TEST-TA-04 |
| REQ-TA-03 | A milestone suite runs serially and is cross-checked | `tools/run_suite.py <suite>`, as specified in §5. | TEST-TA-02, TEST-TA-03 |
| REQ-TA-04 | The harness changes cause no regression | The accepted re-run set (§6), run through the runner, passes with the original criteria. Every run reports the spin thread "ended cleanly". | TEST-TA-04 |
| REQ-TA-05 | GPU-free checks run on GitHub on code changes only | Workflow `.github/workflows/ci.yml`, as specified in §7. | TEST-TA-05 |

## 4. Steps (one bounded step each; Inspect → Plan → Implement → Build → Test → Verify → Document → Commit)
1. **TS-030 helper** (REQ-TA-01).
   - Add `start_spin(executor)` → `stop()` to `TEST-M2_motion_measure.py`.
   - Switch the four harnesses to it.
   - Keep the excepthook capture (TEST-M3-11 pattern) in the shared helper.
   - Verify with the Gazebo-free reproduction (TEST-TA-01).
2. **Stop timing INFO** (REQ-TA-02). Add it to `mode_stop`. The harness already records `cmd_vel_out` (TEST-M2-07 timeout uses it).
3. **Runner** (REQ-TA-03). Write `tools/run_suite.py`, then run its self-test (TEST-TA-02) and a GPU-free suite (TEST-TA-03).
4. **Formal regression re-run** (REQ-TA-04), through the runner (TEST-TA-04).
5. **CI** (REQ-TA-05). Write the workflow, push, and measure (TEST-TA-05).
6. **Closeout.** Update test_plan, environment, TEST_RESULTS and the roadmap. Retire the TS-030 entry if TEST-TA-04 shows no recurrence.

## 5. Runner specification (REQ-TA-03)
- **Suites** are plain Python lists inside the file. Each entry is a test label, the exact procedure command, and its output log path. The commands are those of `test_plan.md` §6/§7, with nothing re-implemented.
- **Before each entry:**
  - check that no `gz sim`, `ros2 launch`, `ros_gz_bridge` or controller-manager process is running; if one is, stop with exit 3 and start nothing;
  - check that the output log does not already exist, so evidence is never overwritten.
- **Serial execution:** never two Gazebo runs at once. The procedures already set a unique `ROS_DOMAIN_ID`/`GZ_PARTITION` per attempt.
- **After each entry:**
  - record the exit code and the log's `# overall:` line;
  - flag **MISMATCH** if exit 0 comes without a passing overall line, or vice versa (the TEST-M3-04 R1 defect class);
  - also count the procedure's DEC-039 line (TS-029 attempts declared invalid).
- **Output:** a summary table (Markdown) with label, command, exit, overall line, mismatch, TS-029 count and duration, written next to the logs. Runner exit codes: 0 when every entry has exit 0 and no mismatch; 1 otherwise; 3 when refused at the start.
- **The runner states results; it never writes PASS anywhere.** A human reviews every log before `TEST_RESULTS.md` changes (DEC-040 item 5).
- `--dry-run` prints the commands; `--from <label>` resumes a suite.

## 6. Formal regression re-run set (REQ-TA-04; my choice "all harness users")
| Re-run | Procedure (as recorded) | Original criteria |
|---|---|---|
| TEST-M2-03 (startup 3, fault 1), TEST-M2-04 (tfcheck, its own procedure), TEST-M2-05 linear, -06 rotate, -07 stop/timeout/stale/wallclock/domainswitch, -08 limits, -10 rest; 3 valid runs each unless stated | `TEST-M2_procedure.sh`, `TEST-M2-04_procedure.sh` | DEC-027 (DEC-019 for rest) |
| TEST-M3-07 (2), -08 (3), -09 (3) | `TEST-M3-D_procedure.sh` | DEC-036 (DEC-038 for D11) |
| TEST-M3-11, 3 per mode | `TEST-M3-11_procedure.sh` | DEC-027, sensors on |
| TEST-M3-14, 3 runs | `TEST-M3-14_procedure.sh` | DEC-038 |

- Corrected 2026-11-04 (TA Task 2): the first version of this table listed only four M2 modes. Under the accepted rule ("every test whose harness uses the changed helper"), every M2 harness mode that was run formally is included. Estimated runtime 1–1.5 h.
- Estimated runtime 1.5–2 h at planning (Calculated from the 2026-11-04 durations).
- New R numbers are assigned at execution. DEC-039 applies to the sensor launches.

## 7. CI specification (REQ-TA-05; my choice "ros:jazzy container")
- **Runner and container:** `ubuntu-latest` runner, container `ros:jazzy-ros-base`.
- **Dependencies:** `rosdep install --from-paths amr_ws/src`, giving the same apt packages as the development machine.
- **Steps:**
  - `colcon build`;
  - `colcon test` (TEST-M3-13 gtest);
  - the M1 default xacro expansion byte-identical to `docs/evidence/M1/TEST-M1-02_amr.urdf`.
- **Triggers:**
  - `push` to `main` with path filters `amr_ws/**`, `tools/**`, `docs/evidence/**/*.py`, `docs/evidence/**/*.sh`, `.github/workflows/**`;
  - `workflow_dispatch`, which also runs the record-consistency checkers TEST-M2-11 and TEST-M3-12 (DEC-040 item 3; those checkers read my private planning files, so the published workflow runs only the `ci` suite). Standalone TEST-M1-08 is excluded (TS-033); the M1 checker and M1 byte identity run inside TEST-M3-02.
- **Budget measures:**
  - `concurrency` with cancel-in-progress;
  - an apt/rosdep cache where the container allows it. *Not implemented (TEST-TA-05): about 3 min per run, so a cache would save little and could go stale. Confirmed by me on 2026-11-04 (DEC-040 amendment).*
- **Minutes:** the minutes per run are **Measured** at TEST-TA-05 and recorded. I check the account's monthly Actions allowance in GitHub Settings → Billing.

## 8. Tests (PLANNED; procedures in `docs/testing/test_plan.md` §8)
TEST-TA-01 to TEST-TA-05, as listed in §3.

## 9. Risks
- **Rosdep in the container.** Rosdep may pull the full Gazebo vendor stack, which makes CI slow; that is the reason for measuring. Mitigation: cache, or a narrower rosdep skip list (to be decided only with evidence).
- **Other causes of TS-030.** The trigger is unknown. If TEST-TA-04 still shows a spin-thread exception after the fix, TS-030 stays open with the new capture.
- **Runner refusing to start.** The runner's process check could refuse to start because of my own GUI session. That is intended: never two Gazebo runs at once.

## 10. Implementation record
- 2026-11-04: plan written; scope choices finalized.
- 2026-11-04: **TA Task 1 complete.**
  - `M2.Spinner` implemented and used by the four harnesses; stop-timing INFO added (guarded, so it can never fail or invalidate a run). Unused imports removed; pyflakes clean.
  - TEST-TA-01 PASS (1000/1000).
- 2026-11-04: **TA Task 2 complete.**
  - `tools/run_suite.py` with suites `static` (TEST-TA-03) and `regression` (TEST-TA-04, all harness users).
  - TEST-TA-02 PASS (18 checks). TEST-TA-03 FAIL: the suite wrongly included standalone TEST-M1-08 (TS-033), which the runner classified correctly. After the fix, R1 PASS (5/5, logs reviewed).
  - Plan §6 corrected to the full harness-user set; §7 CI checker list corrected (TS-033).
  - Informal Gazebo smoke runs of M2 stop and TEST-M3-11 stop: PASS, with the new INFO lines and a clean thread end.
- 2026-11-04: **TA Task 3 complete.**
  - TEST-TA-04 PASS: `regression` suite, tag TA04, revision `cbb80c3` (clean), 21 min. 20 of 20 entries PASS-candidate; every log reviewed.
  - Spin thread "ended cleanly" in 55 of 55 harness runs, so TS-030 is closed under its criterion; TS-029 invalid 0.
  - Stop timing (REQ-TA-02): from the braking onset, 0.1223–0.1235 m in all six stop runs, sensors on and off. The criterion values spread 0.1203–0.1290 m, so the TEST-M3-11 3–6 mm difference was measurement timing (`TEST_RESULTS.md`, TA Task 3).
- 2026-11-04: **TA Task 4 complete.**
  - `.github/workflows/ci.yml`; runner suites `ci` and `records` (the `static` entries split by trigger). Git and procps are installed before checkout; the records step runs before the `ci` suite (the checkers require every evidence file to be indexed).
  - TEST-TA-05: run 1 FAIL (TS-034, shallow checkout; fixed with `fetch-depth: 0`), run 2 PASS on a code push, a documentation-only push started no run, run 3 (dispatch with the record checkers) PASS. About 3 min per run (Measured).
- 2026-11-04: **Closeout (step 6).**
  - All REQ-TA-01 to -05 acceptance criteria are met (TEST-TA-01 to -05 PASS; failure history TS-033, TS-034 kept). TS-030 resolved.
  - From M4 on, test results are written only in `TEST_RESULTS.md`; plans and records link to them.
  - DEC-040 item 3 listed "dependencies are cached"; the workflow has none. I confirmed "no cache" on 2026-11-04 (DEC-040 amendment). I also set the account's $0 Actions budget, and the job timeout is 10 min.
  - M4 is next.
