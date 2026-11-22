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
| TEST-TA-06 | Test automation | PASS (local procedure: 3 of 3 cases as expected; CI run #4: drawing check step PASS, job green) | [local log](docs/evidence/TA/TEST-TA-06_drawing_check.log), [CI step log](docs/evidence/TA/TEST-TA-06_ci_GH4.log) |
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
| TEST-M5-01 | M5 | PASS under DEC-053 (build clean; M1, M2 and M3/M5 expansions identical; protected files unchanged; only the `slam_toolbox` dependency line and a comment in existing files) | [review log](docs/evidence/M5/TEST-M5-01_review.log), [negative control](docs/evidence/M5/TEST-M5-01-negctl_review.log) |
| TEST-M5-02 | M5 | FAIL (all SLAM interface checks PASS in 3 of 3 attempts; attempt 2: `gz sim` exited with code 1 after the SIGINT→SIGTERM shutdown escalation, outside the DEC-039 signature, TS-039) | [review log](docs/evidence/M5/TEST-M5-02_review.log) |
| TEST-M5-02 R1 | M5 | PASS (3 of 3 valid attempts, every SLAM interface check PASS; all shutdowns CLEAN, 0 leftovers by name; 1 attempt invalid for RTF 0.49 < 0.5, repeated; TS-029 invalid 0) | [review log](docs/evidence/M5/TEST-M5-02-R1_review.log) |
| TEST-M5-03 | M5 | PASS (3 of 3 valid mapping runs; wall P95 0.065–0.070 m, ghosts 0, completeness ≥ 99.56 %, interior within 0.019 m, walls within 0.15°, L1 absent) | [review log](docs/evidence/M5/TEST-M5-03_review.log) |
| TEST-M5-04 | M5 | PASS (same runs; SLAM pose within 13.5 mm and 0.200° at every rest point) | [review log](docs/evidence/M5/TEST-M5-03_review.log) |
| TEST-M5-05 | M5 | PASS (reference map = attempt 1; pose graph decompresses byte-identical; map_server serves 0 differing cells; negative control detected) | [review log](docs/evidence/M5/TEST-M5-05_review.log) |
| TEST-M5-05 R1 | M5 | PASS (on the DEC-055 corrected map; origin difference exactly −0.025 m in x and y; 0 differing cells) | [review log](docs/evidence/M5/TEST-M5-05-R1_review.log) |
| TEST-M5-06 | M5 | PASS (3 of 3 valid runs with the TEST-M4-09 overrides; odometry drift 0.199 m / −3.53°, within 0.2 % of CALC-M5-04; SLAM pose within 35.1 mm and 0.353°; maps within bounds) | [review log](docs/evidence/M5/TEST-M5-06_review.log) |
| TEST-M5-07 | M5 | PASS (uncorrected reference map; original PASS, 5 of 5 distortions FAIL on their measure) | [review log](docs/evidence/M5/TEST-M5-07_review.log) |
| TEST-M5-07 R1 | M5 | PASS (corrected reference map, wall P95 0.045 m; 5 of 5 distortions FAIL on their measure) | [review log](docs/evidence/M5/TEST-M5-07-R1_review.log) |
| TEST-M5-08 | M5 | PASS (static 7/7, regression 20/20, m4 9/9 executed entries reviewed; TEST-M4-12/-03 covered by their static logs; TS-029 invalid 1, repeated) | [regression summary](docs/evidence/TA/regression-M508_summary.md), [m4 summary](docs/evidence/TA/m4-M508_summary.md), [static summary](docs/evidence/TA/static-M508_summary.md) |
| TEST-M5-09 | M5 | PASS (observed by me: map grew, walls straight and single, W1 mapped on both faces, scan on the walls at the end, returned to the start, no jumps; logged run PASS, SLAM pose within 7.4 mm and 0.200°) | [review log](docs/evidence/M5/TEST-M5-09_review.log) |
| TEST-M5-10 | M5 | PASS (checker 0 mismatches locally and in CI; every injected fault detected; `m5` suite present; TEST-M5-07 in `ci`; CI run #32 green) | — (checker reads my private planning files; script and log not published) |
| TEST-M6-01 | M6 | PASS (build clean; M1, M2 and M3–M5 expansions identical; M5 product and reference-map files unchanged; existing files changed only by the four Nav2 dependency lines, the maps install rule and comments; AMCL map copy differs only by origin +0.025 m) | [review log](docs/evidence/M6/TEST-M6-01_review.log), [procedure](docs/evidence/M6/TEST-M6-01_procedure.sh) |
| TEST-M6-02 | M6 | PASS (3 of 3 valid attempts, every interface check PASS; one `map → odom` writer; `/map` and `/map_amcl` equal their files; all shutdowns CLEAN, 0 leftovers; TS-029 invalid 0) | [review log](docs/evidence/M6/TEST-M6-02_review.log), [procedure](docs/evidence/M6/TEST-M6-02_procedure.sh), [checker](docs/evidence/M6/TEST-M6-02_interface_check.py) |
| TEST-M6-03 | M6 | PASS 3/3 forward, 3/3 reverse (worst at rest 13.2 mm, 0.139°; moving P95 ≤ 11.7 mm, 0.148°; moving max 13.2 mm) | [forward](docs/evidence/M6/TEST-M6-03-forward_review.log), [reverse](docs/evidence/M6/TEST-M6-03-reverse_review.log) |
| TEST-M6-04 | M6 | PASS 3/3 (recovery 2.12, 2.41, 3.47 m ≤ 4.0 m, DEC-063; afterwards rest ≤ 19.2 mm, moving max ≤ 39.0 mm) | [review log](docs/evidence/M6/TEST-M6-04_review.log) |
| TEST-M6-04 | M6 | FAIL (`m6` suite run M611: recovery 2.36, **4.84**, 2.93 m vs DEC-063's 4.0 m; every bound after recovery PASS) | [review log](docs/evidence/M6/TEST-M6-04-M611_review.log) |
| TEST-M6-04 R1 | M6 | PASS 3/3 under DEC-065 (recovery 5.68, 3.48, 2.91 m ≤ 6.0 m; afterwards rest ≤ 42.3 mm, moving max ≤ 49.9 mm) | [review log](docs/evidence/M6/TEST-M6-04-M611R1_review.log) |
| TEST-M6-05 | M6 | PASS 3/3 forward, 3/3 reverse (odometry drift 198.6 mm, +0.1 %, and 438.6 mm, −0.3 %, of CALC-M5-04; localization rest ≤ 30.4 mm, moving max ≤ 33.5 mm) | [forward](docs/evidence/M6/TEST-M6-05-forward_review.log), [reverse](docs/evidence/M6/TEST-M6-05-reverse_review.log) |
| TEST-M6-06 | M6 | PASS 3/3 forward, 3/3 reverse (unmapped boxes; rest ≤ 11.7 mm, moving max ≤ 11.9 mm) | [forward](docs/evidence/M6/TEST-M6-06-forward_review.log), [reverse](docs/evidence/M6/TEST-M6-06-reverse_review.log) |
| TEST-M6-07 | M6 | FAIL (attempt 1: EKF parameter query got no reply, TS-047 checker defect; every fusion, accuracy and localization measure PASS in 3/3 runs) | [review log](docs/evidence/M6/TEST-M6-07_review.log) |
| TEST-M6-07 R1 | M6 | PASS 3/3 (raw odometry 400.0 mm, +0.1 % of CALC-M5-04; fused ≤ 9.7 mm (≤ 2.4 % of raw), ≤ 0.115°; one `odom → base_footprint` writer, the EKF; localization rest ≤ 24.9 mm, moving max ≤ 24.9 mm) | [review log](docs/evidence/M6/TEST-M6-07-R1_review.log) |
| TEST-M6-08 | M6 | PASS (original PASS; offset 0.08 m, rotation 1.5°, one 0.30 m jump and a 0.5 s delay each FAIL on their expected measure) | [review log](docs/evidence/M6/TEST-M6-08_review.log), [tool](docs/evidence/M6/TEST-M6-08_distort.py) |
| TEST-M6-09 | M6 | FAIL (static 11/11, regression 20/20, m4 11/12, m5 5/7 PASS-candidate; TEST-M4-12 and TEST-M5-10 on unindexed batch evidence (TS-043 class), TEST-M5-01 on M6's approved dependencies (TS-049); every M1–M5 behaviour check PASS) | [static](docs/evidence/TA/static-M609S_summary.md), [regression](docs/evidence/TA/regression-M609RH_summary.md), [m4](docs/evidence/TA/m4-M609M4_summary.md), [m5](docs/evidence/TA/m5-M609M5_summary.md) |
| TEST-M6-09 R1 | M6 | PASS (TEST-M5-01 R1 under DEC-064; records 5/5 after indexing, with TEST-M4-12 and TEST-M5-10 R1) | [TEST-M5-01 R1](docs/evidence/M5/TEST-M5-01-M609M5R1_review.log), records (not published) |
| TEST-M6-10 | M6 | PASS (observed by me: wrong-start particles converged early, scan on the walls, no jumps; global-localization demonstration shown: one cluster, rotated about 180°, not corrected (DEC-058, not judged)) | [wrong start](docs/evidence/M6/TEST-M6-10-wrongstart_review.log), [global](docs/evidence/M6/TEST-M6-10-global_review.log) |
| TEST-M6-11 | M6 | PASS (checker zero mismatches; mutation check 20/20 faults detected; `m6` suite 12 entries, run in full (M611); CI run 44805433769 PASS) | — (checker reads my private planning files; script and log not published) |
| TEST-M7-01 | M7 | PASS (build clean; M1, M2 and M3–M6 expansions identical; 17 simulation, localization and map files unchanged since `9777615`; existing files changed only by the seven Nav2 dependency lines, the `behavior_trees` install rule and comments; both behavior trees = installed minus Spin and BackUp) | [review log](docs/evidence/M7/TEST-M7-01_review.log), [procedure](docs/evidence/M7/TEST-M7-01_procedure.sh) |
| TEST-M7-01 R1 | M7 | PASS (after DEC-075: 27 steps exit 0; `sim.launch.py` changed only by the 12 added `gui_config` lines, 0 removed; negative control with one stray line FAIL as expected) | [review log](docs/evidence/M7/TEST-M7-01-R1_review.log), [procedure](docs/evidence/M7/TEST-M7-01_procedure.sh) |
| TEST-M7-02 | M7 | PASS (3 of 3 valid attempts, 165 PASS lines, 0 FAIL; one `/cmd_vel` publisher; every command forwarded by the guard; footprints = CALC-M7-01 + 0.01 m padding; all shutdowns CLEAN, 0 leftovers; TS-029 invalid 0) | [review log](docs/evidence/M7/TEST-M7-02_review.log), [procedure](docs/evidence/M7/TEST-M7-02_procedure.sh), [checker](docs/evidence/M7/TEST-M7-02_interface_check.py) |
| TEST-M7-02 R1 | M7 | PASS (after DEC-077 and TS-052: 3 of 3 valid attempts, 171 PASS lines, 0 FAIL; NavFn `tolerance` 0.0 and `allow_unknown` false read back; every command forwarded under the guard stamp rule; all shutdowns CLEAN, 0 leftovers; TS-029 invalid 0) | [review log](docs/evidence/M7/TEST-M7-02-R1_review.log), [procedure](docs/evidence/M7/TEST-M7-02_procedure.sh), [checker](docs/evidence/M7/TEST-M7-02_interface_check.py) |
| TEST-M7-07 | M7 | PASS (checker sensitivity: the dry-run-4 sequence log PASSES; the five distorted copies FAIL on arrival_position, arrival_heading, clearance, cmd_limits and moving_p95_position respectively) | [review log](docs/evidence/M7/TEST-M7-07_review.log), [tool](docs/evidence/M7/TEST-M7-07_distort.py), [checker](docs/evidence/M7/TEST-M7_nav_check.py) |
| TEST-M7-03 | M7 | PASS (3 of 3: G1–G6 all SUCCEEDED; arrival ≤ 0.105 m and ≤ 5.66°; time ≤ 1.02× nominal; clearance ≥ 0.481 m; moving P95 ≤ 11.9 mm; 0 guard drops; shutdowns CLEAN) | [review log](docs/evidence/M7/TEST-M7-03_review.log), [procedure](docs/evidence/M7/TEST-M7_procedure.sh) |
| TEST-M7-04 | M7 | PASS (3 of 3: route G1 → G3 → G5 SUCCEEDED in 63.4–63.8 s, 0.78× nominal; final arrival ≤ 0.101 m and ≤ 5.48°; clearance ≥ 0.475 m; moving P95 ≤ 8.9 mm; 0 guard drops; shutdowns CLEAN) | [review log](docs/evidence/M7/TEST-M7-04_review.log), [procedure](docs/evidence/M7/TEST-M7_procedure.sh) |
| TEST-M7-05 | M7 | **FAIL** (measurements PASS in 3 of 3: both goals ABORTED, 0.0 mm of motion, no commands; attempt 3's simulation shutdown exited 1, TS-039, outside DEC-039; handled by DEC-079, re-run as R1) | [review log](docs/evidence/M7/TEST-M7-05_review.log), [kept launch logs](docs/evidence/M7/TEST-M7-05_a3_sim_launch.log) |
| TEST-M7-05 R1 | M7 | PASS (after DEC-079: 3 of 3; both goals ABORTED, inside P1 after 22.5–23.6 s, outside the map after 0.1 s; 0.0 mm of motion, no commands; all shutdowns CLEAN, TS-039 invalid 0) | [review log](docs/evidence/M7/TEST-M7-05-R1_review.log) |
| TEST-M7-06 | M7 | PASS (3 of 3: CANCELED after 1.021–1.029 m; 39.1–52.9 mm of travel after the cancel; stopped within 0.4–0.5 s, then 0.0 mm/s; shutdowns CLEAN) | [review log](docs/evidence/M7/TEST-M7-06_review.log) |
| TEST-M7-08 | M7 | **FAIL** (headless, `8bbebeb`: static 11/11, regression 20/20, m4 9/11, m5 3/7, m6 8/12 PASS-candidate; six offline entries REFUSED because one tag was reused across suites; TEST-M5-01 and TEST-M6-01 failed on the DEC-075 `sim.launch.py` option, handled by DEC-080; TEST-M5-02 and TEST-M6-03 reverse each failed one attempt on a dropped lifecycle `change_state` reply, TS-055; re-run as R1) | [static](docs/evidence/TA/static-M708_summary.md), [regression](docs/evidence/TA/regression-M708_summary.md), [m4](docs/evidence/TA/m4-M708_summary.md), [m5](docs/evidence/TA/m5-M708_summary.md), [m6](docs/evidence/TA/m6-M708_summary.md) summaries |
| TEST-M7-08 R1 | M7 | PASS (after DEC-080: records 6/6, ci 7/7 after the TS-056 fix, TEST-M5-01 and TEST-M6-01 every step, TEST-M5-02 and TEST-M6-03 reverse 3 of 3 valid runs, shutdowns CLEAN) | records summary (not published), [ci summary](docs/evidence/TA/ci-M708C2_summary.md); [TEST-M6-03 reverse log](docs/evidence/M6/TEST-M6-03-M708R1-reverse_review.log) |
| TEST-M7-09 | M7 | PASS (observed by me: path, both costmaps and footprint shown; six goals reached without contact; goals inside a wall refused. L1 probe shown, not judged: the robot drove into the invisible low box, localization was lost, later successes false; TS-058, M8) | [review log](docs/evidence/M7/TEST-M7-09_review.log), [pose mismatch](docs/evidence/M7/TEST-M7-09_a1_pose_mismatch.log) |
| TEST-M7-10 | M7 | PASS (checker all checks passed; mutation check 21/21 faults detected; `m7` suite 8 of 8 entries, GUI shown; TEST-M7-05 attempt 3 INVALID under DEC-079 and repeated; all other shutdowns CLEAN, 0 leftovers) | [summary](docs/evidence/TA/m7-M710_summary.md), checker and mutation logs not published |
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

### TEST-TA-06 — geometry-drawing check in CI, 2026-11-15 00:53–00:58 IST (2026-11-14 19:23–19:28 UTC)
**Under test:** `tools/geometry_drawing.py --check` (the dimensioned drawing `docs/design/amr_geometry_drawing.svg` is current, and the `mechanical_geometry.md` §2 table equals `amr_properties.xacro`) and its new first step in `.github/workflows/ci.yml`.

- **Local procedure** (`bash docs/evidence/TA/TEST-TA-06_procedure.sh`, clean `40d8799`): exit 0. Repository: exit 0, 12 of 12 table rows PASS, drawing up to date. Negative cases on a scratch copy: a hand-edited SVG gave exit 1 (stale); `wheel_track` 0.404 in the table gave exit 1 (mismatch). The repository was not modified ([log](docs/evidence/TA/TEST-TA-06_drawing_check.log)).
- **CI run #4** (GitHub run 43631890515, push of `40d8799`): the step ran on the hosted runner in the `ros:jazzy-ros-base` container and printed 12 of 12 rows PASS and `# overall: PASS`; the job passed ([step log](docs/evidence/TA/TEST-TA-06_ci_GH4.log)).
- **Limitation (by design):** CI starts only on code pushes and on manual dispatch (REQ-TA-05). A push that edits only the drawing or the design table is checked by the next code push or a manual dispatch.
- **Result:** TEST-TA-06 **PASS** for REQ-TA-05.

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

## M5 — SLAM (epic plan [docs/milestones/M5_slam.md](docs/milestones/M5_slam.md); criteria DEC-047, TEST-M5-01 restated by DEC-053)

### Task A — TEST-M5-01, 2026-11-15 01:50 IST
**Under test:** the M5 Task A changes (`10a669d`) against the M4 closeout `517608f`. Revision `7be0c86` (`amr_ws/src` clean). Procedure written before its formal run; no simulation (static test).
**TEST-M5-01** (REQ-M5-09): `bash docs/evidence/M5/TEST-M5-01_procedure.sh`, exit 0 ([log](docs/evidence/M5/TEST-M5-01_review.log)).
- Build: colcon exit 0, 0 warning lines. Default expansion byte-identical to `TEST-M1-02_amr.urdf`; expansions with `use_ros2_control:=true` (6452 bytes) and with `use_sensors:=true` added (9912 bytes) byte-identical to the `517608f` expansions.
- `sim.launch.py`, `controllers.yaml`, `amr.sensors.xacro`, `amr_properties.xacro`: unchanged since `517608f`.
- `amr_ws/src` since `517608f`: 4 new files (`slam_toolbox.yaml`, `slam.launch.py`, `mapping.rviz`, `mapping_arena.sdf`); 2 modified: `package.xml` (only `+  <exec_depend>slam_toolbox</exec_depend>`) and `CMakeLists.txt` (2 changed lines, both comments).
- **Negative control** (same day, `BASE=30d737f`, before the M4 covariance change): exit 1; step 4 flagged `sim.launch.py` and `controllers.yaml`, step 5 flagged them as modified ([log](docs/evidence/M5/TEST-M5-01-negctl_review.log)). The procedure detects real changes.
- Criterion: the accepted wording "only new files" is not met literally (`package.xml`, `CMakeLists.txt`). The restated criterion was accepted as DEC-053 before this result was recorded.
- **Result:** TEST-M5-01 **PASS** (under DEC-053).

### Task A — TEST-M5-02, 2026-11-15 02:02–02:06 IST
**Under test:** the SLAM interface (REQ-M5-02, -03) on `3157779` (`amr_ws/src` clean); `sim.launch.py headless:=false sensors:=true world:=mapping_arena.sdf` + `slam.launch.py`; Gazebo 8.15.0, slam_toolbox 2.8.5; Gazebo GUI and RViz shown (`SHOW=1`); attempt 1 recorded after I arranged the windows. Procedure and checker committed before the formal run; two scratch dry runs found TS-038 and a parameter-timing defect, fixed before it (M5 plan §12).
**TEST-M5-02:** `SHOW=1 LAYOUT_FLAG=<flag> bash docs/evidence/M5/TEST-M5-02_procedure.sh 3 docs/evidence/M5/TEST-M5-02_review.log`, exit 1 ([log](docs/evidence/M5/TEST-M5-02_review.log)).
- Checks, attempts 1–3, each PASS: before SLAM, `/tf` publishers `diff_drive_controller`, `robot_state_publisher`, no `map → odom`, no `/map`. After: `/slam_toolbox` active; `use_sim_time` true; `max_laser_range` 12.0; `/scan` `range_min` 0.12 m (TS-038); `slam_toolbox` subscribes `/scan`; `/map` from `slam_toolbox` only, frame `map`, 0.05 m, 201 × 161 cells; `map → odom` 490 / 482 / 481 messages during the drive, sequence numbers all distinct, no gaps, one transform per message; the only added `/tf` publisher is `slam_toolbox`; never on `/tf_static`; stamps on simulation time; one parent per frame; chain `map → odom → base_footprint → base_link → lidar_mount_link → laser_frame`; `map → laser_frame` resolves.
- INFO: RTF 0.94 / 0.96 / 0.96; scans 93 per drive (10.04–10.05 Hz); pose-graph nodes 2; dropped-scan lines in the SLAM log 0 / 0 / 0.
- Shutdown: SLAM launch CLEAN in all three; simulation launch CLEAN in attempts 1 and 3. **Attempt 2:** `gz sim` did not stop within 5 s of SIGINT, was escalated to SIGTERM and died with **exit code 1**; 0 leftover processes. DEC-039 covers only exit codes −9/−15, so the classifier returned OTHER and the attempt FAILED (TS-039). TS-029 invalid attempts: 0.
- The full launch log of attempt 2 was not kept (procedure defect, TS-039). The attempt-1 pictures were deleted unreviewed-for-commit: portrait camera view with the robot too small, map from 2 scans; to be re-captured.
- **Result:** TEST-M5-02 **FAIL** (shutdown criterion, attempt 2). Re-test after the TS-039 investigation.

### Task A — TEST-M5-02 R1, 2026-11-15 02:16–02:20 IST
**Under test:** as the first run, on `8130ee8` (`amr_ws/src` clean), with the procedure changes made after it (full launch logs of unclean shutdowns kept; leftovers also counted by name; camera view from the layout file). Between the runs: TS-039 source reading and rig, 10 of 10 GUI shutdowns CLEAN ([log](docs/evidence/M5/TS-039_gui_shutdown.log)). No criterion changed.
**TEST-M5-02 R1:** `SHOW=1 LAYOUT_FLAG=<flag> bash docs/evidence/M5/TEST-M5-02_procedure.sh 3 docs/evidence/M5/TEST-M5-02-R1_review.log`, exit 0 ([log](docs/evidence/M5/TEST-M5-02-R1_review.log)). Gazebo GUI and RViz shown; I placed the windows side by side; camera view `0.8 0.0 8.0 3.0 0.0 0`, set from three trial screenshots before the recording.
- Attempts 1, 2, 4 (valid): every check PASS, as in the first run (lifecycle active; `use_sim_time` true; `max_laser_range` 12.0; `/scan` `range_min` 0.12 m; `/scan` subscribed; `/map` from `slam_toolbox` only, frame `map`, 0.05 m, 201 × 161 cells; `map → odom` 502 / 490 / 477 messages, sequence numbers distinct, no gaps, one transform each; only added `/tf` publisher `slam_toolbox`; not on `/tf_static`; simulation-time stamps; one parent per frame; full chain; `map → laser_frame` resolves).
- Attempt 3: every check PASS, but RTF 0.49 (9.25 s of simulation time in 18.99 s wall), below the 0.5 validity limit: INVALID, not counted, repeated as attempt 4. Cause not investigated (a one-off; the other attempts 0.93–0.97).
- INFO: RTF 0.93 / 0.95 / 0.97 (valid attempts); 93 scans per drive (9.99–10.06 Hz); pose-graph nodes 2. Dropped-scan lines: 1 in attempts 1 and 2, both at SLAM start-up (simulation time 14.2 s and 13.2 s, before the drive; tf2 message filter: scan older than the TF cache, and queue full), 0 in attempts 3 and 4.
- Shutdown: SLAM and simulation launches CLEAN in all 4 attempts; 0 leftover processes by name or by process group; no launch log needed keeping. TS-029 invalid attempts: 0. TS-039 did not recur.
- Pictures and videos of attempt 1 in `docs/gallery/_pending/M5/TEST-M5-02/` (awaiting review).
- **Result:** TEST-M5-02 **PASS** (R1). The first run's FAIL stays on record.

### Task C — TEST-M5-03 and TEST-M5-04, 2026-11-15 02:58–03:11 IST
**Under test:** M5 product configuration (Task A) on `59ee7f0` (`amr_ws/src` clean); tooling from Task B (`TEST-M5_route.py`, `TEST-M5_map_run.py`, `TEST-M5_map_check.py`, `TEST-M5_procedure.sh`), dry-run before this run (M5 plan §12). Product controllers file (no injected odometry error). Reference-map rule fixed before the run: attempt 1's map (M5 plan §12).
**Command:** `SHOW=1 LAYOUT_FLAG=<flag> PG_DIR=<scratch> bash docs/evidence/M5/TEST-M5_procedure.sh 3 docs/evidence/M5/TEST-M5-03_review.log`, exit 0 ([log](docs/evidence/M5/TEST-M5-03_review.log)). Gazebo GUI and RViz shown; I placed the windows side by side; camera view `0.8 0.0 8.0 3.0 0.0 0`. Per attempt: rest-point CSV, saved map (`.pgm`/`.yaml`) and checker JSON in `docs/evidence/M5/TEST-M5-03_a<N>_*`.
- Route (all 3 attempts): 11 rest points, about 200.7 s simulation time, RTF 0.96 / 0.99 / 1.00 (all valid), max cross-track 9.8 / 9.8 / 9.7 mm.
- **TEST-M5-04** (REQ-M5-05), `map → base_footprint` vs ground truth at every rest point (bound 0.05 m, 1.0°): largest position error 13.5 / 12.4 / 9.6 mm; largest heading error 0.200° in each attempt (the heading errors take the values 0 or ±0.200°). End of route: 3.9 / 10.8 / 6.8 mm. Odometry error at the end 0.0 mm (no injected error; drift is tested in TEST-M5-06).
- **TEST-M5-03** (REQ-M5-01, -04), checker on each saved map (DEC-047 bounds):
  - wall accuracy P95: 0.070 / 0.065 / 0.068 m (≤ 0.10 m); max 0.079 / 0.065 / 0.072 m;
  - ghost cells beyond 0.25 m: 0 / 0 / 0 (≤ 0.5 %);
  - completeness: 99.78 / 99.56 / 99.89 % (≥ 90 %);
  - interior: 9.993 × 7.985 / 9.985 × 7.981 / 9.989 × 8.000 m (10.0 × 8.0 ± 0.10 m); largest wall rotation 0.05 / 0.15 / 0.10° (≤ 1.0°); parallel and perpendicular within 0.18°;
  - low box L1: 0 occupied cells in its footprint in each map.
  - INFO: maps 202 × 162 (attempt 3: 202 × 163) cells; origins (−2.046, −4.055), (−2.062, −4.060), (−2.053, −4.057); best-fit offset (−0.025, −0.025) m in each, rotation ≤ 0.25°. *Correction (2026-11-15, after recording):* the first wording, "half a cell: the cell-centre convention", had not been checked. The offset is a real half-cell shift: SLAM Toolbox writes the centre of cell 0 where ROS expects its corner (TS-041). The measured values above stand.
- Map save: `map_saver_cli` exit 0 in all 3. Pose graph serialized in all 3 (`result=0`): `.posegraph` 7 403 717 / 7 403 717 / 7 403 933 bytes, `.data` 471 131 bytes (gzip -9 about 333 000 + 233 000 bytes); kept outside the repository (DEC-054: the reference one is committed compressed with TEST-M5-05).
- SLAM log: 0 [ERROR] lines, 0 dropped-scan lines. Shutdown: SLAM and simulation launches CLEAN in all 3; 0 leftover processes; TS-029 invalid attempts 0.
- Pictures and videos of attempt 1: accepted, in `docs/gallery/M5/TEST-M5-03/`.
- **Result:** TEST-M5-03 **PASS**; TEST-M5-04 **PASS**. Attempt 1's map is the reference map (TEST-M5-05).

### Task C — TEST-M5-05, 2026-11-15 03:17 IST
**Under test:** the reference map `amr_ws/src/amr_bringup/maps/mapping_arena.{pgm,yaml}` and the compressed pose graph `mapping_arena.{posegraph,data}.gz` (DEC-054), made from TEST-M5-03 attempt 1 by the commands in the procedure header; revision `dae225d` (`amr_ws/src` clean). No simulation. Procedure dry-run before the formal run (TS-040 found and fixed).
**Command:** `bash docs/evidence/M5/TEST-M5-05_procedure.sh docs/evidence/M5/TEST-M5-05_review.log <PG_DIR>/TEST-M5-03_a1_posegraph`, exit 0 ([log](docs/evidence/M5/TEST-M5-05_review.log)).
- Save (from TEST-M5-03): `map_saver_cli` wrote the `.pgm`/`.yaml` and `serialize_map` returned `result=0` in each attempt (TEST-M5-03 record).
- Reference = attempt 1: `.pgm` byte-identical to `TEST-M5-03_a1_map.pgm`; `.yaml` identical except the image name (`mapping_arena.pgm`).
- Pose graph: both `.gz` files pass `gzip -t` and decompress byte-identical to the attempt 1 serialization: `.posegraph` 7 403 717 bytes (SHA-256 `4a2eb700…0269`), `.data` 471 131 bytes (SHA-256 `43f503b8…601d`); committed size 332 464 + 232 760 bytes.
- Reload: Nav2 `map_server` configured and activated (lifecycle `active`); `/map` from `map_server` only, frame `map`, 202 × 162 cells, 0.05 m, origin (−2.046, −4.055, 0) as in the file; **0 of 32 724 cells differ** (971 occupied, 30 851 free, 902 unknown). `map_server` stopped on SIGINT with exit 0, 0 [ERROR] lines.
- Negative control: a served copy with one occupied cell turned free: the check FAILS with 1 cell differing (as expected).
- Leftover `map_server` processes: 0.
- **Result:** TEST-M5-05 **PASS**.

### Task C — TEST-M5-07, 2026-11-15 03:20 IST (on the uncorrected reference map)
**Under test:** `TEST-M5-07_distort.py` and `TEST-M5_map_check.py` (Task B, `8ea6f20`) on the reference map as first committed (`dae225d`, origin as SLAM saved it), revision `86e3b56`. No simulation.
**Command:** `python3 -I docs/evidence/M5/TEST-M5-07_distort.py amr_ws/src/amr_bringup/maps/mapping_arena.yaml <tmp>`, exit 0 ([log](docs/evidence/M5/TEST-M5-07_review.log), [summary](docs/evidence/M5/TEST-M5-07_summary.json)).
- Original: every measure PASS. Rotate 2°: dimensions FAIL (walls 0.80–1.79°). Shift 0.15 m: wall accuracy FAIL (P95 0.179 m). Scale × 1.02: dimensions FAIL (10.059 × 8.178 m). Erase north wall: completeness FAIL (76.81 %). Ghost wall: ghosts FAIL (7.612 %). Occupied-cell counts of the geometric copies 971 / 971 / 993 (no walls lost off the image).
- **Result:** PASS. Before it was recorded, TS-041 was found and the reference map corrected (DEC-055); re-run below on the corrected map. This run is kept as history.

### Task C — TEST-M5-05 R1 and TEST-M5-07 R1, 2026-11-15 03:27–03:28 IST (corrected reference map, DEC-055)
**Under test:** the reference map with its origin moved by −0.025 m in x and y (DEC-055, TS-041), revision `695f5ea` (`amr_ws/src` clean). TEST-M5-05 procedure updated to check the exact origin difference. No simulation.
**TEST-M5-05 R1:** `bash docs/evidence/M5/TEST-M5-05_procedure.sh docs/evidence/M5/TEST-M5-05-R1_review.log <PG_DIR>/TEST-M5-03_a1_posegraph`, exit 0 ([log](docs/evidence/M5/TEST-M5-05-R1_review.log)).
- `.pgm` byte-identical to attempt 1; `.yaml` identical except the image name and the origin; origin (−2.071, −4.080, 0) = attempt 1 origin + (−0.025, −0.025, 0) exactly.
- Pose graph: as the first run (both `.gz` decompress byte-identical to the attempt 1 serialization).
- Reload: `map_server` active; `/map` frame `map`, 202 × 162, 0.05 m, origin (−2.071, −4.080, 0); 0 of 32 724 cells differ; exit 0 on SIGINT. Negative control: 1 cell differs, FAIL as expected. Leftovers 0.
- **Result:** TEST-M5-05 **PASS** (R1). The first run (on the uncorrected file) also passed and stays on record.
**TEST-M5-07 R1:** the same command on the corrected map, exit 0 ([log](docs/evidence/M5/TEST-M5-07-R1_review.log), [summary](docs/evidence/M5/TEST-M5-07-R1_summary.json)).
- Original: every measure PASS; wall P95 0.045 m (median 0.005 m; was 0.070 m before the correction); interior 9.993 × 7.986 m; checker best-fit offset (0.000, 0.000).
- Rotate 2°: dimensions FAIL (walls 1.24–1.79°). Shift 0.15 m: wall accuracy FAIL (P95 0.154 m). Scale × 1.02: dimensions FAIL (10.059 × 8.178 m). Erase north wall: completeness FAIL. Ghost wall: ghosts FAIL. Each copy also fails other measures where expected (listed in the log); no walls lost off the image.
- **Result:** TEST-M5-07 **PASS** (R1).

### Task D — TEST-M5-06, 2026-11-15 03:35–03:48 IST
**Under test:** M5 product configuration on `6cb8f23` (`amr_ws/src` clean), with the TEST-M4-09 odometry errors injected as test-only overrides (DEC-043): `wheel_separation_multiplier: 1.02`, `left_wheel_radius_multiplier: 1.01`, `right_wheel_radius_multiplier: 1.01` in a temporary copy of `controllers.yaml` (the log shows the diff; the product file was checked unchanged). CALC-M5-04 reviewed before the run (M5 plan §12); procedure dry-run before the formal run (scratch: drift 0.1986 m, −3.530°).
**Command:** `SHOW=1 LAYOUT_FLAG=<flag> bash docs/evidence/M5/TEST-M5-06_procedure.sh 3 docs/evidence/M5/TEST-M5-06_review.log`, exit 0 ([log](docs/evidence/M5/TEST-M5-06_review.log)). Gazebo GUI and RViz shown; I placed the windows side by side. Per attempt: `TEST-M5-06_a<N>_{rest.csv,map.pgm,map.yaml,check.json}`.
- Route: 11 rest points each; RTF 0.92 / 0.96 / 0.98 (all valid); max cross-track 9.8 / 9.8 / 9.9 mm.
- **Odometry drift (the injected error), end of route:** 0.1986 m and −3.530° in each attempt; CALC-M5-04 predicted 0.1983 m and −3.529° (+0.1 to +0.2 % and +0.0 %; bound ± 25 %). Largest odometry error during the route 0.254 m. Exceeds 3× the pose bound (0.15 m, 3.0°) in each attempt.
- **SLAM pose** (`map → base_footprint` vs ground truth; bound 0.05 m, 1.0° at every rest point): largest 31.0 / 35.1 / 20.9 mm and 0.318 / 0.353 / 0.131°; at the end 17.6 / 6.5 / 20.9 mm. Larger than without injected error (TEST-M5-03/-04: up to 13.5 mm), within the bound. `map → odom` at the end corrects 3.4–3.6° of heading.
- **Map** (checker, DEC-047 bounds, maps as saved): wall P95 0.060 / 0.064 / 0.026 m; ghosts 0 / 0 / 0; completeness 99.56 / 99.56 / 99.78 %; interior 9.997 × 7.996 / 9.993 × 7.996 / 9.997 × 7.988 m; largest wall rotation 0.23 / 0.33 / 0.08°; L1 absent in each.
- Map save and pose-graph serialization: OK in each (pose graphs not kept). SLAM log 0 [ERROR] lines, 0 dropped-scan lines; shutdowns CLEAN; 0 leftovers; TS-029 invalid attempts 0.
- Pictures and videos of attempt 1: accepted, in `docs/gallery/M5/TEST-M5-06/`.
- **Result:** TEST-M5-06 **PASS**.

### Task D — TEST-M5-08 regression, 2026-11-15 03:51–04:40 IST
**Scope (REQ-M5-09):** the runner suites `static` (7 entries: TEST-M2-11, TEST-M3-12, TEST-M4-12, TEST-M3-01, -13, -02, TEST-M4-03), `regression` (the 20 M2/M3 entries of TEST-M4-10) and `m4` (TEST-M4-12, -01, -03, -02, -04 to -09), on the M5 product. Same procedures and criteria as their baselines (TEST-M4-10, TEST-M4-12).
**Commands:** `python3 tools/run_suite.py static M508` (exit 0), `SHOW=1 python3 tools/run_suite.py regression M508` (exit 0), `SHOW=1 python3 tools/run_suite.py m4 M508` (exit 1, see the m4 item). `SHOW=1` shows the Gazebo GUI for the M2 and M4 entries (`headless:=false`); the 8 M3 sensor entries run headless as in TEST-M4-10 (TS-029 addendum). Serial, one simulation at a time.
- **Product under test:** `amr_ws/src` unchanged from `5a3414a` to `7832350`, and `tools/` unchanged, so every entry ran the same product and runner. The entry logs record the revision at their own start (`5a3414a` static; `64d38f2` for the first regression entry, later ones up to `7832350`); all `amr_ws/src` clean.
- **Static** ([summary](docs/evidence/TA/static-M508_summary.md), 3 s): 7 of 7 PASS-candidate. TEST-M3-02's four `FAIL` lines are the deliberate M2-scope checks (TS-023), identical to M410R2.
- **Regression** ([summary](docs/evidence/TA/regression-M508_summary.md), 22 min): 20 of 20 PASS-candidate. Reviewed every log: 0 FAIL in counted attempts, 0 leftover processes, every log's `[ERROR]` count 0 except TEST-M3-14 attempt 3, which shows the TS-029 shutdown signature (only `gz` escalated after SIGINT; measurement checks passed), was declared INVALID under DEC-039 and repeated as attempt 4 (3 of 3 valid runs PASS). TS-030 spin thread ended cleanly in all 24 M3 attempts.
- **m4** ([summary](docs/evidence/TA/m4-M508_summary.md), 26 min): the 9 entries that ran are PASS-candidate, 0 `[ERROR]` lines, 0 leftovers; TEST-M4-09 every injected error FAILs its per-run criterion as required and lies within ±25 % of CALC-M4-05 ([check log](docs/evidence/M4/TEST-M4-09-M508_check.log)). TEST-M4-12 and TEST-M4-03 were REFUSED (log exists): the static suite had already written their logs under the same tag, and the runner never overwrites evidence. Both are deterministic, simulation-free checks and their static M508 logs PASS, so they are covered; the suite exit 1 comes only from these two refusals. Lesson: separate tags per suite when suites share entries.
- **Runner defect found:** the summary header showed the revision at the finish of the suite (`7832350` for regression and m4, committed while regression ran). Fixed in `tools/run_suite.py` (revision read at the start; a different HEAD at the finish is stated); the M508 summaries are kept as written.
- **Result:** TEST-M5-08 **PASS** for REQ-M5-09: M5 changed no M2, M3 or M4 behaviour.

### Task D — TEST-M5-09 RViz (observed by me), 2026-11-15 13:58–14:03 IST
**Command:** `SHOW=1 LAYOUT_FLAG=<flag> bash docs/evidence/M5/TEST-M5_procedure.sh 1 docs/evidence/M5/TEST-M5-09_review.log`, exit 0 ([log](docs/evidence/M5/TEST-M5-09_review.log)). Revision `7f3d65b` (`amr_ws/src` clean); product configuration; Gazebo GUI and RViz `mapping.rviz` on one laptop screen (no window layout step: no second monitor, so the windows overlapped). 1 of 1 valid run; outputs `TEST-M5-09_a1_{rest.csv,map.pgm,map.yaml,check.json}`.
- **Observed by me** (2026-11-15): the map grew, also behind the robot; the robot returned to its start point; no sudden jump or snap of the robot model. Checked again on the final RViz frame (`TEST-M5-09_a1_rviz.png`): (A) the four outer walls are straight; (B) no wall is doubled; (C) the W1 partition is mapped as one wall with two faces, its west face seen from the main room and its east face from the alcove, the solid interior unknown; (D) at the end the LiDAR points sit on the mapped walls on every face visible from the start point; (F) the area behind the top-right obstacle stayed unknown (LiDAR shadow). Loop-closure edges: not noticed (not required, DEC-052).
- Logged, not criteria here (TEST-M5-03/-04 own them): SLAM pose within 7.4 mm and 0.200° at all 11 rest points, 2.9 mm at the end; largest `map → odom` correction 23 mm and −0.20° (W3); RTF 0.85; max cross-track 9.8 mm. Map checker PASS: wall P95 0.038 m, ghosts 0 %, completeness 99.67 %, interior 9.998 × 7.995 m, L1 absent (map as saved, origin not corrected; TS-041).
- Map save and pose-graph serialization OK (pose graph not kept); SLAM log 0 [ERROR], 0 dropped-scan lines; both shutdowns CLEAN; 0 leftovers; TS-029 invalid attempts 0.
- Pictures and videos of attempt 1 (`TEST-M5-09_a1_{gazebo,rviz}.{png,mp4}`; the RViz window partly covered on its left by the overlapping Gazebo window): accepted, in `docs/gallery/M5/TEST-M5-09/`.
- **Result:** TEST-M5-09 **PASS** for REQ-M5-11 (observed by me).

### Environment re-verification after the apt upgrade, 2026-11-18 19:57–21:38 IST
**Why:** I upgraded the ROS 2 Jazzy packages with `apt-get upgrade` on 2026-11-18 (versions in [docs/environment.md](docs/environment.md) § Upgrade 2026-11-18; Gazebo Sim unchanged at 8.15.0). Every M1–M5 result was measured on the previous packages, so the existing suites were re-run unchanged before M6 implementation. Same procedures and criteria as their baselines (TEST-M5-08, TEST-M5-10).
**Product under test:** `b044cdc`, `amr_ws/src` clean; workspace rebuilt clean (`colcon build --cmake-target clean`, then `colcon build --symlink-install`, exit 0). Serial, one simulation at a time; Gazebo GUI shown (`SHOW=1`).
**Commands:** `python3 tools/run_suite.py static UPG1118` (exit 0), `SHOW=1 python3 tools/run_suite.py regression UPG1118R` (exit 0), `SHOW=1 python3 tools/run_suite.py m4 UPG1118M4` (exit 1), `SHOW=1 python3 tools/run_suite.py m5 UPG1118M5` (exit 1); re-tests `SHOW=1 bash docs/evidence/M2/TEST-M2_procedure.sh wallclock 3 docs/evidence/M2/TEST-M2-07-UPG1118R1_wallclock.log` and `python3 tools/run_suite.py records UPG1118RR`.
- **Static** ([summary](docs/evidence/TA/static-UPG1118_summary.md)): 9 of 9 PASS-candidate; reviewed: build without warnings, 13 of 13 unit tests, the M1 expansion identical; the FAIL lines in TEST-M3-02 and TEST-M5-07 are their deliberate checks.
- **Regression** ([summary](docs/evidence/TA/regression-UPG1118R_summary.md)): 20 of 20 entries PASS-candidate by the runner. Reviewed every log: 0 FAIL in counted attempts, 0 TS-029 attempts, 0 leftover processes, RTF ≥ 0.962. **TEST-M2-07 wallclock: FAIL** for this check: attempt 1 failed to load `diff_drive_controller` at start-up and the harness classed it invalid, but the test plan's validity rule covers only RTF < 0.5 (TS-044; user decision: counted as a failure, no rule change). **R1** ([log](docs/evidence/M2/TEST-M2-07-UPG1118R1_wallclock.log)): **PASS**, 3 of 3 valid runs, no invalid attempt. The failure did not reproduce in 30 further launches ([TS-044 loop log](docs/evidence/M2/TS-044_startup_loop.log)); TS-044 stays open for monitoring.
- **m4** ([summary](docs/evidence/TA/m4-UPG1118M4_summary.md)): 10 of 11 PASS-candidate; reviewed: odometry accuracy on the upgraded `diff_drive_controller` within every DEC-044 bound; TEST-M4-09 injected errors fail their targets as required and match CALC-M4-05 ([check log](docs/evidence/M4/TEST-M4-09-UPG1118M4_check.log)). **TEST-M4-12: FAIL** on one check, the static suite's log not yet indexed (TS-043); every configuration and record check passed.
- **m5** ([summary](docs/evidence/TA/m5-UPG1118M5_summary.md)): 6 of 7 PASS-candidate; reviewed: SLAM interface, mapping accuracy (3 valid runs), map save and reload with `map_server` 1.3.14 (the one FAIL line is the procedure's negative control), mapping with injected odometry error ([log](docs/evidence/M5/TEST-M5-06-UPG1118M5_review.log)); 0 TS-029 attempts. **TEST-M5-10: FAIL** on one check, for the same reason as TEST-M4-12 (TS-043).
- **Records R1** (summary not published) after indexing the batch's evidence: TEST-M2-11, TEST-M3-12, TEST-M4-12, TEST-M5-10 **PASS**.
- **Result:** **PASS** after the R1 re-tests: the upgraded packages change no M1–M5 behaviour within the existing criteria. Failures kept above: TEST-M2-07 wallclock (TS-044, open), TEST-M4-12 and TEST-M5-10 (TS-043, resolved). The milestone results in the summary table are unchanged; this record adds evidence for the new package versions.

## Record Format for Future Tests

Use the record format in [docs/testing/test_plan.md §3](docs/testing/test_plan.md). It adds requirement IDs, revision, exit codes, status, and evidence to the fields used in the M0 entries above. Record failed runs as well as passing ones; a re-test gets a new dated entry.

## M6 — Localization (plan [docs/milestones/M6_localization.md](docs/milestones/M6_localization.md); criteria DEC-059; AMCL parameters DEC-061, map copy DEC-062)

### Task A — TEST-M6-01, 2026-11-18 22:38 IST
**Under test:** the M6 Task A changes against the M5 closeout `9b85171`, on revision `8a515c2` (`amr_ws/src` clean). Static test, no simulation. The procedure was written and dry-run before its formal run, and its map-copy step was negative-controlled (M6 plan §12).
**TEST-M6-01** (REQ-M6-11): `bash docs/evidence/M6/TEST-M6-01_procedure.sh`, exit 0 ([log](docs/evidence/M6/TEST-M6-01_review.log)).
- **Build and model:**
  - Build: colcon exit 0, 0 warning lines.
  - Default expansion byte-identical to `TEST-M1-02_amr.urdf`.
  - Expansions with `use_ros2_control:=true` (6452 bytes) and with `use_sensors:=true` added (9912 bytes) byte-identical to the `9b85171` expansions.
- **Protected files:** `sim.launch.py`, `controllers.yaml`, `amr.sensors.xacro`, `amr_properties.xacro`, `slam_toolbox.yaml`, `slam.launch.py` and the four reference-map files are unchanged since `9b85171`.
- **Existing files in `amr_ws/src` since `9b85171`:** two are modified:
  - `package.xml`: exactly the four exec_depends `nav2_map_server`, `nav2_amcl`, `nav2_lifecycle_manager` and `nav2_rviz_plugins`;
  - `CMakeLists.txt`: 4 changed lines, which are 2 comment lines and the install rule gaining `maps`.
- **Map copy:** `mapping_arena_amcl.yaml` origin differs from the reference by [0.025, 0.025, 0]; no other key differs; the text is identical apart from comments and the origin (DEC-062).
- **Negative control** (scratch, before the formal run): the map-copy step rejected an origin off by 1 µm, a changed `free_thresh`, and an unshifted copy, and accepted the real copy.
- **Result:** TEST-M6-01 **PASS**.

### Task A — TEST-M6-02, 2026-11-18 22:38–22:46 IST
**Under test:** the localization interface (REQ-M6-01, -02, -03) on `8a515c2` (`amr_ws/src` clean). Launches:
- `sim.launch.py headless:=false sensors:=true world:=mapping_arena.sdf`;
- `localization.launch.py`.

Versions: Gazebo 8.15.0; nav2_amcl and nav2_map_server 1.3.14. Gazebo GUI and RViz (`localization.rviz`) were shown (`SHOW=1`). The procedure and checker were dry-run once before this run (scratch, PASS).
**TEST-M6-02:** `SHOW=1 bash docs/evidence/M6/TEST-M6-02_procedure.sh 3 docs/evidence/M6/TEST-M6-02_review.log`, exit 0 ([log](docs/evidence/M6/TEST-M6-02_review.log)). 144 PASS lines, 0 FAIL.
- **Before localization (attempts 1–3):**
  - `/tf` publishers were `diff_drive_controller` and `robot_state_publisher`;
  - nobody published `map → odom`, `/map` or `/map_amcl`.
- **After localization, every check PASS in all three attempts:**
  - **Lifecycle:** `/map_server`, `/map_server_amcl` and `/amcl` active; `use_sim_time` true on all three; `topic_name` `map` and `map_amcl`.
  - **AMCL parameters:**
    - `laser_max_range` 12.0;
    - `map_topic` `map_amcl`, `scan_topic` `scan`;
    - frames `map` / `odom` / `base_footprint`;
    - `set_initial_pose` true at (0, 0, 0);
    - `alpha1` 0.0016, `alpha2`–`alpha4` 0.0004, `sigma_hit` 0.05 (DEC-061).
  - **Maps:**
    - `/map` comes only from `map_server`: 202 × 162 cells, 0.05 m, origin (−2.071, −4.080), 0 of 32 724 cells differing from the file;
    - `/map_amcl` comes only from `map_server_amcl`: the same cells, origin (−2.046, −4.055);
    - AMCL subscribes to `/map_amcl` and not to `/map`, and to `/scan`;
    - no SLAM node is running.
- **During the drive:**
  - `map → odom` messages: 103 / 102 / 103, all with distinct sequence numbers (one writer);
  - the only node added to the `/tf` publishers is `amcl`;
  - `map → odom` is never on `/tf_static`, its stamps are simulation time, and every message carrying it carries only that transform;
  - every frame has one parent; the chain `map → odom → base_footprint → base_link → lidar_mount_link → laser_frame` holds, and `map → laser_frame` resolves.
- **`/amcl_pose`** comes only from `amcl`. After the drive (frame `map`), with positive variances:

  | Attempt | x (m) | y (m) | yaw | var x (m²) | var y (m²) | var yaw (rad²) |
  |---|---|---|---|---|---|---|
  | 1 | 0.9822 | +0.0002 | 84.1° | 1.11e-4 | 7.4e-5 | 1.8e-4 |
  | 2 | 0.9784 | −0.0001 | 80.8° | 1.34e-4 | 6.9e-5 | 1.8e-4 |
  | 3 | 0.9791 | −0.0011 | 81.0° | 1.11e-4 | 7.1e-5 | 2.0e-4 |
- **INFO:**
  - RTF 0.99 / 1.00 / 0.99;
  - `/amcl_pose` at start (0, 0, 0) with zero position variance (set initial pose);
  - 10 `/amcl_pose` messages per attempt;
  - 1 `/tf` writer for `amcl` in each attempt (the Task A gate's `ros2 topic info` had listed 2 endpoints; not a criterion: the sequence-number check is).
- **Shutdown:** localization and simulation launches CLEAN in all three attempts; 0 leftover processes by process group and by name; 0 [ERROR] lines in either log; no launch log needed keeping. TS-029 invalid attempts: 0.
- **Pictures and videos:** attempt 1 in [`docs/gallery/M6/TEST-M6-02/`](docs/gallery/M6/TEST-M6-02/).
- **Result:** TEST-M6-02 **PASS**.

### Task B — TEST-M6-08, 2026-11-18 23:55 IST
**Under test:** the offline pose checker `TEST-M6_pose_check.py` (DEC-059 bounds; recovery bound DEC-063) on revision `3ed8eb6` (`docs/evidence/M6` clean). Offline, standard library only.
**Input:** the Task B forward dry run (2026-11-18 23:03 IST, product settings), committed as `TEST-M6-08_recorded_{rest,track}.csv`: 11 rest points and 1995 track samples, of which 1719 are moving. This is checker input, not a localization result.
**TEST-M6-08** (REQ-M6-10): `python3 -I docs/evidence/M6/TEST-M6-08_distort.py docs/evidence/M6/TEST-M6-08_recorded`, exit 0 ([log](docs/evidence/M6/TEST-M6-08_review.log)).
- **Original:** PASS (rest max 10.4 mm, 0.107°; moving P95 9.8 mm, 0.131°; moving max 10.4 mm).
- **Offset +0.08 m:** FAIL on `rest_position` (86.8 mm > 50 mm). Moving P95 86.6 mm and max 87.4 mm stay within their bounds, as designed.
- **Rotation +1.5°:** FAIL on `rest_heading` (1.607° > 1.0°). Moving P95 heading 1.583° stays within 2.0°.
- **One 0.30 m jump** (track sample 967, 106.6 s): FAIL on `moving_max_position` (302.5 mm > 250 mm). The P95 measures are unchanged.
- **0.5 s delay:** FAIL on `moving_p95_position` (130.6 mm > 100 mm), and also on `moving_p95_heading` (14.33°), as expected because the turns shift as well.
- **Result:** TEST-M6-08 **PASS** (1 PASS, 4 FAIL, each on the expected measure).

### Task C — TEST-M6-03 to -06, 2026-11-18 23:58 to 2026-11-19 01:32 IST
**Under test:** AMCL localization with the DEC-061 settings and the DEC-062 map copy, on revision `f2d344a` (`amr_ws/src` clean; the M6 tooling unchanged since `3ed8eb6`). Ground truth comes from Gazebo, and estimates come from TF looked up at the ground-truth stamp at 10 Hz. Gazebo GUI and RViz were shown; 3 valid runs per procedure (ROS_DOMAIN_ID 141–143); route 28.68 m (M5 route, forward or reversed). Criteria: DEC-059, with the recovery bound from DEC-063. Command lines are in `docs/testing/test_plan.md` §11.
**Run validity, all 21 runs:**
- RTF 0.97–1.00;
- 0 missing samples in 19 runs and 1 missing in 2 runs (of 2067 and 2068; the limit is 2 %);
- maximum cross-track ≤ 10.0 mm;
- every shutdown CLEAN (0 `[ERROR]` lines), 0 leftover processes, 0 attempts invalid under DEC-039.

Each run's data (`<log>_a<N>_{rest,track}.csv`, `_check.json`; 4.5 MB in total, every file under 0.25 MB) is committed so the checker can be re-run offline.

| Test | Run | Rest max | Moving P95 | Moving max | Other |
|---|---|---|---|---|---|
| TEST-M6-03 forward | 1 / 2 / 3 | 10.3 / 13.2 / 9.4 mm; ≤ 0.099° | 10.6 / 11.7 / 8.8 mm; ≤ 0.133° | 12.4 / 13.2 / 10.2 mm | |
| TEST-M6-03 reverse | 1 / 2 / 3 | 9.3 / 9.7 / 7.7 mm; ≤ 0.139° | 9.3 / 9.7 / 8.3 mm; ≤ 0.148° | 10.6 / 11.3 / 9.4 mm | |
| TEST-M6-04 | 1 / 2 / 3 | 18.5 / 12.0 / 19.2 mm; ≤ 0.220° | 29.7 / 26.4 / 18.4 mm; ≤ 0.260° | 39.0 / 36.6 / 36.9 mm | recovery 2.12 / 2.41 / 3.47 m (≤ 4.0 m); wrong start visible at 92.6 / 81.3 / 164.2 mm |
| TEST-M6-05 forward | 1 / 2 / 3 | 28.1 / 26.1 / 28.0 mm; ≤ 0.211° | 28.8 / 28.4 / 30.6 mm; ≤ 0.668° | 33.5 / 32.6 / 33.2 mm | odometry 198.6 mm, −3.53° each (prediction 198 mm: +0.1 %) |
| TEST-M6-05 reverse | 1 / 2 / 3 | 26.3 / 29.8 / 30.4 mm; ≤ 0.190° | 26.1 / 27.0 / 29.3 mm; ≤ 0.738° | 28.9 / 32.9 / 31.7 mm | odometry 438.6 mm, −8.82° each (prediction 440 mm: −0.3 %) |
| TEST-M6-06 forward | 1 / 2 / 3 | 11.4 / 7.6 / 10.2 mm; ≤ 0.166° | 10.8 / 7.5 / 10.1 mm; ≤ 0.156° | 11.9 / 8.2 / 11.5 mm | |
| TEST-M6-06 reverse | 1 / 2 / 3 | 11.7 / 10.2 / 9.0 mm; ≤ 0.184° | 10.2 / 10.6 / 9.3 mm; ≤ 0.177° | 11.7 / 11.8 / 10.7 mm | |

Bounds: rest ≤ 50 mm and 1.0°; moving P95 ≤ 100 mm and 2.0°; moving max ≤ 250 mm; TEST-M6-05 drift > 150 mm and within ±25 % of CALC-M5-04.

**Results:** TEST-M6-03 **PASS** (REQ-M6-04, -05); TEST-M6-04 **PASS** (REQ-M6-06); TEST-M6-05 **PASS** (REQ-M6-07); TEST-M6-06 **PASS** (REQ-M6-08). Every procedure exited 0 with "ALL 3 VALID RUNS PASSED".
**Observations:**
- With exact odometry (TEST-M6-03, -06), localization error stays near 10 mm, about the 5 cm map cell divided by 5. The unmapped boxes changed nothing measurable.
- With the injected calibration error (TEST-M6-05), error rises to about 30 mm and the moving P95 heading to about 0.7°, yet still holds 3× inside the bounds. Odometry alone was 198.6 mm and 438.6 mm off at the end. The drift is identical in every run because odometry is deterministic.
- TEST-M6-04 run 3 recovered in 3.47 m, which would have failed DEC-059's original 3 m bound.
**Incident during the run (not a test result):** attempt 1 of TEST-M6-04 produced an empty (0-byte) Gazebo screen recording, and the trim step waited for its first frame for about 9 minutes. That attempt's data was already written. The trim process was stopped by PID, after which the teardown ended CLEAN and the procedure continued. The recording tool was fixed before the next recorded attempt; TS-046 in `docs/troubleshooting.md`.

### Task D — TEST-M6-07, 2026-11-20 19:20 to 19:32 IST
**Under test:** odometry + IMU fusion with the `robot_localization` EKF (DEC-057; `ekf.yaml`, `controllers_ekf.yaml`, `localization.launch.py ekf:=true`) and AMCL on the fused odometry, on revision `19200ee` (`amr_ws/src` clean). Injected error: `wheel_separation_multiplier: 1.02` alone, in a test copy of `controllers_ekf.yaml` (the log lists the difference from `controllers.yaml`). Forward M5 route, 28.68 m; Gazebo GUI and RViz shown; 3 runs (ROS_DOMAIN_ID 141–143). Command: `SHOW=1 FUSION=1 INJECT=sep bash docs/evidence/M6/TEST-M6_procedure.sh 3 docs/evidence/M6/TEST-M6-07_review.log`, exit 1 ([log](docs/evidence/M6/TEST-M6-07_review.log)).
**Run validity:** RTF 0.99–1.00; 0, 1 and 0 missing samples (of 1980–1990); maximum cross-track 9.8 mm; every shutdown CLEAN, 0 leftover processes, 0 attempts invalid under DEC-039.

| Run | Fusion check pre / main | Raw odometry at the end | Fused odometry at the end | AMCL rest max | Moving P95 | Moving max |
|---|---|---|---|---|---|---|
| 1 | PASS / **FAIL** (parameters `{}`) | 400.0 mm, −7.060° | 6.6 mm (1.6 %), +0.071° | 20.3 mm, 0.166° | 17.2 mm, 0.328° | 20.4 mm |
| 2 | PASS / PASS | 400.0 mm, −7.059° | 2.9 mm (0.7 %), +0.038° | 19.7 mm, 0.163° | 18.8 mm, 0.348° | 22.1 mm |
| 3 | PASS / PASS | 400.0 mm, −7.059° | 5.6 mm (1.4 %), −0.077° | 19.6 mm, 0.129° | 17.5 mm, 0.343° | 20.9 mm |

Criteria: raw within ± 25 % of CALC-M5-04 for separation × 1.02 alone (400 mm; measured +0.1 %); fused heading ≤ 0.5°; fused position ≤ 25 % of raw; DEC-059 localization bounds. Every pose-checker item PASS in all 3 runs. In all 3 runs the fusion check found: controller TF off; `/imu` gyro variance 1.0e-6 (float32 on the wire); one `odom → base_footprint` writer at 48–50 Hz, every stamp equal to a `/odometry/filtered` stamp.
**Failure:** attempt 1, item 5 of the main fusion check: `get_parameters` on `ekf_filter_node` returned nothing. The EKF logged `failed to send response to /ekf_filter_node/get_parameters (timeout)` in the same second. Diagnosis TS-047: the reply was dropped during discovery of the just-started node; the values themselves were not wrong. Corrective action: the check repeats the query up to 3 times while there is no reply. Re-test R1 follows.
**Result:** TEST-M6-07 **FAIL** (checker defect TS-047; kept as the original result).
**Pictures and videos:** attempt 1 in [`docs/gallery/M6/TEST-M6-07/`](docs/gallery/M6/TEST-M6-07/).

### Task D — TEST-M6-07 R1, 2026-11-20 19:33 to 19:46 IST
**Under test:** as the original run, on revision `c2b6805` (`amr_ws/src` clean). The only change is the TS-047 fix in `TEST-M6-07_fusion_check.py` (query retry); product files unchanged since `19200ee`. Command: `SHOW=1 FUSION=1 INJECT=sep bash docs/evidence/M6/TEST-M6_procedure.sh 3 docs/evidence/M6/TEST-M6-07-R1_review.log`, exit 0 ([log](docs/evidence/M6/TEST-M6-07-R1_review.log)).
**Run validity:** RTF 1.00; 0, 1 and 1 missing samples (of 1988); maximum cross-track ≤ 9.9 mm; every shutdown CLEAN, 0 leftover processes, 0 attempts invalid under DEC-039. The EKF parameter query was answered at the first try in all 3 runs (no TS-047 retry used).

| Run | Fusion check pre / main | Raw odometry at the end | Fused odometry at the end | AMCL rest max | Moving P95 | Moving max |
|---|---|---|---|---|---|---|
| 1 | PASS / PASS | 400.0 mm, −7.059° | 5.3 mm (1.3 %), −0.016° | 24.9 mm, 0.134° | 18.6 mm, 0.320° | 24.9 mm |
| 2 | PASS / PASS | 400.0 mm, −7.059° | 9.7 mm (2.4 %), −0.075° | 18.0 mm, 0.131° | 17.0 mm, 0.334° | 20.2 mm |
| 3 | PASS / PASS | 400.0 mm, −7.059° | 6.8 mm (1.7 %), +0.115° | 19.4 mm, 0.125° | 18.4 mm, 0.336° | 22.6 mm |

In every run the fusion check found:
- the controller TF off (`enable_odom_tf` false, no `odom → base_footprint` without the EKF);
- `/imu` gyro variance 1.0e-6 (float32 on the wire), raw odometry yaw-rate variance 4.0e-4;
- the EKF parameters as `ekf.yaml`;
- one `odom → base_footprint` writer at 50 Hz (251 distinct sequence numbers), added with `ekf_filter_node`, every stamp equal to a `/odometry/filtered` stamp, simulation-time stamps.

**Result:** TEST-M6-07 R1 **PASS** (REQ-M6-09). Every procedure item PASS (60 PASS lines, no FAIL); "ALL 3 VALID RUNS PASSED".
**Observations:**
- Fusion removes the injected calibration error almost entirely: raw odometry ends 400 mm and 7.06° off, fused odometry at most 9.7 mm and 0.115° (six formal runs: 2.9–9.7 mm, ≤ 0.115°). The fused heading error is above the CALC-M6-04 estimate (about 0.09°) in some runs but always at least 4× inside the 0.5° bound.
- AMCL accuracy with fusion (rest ≤ 24.9 mm) is between TEST-M6-03 (exact odometry, ≤ 13.2 mm) and TEST-M6-05 (the larger TEST-M4-09 error without fusion, ≤ 30.4 mm). The runs differ in their injected errors, so this is not a controlled comparison.
**Pictures and videos:** attempt 1 in [`docs/gallery/M6/TEST-M6-07/`](docs/gallery/M6/TEST-M6-07/) (`TEST-M6-07-R1_a1_*`).

### Task E — TEST-M6-09, 2026-11-20 20:15 to 21:46 IST
**Under test:** M1–M5 behaviour with the M6 changes in place (REQ-M6-11). Commands as `docs/testing/test_plan.md` §11, one tag per suite. `static` (M609S) on revision `9c8bb63`; `regression` (M609RH), `m4` (M609M4) and `m5` (M609M5) **headless** on `1a691ac` (`amr_ws/src` clean; the only change from `9c8bb63` is the TS-048 procedure fix). Re-tests of earlier milestones run headless (rule from 2026-11-20).
**Aborted GUI run:** a first `regression` run with the GUI (tag M609R) was stopped by PID during TEST-M2-10 when I switched regression re-tests to headless. Its TEST-M2-04 clock-step FAIL is kept ([log](docs/evidence/M2/TEST-M2-04-M609R_review.log)): `ros2 topic echo` printed "A message was lost!!!" before the value (TS-048, procedure fixed in `1a691ac`). The other partial logs of that run were superseded and are not kept.
**Run validity:** every Gazebo entry reported RTF ≥ 0.99, CLEAN shutdowns and 0 leftover processes. TEST-M3-14 attempt 1 hit the TS-029 shutdown hang (3 launch `[ERROR]` lines, measurements PASS) and was declared invalid under DEC-039; attempt 4 completed 3 valid runs. Every log was reviewed (DEC-040 item 5).

| Suite | Entries PASS-candidate | Not PASS-candidate |
|---|---|---|
| `static` (M609S) | 11 of 11 | — |
| `regression` (M609RH) | 20 of 20 | — |
| `m4` (M609M4) | 11 of 12 | TEST-M4-12: one check, `TEST-M4-03-M609S_recompute.log` not yet indexed |
| `m5` (M609M5) | 5 of 7 | TEST-M5-10: one check, `TEST-M5-07-M609S_review.log` not yet indexed; TEST-M5-01: step 5 on M6's dependency lines (TS-049) |

- **TEST-M4-12, TEST-M5-10:** the `static` suite wrote those logs earlier in the same batch. Same class as TS-043; the recorded practice (index before relying on a records checker) was not followed when the batch was started.
- **TEST-M5-01:** step 5 compared the M4 closeout with the working tree and found the M6 lines. Steps 1–4 passed: build, M1 byte identity, launch-model identity, unchanged simulation and SLAM files. TEST-M6-01 had the matching gap: its list lacked Task D's `robot_localization`. Diagnosis in TS-049; user decision DEC-064.

**Result:** TEST-M6-09 **FAIL** (kept as the original result).

### Task E — TEST-M6-09 R1, 2026-11-20 21:40 to 21:46 IST
**Under test:** the three failed entries, after the batch evidence was indexed and DEC-064 was applied (TEST-M5-01 step 5: `517608f` → `9b85171`; TEST-M6-01: five M6 lines).
- TEST-M5-01 R1: PASS, every step ([log](docs/evidence/M5/TEST-M5-01-M609M5R1_review.log)).
- `records` suite (M609RR): 5 of 5 PASS-candidate, including TEST-M4-12 R1 and TEST-M5-10 R1 (summary not published).
- TEST-M6-01 on the Task E working tree with the corrected list: PASS ([log](docs/evidence/M6/TEST-M6-01-M6E_review.log)). Before the correction, a scratch run of TEST-M6-01 at HEAD failed step 5, so the corrected step still detects a missing line (also covered by the TEST-M6-11 mutation check).

**Result:** TEST-M6-09 R1 **PASS** (REQ-M6-11). With M6 in place, every M1–M5 suite entry passes.

### Task E — TEST-M6-10, 2026-11-20 22:32 to 22:42 IST
**Under test:** localization as seen in RViz `localization.rviz` (REQ-M6-12), revision `00f1b75` (`amr_ws/src` clean), GUI and RViz shown, one run each. Commands as `docs/testing/test_plan.md` §11: `SHOW=1 WRONG=1` (wrong start, as TEST-M6-04) and `SHOW=1 GLOBAL=1` (global-localization demonstration, DEC-058; the `GLOBAL=1` option was added for this test in `00f1b75`).
**Observed by user:**
- Wrong start: "particles converged early, scan on walls, no jumps".
- Global localization: "particles scattered then one cluster, scan rotated off walls, no jumps".

**Instrument record (supporting the observation):**
- Wrong start: start error 453 mm, 14.4°; converged after 2.10 m of travel (≤ 4.0 m); afterwards rest ≤ 13.5 mm, ≤ 0.19°, moving P95 22.9 mm, maximum 34.7 mm; RTF 0.99; shutdowns CLEAN; checker PASS ([log](docs/evidence/M6/TEST-M6-10-wrongstart_review.log)).
- Global localization: the service call succeeded; the estimate started 3.5 m and 67° off and, from the first long leg, held a heading error of 179.8–180.0° with a position error of 2.5–8.9 m depending on the robot's position; end of route 6.0 m, 179.9°. It was never corrected (checker FAIL on every bound, expected and not judged, DEC-058). Wheel odometry exact throughout ([log](docs/evidence/M6/TEST-M6-10-global_review.log)).

**Result:** TEST-M6-10 **PASS** (observed by me): the wrong-start convergence, the scan on the walls and the absence of TF jumps were observed, and the global-localization demonstration was shown.
**Observation:** global localization locked onto one wrong cluster, rotated about 180°, which matches what I saw in RViz ("scan rotated off walls"). This is consistent with a near-symmetry of the arena under a half turn (not verified geometrically). With all particles in that cluster and no random-particle injection (DEC-061), AMCL had no hypothesis left near the truth. It supports DEC-058 (known start pose); for M7 it means the robot must start from a known or user-given pose.
**Pictures and videos:** both runs in [`docs/gallery/M6/TEST-M6-10/`](docs/gallery/M6/TEST-M6-10/).

### Task E — `m6` suite run, TEST-M6-04 characterization and TEST-M6-04 R1, 2026-11-20 22:46 to 2026-11-21 01:15 IST
**Under test:** every automatable M6 test through `python3 tools/run_suite.py m6 M611` (REQ-M6-13), **headless** (regression re-tests always run headless), on revision `b3d975b` (`amr_ws/src` clean). Then a 10-run diagnosis batch and TEST-M6-04 R1 on `5ba09bd` (DEC-065; product files unchanged).
**Run validity:** RTF 0.99–1.00 in every Gazebo entry; every shutdown CLEAN or handled; 0 leftover processes. TEST-M6-05 forward attempt 3 hit the TS-029 shutdown hang (measurements PASS) and was declared invalid under DEC-039; its full launch logs are kept, and attempt 4 completed 3 valid runs. Every log was reviewed (DEC-040 item 5).

| Entry | Result (worst value over the valid runs) |
|---|---|
| TEST-M6-11, -01, -08 | PASS-candidate (checker, build identity under DEC-064, pose-checker sensitivity) |
| TEST-M6-02 | PASS-candidate, 3 valid runs |
| TEST-M6-03 forward / reverse | PASS-candidate; worst position error 11.8 / 11.6 mm |
| **TEST-M6-04** | **FAIL**: recovery 2.36, **4.84**, 2.93 m vs 4.0 m (DEC-063); every bound after recovery PASS |
| TEST-M6-05 forward / reverse | PASS-candidate; 36.9 / 34.5 mm |
| TEST-M6-06 forward / reverse | PASS-candidate; 11.8 / 10.5 mm |
| TEST-M6-07 | PASS-candidate; 22.9 mm (EKF fusion) |

**Diagnosis (measure before deciding):** 10 headless wrong-start runs with the product settings ([log](docs/evidence/M6/TEST-M6-04-char10_review.log); diagnosis data, not a formal result). Recovery: 3.25, 2.18, 3.25, 4.01, 4.62, 2.16, 4.53, 3.50, 3.77, 1.61 m. The start error AMCL showed was 78.5–468.1 mm, and after recovery every bound held (rest ≤ 26.2 mm, moving maximum ≤ 75.4 mm). With the 11 earlier runs (Task B dry runs 2.73, 2.89, 2.90, 3.19; TEST-M6-04 2.12, 2.41, 3.47; TEST-M6-10 2.10; this suite run 2.36, 4.84, 2.93): 21 runs, median 2.93 m, maximum 4.84 m, 4 over 4.0 m. The start error did not predict the recovery distance (a 173 mm start took 4.62 m; a 467 mm start took 1.61 m), and every run converged on the first leg (6.49 m). User decision **DEC-065**: the bound is 6.0 m, AMCL unchanged.

**TEST-M6-04 R1** (DEC-065, `WRONG=1 bash docs/evidence/M6/TEST-M6_procedure.sh 3 docs/evidence/M6/TEST-M6-04-M611R1_review.log`, headless):

| Run | Start error shown | Recovery | Rest max | Moving P95 | Moving max |
|---|---|---|---|---|---|
| 1 | 434.7 mm, 13.48° | 5.68 m | 42.3 mm, 0.116° | 36.6 mm | 49.9 mm |
| 2 | 446.2 mm, 13.74° | 3.48 m | 37.3 mm, 0.056° | 37.3 mm | 44.6 mm |
| 3 | 432.2 mm, 13.88° | 2.91 m | 17.4 mm, 0.096° | 19.2 mm | 46.6 mm |

**Result:** `m6` suite run: TEST-M6-04 **FAIL** (kept); TEST-M6-04 R1 **PASS** (REQ-M6-06). The suite ran every automatable M6 test (part of TEST-M6-11's automation criterion, recorded with TEST-M6-11).
**Observation:** run 1 of R1 set a new maximum (5.68 m), about 5 % under the DEC-065 bound and above the 4.84 m the bound was derived from. Its 42.3 mm rest error was at rest point 1, 0.8 m after convergence, while the estimate was still settling. The recovery distribution has a longer tail than 21 runs showed (24 runs now: median 2.93 m, maximum 5.68 m). The bound held, but a future formal run could exceed it. Accepted as a known risk at closeout (DEC-065 follow-up).

### Task E — TEST-M6-11, 2026-11-21 01:16 to 01:21 IST
**Under test:** M6 configuration against DEC-043 and DEC-055 to DEC-065, the M6 records under DEC-041, the evidence index and links, and the automation (REQ-M6-13), on revision `222aa52`. Commands as `docs/testing/test_plan.md` §11.
- `python3 tools/run_suite.py records M611F`: 5 of 5 PASS-candidate, TEST-M2-11, TEST-M3-12, TEST-M4-12, TEST-M5-10 and TEST-M6-11 (summary and TEST-M6-11 log not published).
- `python3 -I docs/evidence/M6/TEST-M6-11_mutation_check.py`: 20 of 20 injected faults DETECTED; `python3 tools/run_suite.py m6 M611F --dry-run`: the 12 entries of the `m6` suite (log not published).
- The `m6` suite was run in full the evening before (tag M611; record above).
- CI: `gh workflow run ci.yml --ref main -f records=true`, [run 44805433769](https://github.com/Nikhil-Jangid/smart-amr-dev/actions/runs/44805433769): **success**. Record checkers 5 of 5, GPU-free suite 6 of 6 (TEST-M3-01, -M3-13, -M3-02, -M4-03, -M5-07, -M6-08), TEST-TA-06 drawing check PASS.

Defects found while the checker was built and used, all corrected before this run: DEC-041 slips from Tasks A, C and D; the missing TEST-M6-07 traceability entry; my own missing link and restated numbers in Task E (`e5011be`, fixed in `b3d975b`). Checker limitations corrected: the "observed by me" label and attempt numbers above 9.
**Result:** TEST-M6-11 **PASS** (REQ-M6-13).

## M7 — Autonomous Navigation (plan [docs/milestones/M7_navigation.md](docs/milestones/M7_navigation.md); criteria DEC-073; architecture DEC-066 to DEC-072)

### Task A — integration gate (scratch), 2026-11-21 03:05–03:40 IST
**Not a formal test** (M7 plan §7: gate before any formal run). Gazebo GUI and RViz (`navigation.rviz`) shown; three launches (`sim.launch.py sensors:=true world:=mapping_arena.sdf`, `localization.launch.py`, `navigation.launch.py`). Logs in the session scratch directory, not kept.
- **Servers:** the five navigation servers `active` (autostart); `use_sim_time` true.
- **Map:** `/map` read by `global_costmap` (and RViz); `/map_amcl` only by `map_server_amcl` and `amcl` (DEC-062).
- **Footprint:** both costmaps' `footprint` parameter = CALC-M7-01; the published polygon = CALC-M7-01 moved outwards by `footprint_padding` 0.01 m (Nav2 default, kept).
- **Command path:** `/cmd_vel` `TwistStamped`, one publisher (`velocity_smoother`), one subscriber (`cmd_vel_guard`); `cmd_vel_nav` has two publishers (controller, behaviors).
- **Defaults found wrong for this robot, corrected in `nav2.yaml` before the formal runs** (implementing DEC-070; no engineering value changed):
  - `controller_server` `odom_topic` defaulted to `odom`, which has no publisher here: set to `/diff_drive_controller/odom` (TS-051).
  - With `stamp_smoothed_velocity_with_smoothing_time` False (installed), the guard rejected one smoother command (stamp age 0.521 s > 0.5 s) during the G1 drive: set to True (TS-050).
- **Goals** (`ros2 action send_goal /navigate_to_pose`), ground truth from `gz model -m amr -p`:

  | Goal | Settings | Result | Stop vs goal | Commands |
  |---|---|---|---|---|
  | G1 (6.5, −2.6, −90°) | before both fixes | SUCCEEDED | 0.097 m, −3.3° | v 0..0.300 m/s, \|w\| ≤ 0.894 rad/s; stamp age ≤ 0.957 s; 622 sent, 612 forwarded (1 rejected; the rest in flight at the window edges, not attributed) |
  | G6 (0, 0, 0°) | after both fixes | SUCCEEDED | 0.092 m, −5.6° | v 0..0.300 m/s, \|w\| ≤ 1.000 rad/s; stamp age ≤ 0.002 s; 679 sent, 679 forwarded, 0 rejected |
- **RTF** with GUI + LiDAR + AMCL + Nav2 during G1: median 1.00 (minimum single sample 0.14).
- **Default-parameter observations** (inform, do not change, the DEC-073 bounds): the 0.10 m / 0.10 rad goal checker was met without visible oscillation on both goals; RPP plugin defaults recorded from `ros2 param dump /controller_server` (lookahead 0.3–0.9 m, `rotate_to_heading_min_angle` 0.785 rad, regulated and cost-regulated scaling on).

### Task A — TEST-M7-01, 2026-11-21 03:55 IST
**Under test:** the M7 Task A changes against the M6 closeout `9777615` (DEC-064), on revision `e0474ba` (`amr_ws/src` clean). Static test, no simulation. The procedure was dry-run on the uncommitted working tree before its formal run; the dry run found a defect in the procedure's own step 6 (its Spin/BackUp search also matched the trees' header comment), corrected before the formal run.
**TEST-M7-01** (REQ-M7-11): `bash docs/evidence/M7/TEST-M7-01_procedure.sh`, exit 0 ([log](docs/evidence/M7/TEST-M7-01_review.log)). 27 steps, all exit 0.
- **Build and model:** colcon exit 0, 0 warning lines; default expansion byte-identical to `TEST-M1-02_amr.urdf`; the `use_ros2_control:=true` (6452 bytes) and `use_sensors:=true` (9912 bytes) expansions byte-identical to `9777615`.
- **Protected files unchanged since `9777615`:** `sim.launch.py`, `cmd_vel_guard.cpp`, `sensor_bridge.yaml`, `controllers.yaml`, `controllers_ekf.yaml`, `mapping_arena.sdf`, `amr.sensors.xacro`, `amr_properties.xacro`, `slam_toolbox.yaml`, `slam.launch.py`, `localization.launch.py`, `amcl.yaml`, `ekf.yaml` and the five map files.
- **Existing files changed:** `package.xml` (exactly the seven exec_depends `nav2_planner`, `nav2_controller`, `nav2_behaviors`, `nav2_bt_navigator`, `nav2_velocity_smoother`, `nav2_navfn_planner`, `nav2_regulated_pure_pursuit_controller`) and `CMakeLists.txt` (3 changed lines: 1 comment and the install rule gaining `behavior_trees`). Every other change is a new file.
- **Behavior trees:** each equals the installed Nav2 1.3.14 tree (`*_w_replanning_and_recovery.xml`) apart from its header comment, with exactly two installed lines removed (Spin, BackUp) (DEC-071).
- **Result:** TEST-M7-01 **PASS**.

### Task A — TEST-M7-02, 2026-11-21 03:55–04:00 IST
**Under test:** the navigation interface (REQ-M7-01, -02, -03) on `e0474ba` (`amr_ws/src` clean). Launches: `sim.launch.py headless:=false sensors:=true world:=mapping_arena.sdf`, `localization.launch.py`, `navigation.launch.py`. Versions: Gazebo 8.15.0; navigation2 1.3.14. Gazebo GUI and RViz (`navigation.rviz`) shown (`SHOW=1`). The procedure and checker were dry-run once headless before this run (scratch, PASS).
**TEST-M7-02:** `SHOW=1 bash docs/evidence/M7/TEST-M7-02_procedure.sh 3 docs/evidence/M7/TEST-M7-02_review.log`, exit 0 ([log](docs/evidence/M7/TEST-M7-02_review.log)). 165 PASS lines, 0 FAIL.
- **Every check PASS in all three attempts:**
  - **Lifecycle:** the five navigation servers and the three M6 localization nodes `active`; `use_sim_time` true on the five servers and both costmap nodes.
  - **Parameters read back from the running nodes:** RPP (`desired_linear_vel` 0.30, no reversing, rotate-to-heading 1.0 rad/s, angular acceleration 2.0 rad/s²), NavFn, goal checker 0.10 m / 0.10 rad, stamped commands on controller, behaviors and smoother, smoother limits [0.5, 0, 1.0] / [−0.25, 0, −1.0] / accel [0.5, 0, 2.0] / decel [−1.0, 0, −2.0], smoother self-stamping, odometry `/diff_drive_controller/odom`, behaviors `['wait']`, the package's own behavior trees.
  - **Map:** `global_costmap` subscribes to `/map`; no costmap subscribes to `/map_amcl`; `/global_costmap/costmap` frame `map`, 202 × 162 cells, 0.05 m, origin (−2.071, −4.080), the same as `/map`.
  - **Footprint:** both `footprint` parameters = CALC-M7-01; both published footprints (local in `odom`, global in `map`), transformed into `base_link`, = CALC-M7-01 padded by 0.01 m, largest vertex difference 0.0000 m.
  - **Command path:** `/cmd_vel` published only by `velocity_smoother` (`TwistStamped`), read only by `cmd_vel_guard`; `cmd_vel_nav` published by `behavior_server` and `controller_server`, read only by `velocity_smoother`; `/diff_drive_controller/cmd_vel` published only by `cmd_vel_guard`.
- **Navigation goal (1.0, 0.0, 0°)** (interface check, not a DEC-074 goal):

  | Attempt | Result | `/cmd_vel` (non-zero) | Forwarded by the guard | \|clock − stamp\| | v range | \|w\| max | Final pose (AMCL) | RTF |
  |---|---|---|---|---|---|---|---|---|
  | 1 | SUCCEEDED | 134 (114) | 134 of 134 | 0.000–0.004 s | 0–0.300 m/s | 0.037 rad/s | (0.904, 0.004), −2.08° | 0.91 |
  | 2 | SUCCEEDED | 130 (110) | 130 of 130 | 0.000–0.003 s | 0–0.300 m/s | 0.035 rad/s | (0.904, 0.004), −2.15° | 0.95 |
  | 3 | SUCCEEDED | 138 (118) | 138 of 138 | 0.000–0.003 s | 0–0.300 m/s | 0.035 rad/s | (0.903, 0.004), −2.18° | 0.88 |
- **INFO:** local costmap layers `voxel_layer`, `inflation_layer` (no static layer, installed configuration); global `static_layer`, `obstacle_layer`, `inflation_layer`. The final poses are AMCL estimates, about 0.096 m short of the goal: inside the 0.10 m goal-checker tolerance, as the checker stops on the first pose within it (arrival accuracy against ground truth is TEST-M7-03).
- **Shutdown:** navigation, localization and simulation launches CLEAN in all three attempts; 0 [ERROR] lines; 0 leftover processes by group and by name. TS-029 invalid attempts: 0. Navigation log warnings: the controller's once-only notes that no `current_goal_checker` / `current_progress_checker` was named (it uses the single loaded plugin).
- **Pictures and videos:** not used for the gallery (the TEST-M7-02 R1 captures are).
- **Result:** TEST-M7-02 **PASS**.

### Task A follow-up — TEST-M7-01 R1, 2026-11-21 04:25 IST
**Under test:** DEC-075 (optional Gazebo GUI layout for screen recordings, decided 2026-11-21) on revision `da18313` (`amr_ws/src` clean): `sim.launch.py` gains the `gui_config` argument, `config/gazebo_gui_capture.config` is new. TEST-M7-01 changed with it: `sim.launch.py` left step 4 (unchanged files) and has its own step 7 (diff from `9777615` removes no line and adds exactly the 12 `gui_config` lines).
**TEST-M7-01 R1** (REQ-M7-11): `bash docs/evidence/M7/TEST-M7-01_procedure.sh -R1`, exit 0 ([log](docs/evidence/M7/TEST-M7-01-R1_review.log)). 27 steps, all exit 0.
- Build, M1 byte identity and the two launch-model expansions: as TEST-M7-01.
- Step 4: the 16 remaining protected files unchanged since `9777615`.
- Step 5: existing files changed are `CMakeLists.txt`, `launch/sim.launch.py` and `package.xml`; the `package.xml` and `CMakeLists.txt` checks as TEST-M7-01; new files include `config/gazebo_gui_capture.config`.
- Step 6: both behavior trees as TEST-M7-01.
- Step 7: `sim.launch.py` 0 lines removed, 12 added, equal to the expected DEC-075 lines.
- **Negative control** (scratch, after the formal run): one stray comment line appended to `sim.launch.py` made step 7 FAIL (13 lines added, the extra line shown) and the run exit 1; the file was then restored with `git checkout`.
- **Not re-run:** TEST-M7-02 (its launch arguments do not include `gui_config`, so the `gz sim` command it starts is the one it was run with); the M2–M6 suites are re-run headless in TEST-M7-08.
- **Result:** TEST-M7-01 R1 **PASS**.

### Task B — dry runs, 2026-11-21 14:26–14:46 IST (scratch, not formal tests)
Four dry runs of `TEST-M7_nav_run.py` with Gazebo GUI and RViz shown (`docs/evidence/M7/TaskB_dryrun.sh`; consoles `TaskB-dry1_console.log` to `-dry4`), judged afterwards with `TEST-M7_nav_check.py`. Kept as the record of what the harness found before any formal run:
- Dry run 1 (tree `f071a2b`, installed NavFn defaults): sequence, route and cancel completed. Checker: `guard_drops` FAIL in sequence and route, a checker defect (TS-052, fixed); route `clearance` FAIL (0.089 m to P1) because the route started where the inside-P1 goal had parked the robot; TEST-M7-05 `invalid_motion` FAIL: the goal inside P1 was driven to, 3.05 m (TS-053).
- Dry run 2 (NavFn `tolerance` 0.0): inside-P1 still driven to (2.85 m). The first fix was insufficient.
- Dry run 3 (scratch parameter copy with `allow_unknown` false): both invalid goals ABORTED with 0.00 m of motion; the route from the spawn pose "SUCCEEDED" after 0.1 s without motion (TS-054).
- Dry run 4 (DEC-077 and DEC-078 values): invalid, sequence, route and cancel all PASS every checker criterion. Sequence: arrival ≤ 0.102 m and ≤ 6.17°, clearance minimum 0.483 m, moving P95 9.7 mm, goal times 0.84×–1.02× nominal.

### Task B — TEST-M7-07, 2026-11-21 14:48 IST
**TEST-M7-07** (REQ-M7-10): `python3 -I docs/evidence/M7/TEST-M7-07_distort.py docs/evidence/M7/TaskB-dry4_sequence` on revision `2b62a94` (tree clean), exit 0 ([log](docs/evidence/M7/TEST-M7-07_review.log)).
- Original log (dry run 4 sequence, G1 to G6): every TEST-M7-03 criterion PASS.
- `arrival_offset` (+0.20 m): FAIL on `arrival_position` only. `arrival_rotate` (+10°): FAIL on `arrival_heading` only. `path_into_obst` (1 s of track moved to a 0.03 m footprint gap): FAIL on `clearance` only. `cmd_fast` (one command 0.6 m/s): FAIL on `cmd_limits` only. `loc_shift` (estimate +0.30 m): FAIL on `moving_p95_position` and `moving_max_position`.
- **Result:** TEST-M7-07 **PASS**.

### Task B — TEST-M7-02 R1, 2026-11-21 14:48–14:50 IST
**Under test:** DEC-077 (`nav2.yaml`: NavFn `tolerance` 0.0, `allow_unknown` false) and the TS-052 guard matching, on revision `2b62a94` (`amr_ws/src` clean). The check gained the two parameters; the procedure's camera is the M5 view (DEC-075 amendment).
**TEST-M7-02 R1:** `SHOW=1 bash docs/evidence/M7/TEST-M7-02_procedure.sh 3 docs/evidence/M7/TEST-M7-02-R1_review.log`, exit 0 ([log](docs/evidence/M7/TEST-M7-02-R1_review.log)). 171 PASS lines, 0 FAIL; Gazebo GUI and RViz shown in all 3 attempts, attempt 1 recorded.
- Every attempt: servers active, both new parameters read back, guard forwarded 126/126, 128/128, 127/127 (0 clamped), RTF 0.96–0.97, shutdowns CLEAN, 0 leftovers; TS-029 invalid 0.
- **Pictures and videos:** attempt 1 in [`docs/gallery/M7/TEST-M7-02/`](docs/gallery/M7/TEST-M7-02/).
- **Result:** TEST-M7-02 R1 **PASS**.

### Task C — TEST-M7-03, 2026-11-21 14:58–15:07 IST
**Command:** `SHOW=1 bash docs/evidence/M7/TEST-M7_procedure.sh TEST-M7-03 3 docs/evidence/M7/TEST-M7-03_review.log`, revision `b8fc601` (`amr_ws/src` clean), exit 0 ([log](docs/evidence/M7/TEST-M7-03_review.log); recordings `TEST-M7-03_a{1,2,3}_*`). Each attempt from a fresh simulation at the spawn pose; Gazebo GUI (capture layout, M5 camera) and RViz shown in every attempt (`SHOW=1` applies to all attempts; only attempt 1 is recorded).
- All 18 goals SUCCEEDED. Arrival (ground truth after the hold): 0.084–0.105 m, 3.71–5.66° (≤ 0.15 m, ≤ 7.0°). Time 0.85×–1.02× nominal (≤ 2.0×). Clearance minimum 0.481 m (pillar P2; ≥ 0.10 m, L1 included). Moving localization: P95 10.3–11.9 mm and 0.149–0.169°, maximum 15.4 mm. Commands: 2729–2847 per run, v 0.000–0.300 m/s, |w| ≤ 1.000 rad/s, stamps ≤ 0.035 s from the clock; guard forwarded all (1–10 per run with the stamp clamped, TS-052 rule); one `/cmd_vel` publisher (velocity_smoother).
- RTF 0.94–0.98, 0 samples missing; all shutdowns CLEAN, 0 leftovers; TS-029 invalid 0.
- **Pictures and videos:** attempt 1 in [`docs/gallery/M7/TEST-M7-03/`](docs/gallery/M7/TEST-M7-03/).
- **Result:** TEST-M7-03 **PASS**.

### Task C — TEST-M7-04, 2026-11-21 15:08–15:13 IST
**Command:** `SHOW=1 bash docs/evidence/M7/TEST-M7_procedure.sh TEST-M7-04 3 docs/evidence/M7/TEST-M7-04_review.log`, revision `b8fc601`, exit 0 ([log](docs/evidence/M7/TEST-M7-04_review.log)).
- Route G1 → G3 → G5 (one NavigateThroughPoses goal) SUCCEEDED in 63.8, 63.4, 63.5 s (0.78× of 81.6 s nominal); 16.70–16.75 m driven. Final arrival 0.097–0.101 m, 3.66–5.48°. Clearance minimum 0.475 m (P2). Moving P95 8.1–8.9 mm and 0.084–0.123°, maximum 11.2 mm. Commands within DEC-025, 0 guard drops, one publisher.
- RTF 0.96–0.98, 0 samples missing; all shutdowns CLEAN, 0 leftovers; TS-029 invalid 0.
- **Pictures and videos:** attempt 1 in [`docs/gallery/M7/TEST-M7-04/`](docs/gallery/M7/TEST-M7-04/).
- **Result:** TEST-M7-04 **PASS**.

### Task C — TEST-M7-05, 2026-11-21 15:13–15:17 IST
**Command:** `SHOW=1 bash docs/evidence/M7/TEST-M7_procedure.sh TEST-M7-05 3 docs/evidence/M7/TEST-M7-05_review.log`, revision `b8fc601`, exit 1 ([log](docs/evidence/M7/TEST-M7-05_review.log)).
- Measurements, all 3 attempts: inside_P1 ABORTED after 23.8–24.4 s, outside_map ABORTED after 0.1 s (≤ 60 s); ground-truth motion 0.0 mm (≤ 50 mm); no command published; one publisher. RTF 0.97–0.98.
- Shutdown: attempts 1 and 2 CLEAN. **Attempt 3:** the simulation launch's `gz sim` (GUI front end) did not stop within 5 s of SIGINT, was sent SIGTERM and died with exit code 1 after an `Errno::ESRCH` traceback and `Escalating to SIGKILL on [Gazebo Sim GUI]`; 0 leftovers. Classifier OTHER (DEC-039 covers −9/−15 only), so the attempt FAILED. Full launch logs kept (`TEST-M7-05_a3_{sim,loc,nav}_launch.log`). Diagnosis: TS-039 recurrence (docs/troubleshooting.md).
- Corrective action: DEC-079: with the GUI, this exact signature makes an attempt INVALID, as DEC-039 does headless. Classifier and procedure changed; `DEC-079_classifier_check.sh` PASS ([log](docs/evidence/M7/DEC-079_classifier_check.log)).
- **Result:** TEST-M7-05 **FAIL** (shutdown only). Re-run as R1 under DEC-079.

### Task C — TEST-M7-05 R1, 2026-11-21 15:22–15:25 IST
**Command:** `SHOW=1 bash docs/evidence/M7/TEST-M7_procedure.sh TEST-M7-05 3 docs/evidence/M7/TEST-M7-05-R1_review.log`, revision `5e3b728` (`amr_ws/src` clean; DEC-079 in the procedure), exit 0 ([log](docs/evidence/M7/TEST-M7-05-R1_review.log)).
- All 3 attempts: inside_P1 ABORTED after 23.6, 23.4, 22.5 s; outside_map ABORTED after 0.1 s; ground-truth motion 0.0 mm; no command published; one publisher.
- All shutdowns CLEAN, 0 leftovers; TS-029 invalid 0, TS-039 invalid 0 (DEC-079 not needed).
- **Result:** TEST-M7-05 R1 **PASS**.

### Task C — TEST-M7-06, 2026-11-21 15:25–15:28 IST
**Command:** `SHOW=1 bash docs/evidence/M7/TEST-M7_procedure.sh TEST-M7-06 3 docs/evidence/M7/TEST-M7-06_review.log`, revision `5e3b728`, exit 0 ([log](docs/evidence/M7/TEST-M7-06_review.log)).
- Cancel of the G1 goal accepted after 1.021, 1.022, 1.029 m of travel; result CANCELED (3.8 s after the goal was accepted). Travel from the cancel acceptance to the end of the hold 49.3, 52.9, 39.1 mm (≤ 150 mm). Stillness (≤ 0.01 m/s for 5 s) found from 0.3, 0.3, 0.2 s after the cancel; maximum speed in that window 2.73, 8.39, 5.76 mm/s.
- The window maxima are the last deceleration sample: ground-truth speed after the cancel falls from about 0.2–0.3 m/s to 0.0 mm/s within 0.4–0.5 s and stays 0.0 to the end of the hold in every attempt (recomputed from `TEST-M7-06_a{1,2,3}_track.csv`).
- Commands within DEC-025 (99–110 per run), 0 guard drops, one publisher. RTF 0.88–0.96; 1 of 135 samples missing in attempt 1 (≤ 2 %). All shutdowns CLEAN, 0 leftovers; TS-029 and TS-039 invalid 0.
- **Result:** TEST-M7-06 **PASS**. With TEST-M7-03, -04 and -05 R1, Task C's tests are complete.

### Task D — TEST-M7-08, 2026-11-22 23:08 to 2026-11-23 01:49 IST
**Command:** `for s in static regression m4 m5 m6; do python3 tools/run_suite.py $s M708; done`, headless, revision `8bbebeb` (`amr_ws/src` clean throughout). Summaries: [static](docs/evidence/TA/static-M708_summary.md), [regression](docs/evidence/TA/regression-M708_summary.md), [m4](docs/evidence/TA/m4-M708_summary.md), [m5](docs/evidence/TA/m5-M708_summary.md), [m6](docs/evidence/TA/m6-M708_summary.md); evidence index rows "TEST-M7-08".
- **Files changed during the run** (not product files): TEST-M7-10 work edited `tools/run_suite.py` (new `m7` suite; TEST-M7-10 and TEST-M7-07 added to `static`), records and the evidence index (`docs/evidence/README.md`, `docs/milestones/M7_navigation.md`, `docs/requirements.md`, `docs/testing/test_plan.md`) after `static` had finished. Each suite starts the runner afresh; the m4, m5 and m6 commands were compared with the `8bbebeb` runner and are identical. `amr_ws/src` and the test procedures were not changed.
- **static** (exit 0): 11 of 11 PASS-candidate. **regression** (exit 0): 20 of 20.
- **m4, m5, m6** (exit 1 each): the same tag M708 was used for every suite, so the runner refused the six offline entries whose logs `static` had already written (TEST-M4-12, -03; TEST-M5-10, -07; TEST-M6-11, -08). They ran in `static` with the same command on the same tree and passed. Procedure defect of this batch; later batches use one tag per suite.
- **Executed entries:** 51 of 55 PASS-candidate. Failed:
  - TEST-M5-01 and TEST-M6-01: step 4 only, `sim.launch.py` CHANGED vs their baselines by the M7 `gui_config` option (DEC-075). Every other step passed ([M5 log](docs/evidence/M5/TEST-M5-01-M708_review.log), [M6 log](docs/evidence/M6/TEST-M6-01-M708_review.log)). Resolved by DEC-080.
  - TEST-M5-02: attempt 2 main check, `slam_toolbox` stayed `inactive` after a dropped `change_state` reply (TS-055); attempts 1 and 3 passed ([log](docs/evidence/M5/TEST-M5-02-M708_review.log)).
  - TEST-M6-03 reverse: attempt 3 AMCL stayed `unconfigured` (harness exit 2, INVALID, not counted); its localization shutdown then escalated to SIGKILL of the lifecycle manager, which fails the test (TS-055). Attempts 1, 2 and 4 passed, end-of-route error 2.1 mm in attempt 4 ([log](docs/evidence/M6/TEST-M6-03-M708-reverse_review.log)).
- **Review of the passing logs:** every FAIL line is explained: quoted history in PASS lines (TEST-M2-11, -M5-10, -M6-11 records checks), TEST-M3-02's expected scope assertions (TS-016, TS-023), and the injected faults of the sensitivity tests (TEST-M5-07, -M6-08). TS-029 invalid 0; leftover processes 0 in every attempt.
- **Result:** TEST-M7-08 **FAIL** (kept as the original result). Re-run of the failed and refused entries: TEST-M7-08 R1.

### Task D — TEST-M7-08 R1, 2026-11-23 01:58 to 02:13 IST
**Under test:** the six refused and four failed entries of TEST-M7-08, headless, one tag per run, on `6331b91` (DEC-080 in TEST-M5-01 and TEST-M6-01; `amr_ws/src` unchanged since `8bbebeb`).
- `records` suite (M708RR): 6 of 6 PASS-candidate, including TEST-M4-12, -M5-10 and -M6-11 (summary not published).
- `ci` suite (M708C): 6 of 7 PASS-candidate, including TEST-M4-03, -M5-07 and -M6-08; TEST-M7-07 exited 0 but was NO-OVERALL, as in GitHub CI on the same commit (TS-056) ([summary](docs/evidence/TA/ci-M708C_summary.md)). After the fix (the tool also prints an overall line; its checks are unchanged), `ci` (M708C2, working tree): 7 of 7 ([summary](docs/evidence/TA/ci-M708C2_summary.md)).
- TEST-M5-01 and TEST-M6-01 (M708R1): every step passed; step 4 prints the DEC-080 line for `sim.launch.py` ([M5 log](docs/evidence/M5/TEST-M5-01-M708R1_review.log), [M6 log](docs/evidence/M6/TEST-M6-01-M708R1_review.log)).
- TEST-M5-02 (M708R1): 3 of 3 valid runs, `slam_toolbox` active in each, TS-029 invalid 0 ([log](docs/evidence/M5/TEST-M5-02-M708R1_review.log)).
- TEST-M6-03 reverse (M708R1): 3 of 3 valid runs, no invalid attempt; end-of-route error 2.9 to 7.6 mm; all shutdowns CLEAN, 0 leftovers ([log](docs/evidence/M6/TEST-M6-03-M708R1-reverse_review.log)). TS-055 did not recur.
- Remaining FAIL lines in passing logs: TEST-M3-02's expected scope assertions and TEST-M5-07's injected distortions.
- **Result:** TEST-M7-08 R1 **PASS** (REQ-M7-11). With M7 in place, every M2–M6 suite entry passes.

### Task D — TEST-M7-09, 2026-11-23 02:18 to 02:42 IST
**Command:** `SHOW=1 DONE_FLAG=<file> bash docs/evidence/M7/TEST-M7_procedure.sh TEST-M7-09 1 docs/evidence/M7/TEST-M7-09_review.log`, revision `66d197f` (`amr_ws/src` clean; the procedure's new `observe` mode and `TEST-M7-09_goal_status.py` were uncommitted at run time and are committed with this record). GUI and RViz shown, recorded ([log](docs/evidence/M7/TEST-M7-09_review.log)).
- **Earlier session, not a valid formal run** (02:18 to 02:26): started from an ad-hoc script (`TEST-M7-09_session.sh`, now superseded). My observation was the same (path, both costmaps and footprint shown; five goals reached without contact; goals inside a wall did nothing; 6 SUCCEEDED, 4 ABORTED). But the script lacked `set -m`, so all three launches ignored SIGINT and were stopped with SIGTERM, leaving 16 processes. No video was taken ([log](docs/evidence/M7/TEST-M7-09_session.log); TS-057).
- **Observed by user** (formal run): "1 yes 2 yes 3 yes 4 6 and yes 5 nothing happened": the planned path, both costmaps and the footprint shown; six goals reached without contact; goals inside a wall did nothing.
- **Supporting record:** 11 goals with a final status: 8 SUCCEEDED, 3 ABORTED (the goals inside a wall, refused without motion, DEC-077) ([status echo](docs/evidence/M7/TEST-M7-09_a1_status.txt)). All three launches stopped CLEAN, 0 leftovers.
- **Low-box probe (shown, not judged; decided 2026-11-23):** after the six goals, I deliberately set a goal on L1, which is invisible to the LiDAR and not in the map (M7 plan §3.2). Nav2 accepted it and the robot drove into the box at about 215 s of the video and stopped there. The estimate then diverged: about 2.78 m and 87° from ground truth, measured live ([log](docs/evidence/M7/TEST-M7-09_a1_pose_mismatch.log)). The later SUCCEEDED results are in that wrong estimate. Documented M7 limitation; known issue TS-058, carried into M8.
- **Result:** TEST-M7-09 **PASS** (observed by me; REQ-M7-12), with the L1 probe recorded as a demonstrated known limitation.

### Task D — TEST-M7-10, 2026-11-23 02:53 to 03:18 IST
**Command:** `SHOW=1 python3 tools/run_suite.py m7 M710`, revision `85cd1e1` (`amr_ws/src` clean), GUI and RViz shown; attempt 1 of each navigation test recorded to the gallery's pending folder ([summary](docs/evidence/TA/m7-M710_summary.md)).
- Consistency checker (records under DEC-041, configuration against DEC-025 and DEC-062 to DEC-080, evidence index, automation): ALL CHECKS PASSED (log (not published)). Mutation check on the final tree: control PASS, 21 of 21 injected faults detected (log (not published)).
- Suite entries, all PASS-candidate and reviewed: TEST-M7-01 (every step), TEST-M7-07 (original PASS, five distortions FAIL), TEST-M7-02, -03, -04, -05, -06 (3 of 3 valid runs each).
- TEST-M7-05 attempt 3: measurements passed; the GUI shutdown showed the TS-039 signature, so the attempt was INVALID under DEC-079 and repeated; attempt 4 passed (kept launch logs `TEST-M7-05-M710_a3_*_launch.log`). Every other shutdown CLEAN; 0 leftover processes in all 16 attempts; TS-029 invalid 0; RTF 0.79 to 1.00.
- CI: TEST-M7-07 runs in the `ci` slice on every code push (green from `66d197f`, after TS-056); TEST-M7-10 is in the `records` slice, which runs on manual dispatch.
- **Result:** TEST-M7-10 **PASS** (REQ-M7-13). With it, TEST-M7-01 to -10 are all PASS.
