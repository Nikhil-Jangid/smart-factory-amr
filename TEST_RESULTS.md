# Test Results

This file records actual tests performed during development.

Do not add expected or invented results here. Only record tests that were actually performed.

Planned tests, procedures, and state definitions (`PLANNED`, `NOT RUN`, `PASS`, `FAIL`, `BLOCKED`) are in [docs/testing/test_plan.md](docs/testing/test_plan.md). The evidence policy is in [docs/evidence/README.md](docs/evidence/README.md). The environment is described in [docs/environment.md](docs/environment.md).

## Summary

| Test | Milestone | Status | Evidence |
|---|---|---|---|
| TEST-M0-00 | M0 | PASS | none (recorded observation) |
| TEST-M0-01 | M0 | PASS | [log](docs/evidence/M0/TEST-M0-01_talker_listener.log) |
| TEST-M0-02 | M0 | PASS | observed by me |
| TEST-M0-03 | M0 | PASS | observed by me |
| TEST-M0-04 | M0 | PASS | observed by me |
| TEST-M0-04 (re-test 1, headless) | M0 | PASS | [log](docs/evidence/M0/TEST-M0-04-R1_clock_bridge_headless.log), [procedure](docs/evidence/M0/TEST-M0-04-R1_procedure.sh) |
| TEST-M0-05 | M0 | PASS | [log](docs/evidence/M0/TEST-M0-05_environment_inventory.log), [procedure](docs/evidence/M0/TEST-M0-05_procedure.sh) |
| TEST-M1-01 | M1 | PASS | [log](docs/evidence/M1/TEST-M1-01_build.log) |
| TEST-M1-01 (re-test 1, licence change) | M1 | PASS | [log](docs/evidence/M1/TEST-M1-01-R1_build.log), [package output (sanitized)](docs/evidence/M1/TEST-M1-01-R1_package_output_sanitized.log) |
| TEST-M1-02 | M1 | PASS | [check_urdf log](docs/evidence/M1/TEST-M1-02_check_urdf.log), [generated URDF](docs/evidence/M1/TEST-M1-02_amr.urdf) |
| TEST-M1-03 | M1 | FAIL (check-script false positive, TS-007) | [log](docs/evidence/M1/TEST-M1-03_check.log) |
| TEST-M1-03 (re-test 1, corrected check) | M1 | PASS | [log](docs/evidence/M1/TEST-M1-03-R1_check.log), [check script](docs/evidence/M1/TEST-M1-03_check.py), [generated SDF](docs/evidence/M1/TEST-M1-03_amr.sdf), [tree](docs/evidence/M1/TEST-M1-03_amr_tree.pdf) |
| TEST-M1-04 | M1 | PASS (visual criteria observed by me) | [tf2_echo log](docs/evidence/M1/TEST-M1-04_tf2_echo.log), [wheel rotation log](docs/evidence/M1/TEST-M1-04_wheel_rotation.log), [launch log (sanitized)](docs/evidence/M1/TEST-M1-04_display_launch_sanitized.log) |
| TEST-M1-05 | M1 | PASS | [frames.gv](docs/evidence/M1/TEST-M1-05_frames.gv), [frames.pdf](docs/evidence/M1/TEST-M1-05_frames.pdf), [log](docs/evidence/M1/TEST-M1-05_view_frames.log) |
| TEST-M1-06 | M1 | PASS (visual criteria observed by me) | [model list](docs/evidence/M1/TEST-M1-06_model_list.log), [launch log (sanitized)](docs/evidence/M1/TEST-M1-06_gazebo_launch_sanitized.log), [build log](docs/evidence/M1/TEST-M1-06_build.log) |
| TEST-M1-07 | M1 | PASS (jitter criterion observed by me) | [measurement log](docs/evidence/M1/TEST-M1-07_measure.log), [measurement script](docs/evidence/M1/TEST-M1-07_measure.py) |
| TEST-M1-08 | M1 | FAIL (procedure defect, TS-010) | [review log](docs/evidence/M1/TEST-M1-08_review.log), [mesh check](docs/evidence/M1/TEST-M1-08_mesh_check.log) |
| TEST-M1-08 (re-test 1, corrected procedure) | M1 | PASS | [review log](docs/evidence/M1/TEST-M1-08-R1_review.log), [mesh check](docs/evidence/M1/TEST-M1-08-R1_mesh_check.log), [procedure](docs/evidence/M1/TEST-M1-08_procedure.sh), [consistency check](docs/evidence/M1/TEST-M1-08_consistency_check.py), [records check](docs/evidence/M1/TEST-M1-08_records_check.py) |
| TEST-M2-01 | M2 | PASS | [build log](docs/evidence/M2/TEST-M2-01_build.log) |
| TEST-M2-02 | M2 | FAIL (procedure defect, TS-016; every model check passed) | [review log](docs/evidence/M2/TEST-M2-02_review.log), [procedure](docs/evidence/M2/TEST-M2-02_procedure.sh) |
| TEST-M2-03 | M2 | PASS (3/3 startup runs; fault characterized: robot stops) | [startup log](docs/evidence/M2/TEST-M2-03_startup.log), [fault log](docs/evidence/M2/TEST-M2-03_fault.log) |
| TEST-M2-04 | M2 | FAIL (`/gz_ros_control` use_sim_time false, TS-018; `/clock` check parse defect and shutdown hang, TS-017) | [review log](docs/evidence/M2/TEST-M2-04_review.log), [frames.gv](docs/evidence/M2/TEST-M2-04_frames.gv), [frames.pdf](docs/evidence/M2/TEST-M2-04_frames.pdf) |
| TEST-M2-05 | M2 | PASS (3/3 runs) | [log](docs/evidence/M2/TEST-M2-05_linear.log) |
| TEST-M2-06 | M2 | FAIL (3/3 runs: about 196.5° for a 180° command, TS-014) | [log](docs/evidence/M2/TEST-M2-06_rotate.log) |
| TEST-M2-07 | M2 | PASS (stop, timeout, stale 3/3); wall-clock characterization: HAZARD, TS-015 | [stop](docs/evidence/M2/TEST-M2-07_stop.log), [timeout](docs/evidence/M2/TEST-M2-07_timeout.log), [stale](docs/evidence/M2/TEST-M2-07_stale.log), [wallclock](docs/evidence/M2/TEST-M2-07_wallclock.log) |
| TEST-M2-08 | M2 | FAIL (yaw rate 1.096 rad/s > 1.05 in 3/3 runs; angular acceleration 2.2036 > 2.2 in 1 run; TS-014) | [log](docs/evidence/M2/TEST-M2-08_limits.log) |
| TEST-M2-09 | M2 | NOT RUN (needs a GUI session; formal suite 1) | — |
| TEST-M2-10 | M2 | BLOCKED (quantitative OPEN-07 criteria passed in 3/3 runs; the visual jitter criterion needs a GUI observation) | [log](docs/evidence/M2/TEST-M2-10_rest.log) |
| TEST-M2-01 (re-test 1, `7b90453`) | M2 | PASS | [build log](docs/evidence/M2/TEST-M2-01-R1_build.log) |
| TEST-M2-02 (re-test 1, `7b90453`) | M2 | FAIL (procedure not updated for DEC-028, TS-019; default variant fully passed) | [review log](docs/evidence/M2/TEST-M2-02-R1_review.log) |
| TEST-M2-02 (re-test 2, `96b226b`, corrected procedure) | M2 | PASS | [review log](docs/evidence/M2/TEST-M2-02-R2_review.log), [procedure](docs/evidence/M2/TEST-M2-02_procedure.sh) |
| TEST-M2-03 (re-test 1, `7b90453`) | M2 | PASS | [startup](docs/evidence/M2/TEST-M2-03-R1_startup.log), [fault](docs/evidence/M2/TEST-M2-03-R1_fault.log) |
| TEST-M2-04 (re-test 1, `7b90453`) | M2 | PASS | [review log](docs/evidence/M2/TEST-M2-04-R1_review.log), [frames.gv](docs/evidence/M2/TEST-M2-04-R1_frames.gv), [frames.pdf](docs/evidence/M2/TEST-M2-04-R1_frames.pdf) |
| TEST-M2-05 (re-test 1, `7b90453`) | M2 | PASS | [log](docs/evidence/M2/TEST-M2-05-R1_linear.log) |
| TEST-M2-06 (re-test 1, `7b90453`, DEC-028 sphere collision) | M2 | PASS | [log](docs/evidence/M2/TEST-M2-06-R1_rotate.log) |
| TEST-M2-07 (re-test 1, `7b90453` / `4a8aafa`, DEC-029 guard) | M2 | PASS (stop, timeout, stale, wallclock, domainswitch 3/3 each) | [stop](docs/evidence/M2/TEST-M2-07-R1_stop.log), [timeout](docs/evidence/M2/TEST-M2-07-R1_timeout.log), [stale](docs/evidence/M2/TEST-M2-07-R1_stale.log), [wallclock](docs/evidence/M2/TEST-M2-07-R1_wallclock.log), [domainswitch](docs/evidence/M2/TEST-M2-07-R1_domainswitch.log) |
| TEST-M2-08 (re-test 1, `7b90453`) | M2 | PASS | [log](docs/evidence/M2/TEST-M2-08-R1_limits.log) |
| TEST-M2-10 (re-test 1, `7b90453`) | M2 | BLOCKED (quantitative OPEN-07 criteria passed 3/3 on the sphere model; visual jitter needs a GUI session) | [log](docs/evidence/M2/TEST-M2-10-R1_rest.log) |
| TEST-M2-11 | M2 | FAIL (checker did not exclude its own log, TS-020; every other check passed) | — (checker reads my private planning files; script and log not published) |
| TEST-M2-11 (re-test 1, corrected checker) | M2 | PASS (111 checks) | — (checker reads my private planning files; script and log not published) |
| TEST-M2-09 (GUI session, 2026-11-03) | M2 | PASS (observed by me: forward, reverse, rotate both ways, stop; key-release timing not observed) | — (visual observation; no evidence file) |
| TEST-M2-10 (re-test 1 completed, GUI session 2026-11-03) | M2 | PASS (quantitative 3/3 from re-test 1; no visible jitter, observed by me) | [log](docs/evidence/M2/TEST-M2-10-R1_rest.log) |
| TEST-M2-11 (re-test 2, final M2 records) | M2 | PASS (111 checks) | — (checker reads my private planning files; script and log not published) |
| TEST-M3-01 | M3 | PASS (exit 0, no warnings) | [build log](docs/evidence/M3/TEST-M3-01_build.log) |
| TEST-M3-02 | M3 | FAIL (checker defect: XML tail whitespace in 5 new assertions, TS-024; every byte comparison and M1/M2 check passed) | [review log](docs/evidence/M3/TEST-M3-02_review.log) |
| TEST-M3-02 (re-test 1, corrected checker) | M3 | PASS | [review log](docs/evidence/M3/TEST-M3-02-R1_review.log), [procedure](docs/evidence/M3/TEST-M3-02_procedure.sh), [checker](docs/evidence/M3/TEST-M3-02_model_check.py) |
| TEST-M3-03 | M3 | FAIL (harness aborted before any check, TS-025; no measurement) | [log](docs/evidence/M3/TEST-M3-03_attempt1_aborted.log) |
| TEST-M3-03 (re-test 1, corrected procedure) | M3 | PASS | [review log](docs/evidence/M3/TEST-M3-03-R1_review.log), [frames.pdf](docs/evidence/M3/TEST-M3-03-R1_frames.pdf), [TF check](docs/evidence/M3/TEST-M3-03_tf_check.py) |
| TEST-M3-01 (re-test 1, after the Task B changes) | M3 | PASS (exit 0, no warnings) | [build log](docs/evidence/M3/TEST-M3-01-R1_build.log) |
| TEST-M3-04 | M3 | PASS (D1–D4; default launch = M2) | [review log](docs/evidence/M3/TEST-M3-04_review.log), [procedure](docs/evidence/M3/TEST-M3-04_procedure.sh), [topics check](docs/evidence/M3/TEST-M3-04_topics_check.py) |
| TEST-M3-05 | M3 | PASS (S1–S4 at 1, 3, 6 m) | [review log](docs/evidence/M3/TEST-M3-05_review.log), [checker](docs/evidence/M3/TEST-M3-C_lidar_check.py) |
| TEST-M3-06 | M3 | PASS (D6–D8) | [review log](docs/evidence/M3/TEST-M3-06_review.log) |
| TEST-M3-07 | M3 | PASS (D9; S1–S4 on 6 channels) | [review log](docs/evidence/M3/TEST-M3-07_review.log), [harness](docs/evidence/M3/TEST-M3-D_imu_encoder_measure.py) |
| TEST-M3-08 | M3 | FAIL (D11 in 3/3 runs: IMU accel x ≈ 0 during a 0.5 m/s² ramp, TS-027; D10 PASS 3/3) | [review log](docs/evidence/M3/TEST-M3-08_review.log), [TS-027 diagnostic](docs/evidence/M3/TS-027_imu_linear_accel_diag.log) |
| TEST-M3-09 | M3 | PASS (D12, 3/3 runs) | [review log](docs/evidence/M3/TEST-M3-09_review.log) |
| *DEC-038 pre-fix batch, 2026-11-03 19:51–20:01 (superseded; to be re-run on the fixed build; not used for acceptance)* | | | |
| TEST-M3-01 (re-test 2, clean build) | M3 | PASS (exit 0, 0 warnings, plugin and hook installed) | [build log](docs/evidence/M3/TEST-M3-01-R2_build.log) |
| TEST-M3-13 | M3 | PASS (13/13 gtest cases) | [log](docs/evidence/M3/TEST-M3-13_unit.log), [test source](amr_ws/src/amr_gazebo_plugins/test/test_imu_block_averager.cpp) |
| TEST-M3-02 (re-test 2) | M3 | PASS (M1 byte-identical; IMU and plugin = DEC-038) | [review log](docs/evidence/M3/TEST-M3-02-R2_review.log) |
| TEST-M3-03 (re-test 2) | M3 | PASS (D5) | [review log](docs/evidence/M3/TEST-M3-03-R2_review.log) |
| TEST-M3-04 (re-test 1) | M3 | FAIL (all D1–D4 and 10 ms-grid checks passed; `gz sim` needed SIGKILL at shutdown, 3 [ERROR] lines, TS-029) | [review log](docs/evidence/M3/TEST-M3-04-R1_review.log) |
| TEST-M3-05 (re-test 1), TEST-M3-06 (re-test 1) | M3 | PASS | [05 log](docs/evidence/M3/TEST-M3-05-R1_review.log), [06 log](docs/evidence/M3/TEST-M3-06-R1_review.log) |
| TEST-M3-07 (re-test 1) | M3 | PASS (2/2 runs; S2 0.96–1.05 on 6 channels) | [review log](docs/evidence/M3/TEST-M3-07-R1_review.log) |
| TEST-M3-08 (re-test 1) | M3 | PASS (3/3 runs; D11 −0.41 / +0.16 / +0.13 %) | [review log](docs/evidence/M3/TEST-M3-08-R1_review.log) |
| TEST-M3-09 (re-test 1) | M3 | PASS (3/3 runs) | [review log](docs/evidence/M3/TEST-M3-09-R1_review.log) |
| TEST-M3-14 | M3 | FAIL (all (a)–(f) checks passed in 3/3 runs; `gz sim` exceeded 5 s after SIGINT in runs 1–2, TS-029) | [review log](docs/evidence/M3/TEST-M3-14_review.log) |
| *DEC-038 formal re-run, 2026-11-04 15:52–16:13 on `4961817` (counts for the plugin step and Task D)* | | | |
| TEST-M3-01 (R3, clean build) | M3 | PASS (exit 0, 0 warnings) | [build log](docs/evidence/M3/TEST-M3-01-R3_build.log) |
| TEST-M3-13 (R1) | M3 | PASS (13/13) | [log](docs/evidence/M3/TEST-M3-13-R1_unit.log) |
| TEST-M3-02 (R3) | M3 | PASS (M1 byte-identical; IMU and plugin = DEC-038) | [review log](docs/evidence/M3/TEST-M3-02-R3_review.log) |
| TEST-M3-03 (R3) | M3 | PASS (D5) | [review log](docs/evidence/M3/TEST-M3-03-R3_review.log) |
| TEST-M3-04 (R2) | M3 | PASS (D1–D4, 10 ms grid; shutdowns CLEAN) | [review log](docs/evidence/M3/TEST-M3-04-R2_review.log) |
| TEST-M3-05 (R2), TEST-M3-06 (R2) | M3 | PASS (TEST-M3-06 attempt 1 INVALID under DEC-039, TS-029) | [05 log](docs/evidence/M3/TEST-M3-05-R2_review.log), [06 log](docs/evidence/M3/TEST-M3-06-R2_review.log) |
| TEST-M3-07 (R2) | M3 | PASS (2/2; S2 0.966–1.028) | [review log](docs/evidence/M3/TEST-M3-07-R2_review.log) |
| TEST-M3-08 (R2) | M3 | PASS (3/3; D11 −0.26 / +0.39 / +0.05 %) | [review log](docs/evidence/M3/TEST-M3-08-R2_review.log) |
| TEST-M3-09 (R2) | M3 | PASS (3/3; TS-030 note) | [review log](docs/evidence/M3/TEST-M3-09-R2_review.log) |
| TEST-M3-14 (R1), TEST-M3-14 (g) (R1) | M3 | PASS (3/3; invalid configurations refused; TS-030 note) | [review log](docs/evidence/M3/TEST-M3-14-R1_review.log), [(g) log](docs/evidence/M3/TEST-M3-14g-R1_review.log) |
| TEST-M2-11 (R3) | M2 | FAIL (checker counted the git-ignored `__pycache__`, TS-031) | — (checker reads my private planning files; script and log not published) |
| TEST-M2-11 (R4, corrected checker) | M2 | PASS (111 checks) | — (checker reads my private planning files; script and log not published) |
| *Task E, 2026-11-04* | | | |
| TEST-M3-11 | M3 | PASS (linear, rotate, stop, timeout 3/3 each, sensors on; DEC-027 criteria) | [linear](docs/evidence/M3/TEST-M3-11_linear_review.log), [rotate](docs/evidence/M3/TEST-M3-11_rotate_review.log), [stop](docs/evidence/M3/TEST-M3-11_stop_review.log), [timeout](docs/evidence/M3/TEST-M3-11_timeout_review.log), [harness](docs/evidence/M3/TEST-M3-11_m2_regression.py) |
| TEST-M3-01 (R4, clean build, `sensors.rviz` installed) | M3 | PASS (exit 0, 0 warnings) | [build log](docs/evidence/M3/TEST-M3-01-R4_build.log) |
| TEST-M3-10 | M3 | PASS (observed by me, 2026-11-04: four scan lines at the target positions, none for the low target; `laser_frame` and `imu_link` labelled; IMU via topic) | [RViz](docs/evidence/M3/TEST-M3-10_rviz.png), [Gazebo](docs/evidence/M3/TEST-M3-10_gazebo_gui.png), [launch log](docs/evidence/M3/TEST-M3-10_gui_launch.log), [IMU echo](docs/evidence/M3/TEST-M3-10_imu_echo.log) |
| TEST-M3-12 | M3 | FAIL (TEST-M3-10 record not in the record format, TS-032; configuration and all other records passed) | — (checker reads my private planning files; script and log not published) |
| TEST-M3-12 (R1, record corrected) | M3 | PASS (232 checks) | — (checker reads my private planning files; script and log not published) |
| TEST-TA-01 | Test automation | PASS (1000 of 1000 teardowns ended cleanly; no Gazebo) | [log](docs/evidence/TA/TEST-TA-01_spinner_teardown.log), [script](docs/evidence/TA/TEST-TA-01_spinner_teardown.py) |
| TEST-TA-02 | Test automation | PASS (runner self-test, 18 checks) | [log](docs/evidence/TA/TEST-TA-02_runner_selftest.log) |
| TEST-TA-03 | Test automation | FAIL (suite-definition defect TS-033: standalone TEST-M1-08 included; runner classified it correctly) | [summary](docs/evidence/TA/static-TA03_summary.md) |
| TEST-TA-03 (R1, suite corrected) | Test automation | PASS (5 of 5 entries PASS-candidate, logs reviewed) | [summary](docs/evidence/TA/static-TA03R1_summary.md) |
| TEST-TA-04 | Test automation | PASS (20 of 20 regression entries, logs reviewed; spin thread ended cleanly in 55 of 55 runs; TS-029 invalid 0) | [summary](docs/evidence/TA/regression-TA04_summary.md) |
| TEST-TA-05 | Test automation | FAIL at CI run 1 (TS-034: shallow checkout), then PASS: code push run 2 green, documentation-only push started no run, dispatch run 3 green; about 3 min per run | [run 1](docs/evidence/TA/ci-CI1a1_summary.md), [run 2](docs/evidence/TA/ci-CI2a1_summary.md), [run 3](docs/evidence/TA/ci-CI3a1_summary.md) |
| TEST-M4-03 | M4 | PASS (700/700 odometry messages recomputed from joint_states; max 0.000000 mm, 0.00000000°) | [record log](docs/evidence/M4/TEST-M4-03_record.log), [recompute log](docs/evidence/M4/TEST-M4-03_recompute.log) |
| TEST-M4-01 | M4 | PASS (build clean; M1 and M2 expansions identical; only the two covariance keys added) | [review log](docs/evidence/M4/TEST-M4-01_review.log) |
| TEST-M4-02 | M4 | PASS (3/3 runs; covariance = CALC-M4-04, TF = odometry) | [review log](docs/evidence/M4/TEST-M4-02_review.log) |
| TEST-M4-04 | M4 | PASS (3/3; max distance error 0.0045 %, heading 0.0000°) | [review log](docs/evidence/M4/TEST-M4-04_straight_review.log) |
| TEST-M4-05 | M4 | PASS (3/3; max yaw error 0.0114° per turn, position 0.00 mm) | [review log](docs/evidence/M4/TEST-M4-05_rotate_review.log) |
| TEST-M4-06 | M4 | PASS (CCW 3/3, CW 3/3; max 0.13 mm, 0.0006°) | [CCW log](docs/evidence/M4/TEST-M4-06_square_ccw_review.log), [CW log](docs/evidence/M4/TEST-M4-06_square_cw_review.log) |
| TEST-M4-07 | M4 | PASS (3/3; max 0.04 mm, 0.0048°) | [review log](docs/evidence/M4/TEST-M4-07_circle_review.log) |
| TEST-M4-08 | M4 | PASS (3/3; twist +0.17 to +0.22 % high in all runs) | [review log](docs/evidence/M4/TEST-M4-08_twist_review.log) |
| TEST-M4-09 | M4 | PASS (every injected error FAILs its target test, 21/21 within 1 % of CALC-M4-05; product file unchanged) | [check log](docs/evidence/M4/TEST-M4-09_check.log) |
| TEST-M4-09 R1 | M4 | PASS (re-run for clean pictures; 25/25 checks, agrees with the first run) | [check log](docs/evidence/M4/TEST-M4-09-R1_check.log) |
| TEST-M4-11 | M4 | PASS (observed by me: trail closed in both squares, robot and TF moved smoothly) | [CCW log](docs/evidence/M4/TEST-M4-11_square_ccw_review.log), [CW log](docs/evidence/M4/TEST-M4-11_square_cw_review.log) |
| TEST-M4-12 | M4 | PASS (checker 0 mismatches locally and in CI; `m4` suite present; TEST-M4-03 in `ci`; CI runs #15 and #16 green) | — (checker reads my private planning files; script and log not published) |
| TEST-M4-10 | M4 | PASS (regression 20/20 and static 5/5 entries reviewed; M2 with GUI, M3 headless) | [regression summary](docs/evidence/TA/regression-M410_summary.md), [static summary](docs/evidence/TA/static-M410R2_summary.md) |

**Disclosure:** the M0 acceptance criteria (REQ-M0-01 to REQ-M0-05 in [docs/requirements.md](docs/requirements.md)) were written on 2026-10-19, *after* TEST-M0-00 to TEST-M0-04 had been run. The tests were judged against the expected results recorded in each entry. TEST-M0-04 re-test 1 and TEST-M0-05 were run after the criteria were written.

## TEST-M0-00 — Initial Repository Test
*(ID assigned retroactively on 2026-10-19; content unchanged.)*

**Date:** 2026-09-30

**Test:** Verify Git repository status.

**Command:**
```bash
git status
```

**Result:** PASS

**Observation:** Repository is on the `main` branch with no commits yet and a clean working tree.

## M0 — Development Environment Verification

Environment for all M0 tests: Ubuntu 24.04.5 LTS (native), ROS 2 Jazzy (`/opt/ros/jazzy`, sourced from `~/.bashrc`), Gazebo Sim 8.15.0, `ros-jazzy-rviz2` 14.1.24, `ros-jazzy-ros-gz` 1.0.24. Default RMW, `ROS_DOMAIN_ID` unset (0), `ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`.

### TEST-M0-01 — ROS 2 talker/listener
**Date:** 2026-10-19
**Milestone:** M0
**Test:** Verify ROS 2 publish/subscribe between two nodes using `demo_nodes_cpp`.
**Commands:**
```bash
timeout 12 ros2 run demo_nodes_cpp listener   # started first
timeout 8 ros2 run demo_nodes_cpp talker
```
**Expected:** Listener receives every message the talker publishes on `/chatter`.
**Actual:** Talker published `Hello World: 1` through `Hello World: 7`; listener logged `I heard: [Hello World: N]` for all 7. The talker's exit code 124 (stopped by the planned `timeout`) was observed in the terminal but is not captured in the committed log. The listener's exit code was not captured. The log shows the `signal_handler(SIGINT/SIGTERM)` shutdown message for both processes, consistent with the planned timeouts.
*(Corrected 2026-10-19: the original text said "Both processes exited with code 124", which the evidence does not support for the listener.)*
**Result:** PASS
**Measurements:** 7/7 messages received. Log timestamps show each message received ~0.2–0.4 ms after publication (same machine).
**Notes:** Run in a terminal; output captured and reviewed.
**Evidence:** [docs/evidence/M0/TEST-M0-01_talker_listener.log](docs/evidence/M0/TEST-M0-01_talker_listener.log), the unmodified captured output (added 2026-10-19 as part of the M1 documentation baseline).

### TEST-M0-02 — Gazebo Harmonic GUI
**Date:** 2026-10-19
**Milestone:** M0
**Test:** Verify Gazebo Sim GUI launches and simulates a sample world.
**Command (suggested to user):**
```bash
gz sim -v 4 shapes.sdf
```
**Expected:** `shapes.sdf` world renders; simulation time advances after Play; RTF near 100%.
**Actual:** `shapes.sdf` loaded; simulation time advanced after pressing Play.
**Result:** PASS
**Measurements:** Observed RTF approximately 100%.
**Notes:** Performed and observed by me. Qt QML binding-loop warnings appeared; no fatal error was observed.

### TEST-M0-03 — RViz2
**Date:** 2026-10-19
**Milestone:** M0
**Test:** Verify RViz2 launches with working OpenGL rendering.
**Command:** `rviz2` launched by me (exact invocation not captured in this record).
**Expected:** RViz2 window opens without fatal errors.
**Actual:** Window opened and reported OpenGL 4.6.
**Result:** PASS
**Measurements:** OpenGL version 4.6.
**Notes:** Performed and observed by me. `Stereo is NOT SUPPORTED` was printed; this is informational. No fatal error was shown.

### TEST-M0-04 — ROS–Gazebo `/clock` bridge
**Date:** 2026-10-19
**Milestone:** M0
**Test:** Verify `ros_gz_bridge` can bridge Gazebo simulation time to ROS 2.
**Commands:** Gazebo world running; `ros_gz_bridge` `parameter_bridge` bridging `/clock` Gazebo → ROS; `ros2 topic echo /clock`.
**Expected:** `/clock` messages appear in ROS 2 with increasing simulation time.
**Actual:** `ros_gz_bridge` created the Gazebo-to-ROS `/clock` bridge; `ros2 topic echo /clock` showed increasing simulation time.
**Result:** PASS
**Measurements:** Not recorded.
**Notes:** Performed and observed by me. Exact bridge command line was not captured in this record. A reproducible, logged re-test follows.

### TEST-M0-04 (re-test 1) — Headless `/clock` bridge with captured evidence
**Date/time:** 2026-10-19 05:34 IST
**Milestone:** M0
**Requirements:** REQ-M0-04
**Revision:** `c40e5cd` (clean working tree)
**Environment:** [docs/environment.md](docs/environment.md). Isolated with `GZ_PARTITION=amr_m0_retest_40558` and `ROS_DOMAIN_ID=73`, because a pre-existing `gz sim server` (PID 34793, left over from the earlier GUI session) was publishing `/clock` on the default partition. That process was not touched (TS-006).
**Command(s):** run by [TEST-M0-04-R1_procedure.sh](docs/evidence/M0/TEST-M0-04-R1_procedure.sh):
```bash
gz sim -s -r -v 2 shapes.sdf                                                    # headless server, background
ros2 run ros_gz_bridge parameter_bridge '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'   # background
ros2 topic info /clock
timeout 15 ros2 topic echo --once /clock    # sample 1
sleep 2
timeout 15 ros2 topic echo --once /clock    # sample 2
```
**Expected / threshold:**
- Pre-check finds no `/clock` in the isolated partition and domain.
- After start-up, `/clock` has 1 publisher.
- Both samples exit 0, and the second timestamp is strictly greater than the first.

**Actual:**
- Pre-check: no gz or ROS `/clock`.
- Gazebo advertised `/clock` and `/world/shapes/clock` within ~1 s.
- The bridge logged `Creating GZ->ROS Bridge: [/clock (gz.msgs.Clock) -> /clock (rosgraph_msgs/msg/Clock)]`.
- `ros2 topic info /clock`: type `rosgraph_msgs/msg/Clock`, publisher count 1.
- Sample 1 = 7.340000000 s, sample 2 = 10.349000000 s, i.e. Δ = **3.009 s**.

**Exit code(s):** all logged commands exited 0, and both `topic echo` samples exited 0. The test's processes were stopped with SIGINT, and no processes from either test process group remained afterwards. Script exit 0.
**Status:** PASS
**Evidence:**
- [TEST-M0-04-R1_clock_bridge_headless.log](docs/evidence/M0/TEST-M0-04-R1_clock_bridge_headless.log): full captured output, including commands, exit codes, both samples, cleanup, and server and bridge output. It is raw, so it contains terminal colour codes.
- [TEST-M0-04-R1_procedure.sh](docs/evidence/M0/TEST-M0-04-R1_procedure.sh): the exact script that produced the log.

**Notes / deviations / follow-up:**
- Headless (`-s`), so this does not re-verify the GUI; TEST-M0-02 remains the observed GUI result.
- The 3.009 s sim-time delta is not an RTF measurement, because the wall time between samples includes `ros2` CLI start-up and was not measured.
- The server printed DART warnings about ellipsoid and cone collision geometry (TS-005).

## TEST-M0-05 — Environment inventory
**Date/time:** 2026-10-19 05:33 IST
**Milestone:** M0
**Requirements:** REQ-M0-05
**Revision:** `c40e5cd` (clean working tree)
**Environment:** as captured by this test.
**Command(s):** run by [TEST-M0-05_procedure.sh](docs/evidence/M0/TEST-M0-05_procedure.sh) (read-only):
- `lsb_release -ds`
- `uname -r`
- ROS environment variables
- `ls -d /opt/ros/*`
- `gz sim --version`
- `python3 --version`
- `cmake --version`
- `dpkg-query -W` for 25 packages
- `command -v check_urdf urdf_to_graphviz gz ros2`

**Expected / threshold:**
- OS is Ubuntu 24.04.x.
- ROS distro is `jazzy`.
- Gazebo Sim 8.x (Harmonic).
- Every listed package is in state `ii` (installed).
- The CLI tools resolve.
- Values match [docs/environment.md](docs/environment.md).

**Actual:**
- Ubuntu 24.04.5 LTS; kernel 7.0.0-38-generic.
- `ROS_DISTRO=jazzy`, and `/opt/ros/jazzy` is the only ROS install.
- `RMW_IMPLEMENTATION`, `ROS_DOMAIN_ID` unset; `ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET`.
- Gazebo Sim 8.15.0; Python 3.12.3; CMake 3.28.3.
- All 25 packages `ii`, with versions identical to `docs/environment.md`.
- All four tools found.

**Exit code(s):** every command exited 0. Script exit 0.
**Status:** PASS
**Evidence:** [TEST-M0-05_environment_inventory.log](docs/evidence/M0/TEST-M0-05_environment_inventory.log) and [TEST-M0-05_procedure.sh](docs/evidence/M0/TEST-M0-05_procedure.sh).
**Notes / deviations / follow-up:** This verifies that the packages are *installed*, not that they *work*. Integration of Nav2, SLAM Toolbox, and ros2_control is not tested until the corresponding milestones.

## M1 — Custom AMR Model

All eight M1 tests have been executed. TEST-M1-08 is the last; see [docs/testing/test_plan.md](docs/testing/test_plan.md).

### TEST-M1-01 — Build `amr_description`
**Date/time:** 2026-10-19 19:08:56–19:08:57 IST
**Milestone:** M1, step 1
**Requirements:** REQ-M1-01
**Revision:** `2fde983` plus uncommitted (dirty) new files `amr_ws/src/amr_description/{package.xml,CMakeLists.txt,urdf/.gitkeep,launch/.gitkeep,rviz/.gitkeep}`, under user review before commit.
**Environment:** as in [docs/environment.md](docs/environment.md) (Ubuntu 24.04.5, ROS 2 Jazzy binary install, colcon 0.3.0); no differences.
**Command(s):** from `amr_ws/`, after `source /opt/ros/jazzy/setup.bash`:
```bash
EV=../docs/evidence/M1
colcon build --symlink-install --packages-select amr_description 2>&1 | tee $EV/TEST-M1-01_build.log
```
**Expected / threshold:** exit 0; no warnings for the package.
**Actual:**
- Console: `Finished <<< amr_description [0.81s]` and `Summary: 1 package finished [0.94s]`. There is no stderr section.
- Full per-package log `amr_ws/log/build_2026-10-19_19-08-56/amr_description/stdout_stderr.log` (CMake configure, build and symlink-install; not committed, because `amr_ws/log/` is ignored): no line matches `warn|error|deprecat` (case-insensitive), and `stderr.log` is 0 bytes.
- Install tree: `install/amr_description/share/amr_description/` contains `package.xml`, `urdf/`, `launch/` and `rviz/`. No `.gitkeep` was installed.

**Exit code(s):** colcon 0 (read from `${PIPESTATUS[0]}`).
**Status:** PASS
**Evidence:** [TEST-M1-01_build.log](docs/evidence/M1/TEST-M1-01_build.log): the complete console output of the command above.
**Notes / deviations / follow-up:**
- The package is a skeleton. `urdf/`, `launch/` and `rviz/` are empty apart from `.gitkeep` placeholders. This test verifies the package structure, build type and install rules, not the robot model (TEST-M1-02 onward).
- The eight `exec_depend` packages were confirmed to resolve under `/opt/ros/jazzy` with `ros2 pkg prefix` before the build. colcon does not check run-time dependencies during a build.
- `package.xml` uses the placeholder licence `TODO: License declaration`, because no project licence has been selected. *(Changed to `Apache-2.0` on 2026-10-21; see re-test 1 below.)*

### TEST-M1-01 (re-test 1) — Build `amr_description` after the licence change
**Date/time:** 2026-10-21 15:29:42–15:29:43 IST
**Milestone:** M1, step 1
**Requirements:** REQ-M1-01
**Reason for re-test:** `package.xml` changed after TEST-M1-01. Its licence went from `TODO: License declaration` to `Apache-2.0` (decided 2026-10-21), and a root `LICENSE` file (Apache License 2.0, official text) was added. The re-test makes the evidence match the package files being committed.
**Revision:** `2fde983` plus uncommitted (dirty) files: the M1 step 1 package files listed under TEST-M1-01 (with the licence change) and the root `LICENSE`.
**Environment:** as in [docs/environment.md](docs/environment.md); no differences.
**Command(s):** from `amr_ws/`, after `source /opt/ros/jazzy/setup.bash`:
```bash
EV=../docs/evidence/M1
colcon build --symlink-install --packages-select amr_description 2>&1 | tee $EV/TEST-M1-01-R1_build.log
```
**Expected / threshold:** exit 0; no warnings for the package.
**Actual:**
- Console: `Finished <<< amr_description [0.34s]` and `Summary: 1 package finished [0.44s]`. There is no stderr section.
- This was an incremental build in the `amr_ws/build/` directory left by TEST-M1-01. CMake re-ran configure (because `package.xml` changed) and the install step; compiler detection was not repeated.
- Per-package log `amr_ws/log/build_2026-10-21_15-29-43/amr_description/stdout_stderr.log` (22 lines): no line matches `warn|error|deprecat` (case-insensitive), and `stderr.log` is 0 bytes.
- The installed `package.xml` contains `Apache-2.0`.

**Exit code(s):** colcon 0 (read from `${PIPESTATUS[0]}`).
**Status:** PASS
**Evidence:**
- [TEST-M1-01-R1_build.log](docs/evidence/M1/TEST-M1-01-R1_build.log): the complete console output of the command above.
- [TEST-M1-01-R1_package_output_sanitized.log](docs/evidence/M1/TEST-M1-01-R1_package_output_sanitized.log): a **sanitized copy** of the per-package log above.
  - The only change is that the absolute path of the repository checkout (under my home directory) is replaced with `<repo>`, using `sed 's#<absolute repository path>#<repo>#g'`. No other line was altered.
  - Source SHA-256 `cfd5acf7d21ac5b320750f580fbec052f3c1470eeea62845b237040c403e8832`; sanitized copy SHA-256 `e0820eebad78d9f2c9e56d0929295e974d2f7508ba08d4db36f9bb0806d6d175`.

**Notes / deviations / follow-up:** the original TEST-M1-01 record above is kept unchanged as history. Like TEST-M1-01, this verifies the package structure, build type and install rules, not the robot model.

### TEST-M1-02 — Xacro expansion and URDF structure
**Date/time:** 2026-10-21 15:48:54 IST
**Milestone:** M1, steps 2–4
**Requirements:** REQ-M1-02, REQ-M1-09 (link exists; its pose is checked in TEST-M1-03 and TEST-M1-04)
**Revision:** `6227f66` plus uncommitted (dirty) files: new `amr_ws/src/amr_description/urdf/{amr.urdf.xacro,amr_properties.xacro,inertial_macros.xacro}`; `urdf/.gitkeep` removed.
**Environment:** as in [docs/environment.md](docs/environment.md); xacro 2.1.1, urdfdom 4.0.2 (`ros-jazzy-*` packages); no differences.
**Command(s):** from `amr_ws/`, after `source /opt/ros/jazzy/setup.bash`:
```bash
EV=../docs/evidence/M1
xacro src/amr_description/urdf/amr.urdf.xacro > /tmp/amr.urdf
check_urdf /tmp/amr.urdf | tee $EV/TEST-M1-02_check_urdf.log
```
**Expected / threshold:** both exit 0; root `base_footprint`; 6 links / 5 joints as in [frames_and_tf.md §2](docs/design/frames_and_tf.md).
**Actual:**
- `xacro` exit 0; nothing was printed on stderr (shown in the terminal, not redirected to a file). Generated URDF: 143 lines, SHA-256 `061c22ca552fc201d388cb53dd39dd1c730de27c1c6faa0eb1dd5dbca5b197e4`.
- `check_urdf`: "Successfully Parsed XML"; robot `amr`; root `base_footprint` → `base_link` → `caster_link`, `left_wheel_link`, `lidar_mount_link`, `right_wheel_link` (6 links).
- `check_urdf` does not list joints. The 5 joints (names, types, parent/child, origins, axes) were counted and checked in TEST-M1-03 re-test 1 (a) on the same, byte-identical URDF.

**Exit code(s):** xacro 0; check_urdf 0 (read from `${PIPESTATUS[0]}`).
**Status:** PASS
**Evidence:**
- [TEST-M1-02_check_urdf.log](docs/evidence/M1/TEST-M1-02_check_urdf.log): the complete `check_urdf` output.
- [TEST-M1-02_amr.urdf](docs/evidence/M1/TEST-M1-02_amr.urdf): an unmodified copy of `/tmp/amr.urdf`, the generated model that TEST-M1-03 inspects. It contains no absolute paths.

**Notes / deviations / follow-up:** none. This verifies structure only; values are checked in TEST-M1-03.

### TEST-M1-03 — Generated-model properties (URDF and SDF)
**Date/time:** 2026-10-21 15:49:59 IST
**Milestone:** M1, steps 2–4
**Requirements:** REQ-M1-03, REQ-M1-04, REQ-M1-06, REQ-M1-07
**Revision:** as TEST-M1-02, plus the new check script `docs/evidence/M1/TEST-M1-03_check.py` (first version).
**Environment:** as in [docs/environment.md](docs/environment.md); sdformat 14.9.0 (`gz sdf --versions`); no differences.
**Command(s):** from `amr_ws/`, after `source /opt/ros/jazzy/setup.bash`, on the TEST-M1-02 output:
```bash
EV=../docs/evidence/M1
urdf_to_graphviz /tmp/amr.urdf $EV/TEST-M1-03_amr_tree      # writes .gv and .pdf
gz sdf -p /tmp/amr.urdf > /tmp/amr.sdf
python3 -I $EV/TEST-M1-03_check.py /tmp/amr.urdf /tmp/amr.sdf | tee $EV/TEST-M1-03_check.log
```
The script compares the generated URDF (a) and SDF (b) with values typed in from the design documents, not read from the Xacro files. It covers every acceptance criterion of TEST-M1-03 in [docs/testing/test_plan.md §4](docs/testing/test_plan.md).
**Expected / threshold:** as in the test plan: (a) 6 links; per-link masses, inertial origins and tensors equal CALC-M1-07 to -10 to 4 s.f.; sum 9.4 kg; dimensions and joint origins exact; contact heights per CALC-M1-04. (b) 3 links; lumped `base_footprint` 8.4 kg at ≈ (−0.1021, 0, +0.1098); total 9.4 kg; lumped tensor equal to a parallel-axis combination to 4 s.f.
**Actual:** `urdf_to_graphviz` and `gz sdf -p` exited 0 (`gz sdf` stderr 0 bytes). The script reported **50 PASS, 2 FAIL** and exited 1. Every property check passed, including all of part (b). The two failures were the text searches "no mesh references (REQ-M1-10)" and "no Gazebo sensor or plugin elements (REQ-M1-09)".
**Exit code(s):** urdf_to_graphviz 0; gz sdf 0; check script **1**.
**Status:** FAIL
**Evidence:** [TEST-M1-03_check.log](docs/evidence/M1/TEST-M1-03_check.log): the complete output of this run.
**Notes / deviations / follow-up:** diagnosed as a defect in the check script, not in the model ([TS-007](docs/troubleshooting.md)). The script searched the raw file text, and xacro copies XML comments into the URDF; two comments contain the words "meshes", "sensor(s)" and "plugins". The URDF has no `<mesh>`, `<gazebo>`, `<sensor>` or `<plugin>` elements. The check was changed to inspect elements, and the test was repeated as re-test 1.

### TEST-M1-03 (re-test 1) — Generated-model properties, corrected check
**Date/time:** 2026-10-21 15:50:29 IST
**Milestone:** M1, steps 2–4
**Requirements:** REQ-M1-03, REQ-M1-04, REQ-M1-06, REQ-M1-07; also the element checks for REQ-M1-09 (no sensor or plugin) and REQ-M1-10 (no meshes)
**Reason for re-test:** TEST-M1-03 failed because of the check-script defect TS-007. Only the two text-search checks changed; the model files are unchanged.
**Revision:** as TEST-M1-03, with the corrected `TEST-M1-03_check.py`.
**Environment:** as TEST-M1-03.
**Command(s):** the full TEST-M1-02 and TEST-M1-03 command sequence repeated from `amr_ws/`, writing the log to `$EV/TEST-M1-03-R1_check.log`:
```bash
xacro src/amr_description/urdf/amr.urdf.xacro > /tmp/amr.urdf
urdf_to_graphviz /tmp/amr.urdf $EV/TEST-M1-03_amr_tree
gz sdf -p /tmp/amr.urdf > /tmp/amr.sdf
python3 -I $EV/TEST-M1-03_check.py /tmp/amr.urdf /tmp/amr.sdf | tee $EV/TEST-M1-03-R1_check.log
```
**Expected / threshold:** as TEST-M1-03.
**Actual:** every command exited 0. The regenerated URDF, SDF and `.gv` are byte-identical to the TEST-M1-03 inputs (SHA-256 `061c22ca…`, `61779484…` and `1e3805f6…`). The script reported **52 PASS, 0 FAIL**:
- (a) URDF:
  - 6 links and 5 joints with the designed names, types, parents/children and origins; both wheel axes (0, 1, 0).
  - `base_footprint` is massless.
  - Masses 8.0 / 0.5 / 0.5 / 0.2 / 0.2 kg, total **9.4 kg**. Inertial origins as designed: chassis (−0.100, 0, +0.035), bracket (0, 0, −0.015).
  - Tensors equal CALC-M1-07 to -10 to 4 s.f. For example, chassis (0.09127, 0.1446, 0.2167) and wheel Iyy (axial) 1.406 × 10⁻³. All off-diagonal terms 0; all moments positive; triangle inequality holds.
  - Visual and collision geometry identical, with the designed sizes and poses; wheel cylinders rotated rpy (π/2, 0, 0).
  - Wheel and caster bottoms at z = 0 (CALC-M1-04).
  - No `<mesh>`, `filename`, `<gazebo>`, `<sensor>` or `<plugin>` elements.
- (b) SDF:
  - 3 links: `base_footprint`, `left_wheel_link`, `right_wheel_link`.
  - Lumped mass **8.4 kg** with CoM (−0.10214, 0, +0.10976) in `base_footprint`, i.e. **(−0.1021, 0, +0.1098)** at 4 s.f. (CALC-M1-15). Total 9.4 kg.
  - The lumped tensor matches the parallel-axis combination at 4 s.f.: Ixx 0.09401, Iyy 0.1666, Izz 0.2362, Ixz −0.006966, Ixy = Iyz = 0.
  - The 3 lumped collisions are named `base_footprint_fixed_joint_lump__…`. `base_link`, `caster_link` and `lidar_mount_link` survive as `<frame>` elements, and the wheel joints became `revolute`.

**Exit code(s):** xacro 0; urdf_to_graphviz 0; gz sdf 0; check script 0.
**Status:** PASS
**Evidence:**
- [TEST-M1-03-R1_check.log](docs/evidence/M1/TEST-M1-03-R1_check.log): the complete check output (52 lines of results).
- [TEST-M1-03_check.py](docs/evidence/M1/TEST-M1-03_check.py): the corrected check script, with the expected values and their document sources.
- [TEST-M1-03_amr.sdf](docs/evidence/M1/TEST-M1-03_amr.sdf): an unmodified copy of the `gz sdf -p` output.
- [TEST-M1-03_amr_tree.gv](docs/evidence/M1/TEST-M1-03_amr_tree.gv) and [.pdf](docs/evidence/M1/TEST-M1-03_amr_tree.pdf): the `urdf_to_graphviz` link/joint tree. Regenerated by re-test 1; the `.gv` is byte-identical to the TEST-M1-03 output.
- The generated URDF is [TEST-M1-02_amr.urdf](docs/evidence/M1/TEST-M1-02_amr.urdf) (byte-identical).

**Notes / deviations / follow-up:**
- This confirms on the real model the fixed-joint lumping behaviour that was previously expected only from the generic R-08 probe (frames_and_tf.md §4; CALC-M1-15).
- Joint origins match to 1 × 10⁻⁹ m. Xacro arithmetic leaves floating-point residue, e.g. the caster z is written as −0.049999999999999996.
- Static checks only. The wheel rotation sign (REQ-M1-08), the RViz display and the TF values are TEST-M1-04, and Gazebo behaviour is TEST-M1-06/07.

### TEST-M1-04 — RViz display, TF values and wheel direction
**Date/time:** 2026-10-21 16:04:25 IST (launch) to 16:17:41 IST (shutdown); TF values read 16:04:44–16:05:00 IST
**Milestone:** M1, step 5
**Requirements:** REQ-M1-05, REQ-M1-08, REQ-M1-09, REQ-M1-11
**Revision:** `212d871` plus uncommitted (dirty) files: new `amr_ws/src/amr_description/launch/display.launch.py` and `rviz/display.rviz`; `launch/.gitkeep` and `rviz/.gitkeep` removed. The model files are unchanged from `d9a295b`.
**Environment:** as in [docs/environment.md](docs/environment.md); rviz2 14.1.24; Wayland session (`DISPLAY=:0`). **Deviation:** `ROS_DOMAIN_ID=47` was set for every command, to isolate the test from other ROS processes (lesson from TS-006). The package was rebuilt with `colcon build --symlink-install --packages-select amr_description` (exit 0, no warnings) so the new files were installed.
**Command(s):** from `amr_ws/`, after `source /opt/ros/jazzy/setup.bash && source install/setup.bash && export ROS_DOMAIN_ID=47`:
```bash
ros2 launch amr_description display.launch.py          # run in the background; RViz and the slider window on the screen
for f in left_wheel_link right_wheel_link caster_link lidar_mount_link; do
  timeout 4 ros2 run tf2_ros tf2_echo base_footprint $f   # tf2_echo runs until stopped; exit 124 = stopped by timeout
done                                                     # captured to $EV/TEST-M1-04_tf2_echo.log
# user: move each wheel slider to a positive value and observe; leave the sliders there
timeout 5 ros2 topic echo --once /joint_states           # supporting data, captured to
timeout 3 ros2 run tf2_ros tf2_echo base_link <wheel>    # $EV/TEST-M1-04_wheel_rotation.log
```
**Expected / threshold:** model matches the drawing (observed by me); translations (m) ±0.001: left wheel (0, 0.200, 0.075), right wheel (0, −0.200, 0.075), caster (−0.360, 0, 0.025), mount (0.070, 0, 0.200, provisional, OPEN-03); a positive slider rotates each wheel in the forward-rolling sense (OPEN-04).
**Actual:**
- Launch: `robot_state_publisher` ("Robot initialized"), `joint_state_publisher_gui` ("Got description, configuring robot") and `rviz2` (OpenGL 4.6) all started. There were no error lines before shutdown. Two informational/benign messages appeared: `Stereo is NOT SUPPORTED` (TS-002) and a Qt `QSocketNotifier` warning from the slider GUI (TS-008).
- `tf2_echo base_footprint <frame>`, with the sliders at their initial 0:
  - left wheel **(0.000, 0.200, 0.075)**; right wheel **(0.000, −0.200, 0.075)**; caster **(−0.360, 0.000, 0.025)**; mount **(0.070, 0.000, 0.200)**.
  - All rotations are identity. Every value equals the expected one at the 1 mm display resolution, inside ±0.001 m.
  - Each `tf2_echo` first printed one "Waiting for transform … frame does not exist" line. That is a new listener's TF buffer filling at start-up, not a missing frame.
- **Observed by me:** the model in RViz matches the geometry sketches ([mechanical_geometry.md §5](docs/design/mechanical_geometry.md)). The dimensioned SVG drawing does not exist yet (TODO).
- **Observed by me:** with each wheel slider at a positive value, both wheels rolled forward. Each wheel's Z axis tipped toward +X and its X axis tipped down, i.e. the top of the wheel moved forward.
- Supporting data, with the sliders left where I set them:
  - `/joint_states` positions: left **+0.527**, right **+0.560** rad.
  - `tf2_echo base_link <wheel>`: RPY (0, **+0.527**, 0) and (0, **+0.560**, 0). Each wheel is rotated by exactly its joint angle about **+Y**, with the same sign on both sides, so the axis convention needs no inversion.
- Shutdown: SIGINT to `ros2 launch`. `robot_state_publisher` and `rviz2` finished cleanly. `joint_state_publisher_gui` was reported as "process has died … exit code -2", i.e. ended by signal 2 (SIGINT) during this deliberate shutdown (TS-008). Afterwards `ps` showed no remaining ROS display process.

**Exit code(s):** `ros2 launch` 0; each `tf2_echo` 124 (stopped by `timeout`, as intended); `ros2 topic echo --once` 0.
**Status:** PASS
**Evidence:**
- [TEST-M1-04_tf2_echo.log](docs/evidence/M1/TEST-M1-04_tf2_echo.log): the complete output of the four `tf2_echo` runs.
- [TEST-M1-04_wheel_rotation.log](docs/evidence/M1/TEST-M1-04_wheel_rotation.log): the joint positions and wheel rotations with the sliders at their positive values.
- [TEST-M1-04_display_launch_sanitized.log](docs/evidence/M1/TEST-M1-04_display_launch_sanitized.log): the launch output from start to shutdown. **Sanitized:** the home directory is replaced with `<home>` and the machine's hostname with `<host>` (one line, the ROS log path). The copy was verified to differ from the source only in those substitutions. Source SHA-256 `16c5c190befe62547a73bb52745f521e717038dab53cf04e6d98285817ac7940`; copy SHA-256 `5aba1fe8f9bff25976eba95e824222169fbb3224cb2392b229536ff29c4ebc47`.
- The visual results are **observed by me** (answered in the session at about 16:17 IST); there is no screenshot.

**Notes / deviations / follow-up:**
- The wheel-direction check confirms OPEN-04 (DEC-019) in a running system. The M2 controller still has to be configured consistently (frames_and_tf.md §3).
- The mount position is a provisional placeholder until M3 (OPEN-03).

### TEST-M1-05 — TF tree diagram
**Date/time:** 2026-10-21 16:05:09–16:05:15 IST
**Milestone:** M1, step 5
**Requirements:** REQ-M1-05
**Revision:** as TEST-M1-04.
**Environment:** as TEST-M1-04 (same running `display.launch.py`, `ROS_DOMAIN_ID=47`).
**Command(s):** in a scratch directory under the ignored `amr_ws/log/`, with `display.launch.py` running:
```bash
ros2 run tf2_tools view_frames > view_frames.console 2>&1   # listens 5 s; writes frames_<timestamp>.gv/.pdf
cp frames_2026-10-21_16.05.15.gv  $EV/TEST-M1-05_frames.gv
cp frames_2026-10-21_16.05.15.pdf $EV/TEST-M1-05_frames.pdf
cp view_frames.console            $EV/TEST-M1-05_view_frames.log
```
The parent→child edges in the `.gv` were then compared with frames_and_tf.md §2 by a short Python parse.
**Expected / threshold:** the tree equals frames_and_tf.md §2 exactly; no extra or missing frames.
**Actual:**
- `view_frames` exited 0.
- The `.gv` has exactly 5 edges and 6 frames: `base_footprint → base_link`, and `base_link → left_wheel_link`, `right_wheel_link`, `caster_link`, `lidar_mount_link`. None missing, none extra; it equals the designed tree.
- The three fixed joints appear as static transforms ("Average rate: 10000.0", buffer 0). The two wheel joints are dynamic at about 10.2 Hz, driven by `joint_state_publisher_gui`. This matches frames_and_tf.md §2 (fixed joints on `/tf_static`, continuous joints on `/tf`).

**Exit code(s):** view_frames 0.
**Status:** PASS
**Evidence:**
- [TEST-M1-05_frames.gv](docs/evidence/M1/TEST-M1-05_frames.gv) and [TEST-M1-05_frames.pdf](docs/evidence/M1/TEST-M1-05_frames.pdf): the unmodified `view_frames` output, renamed.
- [TEST-M1-05_view_frames.log](docs/evidence/M1/TEST-M1-05_view_frames.log): the console output, including the frame YAML.
- None of these contain personal paths; the PDF streams were decompressed and checked.

**Notes / deviations / follow-up:** none.

### TEST-M1-06 — Gazebo Harmonic spawn
**Date/time:** 2026-10-21 16:34:19 IST (build), 16:34:26 IST (launch) to 16:38:38 IST (shutdown)
**Milestone:** M1, steps 6–7
**Requirements:** REQ-M1-04, REQ-M1-12
**Revision:** `ae3cd90` plus uncommitted (dirty) files: new `amr_ws/src/amr_description/launch/gazebo.launch.py`. The model files are unchanged from `d9a295b`.
**Environment:** as in [docs/environment.md](docs/environment.md); Gazebo Sim 8 (Harmonic) with the stock `empty.sdf` world (1 ms step, real-time factor target 1.0, DART physics); ros_gz_sim 1.0.24; Wayland session. **Isolation:** `GZ_PARTITION=amr_m1_test`, `ROS_DOMAIN_ID=49`. A pre-check found no Gazebo topics in that partition and no running `gz sim` process.
**Command(s):** from `amr_ws/`, after `source /opt/ros/jazzy/setup.bash`:
```bash
colcon build --symlink-install --packages-select amr_description 2>&1 | tee $EV/TEST-M1-06_build.log
source install/setup.bash; export GZ_PARTITION=amr_m1_test ROS_DOMAIN_ID=49
ros2 launch amr_description gazebo.launch.py        # background; default spawn pose x=y=z=roll=pitch=yaw=0
timeout 10 gz model --list                           # captured to $EV/TEST-M1-06_model_list.log
# user observes the Gazebo window; the launch is stopped with SIGINT after TEST-M1-07
```
**Expected / threshold:** model `amr` present; no `[Err]` lines about the model; wheels and caster visibly on the ground; no visible wheel–chassis interpenetration.
**Actual:**
- Build: exit 0, no warnings, `stderr.log` 0 bytes.
- Launch: `robot_state_publisher` "Robot initialized", then `ros_gz_sim create`: "Entity creation successful." `gz model --list` printed `ground_plane` and **`amr`** (exit 0).
- The complete launch log has **no `[Err]` or `[Wrn]` line**. `gz sim` printed nothing at its default verbosity.
- **Observed by me:** the model is present, the wheels and the caster sphere touch the ground plane, and there is no visible wheel–chassis interpenetration.
- Shutdown: SIGINT to `ros2 launch`. `gz` and `robot_state_publisher` finished cleanly, and `ps` showed 0 remaining `gz sim`/ROS processes within about 1 s.

**Exit code(s):** colcon 0; `gz model --list` 0; `ros2 launch` 0.
**Status:** PASS
**Evidence:**
- [TEST-M1-06_build.log](docs/evidence/M1/TEST-M1-06_build.log): the console output of the build.
- [TEST-M1-06_model_list.log](docs/evidence/M1/TEST-M1-06_model_list.log): the `gz model --list` output.
- [TEST-M1-06_gazebo_launch_sanitized.log](docs/evidence/M1/TEST-M1-06_gazebo_launch_sanitized.log): the full launch output from start to shutdown. **Sanitized:** home path → `<home>`, hostname → `<host>`, one line only. Source SHA-256 `9c32bf0d1c0404f31ce7f4917037ff896a0d614b7c625925c437159310c04da6`; copy SHA-256 `408408082ba33901b6b805809e906e4c4d806de00c0109533732bf905a59fbe9`.
- The visual criteria were **observed by me** (answered in the session at about 16:38 IST); there is no screenshot.

**Notes / deviations / follow-up:**
- Before this run, two exploratory launches (not tests) were used to observe the output formats of `gz model`, `/world/empty/stats` and `/world/empty/pose/info`. They showed that stopping the first launch design left `gz sim server`/`gui` running. That was diagnosed and fixed before this run ([TS-009](docs/troubleshooting.md)).
- The physical contact behaviour (OPEN-02) is consistent with the expectation in frames_and_tf.md §4; no wheel–chassis contact was visible.

### TEST-M1-07 — Rest stability
**Date/time:** 2026-10-21 16:34:36–16:35:08 IST (measurement), in the TEST-M1-06 simulation
**Milestone:** M1, steps 6–7
**Requirements:** REQ-M1-13
**Revision:** as TEST-M1-06, plus the new script `docs/evidence/M1/TEST-M1-07_measure.py`.
**Environment:** as TEST-M1-06 (same simulation, `GZ_PARTITION=amr_m1_test`).
**Spawn pose used by the launch file:** `base_footprint` at (0, 0, 0) m, roll = pitch = yaw = 0 rad in the world frame. These are the launch-argument defaults: `base_footprint` is the ground point, so the wheels and caster start tangent to the ground plane (CALC-M1-04).
**Command(s):** from `amr_ws/`, while the TEST-M1-06 launch was running:
```bash
python3 -I $EV/TEST-M1-07_measure.py empty amr 30 > $EV/TEST-M1-07_measure.log   # wrapped with start/end timestamps
```
**Method:**
- *Data sources* (confirmed in the exploratory runs and checked against `gz model --help`):
  - `gz topic -e -t /world/empty/pose/info -n 1`: the `amr` model pose in the world frame, as position (m) and quaternion, at full double precision, stamped with **simulation time**.
  - `/world/empty/stats`: `sim_time`, `real_time`, `real_time_factor`.
  - `gz model -m amr -p`: a cross-check of the final pose (6 decimals, RPY in rad).
- *Samples:* P0 is the first read; **A** is the first pose ≥ 1.0 s of sim time after P0; **B** is the first pose ≥ 30.0 s of sim time after A; 29 samples were taken between them, about one per second.
- *Orientation:* quaternion → roll, pitch, yaw with the ROS/Gazebo fixed-axis X-Y-Z convention, in degrees. The conversion was unit-tested offline on ±10° single-axis rotations before use.
- *Criteria* (OPEN-07, DEC-019, provisional; unchanged): \|z_B − z_A\| < 2 mm; \|roll\| and \|pitch\| < 0.5° at A and B; horizontal drift √(Δx² + Δy²) from A to B < 5 mm; no visible jitter (observed by me).

**Expected / threshold:** as above, at RTF ≈ 100 %.
**Actual (machine-measured):**
- P0 at sim time 7.589 s; A at **8.686 s**; B at **38.793 s**. The window was 30.107 s of sim time against 30.167 s of real time, an **RTF of 0.9996** (stats fields 0.9960 near A and 0.9907 near B). The simulation advanced throughout.
- The `amr` pose was identical in all samples from P0 to B:
  - position (+3.435 × 10⁻⁶, 0, −7.2 × 10⁻⁹) m
  - quaternion (−2.1 × 10⁻¹⁹, −8.534 × 10⁻⁷, 1.6 × 10⁻¹⁹, 0.999999999999636)
  - i.e. roll 0.000000°, pitch −0.000098°, yaw 0.000000°
- **\|Δz\| = 0.000000 mm; \|roll\| = 0.000000°; \|pitch\| = 0.000098° (at A and B); horizontal drift = 0.000000 mm.** The spread from A to B is 0 for z, roll and pitch. All criteria are met.
- The `gz model -m amr -p` cross-check agreed: [0.000003 0.000000 −0.000000] m, [−0.000000 −0.000002 0.000000] rad.
- **Observed by me:** watching for at least 30 s, the robot was completely still, with no jitter, sliding or rotation.

**Exit code(s):** measurement script 0.
**Status:** PASS
**Evidence:**
- [TEST-M1-07_measure.log](docs/evidence/M1/TEST-M1-07_measure.log): the raw samples (time, position, quaternion, RPY), the stats, the cross-check, the computed values and each criterion's result. *Whitespace-only normalization:* line 12 (an empty `gz model` output line that the script had prefixed with `#   `) had its three trailing spaces removed for `git diff --check`. No data changed. Original SHA-256 `688c7a5f0d3d28b3e44bdf9dcf79411336e39f1e71de0ef3ffb7b90590d65c4e`. The script now strips trailing whitespace itself. That one-line formatting change was made after the run; the measurement and calculation logic that produced this log are unchanged.
- [TEST-M1-07_measure.py](docs/evidence/M1/TEST-M1-07_measure.py): the measurement and calculation procedure.

**Notes / deviations / follow-up:**
- *Deviation:* the test plan reads A at "t ≈ 1 s (after the spawn transient)". Here A came 1 s after the script's first read, at sim time 8.686 s, because the model list and the GUI check came first. *Estimate, not measured:* the spawn was confirmed about 0.5 s of wall time after the launch started, and the world runs at RTF ≈ 1 from the start (`-r`), so A is roughly 8 s of sim time after the spawn. The full transient is still bounded: P0 differs from the commanded spawn pose by only 3.4 µm in x, 7 nm in z and 0.0001° in pitch.
- *Interpretation:* the identical values are not stale data. The message stamps advanced from 7.589 to 38.793 s, and P0 shows that physics settled the model (a 7 nm contact penetration, a tiny pitch) before it reached an exact equilibrium. Both exploratory runs gave exactly the same pose, consistent with deterministic DART stepping on a flat plane. The unactuated, undamped wheels did not roll, because no horizontal force acts at rest.
- OPEN-07 (DEC-019) is provisional "until TEST-M1-07". After this PASS, I decided on 2026-10-21 to keep the thresholds provisional. Later the same day M2 was named as the follow-up milestone (recorded in DEC-019). The thresholds used here are unchanged.
- I finalized the TEST-M1-06 and TEST-M1-07 results on 2026-10-21.

### TEST-M1-08 — Documentation / code consistency
**Date/time:** 2026-10-21 17:03:05 IST
**Milestone:** M1, step 8
**Requirements:** REQ-M1-03, REQ-M1-10, REQ-M1-14
**Revision:** `9a1bffd`, `amr_ws/src` clean (unchanged). Uncommitted (dirty) documentation corrections made earlier in this review, before the run:
- `docs/design/frames_and_tf.md` §4, `mass_inertia.md` (status, §5, §11) and `mechanical_geometry.md` (CALC-M1-03, -13): dated confirmations added to statements that predated TEST-M1-03/06/07.
- `docs/requirements.md`: the planned-path marker wording, and the REQ-M1-13 threshold status label.
- New `docs/evidence/M1/TEST-M1-08_*` scripts.
No numeric design value changed.
**Environment:** as in [docs/environment.md](docs/environment.md); xacro 2.1.1, sdformat 14.9.0.
**Command(s):** from the repository root, after `source /opt/ros/jazzy/setup.bash`:
```bash
bash docs/evidence/M1/TEST-M1-08_procedure.sh      # writes $EV/TEST-M1-08_review.log and $EV/TEST-M1-08_mesh_check.log
```
The procedure runs these steps:
1. Regenerate the URDF with `xacro` and the SDF with `gz sdf -p`, and compare both byte-for-byte with the committed [TEST-M1-02_amr.urdf](docs/evidence/M1/TEST-M1-02_amr.urdf) and [TEST-M1-03_amr.sdf](docs/evidence/M1/TEST-M1-03_amr.sdf).
2. Run `check_urdf`.
3. Run [TEST-M1-03_check.py](docs/evidence/M1/TEST-M1-03_check.py) for the per-link inertials and the lumped SDF.
4. Run [TEST-M1-08_consistency_check.py](docs/evidence/M1/TEST-M1-08_consistency_check.py) for the design documents against `amr_properties.xacro` and the generated URDF.
5. Run [TEST-M1-08_records_check.py](docs/evidence/M1/TEST-M1-08_records_check.py) for the records, statuses, traceability, links and evidence index.
6. Run the element-level `<mesh>` check from test_plan.md §4.
**Expected / threshold:** zero mismatches; zero `<mesh>` elements in the source Xacro files and the generated URDF; every executed test has a record and evidence.
**Actual:** every step passed except the URDF byte comparison (`cmp` exit 1).
- The only difference was the xacro header comment `autogenerated by xacro from amr_ws/src/amr_description/urdf/amr.urdf.xacro`. The evidence copy says `… from src/amr_description/urdf/amr.urdf.xacro`.
- The procedure had run `xacro` from the repository root. TEST-M1-02 ran it from `amr_ws/`, the shell context test_plan.md §4 assumes.
- Run from `amr_ws/`, the regenerated URDF is byte-identical to the evidence.
**Exit code(s):** procedure 1. Steps: xacro 0, URDF `cmp` **1**, `gz sdf` 0, SDF `cmp` 0, `check_urdf` 0, TEST-M1-03 check 0, consistency check 0, records check 0, mesh check 0.
**Status:** FAIL
**Evidence:**
- [TEST-M1-08_review.log](docs/evidence/M1/TEST-M1-08_review.log): the complete output of this run.
- [TEST-M1-08_mesh_check.log](docs/evidence/M1/TEST-M1-08_mesh_check.log): the mesh check, which passed.
**Notes / deviations / follow-up:** a procedure defect, not a model or documentation mismatch ([TS-010](docs/troubleshooting.md)). The procedure was corrected to run `xacro` in `amr_ws/`, the log names gained a `-R1` tag, and the test was repeated as re-test 1. The procedure script and the records check's self-exclusion pattern were edited after this run; the first lines of this run's log show the original commands.

### TEST-M1-08 (re-test 1) — Documentation / code consistency, corrected procedure
**Date/time:** 2026-10-21 17:03:55 IST
**Milestone:** M1, step 8
**Requirements:** REQ-M1-03, REQ-M1-10, REQ-M1-14
**Reason for re-test:** TEST-M1-08 failed because of the procedure defect TS-010.
**Revision:** as TEST-M1-08, with the corrected `TEST-M1-08_procedure.sh` (xacro run in `amr_ws/`) and `TEST-M1-08_records_check.py` (excludes TEST-M1-08's own `-R1` files while its record was unwritten).
**Environment:** as TEST-M1-08.
**Command(s):** from the repository root:
```bash
bash docs/evidence/M1/TEST-M1-08_procedure.sh -R1   # writes $EV/TEST-M1-08-R1_review.log and $EV/TEST-M1-08-R1_mesh_check.log
```
**Expected / threshold:** as TEST-M1-08.
**Actual:** procedure exit 0, with **230 PASS and 0 FAIL** check lines:
- **Regeneration:** the URDF and SDF regenerated from the current source are **byte-identical** to the committed TEST-M1-02/03 evidence, so that evidence matches the code. `check_urdf` parsed it, with root `base_footprint`.
- **TEST-M1-03 property check (re-run):** 52/52. Per-link masses, inertial origins and tensors equal CALC-M1-07 to -10 to 4 s.f., and the lumped SDF link matches CALC-M1-15.
- **Consistency check, 84/84.** Expected values were parsed from the design documents or typed from their CALC results, never taken from the Xacro:
  - All 18 literal properties in `amr_properties.xacro` equal the documented values (mechanical_geometry.md §2, mass_inertia.md §1), and every literal is documented. The documented masses sum to 9.4 kg.
  - The generated URDF has the 6 links and 5 joints of frames_and_tf.md §2, with documented names, types, parent/child, origins, axes (0, 1, 0) and inertial origins; it is a single tree rooted at `base_footprint`, which is massless.
  - Collision geometry equals visual geometry on every link.
  - Derived placements match mechanical_geometry.md §3: chassis centre (−0.100, 0, +0.035), wheels at y = ±0.200, caster (−0.360, 0, −0.050), mount (0.070, 0, 0.125).
  - CALC results reproduced from the generated geometry:
    - CALC-M1-01 extents −0.325 … +0.125 m.
    - CALC-M1-02 ground clearance 0.050 m, platform 0.170 m, wheel top 0.150 m.
    - CALC-M1-03 gap 7.5 mm per side, width 0.435 m.
    - CALC-M1-04 wheel and caster bottoms at z = 0.
    - CALC-M1-05 length 0.510 m, height 0.200 m.
    - CALC-M1-13 caster clearance 18.0 mm (18.0116 mm), sphere behind the rear face, swept radius 0.385 m.
    - CALC-M1-14 bracket 0.015 m behind the front, base on the platform.
  - OPEN-04 cylinder rotation (π/2, 0, 0).
  - No `mesh`, `gazebo`, `sensor`, `plugin`, `transmission` or `ros2_control` elements in any source Xacro file or in the generated URDF.
- **Records check:**
  - Every executed test (TEST-M1-01 to -07, including the TEST-M1-01 and -03 re-tests and the TEST-M1-03 FAIL) has a record heading and evidence links.
  - The summary, the test plan and the requirements traceability agree, and nothing claims PASS for a PLANNED test.
  - All 132 relative links in TEST_RESULTS.md, test_plan.md, requirements.md and the evidence README resolve.
  - Every evidence file is indexed, and every TEST-M1 evidence file is referenced from this file. TEST-M1-08's own files are excluded because this record was not yet written; they were checked after writing it (see the notes).
- **Mesh check** (test_plan.md §4): 0 `<mesh>` elements in `amr_properties.xacro`, `amr.urdf.xacro`, `inertial_macros.xacro` and the generated URDF.

**Exit code(s):** procedure 0; every step 0.
**Status:** PASS
**Evidence:**
- [TEST-M1-08-R1_review.log](docs/evidence/M1/TEST-M1-08-R1_review.log): the complete output of every step.
- [TEST-M1-08-R1_mesh_check.log](docs/evidence/M1/TEST-M1-08-R1_mesh_check.log): the mesh check.
- [TEST-M1-08_procedure.sh](docs/evidence/M1/TEST-M1-08_procedure.sh), [TEST-M1-08_consistency_check.py](docs/evidence/M1/TEST-M1-08_consistency_check.py) and [TEST-M1-08_records_check.py](docs/evidence/M1/TEST-M1-08_records_check.py): the procedure and the two checkers.

**Notes / deviations / follow-up:**
- *Checker validation:* before the run, the consistency check was confirmed to fail on deliberately corrupted copies of the generated URDF:
  - caster raised 5 mm: 4 FAILs, including CALC-M1-04 and CALC-M1-13;
  - left wheel axis flipped: 1 FAIL;
  - a `<mesh>` replacing the caster sphere: 2 FAILs.
  During development it also found its own parser bug (the `lidar_bracket_*` table row), which was fixed before the first run.
- *Prose consistency:* besides the numeric checks, the review found design-document statements that later tests had made out of date, such as "not yet observed" or "nothing verified in simulation yet". They were corrected with dated notes before the run; see the revision above. Items that need a my decision are listed in the M1 milestone record §8 (step 8) and were not changed.
- TEST-M1-08 passing does **not** close M1 by itself. The M1 exit criteria also need every OPEN item resolved, or provisional with a recorded follow-up milestone. At the time of this run OPEN-07 had none. On 2026-10-21 I named **M2** (DEC-019), so that criterion is now met. Closure still needed my final diff review.
- **I accepted this re-test 1 PASS on 2026-10-21.** The failed first run and TS-010 are kept.

## M2 — Basic Movement

Shared procedure and harness: [test_plan.md §6](docs/testing/test_plan.md), [`TEST-M2_procedure.sh`](docs/evidence/M2/TEST-M2_procedure.sh), [`TEST-M2_motion_measure.py`](docs/evidence/M2/TEST-M2_motion_measure.py). Each motion run used a fresh headless launch (`sim.launch.py headless:=true`), an isolated `ROS_DOMAIN_ID`/`GZ_PARTITION`, the stock `empty.sdf` (1 kHz physics), the robot spawned at the origin, and a 2.0 s zero-command settle after the drive controller became active.
- **Ground truth:** Gazebo `/world/empty/pose/info`.
- **Controller outputs:** odometry, `/joint_states` and `cmd_vel_out`.
- **Runs:** 3 valid runs per test; RTF was ≥ 0.967 in every run, so none was rejected.
- **Preliminary and diagnostic runs** (scratch output, not formal results) found the harness/procedure defects TS-011 to TS-013 before this suite. Their findings TS-014 and TS-015 are recorded in [troubleshooting](docs/troubleshooting.md) with the diagnostic evidence named there.

### Formal suite 1 — revision `26a6048` (clean), 2026-10-22 21:38–21:51 IST
**Environment:** [docs/environment.md](docs/environment.md); ros2_control 4.48.1, diff_drive_controller 4.42.1, gz_ros2_control 1.2.20 (recorded in each log). Model: accepted DEC-024 configuration (cylinder wheel collision). **Commands** (from the repository root, after sourcing ROS and `amr_ws/install`): the `TEST-M2-01` build; `bash docs/evidence/M2/TEST-M2-02_procedure.sh`; `bash docs/evidence/M2/TEST-M2_procedure.sh <mode> <runs> <log>` for startup 3, fault 1, linear 3, rotate 3, stop 3, timeout 3, stale 3, wallclock 1, limits 3, rest 3; and `bash docs/evidence/M2/TEST-M2-04_procedure.sh <log> <frames>`. Exit codes: TEST-M2-01 0, -02 1, startup 0, fault 0, linear 0, rotate 1, stop 0, timeout 0, stale 0, wallclock 0, limits 1, rest 0, TEST-M2-04 1.

**TEST-M2-01 — Build.** `colcon build --symlink-install --packages-select amr_description amr_bringup`: exit 0, both packages finished, no stderr section. **PASS.**

**TEST-M2-02 — Model regression and control description.** Exit 1. **FAIL (procedure defect, TS-016).**
- Default variant: URDF and SDF byte-identical to the M1 evidence; `check_urdf`, TEST-M1-03 and the mesh check passed.
- `TEST-M1-08_consistency_check.py` failed exactly one check: "amr.ros2_control.xacro: no mesh, gazebo, sensor, plugin, transmission, ros2_control elements". That M1-scope source-file assertion necessarily fails for the new M2 file; the procedure handled the equivalent TEST-M1-03 assertions but not this one.
- Enabled variant: TEST-M1-03 failed only the two expected M1-scope assertions, and `TEST-M2-02_control_check.py` passed every check.

**TEST-M2-03 — Controller startup and fault behaviour.** **PASS.**
- Startup, 3/3 runs with 0.2 m/s published from launch: drive controller active 1.341 / 1.531 / 1.307 s of simulation time after spawn (≤ 10 s); displacement before activation 0.000 mm (< 5 mm); both controllers `active`; both wheel velocity interfaces `claimed`; 0 `[ERROR]` lines.
- Fault (characterization, 1 run): `switch_controllers --deactivate diff_drive_controller` at 0.2 m/s returned exit 0, and the robot **stopped** (speed 0.000 m/s and wheel velocities 0 three seconds later).

**TEST-M2-04 — Simulation time, joint states, TF, odometry frames.** **FAIL.**
- `/clock` advanced (4 s, then 7 s), but the check errored on the `---` separator in the `ros2 topic echo` output (procedure defect, TS-017).
- `use_sim_time` was true on `/controller_manager`, `/diff_drive_controller`, `/joint_state_broadcaster`, `/robot_state_publisher` and `/ros_gz_bridge`, but **false on `/gz_ros_control`** (the gz_ros2_control plugin node): a deviation from REQ-M2-05 (TS-018).
- Passed: `/joint_states` with both wheel joints (position, velocity); odometry `frame_id odom`, `child_frame_id base_footprint`; `tf2_echo odom base_footprint`; the `view_frames` tree is exactly `odom → base_footprint →` the M1 tree with one parent per frame; TF equals odometry at the same stamp (352 pairs, 0.000000 mm / 0.000000°).
- After the checks the procedure hung: its launch ran inside a `| sed` pipeline, without job control, so SIGINT was ignored (TS-017). This session's leftover processes were stopped with SIGTERM at 21:50, after which the log was written; it reports 0 leftover gz processes.

**TEST-M2-05 — Forward and reverse.** **PASS** (3/3 runs).
- Forward +0.9799 / +0.9798 / +0.9801 m and reverse −0.9802 / −0.9802 / −0.9819 m (target ±0.980 m ± 5 %).
- Lateral deviation 0.00 mm; heading change ≤ 0.0001°; both wheel velocities with the commanded sign in cruise; tilt ≤ 0.0001°.
- Odometry ratio 0.9999–1.0000 (gross-fault check only); slip −0.004 % to −0.006 %.

**TEST-M2-06 — In-place rotation.** **FAIL** (3/3 runs).
- Ground-truth yaw +196.626 / +196.641 / +196.634° and −196.378 / −196.401 / −196.426° (target 180° ± 5 %).
- Odometry +180.18 to +180.21° and −179.87 to −179.94° (ratio 0.916).
- Passed: translation ≤ 0.34 mm; wheel signs correct (right > 0 > left for +ω); tilt ≈ 0°.
- Cause investigated in TS-014: an effective track of ≈ 0.3665 m with cylinder wheel collision.

**TEST-M2-07 — Stop, timeout, stale and wall-clock stamps.** **PASS** for the pass/fail modes (3/3 runs each).
- Stop from 0.5 m/s: at rest 0.520 / 0.518 / 0.534 s after the zero command (≤ 0.70 s); distance 0.1284 / 0.1200 / 0.1234 m (≤ 0.150 m; 0.125 m expected).
- Timeout: `cmd_vel_out` started decreasing 0.497 / 0.480 / 0.482 s after the last message (≤ 0.52 s); at rest 0.721 / 0.708 / 0.709 s (≤ 0.90 s).
- Stale (stamps 1.0 s old): displacement 0.000 mm in all runs.
- **Wall-clock characterization: HAZARD.** The robot moved 0.358 m while the commands were published and kept moving after them (0.598 m in the following 3 s); it never came to rest (TS-015).

**TEST-M2-08 — Limit enforcement.** **FAIL.**
- Passed: `cmd_vel_out` stayed within [−0.25, 0.50] m/s and |ω| ≤ 1.0 rad/s; measured linear acceleration 0.504 / 0.503 / 0.505 m/s² speeding up (≤ 0.55) and 1.008 / 1.003 / 1.003 m/s² slowing down (≤ 1.10); ground-truth speed within [−0.2500, +0.5000] m/s; tilt ≈ 0°.
- Failed: ground-truth yaw rate **1.0959 rad/s** (> 1.05) in all runs, and angular acceleration 2.2036 rad/s² (> 2.2) in one run (2.1975 and 2.2000 in the others). Both reflect the TS-014 factor of about 1.09 between commanded and physical rotation.

**TEST-M2-10 — Rest stability, OPEN-07 follow-up.** **BLOCKED.**
- Quantitative criteria passed in 3/3 runs with the controllers active, a zero command and the DEC-024 contact: Δz 0.000000 mm, roll 0.000000°, pitch 0.000098°, drift 0.000000 mm (thresholds unchanged and provisional, DEC-019).
- The criterion "no visible jitter (observed by me)" needs a GUI session.
- This run used the cylinder wheel collision; it is repeated after any collision change.

**TEST-M2-09 — Manual control.** **NOT RUN:** keyboard teleop and the jitter observation need someone at the GUI.

### Re-test 1 — revision `7b90453` (clean; DEC-028 sphere wheel collision, DEC-029 `cmd_vel_guard`, TS-018), 2026-10-22 21:58–22:08 IST
**Why:** formal suite 1 failed TEST-M2-02 (TS-016), -04 (TS-017/018), -06 and -08 (TS-014), and characterized the hazard TS-015. The fixes are in `7b90453`.
**Commands:** as suite 1, with `-R1` log names. TEST-M2-07 `wallclock` was run with 3 runs (pass/fail since DEC-029). The `domainswitch` case was added afterwards in `4a8aafa`; `amr_ws/src` is identical to `7b90453`.
**Exit codes:** TEST-M2-01 0, -02 1, startup 0, fault 0, linear 0, rotate 0, stop 0, timeout 0, stale 0, wallclock 0, limits 0, rest 0, TEST-M2-04 0, domainswitch 0. No leftover processes. RTF ≥ 0.996 in every run.

**TEST-M2-01 (re-test 1).** Build including the new C++ `cmd_vel_guard` (compiled with `-Wall -Wextra -Wpedantic`): exit 0, no stderr section. **PASS.**

**TEST-M2-02 (re-test 1).** **FAIL (procedure defect, TS-019).**
- Default variant: fully passed. URDF/SDF byte-identical; the M1 consistency check failed only its expected M1-scope assertion for `amr.ros2_control.xacro` (TS-016 fix confirmed).
- Enabled variant: `TEST-M1-03_check.py` failed four assertions. Two are the expected M1-scope assertions; the other two are "left/right_wheel_link collision: cylinder …", the intended DEC-028 difference, which the procedure did not yet expect. The M2 control check passed, including the sphere collision.

**TEST-M2-02 (re-test 2, `96b226b`; procedure and REQ-M2-02 wording corrected, `amr_ws/src` unchanged).** Every step passed. On the enabled variant exactly the four named assertions failed, as expected. **PASS.**

**TEST-M2-03 (re-test 1).** **PASS.**
- Startup 3/3: active 1.441 / 2.170 / 2.272 s after spawn (≤ 10 s); 0.000 mm motion before activation with 0.2 m/s published from launch through the guard.
- Fault: on deactivation the robot stops.

**TEST-M2-04 (re-test 1).** **PASS.**
- `/clock` 4 s, then 8 s.
- `use_sim_time` **true on all 7 nodes**, including `/gz_ros_control` (TS-018 fixed) and `/cmd_vel_guard`.
- Joint states, odometry frames, `tf2_echo`, `view_frames` tree, and TF = odometry (353 pairs, 0.000000 mm / 0.000000°).
- The procedure finished by itself (TS-017 fix confirmed).

**TEST-M2-05 (re-test 1).** **PASS** (3/3). Forward +0.9800 / +0.9802 / +0.9801 m; reverse −0.9802 / −0.9802 / −0.9801 m; lateral 0 mm; odometry ratio 0.9999; slip −0.005 % / −0.006 %. Unchanged by the collision change.

**TEST-M2-06 (re-test 1, sphere collision).** **PASS** (3/3).
- Ground truth **+179.905 / +180.184 / +180.196°** and **−180.192 / −179.902 / −179.906°** (180° ± 5 %).
- Odometry ratio 0.9999–1.0001; translation 0.00 mm; wheel signs correct; tilt ≈ 0°.
- Compared with suite 1 (cylinder, about 196.5°): identical command profile, initial conditions, harness and controller.

**TEST-M2-07 (re-test 1).** **PASS.**
- Stop: at rest 0.529 / 0.532 / 0.531 s, distance 0.1234 / 0.1230 / 0.1225 m.
- Timeout (valid stream stops): `cmd_vel_out` decreasing after 0.501 / 0.500 / 0.486 s; at rest 0.726 / 0.715 / 0.702 s.
- Stale (1.0 s old): 0.000 mm; the guard logged "rejected command: stale stamp (age 1.000 s, window 0.500 s)".
- **Wall-clock** (3 runs): **0.000 mm** while publishing and afterwards; the guard logged "future stamp (clock-domain mismatch?) (age −1.79·10⁹ s)".
- **domainswitch** (3 runs, `4a8aafa`): last valid simulation-time command at 0.2000 m/s; the following wall-clock stream was rejected (95 messages per run); at rest **0.719 / 0.709 / 0.718 s** after the last valid command (≤ 0.90 s); distance 0.1188 / 0.1166 / 0.1178 m (0.12 m expected); still at rest at the end.

**TEST-M2-08 (re-test 1).** **PASS** (3/3).
- `cmd_vel_out` within the limits.
- Linear acceleration 0.5025 / 0.5038 / 0.5039 m/s² speeding up and 1.0095 / 1.0046 / 1.0060 m/s² slowing down.
- **Ground-truth yaw rate 1.0000 rad/s** (≤ 1.05); angular acceleration 2.0075 / 2.0069 / 2.0128 rad/s² (≤ 2.2); speed range [−0.2500, +0.5000] m/s; tilt ≈ 0°.

**TEST-M2-10 (re-test 1, sphere collision, DEC-024 contact, active controllers, zero command).** **BLOCKED** on the visual criterion.
- Quantitative OPEN-07 criteria passed 3/3: Δz 0.000000 mm, roll 0.000000°, pitch 0.000001°, drift 0.000000 mm (thresholds unchanged and provisional, DEC-019).
- "No visible jitter" needs a GUI observation.
- Under the proposed evaluation rule (motion_control.md §7) every value is far below 50 % of its threshold, but OPEN-07 was **not** finalized at this point.

### GUI session — 2026-11-03 (TEST-M2-09; TEST-M2-10 visual criterion)
**Revision:** `0be1661`; `amr_ws/src` identical to the re-test revision `7b90453` (`git diff 7b90453 HEAD -- amr_ws/src` empty). The workspace was rebuilt at 13:57 IST (`colcon build --symlink-install`, exit 0, 2 packages).
**Setup:**
- A first launch of `ros2 launch amr_bringup sim.launch.py` (GUI) at 13:57:58 IST confirmed `diff_drive_controller` and `joint_state_broadcaster` active and all 7 nodes up; I closed it at 13:58:46 (clean exit 0).
- I then ran the session by hand in my own terminals, between 13:58 and 15:52 IST: `sim.launch.py` and the TEST-M2-09 teleop command (`stamped:=true`, `frame_id:=base_footprint`, `use_sim_time:=true`).
- The exact invocation in my terminals was not logged.

**TEST-M2-09 — Manual control.** **PASS (observed by me).**
- The robot moved correctly forward, backward, right, left, clockwise and counter-clockwise.
- Stop with `k` worked.
- The key-hold/key-release (0.5 s timeout) behaviour was **not** specifically observed. The timeout itself is verified headless by TEST-M2-07 re-test 1 (timeout mode, at rest ≤ 0.72 s). The milestone risk "key auto-repeat vs the timeout" therefore has no visual observation; nothing reported suggests stop/start stutter.
- No evidence file: GUI observation, recorded as observed by me.

**TEST-M2-10 — Rest stability, OPEN-07 follow-up (re-test 1 completed).** **PASS.**
- The quantitative criteria passed in 3/3 runs in re-test 1 on `7b90453`, with unchanged source (Δz 0.000000 mm, roll 0.000000°, pitch 0.000001°, drift 0.000000 mm; [log](docs/evidence/M2/TEST-M2-10-R1_rest.log)).
- The visual criterion was met: **no visible jitter, observed by me** (2026-11-03 session).
- The quantitative and visual parts come from separate sessions on the same source revision.
- Outcome for OPEN-07 (rule in `docs/design/motion_control.md` §7): every value is far below 50 % of its threshold. I decided on 2026-11-03 to **finalize the thresholds unchanged**; see DEC-019.

- TEST-M1-08 on the default model expansion (M2 exit criterion): covered by TEST-M2-02 re-test 2 (`96b226b`). `amr_ws/src` is unchanged since then.

## M3 — Sensors

Plan: [M3 plan](docs/milestones/M3_sensors.md) §7.1 (Tasks A–E finalized on 2026-11-03). Procedures: [test_plan.md §7](docs/testing/test_plan.md), recorded before each formal run. Specification: [sensors.md §7](docs/design/sensors.md) (DEC-036).

### Task A — TEST-M3-01 to -03, 2026-11-03 17:36–17:41 IST
**Revision under test:** the working tree of `5b9332e` plus the uncommitted Task A changes. These are `amr_ws/src/amr_description/urdf/amr.sensors.xacro` (new) and `amr.urdf.xacro` (one `use_sensors` argument and one conditional include). The tested files are committed unchanged together with this record; their SHA-256 values are `71bbba687f0050c3…` (`amr.sensors.xacro`) and `752d65b4d05ff6d5…` (`amr.urdf.xacro`).
**Environment:** as M2 ([environment](docs/environment.md)); xacro 2.1.1, Gazebo Sim 8.15.0, colcon-core 0.21.3. Run from the repository root after sourcing `/opt/ros/jazzy/setup.bash` and `amr_ws/install/setup.bash`.

**TEST-M3-01 — Build.** **PASS.**
- Command: `bash docs/evidence/M3/TEST-M3-01_procedure.sh`.
- Result: `colcon build --symlink-install --packages-select amr_description amr_bringup` exited 0 with 0 warning lines, and `amr.sensors.xacro` is installed. The build was incremental (`--symlink-install`), as in the M2 build records. [Log](docs/evidence/M3/TEST-M3-01_build.log).
- Harness note: the run's `colcon version-check` call wrote a `log/` directory in the repository root and printed "colcon 0.21.3:" in the header. The directory was deleted (it was not committed). The procedure now runs that call inside `amr_ws`; the build command is unchanged.

**TEST-M3-02 — Model regression (first formal run, 17:36:32).** **FAIL.**
- Command: `bash docs/evidence/M3/TEST-M3-02_procedure.sh`.
- Exit 1. [Log](docs/evidence/M3/TEST-M3-02_review.log): 251 PASS lines, 9 FAIL lines.
  - The 4 pre-declared M1/M2-scope assertions failed as expected.
  - 5 new assertions of `TEST-M3-02_model_check.py` failed. They are the element comparisons that involve the last element before `</robot>`: `lidar_mount_link` in the default variant, `<gazebo reference="caster_link">` in the M2 variant.
- Diagnosis ([TS-024](docs/troubleshooting.md)): a **checker defect**. `ET.tostring()` includes the element's tail (the whitespace after it), and xacro emits a different tail when the sensor elements follow. With the tail excluded the elements are byte-identical; this was checked directly. Every byte comparison, `check_urdf`, `gz sdf` and the M1/M2 checks passed in this run.
- Corrective action: the checker compares elements without their tail; element content is still compared byte for byte. The model was not changed.

**TEST-M3-02 (re-test 1, corrected checker, 17:37:17).** **PASS.** Exit 0, 256 PASS lines. [Log](docs/evidence/M3/TEST-M3-02-R1_review.log).
- **Default (M1) baseline:**
  - the default and explicit `use_sensors:=false` expansions are byte-identical to `TEST-M1-02_amr.urdf` (SHA-256 `061c22ca…`, the gate G5 value);
  - its SDF is identical to `TEST-M1-03_amr.sdf`;
  - `check_urdf` and `TEST-M1-03_check.py` pass.
- **M2 baseline:** the M2 enabled expansion is byte-identical to the one from `5b9332e` (SHA-256 `df845c99…`). `TEST-M2-02_control_check.py` passes completely on it.
- **Pre-declared scope assertions ([TS-023](docs/troubleshooting.md)):**
  - `TEST-M1-08_consistency_check.py` failed only its M1-scope source-file assertion, for `amr.ros2_control.xacro` (TS-016) and `amr.sensors.xacro`.
  - On the sensors-on M2 model, `TEST-M2-02_control_check.py` failed only "6 links / 5 joints" and "no `<sensor>` elements". Everything else passed: plugin, friction and the DEC-028 sphere collision.
- **Sensors on (both variants):**
  - all top-level elements of the sensors-off variant are unchanged (11 for the default variant, 16 for M2);
  - the only additions are `laser_frame`, `imu_link` (no inertial, visual or collision), their fixed joints at (0, 0, 0.030) and (0, 0, 0), and the two sensor blocks;
  - `check_urdf` passes; `gz sdf -p` exits 0, and its stderr contains only the expected `gz_frame_id` warnings.
- **SDF (both sensors-on variants):**
  - 3 links, total **9.400000000 kg**, every mass and Ixx/Iyy/Izz > 0;
  - `laser_frame` and `imu_link` are lumped, and the inertial blocks are identical to M2;
  - the LiDAR pose is (0.070, 0, 0.230) m and the IMU pose (0, 0, 0.075) m in `base_footprint`, with zero rotation.
- **Sensor configuration vs DEC-031/032:**
  - exactly 2 sensors, `gpu_lidar` and `imu`; no camera (DEC-037);
  - LiDAR: min −π, max 3.12413936106985 rad, 360 samples at exactly 1°, 10 Hz, 0.12–12.0 m, Gaussian σ 0.01 m, `/scan`, `laser_frame`;
  - IMU: 100 Hz, Gaussian σ 0.001 rad/s and 0.01 m/s² on each axis, mean 0, no bias terms, `/imu`, `imu_link`.

**TEST-M3-03 — Sensor frames (first formal attempt, 17:38:00).** **FAIL.** No check ran.
- Command: `bash docs/evidence/M3/TEST-M3-03_procedure.sh`. The script was killed by SIGINT (exit 130) during its first `tf2_echo` step, before writing its review log. The temporary logs were preserved: [log](docs/evidence/M3/TEST-M3-03_attempt1_aborted.log).
- Diagnosis ([TS-025](docs/troubleshooting.md)): two **harness defects**.
  1. `robot_state_publisher` aborted: rcl could not parse the URDF passed inline as `-p robot_description:=…`.
  2. Under `set -m`, a plain `timeout -s INT` also signalled the calling script. This was reproduced in isolation; `timeout --foreground` does not.
- The aborted run left its `joint_state_publisher` process group running. It was stopped with SIGINT (that process group only). My own `gz sim` server was not touched.
- Corrective action: `robot_description` goes through a params file, and every `timeout` uses `--foreground`. Model and checks unchanged.

**TEST-M3-03 (re-test 1, corrected procedure, 17:39:18).** **PASS.** Exit 0. [Log](docs/evidence/M3/TEST-M3-03-R1_review.log), [frames.gv](docs/evidence/M3/TEST-M3-03-R1_frames.gv), [frames.pdf](docs/evidence/M3/TEST-M3-03-R1_frames.pdf).
- **Setup:** `robot_state_publisher` with the sensors-on M2 model and `joint_state_publisher` on `ROS_DOMAIN_ID` 87. No Gazebo: both transforms are fixed URDF joints.
- **D5 (`TEST-M3-03_tf_check.py`, full precision):**
  - `lidar_mount_link → laser_frame` = (0.000000000, 0.000000000, 0.030000000) m;
  - `base_link → imu_link` = (0, 0, 0);
  - both with the identity quaternion, within 1e-6.
- **Derived:** `base_footprint → laser_frame` = (0.070, 0, 0.230) m (scan plane, CALC-M3-01) and `base_footprint → imu_link` = (0, 0, 0.075) m.
- **Single tree:** rooted at `base_footprint`, with the M1 frames plus `laser_frame` and `imu_link`. `view_frames` shows the same 7 edges.
- `tf2_echo` output is recorded (3 decimals; consistent).
- 0 ERROR/FATAL lines and 0 leftover test processes.

**Scope of these results.** Simulation model only: no Gazebo sensor output was measured in Task A. Topic rates, LiDAR range and noise, and IMU statistics are Task B–D tests (TEST-M3-04 to -09, PLANNED). Nothing here is hardware validation.

### Task B — TEST-M3-01 re-test 1 and TEST-M3-04, 2026-11-03 17:58–18:01 IST
**Revision under test:** the working tree of `0004a74` plus the uncommitted Task B changes, committed unchanged with this record:
- `amr_bringup/worlds/sensor_test.sdf` (new; targets in [test plan §7.1](docs/testing/test_plan.md));
- `amr_bringup/config/sensor_bridge.yaml` (new; `/scan`, `/imu`, Gazebo → ROS);
- `amr_bringup/launch/sim.launch.py` (`sensors` and `world` arguments);
- `CMakeLists.txt` (installs `worlds/`) and `package.xml` (`ament_index_python`).

**TEST-M3-01 (re-test 1, after the Task B changes, 17:58).** **PASS.** `bash docs/evidence/M3/TEST-M3-01_procedure.sh -R1`: exit 0, 0 warning lines ([log](docs/evidence/M3/TEST-M3-01-R1_build.log)). Re-run because `amr_bringup` changed, as TEST-M1-01 re-test 1 after the licence change. Not a failure re-test.

**Informal dry run before the formal run (not a test result; [TS-026](docs/troubleshooting.md)).** The first dry run of the new procedure (17:54) found two things:
- the Gazebo command-line capture was empty (`ps -g` does not select a process group; fixed with `pgrep -g`);
- D3 for `/scan` reached 0.115 s once, against the 0.1 s limit; every other check passed.

The limit and the settle window were **not** changed. Two scratch diagnostics showed `/scan` gaps of 0.12–0.33 s only for the first three scans after start-up, and a steady state of p50 0.003 s, max 0.014 s over 653 scans. The checker now prints the signed gap distribution and the worst message's stamp. Evidence: [dry-run log](docs/evidence/M3/TS-026_TEST-M3-04_dryrun_informal.log), [diagnostic](docs/evidence/M3/TS-026_scan_latency_diag.log).

**TEST-M3-04 — Topics, rates, frames, stamps; default launch (18:00).** **PASS** on the first formal run. Command: `bash docs/evidence/M3/TEST-M3-04_procedure.sh`, exit 0. [Log](docs/evidence/M3/TEST-M3-04_review.log).
- **Part 1** (`sensors:=true world:=sensor_test.sdf`, robot at rest at the origin; attempt 1 valid, RTF 1.000):
  - Gazebo ran `gz sim -r -s --headless-rendering <share>/worlds/sensor_test.sdf`; world `sensor_test`; both controllers active.
  - Window: first `/scan` at 7.300 s; 2.0 s settle; 10.0 s window with 100 `/scan`, 1000 `/imu` and 1001 `/joint_states` messages.
  - **D1:** types `LaserScan`, `Imu`, `JointState`; every `/scan` in `laser_frame`, every `/imu` in `imu_link`; `/joint_states` always has both wheels with finite positions.
  - **D2:** `/scan` 10.0000 Hz, `/imu` 100.0000 Hz, `/joint_states` 100.0100 Hz (each limit ± 2 %).
  - **D3:** stamps strictly increasing; max \|stamp − `/clock`\| 0.0040 s (`/scan`), 0.0010 s (`/imu`), 0.0020 s (`/joint_states`); no message over 0.1 s.
  - **D4:** `angle_min` −3.141592741, `angle_max` 3.124139309, `angle_increment` 0.017453292 rad, `range_min` 0.119999997 m, `range_max` 12.0 m (float32 values; each within 1e-6 of DEC-031); 360 ranges in every scan.
- **Part 2** (default `sim.launch.py headless:=true`, Task B criterion 2):
  - Gazebo command exactly `gz sim -r -s empty.sdf`; world `empty` (`/world/empty/pose/info` exists, the M2 ground-truth topic).
  - Published `robot_description` byte-identical to the M2 expansion (SHA-256 `c2a2ab54…`); no `/scan`, `/imu` or `sensor_bridge`.
- **Both parts:** 0 `[ERROR]` lines; 0 leftover processes. The expected warnings were present: the `gz_ros2_control` IMU "skipping" (part 1 only), and the M2 start-up and "Velocity command timed out" warnings with no command. One `list_controllers` service-response timeout warning came from the procedure's polling.

**Scope.** Simulation only; robot at rest. LiDAR range and noise, FOV and blind zone (Task C), IMU and encoders (Task D), and the M2 motion regression with sensors on (TEST-M3-11) are still PLANNED. The default launch was checked for command, world, model and topics, not by re-running the M2 motion tests.

### Tasks C and D — TEST-M3-05 to -09, 2026-11-03 18:20–18:25 IST
**Revision under test:** `f45313c`, with `amr_ws/src` clean: no robot, world, bridge or launch change in Tasks C and D. Only test files are new: `TEST-M3_noise_stats.py` (shared S1–S4), `TEST-M3-C_*` and `TEST-M3-D_*`. They are committed unchanged with this record. Procedures: [test plan §7](docs/testing/test_plan.md), recorded before the formal runs.

**Coordination.** The two tasks are separate workstreams with separate files. Each has its own `ROS_DOMAIN_ID` range (C 101–109, D 111–129) and its own `GZ_PARTITION`s. Every Gazebo run (dry and formal) ran one at a time, in this order: C range, C fov, D imu_rest, D encoders, D imu_motion. Every formal attempt was valid (RTF 0.997–1.000) and ended with 0 `[ERROR]` lines and 0 leftover processes.

**Informal dry runs (18:15–18:18; not test results; logs kept as `*_dryrun_*_informal.log`):**
- C range and fov passed, and D imu_rest and encoders passed.
- D imu_motion failed D11. It was diagnosed before the formal runs ([TS-027](docs/troubleshooting.md), [diagnostic](docs/evidence/M3/TS-027_imu_linear_accel_diag.log)).
- No procedure, checker or criterion was changed after the dry runs.

**TEST-M3-05 — LiDAR range and noise (Task C, 18:20).** **PASS.** `bash docs/evidence/M3/TEST-M3-C_procedure.sh range docs/evidence/M3/TEST-M3-05_review.log`, exit 0. [Log](docs/evidence/M3/TEST-M3-05_review.log).
- Laser pose from ground truth: (0.07000, 0.00000, 0.23000) m, yaw, roll and pitch 0.00000°. Window: 60 scans (10.1–16.0 s). Non-finite target-face returns: 0.
- Per distance (edge beams excluded):

| Target | n | Mean error | s | s/σ | Within 2s | Beyond 6σ |
|---|---|---|---|---|---|---|
| 1.0 m (0°) | 3060 | +0.272 mm | 9.957 mm | 0.9957 | 0.9536 | 0 |
| 3.0 m (+90°) | 1620 | −0.097 mm | 9.908 mm | 0.9908 | 0.9568 | 0 |
| 6.0 m (180°) | 1020 | −0.996 mm | 10.535 mm | 1.0535 | 0.9627 | 0 |

- Limits: S1 \|mean\| ≤ 10 mm; S2 0.8–1.2; S3 0.93–0.98; S4 0. The noise is measured, and it matches the configured σ_r = 0.01 m.

**TEST-M3-06 — LiDAR FOV, self-returns, blind zone (Task C, 18:20).** **PASS.** `bash docs/evidence/M3/TEST-M3-C_procedure.sh fov docs/evidence/M3/TEST-M3-06_review.log`, exit 0. [Log](docs/evidence/M3/TEST-M3-06_review.log). 20 scans.
- **D6:** every scan had at least 51 / 27 / 27 / 17 finite returns on the targets at 0° / +90° / −90° / 180°. The largest \|median error\| was 4.1 / 5.6 / 6.4 / 7.6 mm (limit 50 mm).
- **D7:** 0 finite returns closer than 0.45 m; the nearest finite return was 0.969 m (the 1 m target face). 0 `-inf` returns.
- **D8:** 0 finite returns in the low target's whole sector, +33.02° to +56.98° (23 beams per scan, 20 scans).
- **Recorded:**
  - Edge registration is exact: 53 of 53 beams on the front target and 19 of 19 on the rear target return the target range.
  - Beam 0 (−180.000°, 6.010 m) and beam 359 (+179.000°, 6.014 m) both see the rear target, which confirms 360° coverage at 1° steps.
  - Blind-zone characterization: the laser is at z 0.2300 m with 0.0000° roll and pitch, so the scan plane is 0.2300 m high at 2 m and at 12 m. The 0.150 m low box sits 0.080 m below the plane and is not detected. Any object whose top is below the plane is invisible to this LiDAR (DEC-030; the M8 depth camera, DEC-037). This is the M3 part of the blind-zone item.
  - TS-022 (low mounts seeing through the body) does not apply at 0.230 m: no self-returns.

**TEST-M3-07 — IMU at rest (Task D, 18:20).** **PASS.** `bash docs/evidence/M3/TEST-M3-D_procedure.sh imu_rest 1 docs/evidence/M3/TEST-M3-07_review.log`, exit 0. [Log](docs/evidence/M3/TEST-M3-07_review.log).
- **Clearance check** (before the run): **OK**. Nearest model `target_right_2m` is 17.10 m from the swept area; the plane edge is 29.30 m away (limit 5 m each).
- **Window:** 10.0 s, 1000 samples. Robot at rest: ground-truth max speed 0.000 mm/s, max tilt 0.0000°.
- **D9:** mean specific force z = +9.80077 m/s².
- **S1–S4 (all pass):**

| Channel | Mean error | s | s/σ | Within 2s | Beyond 6σ |
|---|---|---|---|---|---|
| accel x | +0.000066 m/s² | 0.009803 | 0.9803 | 0.956 | 0 |
| accel y | +0.000201 m/s² | 0.009986 | 0.9986 | 0.959 | 0 |
| accel z (vs 9.8) | +0.000774 m/s² | 0.009842 | 0.9842 | 0.952 | 0 |
| gyro x | −0.000066 rad/s | 0.001005 | 1.0055 | 0.954 | 0 |
| gyro y | +0.000017 rad/s | 0.000991 | 0.9911 | 0.952 | 0 |
| gyro z | +0.000006 rad/s | 0.000999 | 0.9987 | 0.964 | 0 |

**TEST-M3-09 — Encoder consistency (Task D, 18:21).** **PASS**, 3 of 3 valid runs. `bash docs/evidence/M3/TEST-M3-D_procedure.sh encoders 3 docs/evidence/M3/TEST-M3-09_review.log`, exit 0. [Log](docs/evidence/M3/TEST-M3-09_review.log).
- **D12 linear**, encoder travel vs ground truth (limit ± 2 %):
  - forward: −0.0031 %, −0.0052 %, −0.0051 % (e.g. +0.97998 m vs +0.98001 m);
  - reverse: −0.0036 %, −0.0056 %, −0.0056 %.
- **D12 rotation:** Δθ_L and Δθ_R have opposite signs, with the right wheel positive for +0.5 rad/s, in all 6 legs.
- **Recorded:** the wheel arcs r(Δθ_R − Δθ_L)/2 equal (track/2) × ground-truth yaw to within 0.07 mm. Excursion from the spawn point: x 0 to +0.980 m, |y| < 1 mm.

**TEST-M3-08 — IMU in motion (Task D, 18:23).** **FAIL**: D11 failed in all 3 valid runs. `bash docs/evidence/M3/TEST-M3-D_procedure.sh imu_motion 3 docs/evidence/M3/TEST-M3-08_review.log`, exit 1. [Log](docs/evidence/M3/TEST-M3-08_review.log).
- **D10, PASS in 3 of 3 runs**, mean gyro z vs ground-truth yaw rate over about 5.07 s per leg (507 samples):
  - +0.5 rad/s leg: −0.003 %, +0.001 %, +0.016 %;
  - −0.5 rad/s leg: −0.007 %, +0.000 %, −0.008 %;
  - limit ± 3 %. Mean accel x and y during rotation are ≤ 0.0007 m/s², as expected with the IMU on the rotation axis.
- **D11, FAIL in 3 of 3 runs**, mean accel x over the 10–90 % ramp vs ground-truth acceleration:

| Run | Mean accel x | Ground-truth acceleration | Error |
|---|---|---|---|
| 1 | +0.0012 m/s² | +0.5000 m/s² | −99.75 % |
| 2 | −0.0002 m/s² | +0.5000 m/s² | −100.04 % |
| 3 | −0.0004 m/s² | +0.4997 m/s² | −100.08 % |

  - The limit is ± 20 % with the correct sign. Each ramp spans about 0.10 to 0.91 s with 79–81 IMU samples; the plateau is 0.5000 m/s and the ground-truth pitch 0.0000°. Excursion: x up to +1.376 m.
- **Diagnosis ([TS-027](docs/troubleshooting.md)):** a sensor-model/simulator result, not a harness defect. The simulated IMU's linear-acceleration channel shows no response to the robot's own acceleration, neither +0.5 m/s² nor about −1.0 m/s² braking. Gravity, the gyro and the noise model behave as specified. The cause is not established.
- **Action:** DEC-032 and DEC-036 are unchanged, and nothing was modified to obtain a pass. Held for a design decision. Task D stays In Progress.
- **Later (bounded investigation, informal; not a re-test):** the cause was identified as sampling aliasing. The wheel command is held for 10 ms at the 100 Hz controller rate, so the chassis acceleration arrives as a one-step spike; the 100 Hz IMU samples the instantaneous acceleration at a fixed phase and misses it ([TS-027](docs/troubleshooting.md), [log](docs/evidence/M3/TS-027_investigation.log)). This result stays FAIL. A scratch prototype of correction C4 (IMU at 1 kHz, 10-sample mean to 100 Hz) passed the unchanged harness informally, 3/3 runs, but only with the raw noise scaled by √10 ([TS-027](docs/troubleshooting.md), [log](docs/evidence/M3/TS-027_C4_validation.log)). It is not a re-test.

**Scope.** Simulation only; no hardware validation. TEST-M3-10 (observed by me), -11 and -12 are Task E, not started.

### DEC-038 implementation — pre-fix formal batch, 2026-11-03 19:51–20:01 IST (superseded)
**Scope:**
- The first formal execution of `docs/testing/test_plan.md` §7.3, on the first build of `amr_gazebo_plugins`.
- Procedures: `TEST-M3-01_procedure.sh` (`CLEAN=1`, tag `-R2`), `TEST-M3-13_procedure.sh`, `TEST-M3-02/03_procedure.sh -R2`, `TEST-M3-04_procedure.sh -R1`, `TEST-M3-C_procedure.sh range|fov`, `TEST-M3-D_procedure.sh imu_rest 2 | imu_motion 3 | encoders 3`, `TEST-M3-14_procedure.sh 3`.
- Revision `349064c` plus the uncommitted plugin changes.

**Status of this batch:** **superseded.** Two defects were found:
- **TS-028:** the validation runs in `Configure()`, and fails when the robot is part of the world file.
- **TS-029:** an intermittent shutdown hang of `gz sim`.

Both change the plugin binary, so every test that loads the plugin is re-run on the fixed build, and only that re-run counts for the plugin step and Task D. The logs below are kept as recorded.

**Results:**
- **TEST-M3-01 R2:** PASS. Clean build, 0 warnings; `libamr_imu_decimator_system.so` and the `GZ_SIM_SYSTEM_PLUGIN_PATH` hook installed.
- **TEST-M3-13:** PASS. 13/13 gtest cases.
- **TEST-M3-02 R2:** PASS. The default expansion is byte-identical to M1; the M2 expansion is unchanged; the IMU is 1000 Hz on `/imu_raw` with raw σ = DEC-032 × √10; the plugin parameters are as in DEC-038.
- **TEST-M3-03 R2:** PASS.
- **TEST-M3-04 R1:** **FAIL.**
  - Every topic, rate and stamp check passed, including the new one: every `/imu` stamp on the 10 ms grid.
  - But at shutdown `gz sim` ignored SIGINT for 5 s, then SIGTERM for 10 s, and was SIGKILLed: 3 `[ERROR]` lines, against 0 required.
  - The procedure still exited 0, because its final `grep` matched the checker's own "ALL CHECKS PASSED" line. Corrected the same day in the TEST-M3-03, -04 and Task C procedures, which now use their own `# overall:` line.
- **TEST-M3-05 R1, -06 R1:** PASS.
- **TEST-M3-07 R1:** PASS, 2/2 runs. Output s/σ 0.96–1.05 on six channels, within S2's [0.8, 1.2]. This is the first formal evidence that the derived raw noise gives the DEC-032 output noise.
- **TEST-M3-08 R1:** PASS, 3/3 runs. D11 mean accel x +0.4977 / +0.5005 / +0.5008 m/s² vs ground truth +0.4997 / +0.4997 / +0.5001 m/s² (−0.41 / +0.16 / +0.13 %); D10 within ± 0.014 %.
- **TEST-M3-09 R1:** PASS, 3/3 runs.
- **TEST-M3-14:** **FAIL** (shutdown only). In all 3 runs:
  - (a) max \|output − raw mean\| 3.6e-15, stamps and orientation from the newest sample, covariances correct;
  - (b) 10 ms spacing; plugin counters all 0 (1 startup partial);
  - (c) braking +0.29 / +0.48 / −0.06 %;
  - (d) cruise \|mean\| ≤ 0.0004 m/s²;
  - (e) D10 and the published covariances 1e-6 / 1e-4;
  - (f) static rate check;
  - INFO: controller-step delay histogram {8 ms: 50, 9 ms: 150} in every run, matching the prototype.
  - Runs 1 and 2: `gz sim` exceeded 5 s after SIGINT and got SIGTERM (1 `[ERROR]` line each), so the launch-log condition failed.
- RTF 0.980–1.000 in all launch runs.

**Diagnosis and action:** see TS-028 and TS-029 in `docs/troubleshooting.md`.

### DEC-038 implementation — formal re-run on the fixed build, 2026-11-04 15:52–16:10 IST
**Scope:**
- The formal execution of `docs/testing/test_plan.md` §7.3 that counts for the plugin step and Task D, replacing the superseded 2026-11-03 batch.
- Revision `4961817`, `amr_ws/src` clean in every log header (TS-028 fix included). Gazebo Sim 8.15.0.
- DEC-039 applies to the sensor launches: an attempt whose only defect is the TS-029 shutdown signature is INVALID, recorded and repeated.
- One test at a time, 0 leftover processes before and after each; new tags, no log overwritten.

**Results** (evidence under `docs/evidence/M3/`):
- **TEST-M3-01 R3:** PASS. Clean build, 0 warnings; plugin and `GZ_SIM_SYSTEM_PLUGIN_PATH` hook installed ([log](docs/evidence/M3/TEST-M3-01-R3_build.log)).
- **TEST-M3-13 R1:** PASS. 13/13 gtest cases ([log](docs/evidence/M3/TEST-M3-13-R1_unit.log)).
- **TEST-M3-02 R3:** PASS ([log](docs/evidence/M3/TEST-M3-02-R3_review.log)). Default expansion byte-identical to M1 (also the explicit M1 identity check of the §7.3 last row); M2 expansion unchanged; IMU 1000 Hz on `/imu_raw`, raw σ = DEC-032 × √10, plugin parameters as DEC-038. Its four `FAIL` lines are the expected assertions of the frozen M1/M2 checkers (TS-016, TS-023), asserted as "only the expected … fail".
- **TEST-M3-03 R3:** PASS; D5 unchanged ([log](docs/evidence/M3/TEST-M3-03-R3_review.log), [frames](docs/evidence/M3/TEST-M3-03-R3_frames.pdf)).
- **TEST-M3-04 R2:** PASS, 1 attempt ([log](docs/evidence/M3/TEST-M3-04-R2_review.log)). `/imu` 100.0000 Hz (n = 1000), stamps strictly increasing, 1000 of 1000 on the 10 ms grid, max |stamp − clock| 0.0000 s; `/scan` 10.0000 Hz; `/joint_states` 100.0100 Hz. Part 2: default launch = M2 (no `/scan`, no `/imu`). Both shutdowns CLEAN.
- **TEST-M3-05 R2:** PASS, 1 attempt ([log](docs/evidence/M3/TEST-M3-05-R2_review.log)). S1 |mean error| ≤ 0.0015 m; S2 s/σ 1.015–1.020; S3 0.953–0.962; S4 0 outliers at 1, 3, 6 m.
- **TEST-M3-06 R2:** PASS ([log](docs/evidence/M3/TEST-M3-06-R2_review.log)). **Attempt 1 INVALID under DEC-039**: its checks passed, but `gz sim` hit TS-029 at shutdown (SIGINT → SIGTERM → SIGKILL, exit −9; every other process finished cleanly; 0 leftovers). Attempt 2 PASS: targets at the expected bearings, max |median error| ≤ 0.0071 m, `target_low` 0 returns, 0 returns < 0.45 m.
- **TEST-M3-07 R2:** PASS, 2/2 ([log](docs/evidence/M3/TEST-M3-07-R2_review.log)). S2 s/σ 0.966–1.028 on six channels.
- **TEST-M3-08 R2:** PASS, 3/3 ([log](docs/evidence/M3/TEST-M3-08-R2_review.log)). D11 −0.26 / +0.39 / +0.05 %; D10 within ± 0.015 %.
- **TEST-M3-09 R2:** PASS, 3/3 ([log](docs/evidence/M3/TEST-M3-09-R2_review.log)). D12 travel error −0.0040 to −0.0056 %; rotation signs correct.
- **TEST-M3-14 R1:** PASS, 3/3 ([log](docs/evidence/M3/TEST-M3-14-R1_review.log)). (f) static rates; (a) max |output − raw mean| 3.55e-15, 100 % of outputs checked; (b) 0 off-grid, all 10 ms, raw all 1 ms; plugin counters 0, `discarded_partial` 2, unpublished raw 10–13; (c) braking −0.33 / +0.02 / −0.02 %; (d) cruise |mean| ≤ 0.0011 m/s²; (e) D10 and covariances 1e-6 / 1e-4. INFO delay histogram {8 ms: 50, 9 ms: 150} in every run.
- **TEST-M3-14 (g) R1:** PASS ([log](docs/evidence/M3/TEST-M3-14g-R1_review.log)). Valid: active once, `/imu_raw` 4000, `/imu` 400. `bad_rate` and `bad_sensor`: "invalid configuration, NOT active" naming the value at default verbosity, `/imu_raw` published, `/imu` 0. INFO: block-mean variance ratio 0.905–1.142, max lag |r| 0.046 (raw samples independent, DEC-038 item 8).
- RTF 0.998–1.000 in all launch runs. Every procedure exit code agreed with its `# overall:` line.

**Anomalies (preserved, not counted against the criteria):**
- TS-029: 1 of 15 sensor launches (TEST-M3-06 attempt 1), handled by DEC-039.
- TS-030: a truncated `Exception in thread Thread-1 (spin)` in harness stderr in TEST-M3-09 R2 attempt 3 and TEST-M3-14 R1 attempt 3, at harness teardown after the measurements; sample counts complete. The cause is suspected, not reproduced (full traceback never captured); details and the deferred harness fix: `docs/troubleshooting.md` TS-030.

### Task E — TEST-M3-11 and TEST-M3-01 R4, 2026-11-04 16:28–16:35 IST
**Scope:** M2 motion regression with the sensors on (REQ-M3-13) and the build after the `sensors.rviz` install rule. TEST-M3-10 (observed by me) is recorded separately.

**TEST-M3-11:** PASS, 3/3 valid runs in each mode, revision `a49369c`, `amr_ws/src` clean.
- Procedure `TEST-M3-11_procedure.sh` (a copy of the Task D procedure with its own harness and domains; written before its first run) and harness `TEST-M3-11_m2_regression.py`, which runs the M2 mode functions and DEC-027 criteria unchanged.
- Launch `sim.launch.py headless:=true sensors:=true world:=sensor_test.sdf y:=-20.0`. The stock `empty.sdf` loads no Sensors or IMU system, so "sensors on" there would publish nothing.
- An informal smoke run (1 timeout run, scratch, not evidence) preceded the batch to check the new harness wiring. It passed.

| Mode | Result | Key values (3 runs) | M2 R1 without sensors |
|---|---|---|---|
| linear ([log](docs/evidence/M3/TEST-M3-11_linear_review.log)) | PASS 3/3 | odometry/ground-truth ratio 0.9999–1.0000; lateral 0.00 mm; heading 0.0000° | (TEST-M2-05 R1 PASS) |
| rotate ([log](docs/evidence/M3/TEST-M3-11_rotate_review.log)) | PASS 3/3 | yaw change 179.875–180.215°; translation 0.00 mm | 179.902–180.196° |
| stop ([log](docs/evidence/M3/TEST-M3-11_stop_review.log)) | PASS 3/3 | distance 0.1257 / 0.1283 / 0.1298 m (≤ 0.150); at rest 0.522–0.538 s (≤ 0.70) | 0.1225 / 0.1230 / 0.1234 m |
| timeout ([log](docs/evidence/M3/TEST-M3-11_timeout_review.log)) | PASS 3/3 | decay starts 0.494–0.507 s (≤ 0.52); at rest 0.718–0.735 s (≤ 0.90) | at rest 0.702–0.726 s |

- Sensors live during every profile (INFO): `/scan` 10.00 Hz, `/imu` 100.00 Hz, largest gaps 100 ms and 10 ms. RTF 0.996–1.000.
- All 12 shutdowns CLEAN, 0 leftovers, 0 TS-029 attempts.
- **TS-030 capture:** the spin thread ended cleanly in all 12 runs; no spin-thread exception occurred, so the suspected cause stays unconfirmed (TS-030).
- **Observation, not explained:** the stop distance with sensors on is 3–6 mm longer than in M2 R1 (0.128 vs 0.123 m mean). It is within the criterion and close to the 0.125 m expected value. With 3 runs per side and a different world and spawn point, it is not attributed to the sensors.

**TEST-M3-01 R4:** PASS ([log](docs/evidence/M3/TEST-M3-01-R4_build.log)). Clean build, 0 warnings; `share/amr_bringup/rviz/sensors.rviz` installed. The log header shows uncommitted `amr_ws/src` changes: the `sensors.rviz` file and its install rule, committed unchanged afterwards.

### Task E — TEST-M3-10 GUI session, 2026-11-04 16:43–16:52 IST
**Set-up** (revision `8e1d623`, local):
- I started `ros2 launch amr_bringup sim.launch.py sensors:=true world:=sensor_test.sdf` (Gazebo GUI, robot at the origin); output captured.
- Then `rviz2 -d $(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz/sensors.rviz --ros-args -p use_sim_time:=true` and `ros2 topic echo /imu --once`.
- A first attempt had no simulation running: only the setup line of the launch block had been run, so RViz had no data and `/imu` had no publisher. Diagnosed from the process list and the absence of a new `~/.ros/log` launch directory; no defect.

**Observed by me** (confirmed in the session, with screenshots [RViz](docs/evidence/M3/TEST-M3-10_rviz.png) and [Gazebo](docs/evidence/M3/TEST-M3-10_gazebo_gui.png)):
- The four LiDAR scan lines match the four targets in Gazebo (front 1 m, left 3 m, right 2 m, rear 6 m); there is no scan line for `target_low` (below the 0.230 m scan plane, the TEST-M3-06 blind zone).
- The TF labels `laser_frame` and `imu_link` are visible (after zooming onto the robot). RViz Global Status Ok; all four displays loaded.
- A pixel check of the RViz screenshot agrees: the left and right lines sit 193 and 129 px from the robot (ratio 1.50 = 3 m / 2 m); the rear line is dotted (about 19 beams on the 2 m face at 6 m).

**Recorded alongside (not part of the visual criterion):**
- `gpu_lidar` with the Gazebo GUI (the one gate G1 aspect not covered headless): runs, RTF 99.83 % in the GUI.
- IMU via topic ([echo](docs/evidence/M3/TEST-M3-10_imu_echo.log)): `frame_id imu_link`, linear acceleration (0.0011, −0.0011, 9.7885) m/s², covariances 1e-6 / 1e-4 (DEC-032 at the output).
- Launch log ([log](docs/evidence/M3/TEST-M3-10_gui_launch.log)): 0 `[ERROR]` lines. 269 of 270 `[WARN]` lines are `Velocity command timed out. Braking.`: no `/cmd_vel` publisher in this session, so the DEC-026 timeout holds the robot braked, as designed. Shutdown CLEAN (classifier), 0 leftovers. ImuDecimator counters over the session: raw 627 987, published 62 797, all error counters 0.
- RViz terminal: only `Stereo is NOT SUPPORTED` (TS-002, benign).
- The RViz screenshot was cropped to remove the window title, which contained an absolute home path.

**TEST-M3-10:** **PASS (observed by me)**.

## Test automation (DEC-040)

Plan: [docs/milestones/M3-M4_test_automation.md](docs/milestones/M3-M4_test_automation.md). These tests verify the test infrastructure; robot criteria are unchanged.

### TA Task 1 — TEST-TA-01, 2026-11-04 18:17 IST
**Change under test (uncommitted at the run, committed unchanged afterwards):**
- `M2.Spinner` in `docs/evidence/M2/TEST-M2_motion_measure.py`: a stop flag and a `spin_once` loop; join before the executor/node/context shutdown; prints `# TS-030 check: spin thread ...`. It is used by the four formal harnesses (M2 motion, M3 Task D, TEST-M3-11, TEST-M3-14).
- The M2 stop mode also prints the DEC-040 (d) stop-timing INFO.

- **TEST-TA-01:** **PASS** ([log](docs/evidence/TA/TEST-TA-01_spinner_teardown.log)).
  - Command: `python3 docs/evidence/TA/TEST-TA-01_spinner_teardown.py 1000` (no Gazebo; 4 timers at 2 kHz, 4 busy subscriptions, random 0–50 ms hold).
  - Result: 1000 of 1000 teardowns ended cleanly, 0 threads alive, 0 other thread exceptions, 120.6 s; exit 0.
  - **Limitation:** the old teardown order also gave 0 errors in the same kind of test (troubleshooting TS-030, 0 in 1300). TEST-TA-01 shows the helper is correct and leak-free. It cannot show that TS-030 is fixed, because TS-030 has never been reproduced outside Gazebo. That evidence is TEST-TA-04 (the spin-thread state in every formal run).
- **Informal smoke runs** (scratch logs, not evidence; one valid run each, procedure unchanged):
  - TEST-M2_procedure.sh stop: PASS. INFO: braking onset +7.0 ms after the estimated zero-command time; stop distance 0.1240 m nearest-sample (criterion), 0.1260 m interpolated at the estimate, 0.1225 m from the onset.
  - TEST-M3-11_procedure.sh stop: PASS. Onset +7.0 ms; 0.1252 / 0.1262 / 0.1227 m; shutdown CLEAN.
  - Both runs: `# TS-030 check: spin thread ended cleanly`.
  - Observation, not a result: from the braking onset, sensors on and off agree within 0.2 mm (one run each). This supports the measurement-timing explanation of the TEST-M3-11 3–6 mm difference. TEST-TA-04 gives the formal numbers.

### TA Task 2 — TEST-TA-02 and TEST-TA-03, 2026-11-04 18:23–18:25 IST
**Under test:** `tools/run_suite.py` (uncommitted at the runs, committed unchanged afterwards apart from the TS-033 suite fix). Every run was on `c898116`; `amr_ws/src` was clean.

- **TEST-TA-02:** **PASS** ([log](docs/evidence/TA/TEST-TA-02_runner_selftest.log)).
  - Command: `python3 -I tools/run_suite.py --self-test`; 18 checks, exit 0.
  - Classifications covered: PASS-candidate, FAIL, MISMATCH (both directions), NO-OVERALL, the checker overall format, and the TS-029 line sum.
  - Refusals covered: an existing log is not executed; a reused tag; a running simulation refuses the start (exit 3, nothing run); a leftover process between entries stops the suite (exit 1).
- **TEST-TA-03:** **FAIL** ([summary](docs/evidence/TA/static-TA03_summary.md)).
  - Command: `python3 -I tools/run_suite.py static TA03`.
  - Results: 5 entries PASS-candidate; TEST-M1-08 exit 1 with a failing overall line, classified FAIL (correct, no mismatch).
  - Diagnosis (TS-033): standalone TEST-M1-08 asserts the M1 scope on every Xacro source. It gives 84 PASS plus the 2 expected FAIL (TS-016, TS-023), as on any post-M2 tree. Including it was a suite-definition defect; the runner behaved correctly.
- **TEST-TA-03 R1:** **PASS** ([summary](docs/evidence/TA/static-TA03R1_summary.md)).
  - Command: `python3 -I tools/run_suite.py static TA03R1`, after TEST-M1-08 was removed from the suite.
  - Results: 5 of 5 PASS-candidate, runner exit 0, no simulation process left.
  - Human review of every log: records checks PASS; build exit 0 with no warnings; 13 of 13 gtest cases OK; M3-02 all steps passed, with only its declared expected assertions failing and the same `gz_frame_id` stderr as in R3.

### TA Task 3 — TEST-TA-04, 2026-11-04 18:26–18:47 IST
**Under test:** the TA Task 1 harness changes (`M2.Spinner`, stop-timing INFO) in every formal harness user, run through the runner on revision `cbb80c3` (summary header: "clean": `amr_ws/src`, `docs/evidence` and `tools` unchanged from HEAD). Procedures and criteria unchanged from the original formal runs (DEC-027, DEC-036, DEC-038, DEC-039).

- **TEST-TA-04:** **PASS** ([summary](docs/evidence/TA/regression-TA04_summary.md)).
  - Command: `python3 -I tools/run_suite.py regression TA04` (ROS and `amr_ws/install` sourced). Runner exit 0, 21 min 13 s, no simulation process left.
  - Runner: 20 of 20 entries PASS-candidate (exit 0 and a passing overall line in each; no MISMATCH).
  - Human review of all 20 logs: 0 FAIL lines, 0 tracebacks. Every criterion line is PASS: M2-03 startup 3 runs and fault 1; M2-04; M2-05, -06; the five M2-07 modes; M2-08; M2-10; M3-07 (2 runs); M3-08, -09; the four M3-11 modes; M3-14. Each has 3 valid runs unless stated.
  - TS-029 (DEC-039): 0 attempts declared invalid in the M3 entries.
  - **REQ-TA-01 / TS-030:** `# TS-030 check: spin thread ended cleanly` in 55 of 55 harness runs (32 M2, 23 M3), with no other spin-thread state.
  - **REQ-TA-02:** both stop entries print the two stop-timing INFO lines in every run:

    | Run | Braking onset after the estimate | Criterion (nearest sample) | Interpolated, from the estimate | From the braking onset |
    |---|---|---|---|---|
    | M2-07 stop 1 | +2.9 ms | 0.1250 m | 0.1249 m | 0.1235 m |
    | M2-07 stop 2 | +4.3 ms | 0.1290 m | 0.1257 m | 0.1235 m |
    | M2-07 stop 3 | +1.9 ms | 0.1251 m | 0.1240 m | 0.1231 m |
    | M3-11 stop 1 | +3.4 ms | 0.1223 m | 0.1250 m | 0.1233 m |
    | M3-11 stop 2 | +2.1 ms | 0.1228 m | 0.1238 m | 0.1228 m |
    | M3-11 stop 3 | +1.9 ms | 0.1203 m | 0.1232 m | 0.1223 m |

  - Interpretation (Calculated from the logs): the criterion values spread over 8.7 mm (0.1203–0.1290 m), and this time M3-11 is the shorter one, which is the opposite sign to the earlier 3–6 mm difference. Measured from the braking onset, all six runs fall in 0.1223–0.1235 m (1.2 mm spread), with means of 0.1234 m sensors-off and 0.1228 m sensors-on. The sensor difference therefore sits in the sampling time (one ground-truth sample at about 59 Hz is about ±4 mm at 0.5 m/s), not in the robot's braking. Every criterion (≤ 0.150 m; at rest ≤ 0.70 s) passes as before. The onset values are 1.5–2.7 mm below the 0.125 m expected value. This is noted, not diagnosed, and is not a criterion.
  - **Limitation:** before the fix, TS-030 appeared in 2 of 11 runs of the affected harnesses (Task D, TEST-M3-14). TEST-TA-04 has 11 such runs with 0 recurrences. If the fix had no effect, that outcome would still have about an 11 % chance ((9/11)^11). The closure follows the pre-agreed criterion (troubleshooting TS-030); every run keeps the capture, so any recurrence is seen with its full traceback.

### TA Task 4 — TEST-TA-05, 2026-11-04 18:51–19:03 IST (13:21–13:33 UTC)
**Under test:** `.github/workflows/ci.yml` and the runner suite `ci` (TEST-M3-01, -13, -02) in `tools/run_suite.py`. Hosted runner `ubuntu-latest`, container `ros:jazzy-ros-base`, dependencies by `rosdep install --from-paths amr_ws/src` (all types).

- **CI run 1** (GitHub run 41837281025, push of `6f4a7b0`): **FAIL** ([summary](docs/evidence/TA/ci-CI1a1_summary.md)).
  - TEST-M3-01 and -13 PASS-candidate; TEST-M3-02 exit 1, classified FAIL (exit and overall line agree).
  - Diagnosis TS-034: only step 2 failed, `fatal: not a valid object name: 5b9332e`, because `actions/checkout` fetched one commit. Every other FAIL line equals the local TEST-TA-03 R1 log (the declared expected assertions).
  - Fix: `fetch-depth: 0` (`477c880`). The procedure is unchanged.
- **CI run 2** (run 41837931388, push of `477c880`, code path): **PASS** ([summary](docs/evidence/TA/ci-CI2a1_summary.md)).
  - 3 of 3 entries PASS-candidate, logs reviewed: build exit 0 with 0 warnings; 13 of 13 gtest cases OK; TEST-M3-02 all steps passed.
  - M1 byte identity in the container: default URDF SHA-256 `061c22ca…` identical to `docs/evidence/M1/TEST-M1-02_amr.urdf`; M2 variant identical to baseline `5b9332e`.
- **Documentation-only push** (`4efa007`: logs, `docs/evidence/README.md`, `docs/troubleshooting.md`): **no run started** (`gh run list` after the push still listed run 2 as the latest; checked again before this record).
- **CI run 3** (run 41838700399, `workflow_dispatch` on `4efa007`): **PASS** ([ci summary](docs/evidence/TA/ci-CI3a1_summary.md)).
  - The `ci` suite: 3 of 3 PASS-candidate.
- **Minutes (Measured):** runs 1–3 lasted 179 s, 184 s and 182 s; each is billed as 3 min (one job, rounded up to the minute). GitHub billing on 2026-11-04 showed "Actions Linux 3 min, gross $0.02, billed $0" (observed by me; it had not yet included runs 2 and 3). The timing API reported 0 billable ms, so it is not used.
- **Deviation from plan §7:** no apt/rosdep cache. At about 3 min per run, a cache would save little and add another thing that can go stale; recorded in the plan.
- **Result:** TEST-TA-05 **PASS** for REQ-TA-05, after the run-1 FAIL (preserved above).

## M4 — Odometry (plan [docs/milestones/M4_odometry.md](docs/milestones/M4_odometry.md); criteria DEC-044)

### Task A — TEST-M4-03, 2026-11-13 13:58 IST
**Under test:** the odometry integration of the installed `diff_drive_controller` 4.42.1 against an independent recomputation (CALC-M4-01, M4 plan §3.1). Revision `0ca7ee4` (`amr_ws/src` clean); default M2 launch, sensors off (DEC-045); ros2_control 4.48.1, gz_ros2_control 1.2.20.
**Requirement:** REQ-M4-01. **Procedure:** `bash docs/evidence/M4/TEST-M4_procedure.sh record 1 docs/evidence/M4/TEST-M4-03_record.log docs/evidence/M4/TEST-M4-03_record.csv`, then `python3 -I docs/evidence/M4/TEST-M4-03_recompute.py` (r = 0.075 m and b = 0.400 m read from `amr_properties.xacro`).
- **Recording** (exit 0): profile straight 0.2 m/s 3 s, arc 0.2 m/s + 0.3 rad/s 4 s, rotation −0.5 rad/s 3 s, reverse −0.15 m/s 2 s, stop 2 s. 1451 joint_states (spacing 9–11 ms, none missing) and 701 odometry messages; RTF 1.000; spin thread ended cleanly; 0 `[ERROR]` lines; no leftover process.
- **Recomputation** (exit 0): 700 of 700 later odometry messages compared; max position difference 0.000000 mm (≤ 1 mm), max yaw difference 0.00000000° (≤ 0.01°). Path 1.670 m, 150.4° turned in total. 35 of 701 odometry stamps were 1 ms earlier than the joint_states stamp of their control cycle (TS-035, handled by pairing by cycle).
- **Before the formal run** (informal dry runs on `557141e`, scratch output, not evidence): the first checker draft paired by equal stamps and failed its coverage check (647/698); diagnosed as TS-035 and fixed before this run. A negative check with b = 0.404 m failed as expected (4.99 mm, 0.68°).
- **Interpretation:** the exact match shows that the installed controller integrates exactly CALC-M4-01 with the configured r and b. It does not measure accuracy against the real motion; that is TEST-M4-04 to -07.
- **Result:** TEST-M4-03 **PASS** for REQ-M4-01.

### Task B — TEST-M4-01 and TEST-M4-02, 2026-11-13 14:09–14:12 IST
**Under test:** the DEC-042 odometry covariance in `controllers.yaml` (CALC-M4-04, finalized 2026-11-13). Revision `76a67a2` (`amr_ws/src` clean); default M2 launch, sensors off (DEC-045). Both procedures were written before their formal runs.
**TEST-M4-01** (REQ-M4-09): `bash docs/evidence/M4/TEST-M4-01_procedure.sh`, exit 0 ([log](docs/evidence/M4/TEST-M4-01_review.log)).
- Build: colcon exit 0, 0 warning lines. Default expansion byte-identical to `TEST-M1-02_amr.urdf`; M2 enabled expansion byte-identical to the `30d737f` expansion.
- `controllers.yaml` vs `30d737f`: 0 removed lines; added only 3 comment lines and the two covariance keys. Values equal CALC-M4-04 (pose [0.01, 0.01, 1e3, 1e3, 1e3, 0.0158], twist [2.5e-5, 2.5e-5, 1e3, 1e3, 1e3, 4.0e-4]).
- **Result:** TEST-M4-01 **PASS**.
**TEST-M4-02** (REQ-M4-02, -07): `bash docs/evidence/M4/TEST-M4_procedure.sh interface 3 docs/evidence/M4/TEST-M4-02_review.log`, exit 0, 3 of 3 valid runs, no invalid attempt ([log](docs/evidence/M4/TEST-M4-02_review.log)).
- Each run (profile 0.2 m/s 5 s, 0.5 rad/s 3 s, stop 2 s): frames `odom` → `base_footprint`; rate 49.995 / 49.995 / 50.045 Hz (50 ± 1); receipt minus stamp within −0.0029 to +0.0062 s (sim time); published covariance diagonals equal `controllers.yaml` and are non-zero in every message.
- TF `odom → base_footprint`: 500 transforms per run, no duplicate stamp, count equal to the odometry count, 500 of 500 equal to the odometry pose at the same stamp (max 0.0000 mm, 0.00000°). Spin thread ended cleanly; 0 `[ERROR]` lines; no leftover process.
- Before the formal run, an informal dry run on `557141e` (zero covariance) failed only the non-zero covariance check, as expected before this change.
- **Result:** TEST-M4-02 **PASS**.
**CI:** run 43394884688 on the push of `76a67a2` passed (build, unit tests, TEST-M3-02 model regression in the container).
**Regression of the motion tests:** not re-run in Task B. The covariance values are only copied into the published messages and do not enter the controller's motion or odometry computation; TEST-M4-10 (Task D) re-runs the M2 suite and the M3 static checks on the final M4 configuration.

### Task C — TEST-M4-04 to -08, 2026-11-13 14:18–14:30 IST
**Under test:** odometry accuracy against Gazebo ground truth at rest points (M4 plan §3.4; criteria DEC-044). Revision `1d0b967` (`amr_ws/src` clean, DEC-042 covariance in place); default M2 launch, sensors off (DEC-045). Procedure `bash docs/evidence/M4/TEST-M4_procedure.sh <mode> 3 <log>` for modes straight, rotate, square_ccw, square_cw, circle, twist, run serially. 18 of 18 attempts valid (RTF 0.986–1.000); every run: spin thread ended cleanly, 0 `[ERROR]` lines, no leftover process.
- **TEST-M4-04** (REQ-M4-03), +0.2 m/s for 10 s then −0.2 m/s for 10 s ([log](docs/evidence/M4/TEST-M4-04_straight_review.log)): distance errors per leg +0.0003 / −0.0006, −0.0014 / −0.0027, −0.0043 / −0.0045 % of about 1.980 m (≤ 0.5 %); heading errors 0.0000° (≤ 0.5°). **PASS.**
- **TEST-M4-05** (REQ-M4-04), ±0.5 rad/s for 4π s ([log](docs/evidence/M4/TEST-M4-05_rotate_review.log)): yaw errors +0.0013 / −0.0012, +0.0001 / +0.0114, +0.0070 / +0.0068° per turn (≤ 1°); position errors 0.00 mm (≤ 20 mm). **PASS.**
- **TEST-M4-06** (REQ-M4-05), 1 m square, stop and turn ([CCW](docs/evidence/M4/TEST-M4-06_square_ccw_review.log), [CW](docs/evidence/M4/TEST-M4-06_square_cw_review.log)): CCW 0.00 / 0.05 / 0.13 mm and −0.0003 / +0.0006 / −0.0002°; CW 0.02 / 0.00 / 0.04 mm and −0.0005 / +0.0001 / −0.0006° (≤ 20 mm, ≤ 1°). **PASS.**
- **TEST-M4-07** (REQ-M4-05), v 0.2 m/s, ω 0.2 rad/s for 10π s ([log](docs/evidence/M4/TEST-M4-07_circle_review.log)): 0.04 / 0.03 / 0.01 mm and −0.0048 / −0.0012 / +0.0033° (≤ 20 mm, ≤ 1°). **PASS.**
- **TEST-M4-08** (REQ-M4-06), cruise means ([log](docs/evidence/M4/TEST-M4-08_twist_review.log)): linear +0.222 / +0.192 / +0.172 %, angular +0.209 / +0.170 / +0.220 % (≤ ± 2 %, signs equal). **PASS.** The published twist is high by about 0.2 % in all six cases (systematic; the pose is not affected). Possible link to TS-035 recorded there as a hypothesis, not verified.
- **Interpretation:** the odometry errors are 100–1000× below the DEC-044 bounds, as expected from the ideal simulation (plan §3.3). These PASS results show the odometry pipeline is correct in simulation; whether the bounds can detect real calibration errors is TEST-M4-09 (Task D).
- **Result:** TEST-M4-04 to -08 **PASS** for REQ-M4-03 to -06.

### Task D — TEST-M4-09, 2026-11-13 14:45–14:54 IST
**Under test:** whether the DEC-044 accuracy criteria detect calibration errors (REQ-M4-08; DEC-043). Revision `ecbf64c` (`amr_ws/src` clean); default M2 launch, sensors off (DEC-045), **with the Gazebo GUI and RViz shown** (`SHOW=1`, my request). Procedure and checker written before the run.
**Procedure:** `SHOW=1 bash docs/evidence/M4/TEST-M4-09_procedure.sh`, exit 0. Each case loads a run-time copy of `controllers.yaml` with the override lines inserted (logged as a diff at the end of each case log) through `controllers_file:=`. 12 of 12 attempts valid (RTF 0.961–0.999); every attempt: 0 `[ERROR]` lines, no leftover process; harness exit 1 in every attempt, as expected (the target criterion fails).
- **R** (both radii × 1.01, straight; [log](docs/evidence/M4/TEST-M4-09_R_straight_review.log)): distance criterion FAIL in all 6 legs, error +0.9965 to +1.0009 % (prediction +1.00 %).
- **B** (separation × 1.02, rotate; [log](docs/evidence/M4/TEST-M4-09_B_rotate_review.log)): yaw criterion FAIL in all 6 turns, error ∓7.189 to ∓7.212° (prediction ∓7.196 to ∓7.202° from the measured true turn).
- **L** (left radius × 1.005; [CCW log](docs/evidence/M4/TEST-M4-09_L_square_ccw_review.log), [CW log](docs/evidence/M4/TEST-M4-09_L_square_cw_review.log)): yaw criterion FAIL in all 6 squares; CCW −1.897 to −1.901° (prediction −1.904/−1.905°), CW −3.688 to −3.690° (prediction −3.695 to −3.697°).
- Checker ([log](docs/evidence/M4/TEST-M4-09_check.log)): 25 of 25 checks PASS, every error within 1 % of its prediction (tolerance 25 %); product `controllers.yaml` unchanged.
- **Screenshots:** 8 PNG, attempt 1 of each case, written next to the logs and committed in `08fbae7`. In the 4 RViz shots the right part of the window was covered by the Gazebo window, cutting off part of the trail (TS-036). Removed on 2026-11-13 (no imperfect pictures). The numbers come from the logs, not the images. Replaced by the R1 captures below.
- **Interpretation:** the bounds are not vacuous: errors of 1 % in the radii, 2 % in the track and 0.5 % in one radius are each detected, with the size the kinematics predicts. The Task C PASS results therefore show a correctly calibrated odometry, not insensitive tests.
- **Result:** TEST-M4-09 **PASS** for REQ-M4-08.

### Task D — TEST-M4-09 R1 (re-run for clean pictures), 2026-11-13 15:34–15:44 IST
**Why:** the first run's RViz screenshots were partly covered (TS-036). The re-run repeats the formal procedure unchanged in its test steps, with the corrected window layout (RViz started after Gazebo, 860 px, beside it) and screen recording of attempt 1. Revision `4db5197` (`amr_ws/src` clean), GUI and RViz shown.
**Procedure:** `SHOW=1 bash docs/evidence/M4/TEST-M4-09_procedure.sh -R1 3`, exit 0. 12 of 12 attempts valid (RTF 0.961–1.000); every attempt: 0 `[ERROR]` lines, no leftover process; harness exit 1 in every attempt, as expected.
- **R** ([log](docs/evidence/M4/TEST-M4-09-R1_R_straight_review.log)): distance criterion FAIL in all 6 legs, +0.9956 to +0.9998 % (prediction +1.00 %).
- **B** ([log](docs/evidence/M4/TEST-M4-09-R1_B_rotate_review.log)): yaw criterion FAIL in all 6 turns, ∓7.190 to ∓7.213° (prediction ∓7.196 to ∓7.202°).
- **L** ([CCW log](docs/evidence/M4/TEST-M4-09-R1_L_square_ccw_review.log), [CW log](docs/evidence/M4/TEST-M4-09-R1_L_square_cw_review.log)): CCW −1.898 to −1.901° (prediction −1.905°), CW −3.689 to −3.691° (prediction −3.696/−3.697°).
- Checker ([log](docs/evidence/M4/TEST-M4-09-R1_check.log)): 25 of 25 checks PASS; product `controllers.yaml` unchanged. Agreement with the first run: within 0.005 % (R) and 0.03° (B, L).
- **Pictures:** Gazebo and RViz stills and videos of attempt 1 per case (`TEST-M4-09-R1_<case>_a1_{gazebo,rviz}.{png,webm}`), reviewed: no error status, no covered window, full trail. Finalized and stored in [`docs/gallery/M4/TEST-M4-09/`](docs/gallery/M4/TEST-M4-09/) (videos converted to H.264 MP4). The videos start 2.1–5.0 s after recording began (stale frames cut, TS-036), so they miss the first ~1–4 s of the first motion; the stills are unaffected.
- **Result:** TEST-M4-09 R1 **PASS** for REQ-M4-08 (confirms the first run).

### Task D — TEST-M4-10 regression, 2026-11-13 17:02–17:37 IST
**Scope:** the runner suites `static` (TEST-M3-01, -13, -02 plus my records consistency checks) and `regression` (20 entries: every M2 motion/fault/frame procedure, M3 Task D IMU/encoder runs, TEST-M3-11 M2-with-sensors, TEST-M3-14), i.e. the plan's "M2 suite and M3 static checks" plus the M3 dynamic regression. Same procedures and criteria as their baselines (TA03R1, TA04).
**Procedure:** `python3 tools/run_suite.py static M410R2` and `SHOW=1 python3 tools/run_suite.py regression M410`, both exit 0. `SHOW=1` shows the Gazebo GUI for the 12 M2 entries (logs record `headless:=false`); the 8 M3 sensor entries run headless (`headless:=true`) because a GUI-mode shutdown hang is outside DEC-039 (TS-029 addendum, my decision).
- **Static** ([M410R2 summary](docs/evidence/TA/static-M410R2_summary.md), revision `16a5255`, clean): every entry PASS-candidate. TEST-M3-02's four `FAIL` lines are the deliberate M2-scope checks (TS-023), identical to TA03R1. Two earlier static runs are kept as history: [M410](docs/evidence/TA/static-M410_summary.md) (`colcon version-check` hung 10 min, ended by hand) and [M410R1](docs/evidence/TA/static-M410R1_summary.md) (30 s timeout fired); both left an empty `# colcon-core` line, otherwise 5/5 PASS-candidate (TS-037).
- **Regression** ([M410 summary](docs/evidence/TA/regression-M410_summary.md), revision `16a5255`, clean, 21 min): 20 of 20 PASS-candidate. Reviewed every log: 0 FAIL, 0 INVALID attempts, 0 `[ERROR]` lines, 0 leftover processes; TS-029 invalid (DEC-039) 0; TS-030 spin thread ended cleanly in all 23 M3 attempts; warnings the same as TA04.
- **Result:** TEST-M4-10 **PASS** for REQ-M4-09: M4 changed no M2 or M3 behaviour.

### Task D — TEST-M4-11 RViz (observed by me), 2026-11-13 17:45–17:47 IST
**Procedure:** `SHOW=1 bash docs/evidence/M4/TEST-M4_procedure.sh square_ccw 1 docs/evidence/M4/TEST-M4-11_square_ccw_review.log`, then `square_cw` with `TEST-M4-11_square_cw_review.log`, both exit 0. Revision `adfc7ea` (`amr_ws/src` clean); default M2 launch (DEC-045) with the Gazebo GUI and RViz `odometry.rviz` (fixed frame `odom`; RobotModel, TF, Odometry on `/diff_drive_controller/odom`). 1 of 1 valid run each (RTF 0.984 CCW, 0.987 CW); 0 `[ERROR]` lines, no leftover process.
- **Observed by me** (answers to the two criterion questions, 2026-11-13): (1) "Yes, closed both times": the odometry trail returned to its start and closed the square in the CCW and the CW run; (2) "Smooth, no jumps": the robot model and the TF frames moved continuously, with no jump, flicker or reset.
- Logged accuracy, recorded but not a criterion here (TEST-M4-06 owns it): end point CCW 0.02 mm, CW 0.00 mm; yaw −0.0000° in both.
- **Pictures:** RViz and Gazebo stills and videos of both runs (`TEST-M4-11_square_{ccw,cw}_a1_{gazebo,rviz}.{png,mp4}`), reviewed: RViz status OK, the closed square trail under the robot at its start, no covered window. Finalized (2026-11-13) and stored in [`docs/gallery/M4/TEST-M4-11/`](docs/gallery/M4/TEST-M4-11/).
- **Result:** TEST-M4-11 **PASS** for REQ-M4-02 (observed by me).

## Record Format for Future Tests

Use the record format in [docs/testing/test_plan.md §3](docs/testing/test_plan.md). It adds requirement IDs, revision, exit codes, status, and evidence to the fields used in the M0 entries above. Record failed runs as well as passing ones; a re-test gets a new dated entry.
