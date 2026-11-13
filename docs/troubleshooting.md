# Troubleshooting and Known Issues

Record every significant warning, failure, diagnosis, and fix. Do not delete entries; mark them resolved instead.

## Entry template
```
### TS-nnn — Short title
**Date:** YYYY-MM-DD   **Milestone:** Mx   **Status:** Open | Resolved | Accepted (benign)
**Symptom:** exact message or behaviour
**Context:** command, environment, related test ID
**Diagnosis:** cause, and how it was determined
**Fix / action:** what was changed (or why no change is needed)
**Verification:** test or observation confirming the fix
```

## Entries

### TS-001 — Gazebo GUI Qt QML binding-loop warnings
**Date:** 2026-10-19   **Milestone:** M0   **Status:** Accepted (benign)
**Symptom:** Qt QML binding-loop warnings printed when the Gazebo Sim GUI launched (exact text not captured).
**Context:** `gz sim -v 4 shapes.sdf`, TEST-M0-02.
**Diagnosis:** Not investigated. No fatal error was observed, and the simulation ran with RTF ≈ 100 % (observed by me).
**Fix / action:** None. Re-evaluate if GUI problems appear.
**Verification:** TEST-M0-02 PASS.

### TS-002 — RViz2 "Stereo is NOT SUPPORTED"
**Date:** 2026-10-19   **Milestone:** M0   **Status:** Accepted (benign)
**Symptom:** `Stereo is NOT SUPPORTED` printed at RViz2 start-up.
**Context:** RViz2 launch, TEST-M0-03.
**Diagnosis:** An informational message about stereoscopic rendering support. RViz2 opened and reported OpenGL 4.6 (observed by me).
**Fix / action:** None required.
**Verification:** TEST-M0-03 PASS.

### TS-003 — Git identity not configured
**Date:** 2026-10-19   **Milestone:** M0   **Status:** Resolved
**Symptom:** `git config user.name` / `user.email` returned nothing at any config level before the M0 commit.
**Context:** Preparing commit `8770ad2`.
**Diagnosis:** No `user.*` entries in the system, global, or local Git configuration (`git config --show-origin --get-regexp '^user\.'` returned nothing).
**Fix / action:** I set the identity in `~/.gitconfig`.
**Verification:** Commit `8770ad2` was authored with the configured identity.

### TS-005 — DART warnings for ellipsoid and cone collision shapes
**Date:** 2026-10-19   **Milestone:** M0   **Status:** Accepted (benign)
**Symptom:** `[Wrn] [SDFFeatures.cc:366] DART: Ellipsoid is not a supported collision geomerty primitive, using generated mesh of an ellipsoid instead` and the same message for Cone (`SDFFeatures.cc:351`). The spelling is Gazebo's.
**Context:** `gz sim -s -r -v 2 shapes.sdf`, TEST-M0-04 re-test 1.
**Diagnosis:** The DART physics engine has no native ellipsoid or cone collision primitive, so Gazebo substitutes generated meshes for the sample world's shapes. The simulation ran and `/clock` advanced.
**Fix / action:** None. The M1 model uses only box, cylinder, and sphere primitives (DEC-017).
**Verification:** TEST-M0-04 re-test 1 PASS.

### TS-006 — Leftover Gazebo server from an earlier GUI session
**Date:** 2026-10-19   **Milestone:** M0   **Status:** Resolved (process terminated manually after testing)
**Symptom:** A `gz sim server` process (PID 34793, started 04:41:37, re-parented to `systemd --user`) was still running and publishing `/clock` and `/world/shapes/*` on the default Gazebo partition.
**Context:** Found by the pre-check for TEST-M0-04 re-test 1. It is most likely left over from the TEST-M0-02 GUI session; that origin is inferred from the start time and the `shapes` world, not confirmed.
**Diagnosis:** Two simulators on the same partition would both publish `/clock`, which could contaminate a bridge test.
**Fix / action:** the test did not stop the process, because it was not started by this test. The re-test was isolated instead with `GZ_PARTITION` and `ROS_DOMAIN_ID`; the process was to be stopped by hand (`kill 34793`) after confirming it was not needed.
**Verification:** The re-test pre-check found no `/clock` in the isolated partition; after the test, PID 34793 was still running and unchanged.

**Update (2026-10-19, after TEST-M0-04 re-test 1):**
- *Outcome:* I terminated the leftover Gazebo process manually after testing. The test script did not terminate it: the script signalled only its own process groups (40605 and 40666), and the log shows PID 34793 still running after that cleanup.
- *PID:* **34793**, confirmed by two independent `ps` observations: the pre-test inspection (`ps -o pid,ppid,lstart,etime,cmd -p 34793`, which showed it started at 04:41:37 with parent `systemd --user`) and line 54 of [TEST-M0-04-R1_clock_bridge_headless.log](evidence/M0/TEST-M0-04-R1_clock_bridge_headless.log) (`34793 gz sim server`).
- *Alternative PID 24793:* this number appears in no captured evidence, and no process with it existed when checked. The PID used in my termination command was not captured.
- *Later checks:* `ps -p 34793` returned no process (first observed after the M0 evidence commit `2ee62da`). No exit status or termination signal was captured.
- The historical test log is unchanged.

### TS-007 — TEST-M1-03 check reported meshes and plugins that the model does not contain
**Date:** 2026-10-21   **Milestone:** M1   **Status:** Resolved
**Symptom:** `TEST-M1-03_check.py` reported `FAIL  no mesh references (REQ-M1-10)` and `FAIL  no Gazebo sensor or plugin elements (REQ-M1-09)`, and exited 1. All 50 property checks passed ([TEST-M1-03_check.log](evidence/M1/TEST-M1-03_check.log)).
**Context:** TEST-M1-03, first run, on the URDF generated in TEST-M1-02.
**Diagnosis:** a false positive in the check script. Its first version tested `'mesh' not in text.lower()` and `'sensor' not in text and 'plugin' not in text` on the raw file text. xacro copies XML comments into the generated URDF, and two comments from `amr.urdf.xacro` match ("Primitive geometry only, no meshes … No sensors, controllers or Gazebo plugins in M1" and "the M3 sensor frame will attach"). `grep -niE 'mesh|sensor|plugin'` found only those two comment lines. An element-level parse found 0 `<mesh>`, `<gazebo>`, `<sensor>` and `<plugin>` elements and no `filename` attributes.
**Fix / action:** the two checks now inspect XML elements (comments excluded): no `<mesh>` elements or `filename` attributes, and no `<gazebo>`, `<sensor>` or `<plugin>` elements. The model files were not changed.
**Verification:** TEST-M1-03 re-test 1 passed 52/52 on byte-identical URDF and SDF ([TEST-M1-03-R1_check.log](evidence/M1/TEST-M1-03-R1_check.log)).
**Follow-up (resolved 2026-10-21):** the planned TEST-M1-08 procedure `grep -ri mesh src/amr_description/urdf` would have matched the same comment. It was replaced, before TEST-M1-08 was run, with an element-level check of the source Xacro files and the generated URDF ([test_plan.md §4](testing/test_plan.md)). TEST-M1-08 is still PLANNED.

### TS-008 — `joint_state_publisher_gui` Qt warning at start-up and exit code −2 at shutdown
**Date:** 2026-10-21   **Milestone:** M1   **Status:** Accepted (benign)
**Symptom:** at start-up, `[joint_state_publisher_gui-2] QSocketNotifier: Can only be used with threads started with QThread`. At shutdown, `[ERROR] [joint_state_publisher_gui-2]: process has died [pid …, exit code -2, …]`.
**Context:** `ros2 launch amr_description display.launch.py`, TEST-M1-04 ([sanitized launch log](evidence/M1/TEST-M1-04_display_launch_sanitized.log)).
**Diagnosis:**
- The Qt warning was printed once, before the node reported "Got description, configuring robot". The slider GUI then worked: I moved both sliders, and `/joint_states` and TF followed. The root cause was not investigated.
- A negative exit code in `ros2 launch` means the process ended on that signal number. −2 is SIGINT, which the shutdown deliberately sent to the launch. `robot_state_publisher` and `rviz2` finished cleanly, and `ps` afterwards showed no remaining process.
**Fix / action:** none. Both messages are cosmetic for M1. Revisit if the slider GUI misbehaves or a node remains after shutdown.
**Verification:** TEST-M1-04 PASS with the GUI working as expected.

### TS-009 — Stopping the first Gazebo launch design left `gz sim server` and `gui` running
**Date:** 2026-10-21   **Milestone:** M1   **Status:** Resolved
**Symptom:** after SIGINT to the first version of `gazebo.launch.py`, launch printed `process[gazebo-2] failed to terminate '5' seconds after receiving 'SIGINT', escalating to 'SIGTERM'`, then `process has died [pid …, exit code -15, cmd 'ruby …/gz sim -r empty.sdf --force-version 8']`. `ps` then showed `gz sim -r empty.sdf`, `gz sim server` and `gz sim gui` still running for more than 30 s (the same class of leftover as TS-006).
**Context:** first exploratory run for M1 steps 6–7, before TEST-M1-06. That version included `ros_gz_sim/launch/gz_sim.launch.py` with `gz_args:='-r empty.sdf'`.
**Diagnosis:**
- `ps` showed the launch-managed process was `/bin/sh -c ruby …/gz sim …`. `gz_sim.launch.py` starts Gazebo through a shell, and the shell does not forward SIGINT. SIGTERM after 5 s killed only the shell, so the real `gz sim` (now re-parented) and its server and GUI were orphaned.
- Sending SIGINT directly to the orphaned `gz sim` parent stopped all three processes within about 1 s. So `gz` itself shuts down cleanly when it receives SIGINT.
**Fix / action:**
- `gazebo.launch.py` now starts Gazebo with `ExecuteProcess(cmd=['gz', 'sim', '-r', 'empty.sdf'], on_exit=Shutdown())`, with no shell. Spawning still uses `ros_gz_sim create`.
- The orphaned processes from the exploratory run were stopped by that SIGINT.
**Verification:**
- A second exploratory run: on SIGINT, `gz-2` "finished cleanly", with no escalation and 0 leftover processes.
- The TEST-M1-06/07 run: same result, with 0 leftovers within about 1 s ([launch log](evidence/M1/TEST-M1-06_gazebo_launch_sanitized.log)).

### TS-010 — TEST-M1-08 URDF byte comparison failed on xacro's header comment
**Date:** 2026-10-21   **Milestone:** M1   **Status:** Resolved
**Symptom:** in the first TEST-M1-08 run, `cmp <tmp>/amr.urdf docs/evidence/M1/TEST-M1-02_amr.urdf` exited 1. Every other step passed ([TEST-M1-08_review.log](evidence/M1/TEST-M1-08_review.log)).
**Context:** `TEST-M1-08_procedure.sh` ran `xacro amr_ws/src/amr_description/urdf/amr.urdf.xacro` from the repository root.
**Diagnosis:** `diff` showed one line only. xacro writes the path it was invoked with into the generated header comment ("autogenerated by xacro from …"), so the new file says `amr_ws/src/…` while the evidence says `src/…`. TEST-M1-02 ran xacro from `amr_ws/`, the shell context test_plan.md §4 assumes. Run from `amr_ws/`, the regenerated URDF is byte-identical to the evidence, so the model content was never different.
**Fix / action:** the procedure now runs `(cd amr_ws && xacro src/amr_description/urdf/amr.urdf.xacro)`, and its log names take a re-test tag. test_plan.md §4 states the working directory explicitly. No model or evidence file changed.
**Verification:** TEST-M1-08 re-test 1: URDF and SDF byte-identical, every step exit 0 ([TEST-M1-08-R1_review.log](evidence/M1/TEST-M1-08-R1_review.log)).

### TS-011 — M2 test procedure: launch not stoppable by SIGINT, and the harness could not import `rclpy`
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (before any formal test)
**Symptom:** in the first preliminary run of `TEST-M2_procedure.sh` (output in scratch, not evidence):
- the harness failed at once with `ModuleNotFoundError: No module named 'rclpy'`;
- after the procedure ended, `ros2 launch`, `robot_state_publisher`, `parameter_bridge` and `gz sim -s` were still running.
**Diagnosis:**
- (1) `python3 -I` (isolated mode) ignores `PYTHONPATH`, which is how the ROS environment provides `rclpy`.
- (2) `/proc/<pid>/status` showed `SigIgn: …1001006`, i.e. **SIGINT ignored**. Bash starts background jobs of a non-interactive shell with SIGINT and SIGQUIT ignored. So `kill -INT` never reached `ros2 launch`, and its children (which inherit the ignored SIGINT) survived a SIGTERM of the launch.
**Fix / action:**
- The harness runs with plain `python3`; `-I` stays in use for the scripts that need no ROS imports.
- The procedure runs with job control (`set -m`), which gives background jobs their own process group and default signal handling. It sends SIGINT to the launch (the TS-009 shutdown path) and SIGTERM to the process group only if the launch is still alive after 30 s.
- The leftover processes of the preliminary runs (all started by this session) were stopped with SIGTERM.
**Verification:** subsequent runs show `SigIgn: …1001000` (SIGINT not ignored) for the launch, and "leftover gz processes: 0" in every procedure log.

### TS-012 — Reverse motion slowed at 0.5 m/s² instead of 1.0 m/s² with the reverse limits unset
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (before any formal test)
**Symptom:** a preliminary diagnostic of the `/diff_drive_controller/cmd_vel_out` timeline (scratch output):
- forward speed-up was ≈ 0.5 m/s² and forward slowing ≈ 1.0 m/s², as configured;
- but slowing down from reverse (−0.2 → 0 m/s) took ≈ 0.40 s, i.e. ≈ 0.5 m/s².
**Context:** DEC-025 configured `linear.x.max_acceleration: 0.5` and `linear.x.max_deceleration: -1.0`, and left `max_acceleration_reverse` and `max_deceleration_reverse` unset. The installed parameter descriptions say unset reverse limits use −max_acceleration and −max_deceleration.
**Diagnosis:** the installed controller (diff_drive_controller 4.42.1) did not apply −max_deceleration when slowing from reverse. The cause inside the controller was not investigated further; the observable behaviour contradicts its description.
**Fix / action:** `amr_bringup/config/controllers.yaml` sets all four linear and all four angular limit parameters explicitly to the DEC-025 values (`max_acceleration_reverse: -0.5`, `max_deceleration_reverse: 1.0`, and the angular equivalents). No value changed; DEC-025 is implemented as decided.
**Verification:** TEST-M2-05 (reverse distance) and TEST-M2-08 (measured slowing from reverse ≤ 1.10 m/s²).

### TS-013 — Python harness lagged behind simulation time when subscribed to the 1 kHz `/clock`
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (before any formal test)
**Symptom:** in preliminary runs (scratch output):
- a commanded 5.0 s leg lasted 5.88 s of simulation time;
- ground-truth speed dropped to ≈ 0 mid-leg while the controller was still commanding −0.2 m/s;
- an earlier reverse leg travelled 1.062 m instead of the expected value.
**Diagnosis:**
- `ros2 topic hz /clock` measured 1000.2 to 1000.5 Hz: the bridge publishes every 1 ms physics step.
- The harness node used `use_sim_time`, so rclpy processed every `/clock` message in Python.
- Comparing the harness's `/clock` time with the latest Gazebo pose stamp showed lags of up to 0.71 s, with the ground-truth sample rate collapsing. The harness was starved: its stretched timing lengthened the legs, and late stamps and gaps paused the commands.
- The robot and controller were not at fault.
**Fix / action:**
- The harness takes simulation time from the Gazebo pose stream stamps (the same simulation clock, about 60 Hz) and no longer subscribes to `/clock` (`use_sim_time` false on the harness node only).
- Commands are still stamped in simulation time, so DEC-026's publisher/controller clock consistency is kept.
- Teleop (TEST-M2-09) is unaffected: it publishes only on key presses.
**Verification:** the repeated diagnostic and the formal M2 runs (RTF and leg durations recorded in each log).

### TS-014 — In-place rotation 9 % larger than commanded: cylinder wheel contact in DART
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (DEC-028): sphere wheel collision in the M2 simulation model; verified by TEST-M2-06/08 re-test 1 (+179.90 to +180.20° / −179.90 to −180.19°, yaw rate 1.0000 rad/s). The DART-contact explanation remains a supported hypothesis; the contact points were not measured
**Symptom:**
- Preliminary TEST-M2-06 runs on the accepted model ([cylinder log](evidence/M2/TS-014_rotate_cylinder_wheels.log)): commanding ±0.5 rad/s for π/0.5 s turned the robot **+196.34° / −196.39°** (target 180° ± 5 %).
- Odometry reported +179.93° / −179.91° (ratio 0.916). Translation was < 0.4 mm and wheel velocities had the correct signs.
- TEST-M2-08 showed the same factor: ground-truth yaw rate 1.096 rad/s for a limited command of 1.0 rad/s.
- Straight motion is unaffected (TEST-M2-05 preliminary: 0.980 m, odometry ratio 1.000).
**Diagnosis:**
- The physical yaw rate is 1.091 × the kinematic rate (v_R − v_L)/b with b = `wheel_track` = 0.400 m, i.e. an effective track of 0.400 / 1.091 ≈ **0.3665 m**. That is close to the inner-rim spacing of the 0.035 m-wide wheels, 0.400 − 0.035 = 0.365 m.
- Diagnostic ([script](evidence/M2/TS-014_sphere_wheel_diag.sh), [sphere log](evidence/M2/TS-014_rotate_sphere_wheels.log)): in a temporary copy, only the wheel *collision* geometry was replaced by a sphere of the same radius (contact on the wheel mid-plane); visuals, inertia, joints, friction and controller were unchanged. The same rotate run then turned **+180.18° / −179.87°**, with odometry ratio 1.000.
- So the installed DART cylinder–ground contact acts effectively at the inner rims during rotation. Where exactly the contact points lie was not measured.
**Fix / action:** none applied. The choices change robot geometry or controller calibration, so they need a my decision:
- (a) sphere (or narrower) wheel collision geometry, keeping the cylinder visual;
- (b) calibrate the controller (`wheel_separation_multiplier` ≈ 0.916, or `wheel_separation` 0.3665 m), which also changes odometry;
- (c) accept and record the deviation as a simulation limitation; this would need a revision of DEC-027's angle criterion.
The formal TEST-M2-06/08 runs on the accepted model are recorded as they are.
**Verification:** pending the decision. A re-test of TEST-M2-06 and TEST-M2-08 is needed afterwards.

### TS-015 — Commands stamped in wall-clock time never time out in simulation (hazard)
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved for the simulation interface (DEC-029 `cmd_vel_guard`; TEST-M2-07 re-test 1: wall-clock commands cause 0.000 mm of motion; after a domain switch the robot is at rest ≤ 0.719 s after the last valid command). Residual limits in DEC-029
**Symptom:** TEST-M2-07 `wallclock` characterization:
- a publisher without `use_sim_time` (stamps ≈ 1.8·10⁹ s) sent 0.2 m/s commands for 2 s while the controller ran on simulation time (≈ 10 s);
- the robot accepted the commands and **kept moving at about 0.2 m/s for the whole 3 s after the last message** (about 0.6 m) instead of stopping after `cmd_vel_timeout` (0.5 s);
- commands stamped 1.0 s in the past (`stale`) were correctly ignored.
**Diagnosis:** the installed controller compares the command's header stamp with its own clock. A stamp far in the *future* is never judged stale, so the timeout cannot trigger. This is the hypothesis recorded in DEC-026 / motion_control.md §5, now observed.
**Fix / action (mitigation in place):**
- DEC-026 requires every publisher of stamped commands to use simulation time: teleop runs with `use_sim_time:=true`, and the test harness stamps simulation time.
- Not fixed: any publisher with a wrong clock (or, on hardware, clock skew between machines) defeats the command timeout.
- A further safeguard, such as a command watchdog or rejecting future stamps, would be a new design decision.
**Verification:** formal TEST-M2-07 `wallclock` run (characterization) in `TEST_RESULTS.md`.

### TS-016 — TEST-M2-02: the M1 consistency checker rejects the new M2 Xacro file
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (default variant passed in re-test 1 and re-test 2)
**Symptom:** formal TEST-M2-02 (revision `26a6048`) exited 1. The only failing check was `TEST-M1-08_consistency_check.py`: "amr_ws/src/amr_description/urdf/amr.ros2_control.xacro: no mesh, gazebo, sensor, plugin, transmission, ros2_control elements [gazebo=4, plugin=2, ros2_control=1]" ([log](evidence/M2/TEST-M2-02_review.log)).
**Diagnosis:** the M1 checker scans every Xacro source file in `urdf/` for M1-scope content. The DEC-023 file is meant to contain exactly those elements. The model itself is correct: every default-variant comparison and check, and every enabled-variant control check, passed. The procedure accepted the equivalent M1-scope assertions of TEST-M1-03 but not this one.
**Fix / action:** `TEST-M2-02_procedure.sh` now requires the M1 consistency check to fail on exactly that one assertion for `amr.ros2_control.xacro` and pass everything else, mirroring the TEST-M1-03 handling. No checker, model or evidence file changed.
**Verification:** TEST-M2-02 re-test 1.

### TS-017 — TEST-M2-04 procedure: `/clock` parse error and shutdown hang
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (TEST-M2-04 re-test 1 finished by itself; clock 4 → 8 s parsed)
**Symptom:** in formal TEST-M2-04:
- the `/clock` check errored ("integer expression expected"), although the clock advanced from 4 to 7 s;
- after the checks, the procedure never finished, and its launch was still running two minutes later.
**Diagnosis:**
- (1) `ros2 topic echo --once --field clock.sec` prints a `---` separator line after the value, which was compared as an integer.
- (2) The launch was started inside `{ …; } | sed …`. A pipeline element runs in a subshell without job control, so the `set -m` fix of TS-011 did not apply: `/proc/<pid>/status` showed `SigIgn …1001006` (SIGINT ignored), and `kill -INT` plus `wait` blocked forever.
- The checks had already completed; this session's leftover processes were stopped with SIGTERM (launch, then the orphaned `robot_state_publisher` and `parameter_bridge`).
**Fix / action:** the procedure takes only the first line of the echo output, and starts and stops the launch outside the logging pipeline (output collected in a file, sanitized afterwards), as `TEST-M2_procedure.sh` does.
**Verification:** TEST-M2-04 re-test 1.

### TS-018 — `/gz_ros_control` node runs on wall time (`use_sim_time` false)
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (TEST-M2-04 re-test 1: `use_sim_time` true on all 7 nodes)
**Symptom:** formal TEST-M2-04: `ros2 param get /gz_ros_control use_sim_time` returned False, while `controller_manager`, both controllers, `robot_state_publisher` and the bridge returned True. This deviates from REQ-M2-05.
**Diagnosis:** `/gz_ros_control` is the ROS node created by the gz_ros2_control system plugin. The plugin passes the `<parameters>` file (`controllers.yaml`) to its ROS context, which sets `use_sim_time` for the controller nodes listed there but has no entry for this node. No stamped output from this node was identified, and the controllers run on simulation time, so no functional effect was observed. The requirement covers every runtime node.
**Fix / action:** add `gz_ros_control: ros__parameters: use_sim_time: true` to `controllers.yaml`.
**Verification:** TEST-M2-04 re-test 1 (`use_sim_time` true on every node).

### TS-019 — TEST-M2-02 re-test 1: expected-difference list not updated for DEC-028
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (TEST-M2-02 re-test 2 PASS)
**Symptom:** TEST-M2-02 re-test 1 (revision `7b90453`) exited 1 ([log](evidence/M2/TEST-M2-02-R1_review.log)). The default variant passed completely, which confirmed the TS-016 fix. On the enabled variant, `TEST-M1-03_check.py` failed four assertions instead of the expected two: the two M1-scope ones, plus "left/right_wheel_link collision: cylinder …".
**Diagnosis:** DEC-028 deliberately replaces the wheel collision of the enabled (M2 simulation) model with a sphere. The M1 check asserts the M1 cylinder, so these two failures are the intended difference. `TEST-M2-02_control_check.py` passed and positively verified the sphere (radius 0.075 m, cylinder visual unchanged). The procedure and REQ-M2-02's wording had not been updated with DEC-028.
**Fix / action:** the procedure expects exactly those four named assertions to fail on the enabled variant, and REQ-M2-02 states the DEC-028 exception. The M1 checker, the model and the evidence are unchanged.
**Verification:** TEST-M2-02 re-test 2.

### TS-020 — TEST-M2-11 failed on its own, not yet indexed, log
**Date:** 2026-10-22   **Milestone:** M2   **Status:** Resolved (re-test 1)
**Symptom:** the first TEST-M2-11 run failed exactly one check: "TEST-M2-11_consistency.log: listed in docs/evidence/README.md" (log). Every configuration, decision and record check passed.
**Diagnosis:** the checker requires every file in `docs/evidence/M2/` to be indexed, including the log being written by the same run. `TEST-M1-08_records_check.py` excludes its own evidence for this reason; the M2 checker did not.
**Fix / action:** the checker skips `TEST-M2-11*.log` in the index check, and both logs are indexed.
**Verification:** TEST-M2-11 re-test 1.

### TS-021 — M3 feasibility-gate harness: launch ignored SIGINT, and an absolute-path xacro header broke the byte comparison
**Date:** 2026-11-03   **Milestone:** M3 (feasibility gate)   **Status:** Resolved (gate run 2 and the corrected static gate)
**Symptom:**
- (1) Gate run 1 ([log](evidence/M3/FEAS-M3_runtime_gate_run1.log)): "launch did not exit after SIGINT; sending TERM", then `gz sim -r -s --headless-rendering … gate_world.sdf` was still running, with `robot_state_publisher` and `parameter_bridge`.
- (2) The first static-gate attempt: `cmp` of the default expansion against `TEST-M1-02_amr.urdf` reported "differ: byte 173, line 3".
**Context:** throwaway gate scripts (sensors.md §6.1), not a TEST-M3 procedure. The gate's measurements in run 1 had completed (exit 0) before the shutdown step.
**Diagnosis:**
- (1) Same cause as TS-011: `gate_run.sh` started `ros2 launch` in the background of a non-interactive shell without job control, so it inherited an ignored SIGINT. Run 2 logs the launch's `SigIgn` as `0000000000000000` after the fix.
- (2) Same cause as TS-010: `diff` showed only xacro's "autogenerated by xacro from <path>" comment, because the script passed absolute paths. The model content was identical.
**Fix / action:**
- `gate_run.sh` uses `set -m`.
- `gate_static.sh` runs xacro from inside each workspace with the relative path, as the M1/M2 procedures do.
- This session's run-1 leftover processes (PIDs 23042–23044) were stopped with SIGINT. A `gz sim server` that was already running from an earlier user session (PID 11466, default partition) was not touched.
- The TEST-M3 procedures must keep both rules (job control; xacro from the workspace).
**Verification:**
- Gate run 2 ([log](evidence/M3/FEAS-M3_runtime_gate_run2.log)): "leftover gz sim processes: none".
- The corrected static gate ([log](evidence/M3/FEAS-M3_static_gate.log)): G5a and G5b byte-identical.

### TS-022 — A low-mounted `gpu_lidar` sees through the robot's own chassis
**Date:** 2026-11-03   **Milestone:** M3 (low-obstacle investigation, M3 plan §12)   **Status:** Accepted (simulator behaviour; documented constraint)
**Symptom:** in scratch run B (LiDAR trial-mounted at (0.160, 0, 0.120) m, in front of the chassis), the rear box at −1.5 m was "detected" ([log](evidence/M3/LOWOBS_run_B.log)). CALC-M3-04 says the chassis blocks all bearings beyond ±102°.
**Diagnosis:** the per-bearing ranges in run B show:
- ±102°: 0.17 m, the chassis front face. This matches the calculated edge at 101.3°.
- ±108–116°: −inf, a hit closer than `range_min` 0.12 m.
- ±120–138°: 0.21–0.27 m, the *inner* face of the wheel, reached after the beam crossed the chassis.
- ±144–180°: the 5 m walls, and the rear box at 1.51 m.

`gpu_lidar` is rendering-based. Geometry nearer than its near clip (`range_min`) is not drawn, and the inside faces of a box are not drawn from within (back-face culling). So a beam that starts inside or just in front of the robot body passes through it. A physical sensor would be blocked.
**Fix / action:** none to the model. Rules carried forward:
- Any LiDAR placed in or near the body band must have its blocked sector restricted or masked explicitly. Otherwise the simulation over-states coverage.
- The accepted 0.230 m plane (DEC-030) is above every body part and is not affected: 0 self-returns in gate G2 and in LOWOBS run A.
**Verification:** [LOWOBS_run_B.log](evidence/M3/LOWOBS_run_B.log), per-bearing dump; [LOWOBS_geometry.log](evidence/M3/LOWOBS_geometry.log), CALC-M3-04.

### TS-023 — M3 sensors model: M1/M2-scope assertions fail by design on the new sensor content
**Date:** 2026-11-03   **Milestone:** M3 (Task A, TEST-M3-02)   **Status:** Accepted (expected; declared before the formal run)
**Symptom:** while developing TEST-M3-02, two checks failed on assertions that encode the scope of earlier milestones:
- `TEST-M1-08_consistency_check.py`: "amr_ws/src/amr_description/urdf/amr.sensors.xacro: no mesh, gazebo, sensor, plugin, transmission, ros2_control elements". This is in addition to the TS-016 failure for `amr.ros2_control.xacro`.
- `TEST-M2-02_control_check.py` on the sensors-on M2 model: "6 links / 5 joints (M1 tree unchanged)" and "no <sensor> elements (no active sensors in M2)".
**Diagnosis:** the same category as TS-016. The M1 checker scans every Xacro source file for M1-scope content, and the M2 check asserts that M2 has no sensors. `amr.sensors.xacro` (DEC-034) is meant to add exactly two frames and two `<sensor>` elements. Every other assertion of both checks passed. The default variant is byte-identical to the M1 evidence. The sensors-off M2 model passes the M2 check completely.
**Fix / action:** `TEST-M3-02_procedure.sh` requires exactly these named assertions to fail and everything else to pass. The procedure and test plan §7.2 declared this before the formal run. The M1 and M2 checkers are unchanged. The standalone M1-08 baseline on the current tree is therefore 84 PASS plus 2 expected FAIL.
**Verification:** TEST-M3-02 re-test 1 ([log](evidence/M3/TEST-M3-02-R1_review.log)): "only the two expected M1-scope source-file assertions fail" and "only the two expected M2-scope assertions fail".

### TS-024 — TEST-M3-02: element comparison included XML tail whitespace
**Date:** 2026-11-03   **Milestone:** M3 (Task A)   **Status:** Resolved (TEST-M3-02 re-test 1 PASS)
**Symptom:** formal TEST-M3-02 ([log](evidence/M3/TEST-M3-02_review.log)) exited 1. Apart from the 4 expected TS-023 assertions, 5 new assertions of `TEST-M3-02_model_check.py` failed:
- default variant: "link lidar_mount_link identical with sensors on" and the matching top-level comparisons;
- M2 variant: the top-level comparison of `<gazebo reference="caster_link">`.
**Diagnosis:** each failing element is the last one before `</robot>` in the sensors-off variant. `xml.etree.ElementTree.tostring()` serializes the element's *tail*, the text after its closing tag. That tail is `'\n'` with sensors off and `'\n  \n  \n  '` with sensors on, because the conditional include adds content after it. Serialized without the tail, the elements were byte-identical, which was checked directly. The model was correct: the byte comparisons, `check_urdf`, `gz sdf` and the M1/M2 checks in the same run all passed.
**Fix / action:** the checker compares elements through `canon()`, which serializes an element with its tail removed and then restores the tail. Element content (attributes, children and their text) is still compared byte for byte. The model is unchanged.
**Verification:** TEST-M3-02 re-test 1 ([log](evidence/M3/TEST-M3-02-R1_review.log)): ALL STEPS PASSED.

### TS-025 — TEST-M3-03 harness: inline `robot_description` rejected, and `timeout` under `set -m` interrupted the script
**Date:** 2026-11-03   **Milestone:** M3 (Task A)   **Status:** Resolved (TEST-M3-03 re-test 1 PASS)
**Symptom:** the first formal TEST-M3-03 attempt ended with exit 130 during its first `tf2_echo` step. It had written no review log, and no check had run. `robot_state_publisher` had exited at start-up with "Couldn't parse parameter override rule". The temporary logs were preserved in [the attempt-1 log](evidence/M3/TEST-M3-03_attempt1_aborted.log).
**Diagnosis:**
- (1) The procedure passed the whole URDF as `--ros-args -p robot_description:=<URDF>`. rcl parses an inline override as a YAML value, and the multi-line XML document is not a valid override rule, so the node aborted.
- (2) The procedure uses `set -m` (TS-011, TS-021), so each background job has its own process group. `timeout -s INT` without `--foreground` runs its command in a new process group and signals that group. In a job-control shell this interrupt also reached the calling script, which was killed. Reproduced with a minimal script; `timeout --foreground` does not do this.
- The aborted run left its `joint_state_publisher` process group running. It was stopped with SIGINT, for that process group only. My unrelated `gz sim server` (PID 11466) was not touched.
- **Related harness side effect (TEST-M3-01):** `colcon version-check`, called from the repository root, created a `log/` directory there and printed "0.21.3:". The directory was deleted, uncommitted. The procedure now runs that call inside `amr_ws`.
**Fix / action:**
- `robot_description` is written to a parameters YAML file with `yaml.safe_dump` and passed with `--params-file`.
- Every `timeout` in the procedure uses `--foreground`.
- The leftover-process check uses the two jobs' process groups.
- The model and the checks are unchanged.
**Verification:** TEST-M3-03 re-test 1 ([log](evidence/M3/TEST-M3-03-R1_review.log)): ALL CHECKS PASSED, 0 ERROR/FATAL lines, 0 leftover test processes.

### TS-026 — `/scan` stamp-to-clock gap above 0.1 s in an informal TEST-M3-04 dry run
**Date:** 2026-11-03   **Milestone:** M3 (Task B)   **Status:** Open (monitor; formal TEST-M3-04 clean)
**Symptom:** in the informal dry run of `TEST-M3-04_procedure.sh` ([log](evidence/M3/TS-026_TEST-M3-04_dryrun_informal.log)), D3 failed for `/scan` only: max \|stamp − latest `/clock` at receipt\| 0.1150 s over 100 messages, against the 0.1 s limit. `/imu` and `/joint_states` stayed within 0.001 s, and D1, D2 and D4 passed. The same dry run showed an empty Gazebo command-line capture, a harness defect fixed before the formal run (`ps -o args= -g` → `pgrep -a -g`).
**Context:** robot at rest in `sensor_test.sdf`, headless rendering (`ogre2`, Intel GPU). Window: 2.0 s after the first scan (first scan stamp 8.0 s), then 10 s.
**Diagnosis (partial):** two scratch runs recorded the signed gap (`/clock` − stamp) per message ([diagnostic](evidence/M3/TS-026_scan_latency_diag.log)).
- Large gaps (0.12–0.33 s) appear only on the first three scans after start-up, with both reliable and best-effort subscriptions. Positive means the scan arrives after its stamp in simulation time, consistent with `gpu_lidar` rendering warm-up.
- Steady state (stamps ≥ 8 s, 653 scans): p50 0.003 s, max 0.014 s, no gaps between stamps, no receipt stalls.
- `/imu` showed one −0.097 s value at start-up: the checker's own `/clock` was stale briefly (an executor delay, TS-013 category).
- The cause of the dry-run value is not established: either a start-up transient that outlasted the 2.0 s settle, or a sporadic rendering delay. The dry-run checker did not record the sign or the stamp of the worst message.
**Fix / action:**
- No change to the D3 limit or the settle window (DEC-036).
- `TEST-M3-04_topics_check.py` prints the signed distribution, the count over the limit and the worst message's stamp per topic, so any recurrence can be classified.
- Tasks C–E: watch for recurrence. A formal D3 failure would be recorded as FAIL and diagnosed, not re-run away.
**Verification:** formal TEST-M3-04 ([log](evidence/M3/TEST-M3-04_review.log)): `/scan` max 0.0040 s, 0 messages over 0.1 s. Open until Tasks C–E show no recurrence, or the cause is found. Tasks C and D (2026-11-03): no recurrence observed; TEST-M3-05 to -09 do not check D3 and TEST-M3-04 was not re-run, so this is not new evidence for D3. Still open (Task E).

### TS-027 — Simulated IMU reports no linear acceleration from the robot's own motion (TEST-M3-08 D11)
**Date:** 2026-11-03   **Milestone:** M3 (Task D)   **Status:** Open: mechanism identified by the bounded investigation (2026-11-03); a correction needs a my decision (blocker for TEST-M3-08 D11; DEC-026, DEC-032 and DEC-036 unchanged)
**Symptom:** in the informal dry run of `TEST-M3-D_procedure.sh imu_motion 1`, D10 passed (gyro z +0.50009 vs ground truth +0.50000 rad/s), but D11 failed. While the robot accelerated to 0.5 m/s at a ground-truth +0.4999 m/s², the mean IMU accel x was −0.0010 m/s² (−100.2 %).
**Context:** `sensor_test.sdf`, spawn (0, −20) m, DART (gz-sim default), wheels driven by `gz_ros2_control` velocity commands (DEC-024 to DEC-026), IMU on the lumped `base_footprint` link (DEC-032, DEC-034).
**Diagnosis (cause not established):** a scratch run of the same stop profile recorded the IMU and ground truth sample by sample ([diagnostic](evidence/M3/TS-027_imu_linear_accel_diag.log)).
- **Speed-up:** the ground-truth speed rises linearly from 0 to 0.500 m/s in about 1.0 s (0.5 m/s², the DEC-025 limit).
- **Braking:** it falls from 0.500 to 0 in about 0.5 s (≈ 1.0 m/s²).
- **What the IMU reports:** accel x stays at noise level throughout both ramps (0.05 s means between −0.009 and +0.010 m/s²). The largest |ax| over 700 samples of the whole profile is 0.034 m/s², about 3.4 σ, which is noise alone. Accel z stays at +9.80 m/s².
- **Not affected:** the gyro (D10 within 0.02 %), gravity (TEST-M3-07 dry run: +9.7996 m/s²), and the noise model (S1–S4 pass on all six channels at rest).
- **Not a harness defect:** the same IMU samples and time base pass D10. The ground truth is independent of the IMU.
- **First hypothesis (superseded by the investigation below; disproved in this form):** the robot's velocity changes through the wheel-joint velocity commands and contact constraints. The physics engine may not count that as link acceleration, and the IMU linear acceleration is derived from link acceleration. Not checked against the gz-sim or DART source or documentation in this session.
**Fix / action:**
- **No change** to DEC-032, DEC-036 (D11 ± 20 %), the model, the physics or the harness. The formal TEST-M3-08 runs D11 as specified, and its result is recorded as measured.
- Held for a decision, with options: (a) a bounded scratch investigation of the cause and of a model-level remedy, (b) keep D11 as a recorded FAIL, (c) a decision to amend DEC-036 D11 / DEC-032 so that the simulated accelerometer's linear acceleration is a documented limitation.
- Consequence for later milestones: the simulated accelerometer cannot be used for longitudinal dynamics (e.g. IMU fusion in M4) until this is resolved.
**Formal result:** TEST-M3-08 ([log](evidence/M3/TEST-M3-08_review.log)), 3 valid runs: D11 FAIL in each (accel x +0.0012 / −0.0002 / −0.0004 m/s² against a ground-truth +0.5000 / +0.5000 / +0.4997 m/s²); D10 PASS in each.
**Bounded investigation (2026-11-03 18:36–18:50, decided by me; scratch only, production files and formal evidence unchanged; [log](evidence/M3/TS-027_investigation.log)):**
- **Source reading:**
  - The gz-sim IMU system copies the IMU entity's `LinearAcceleration` component into gz-sensors, which subtracts gravity.
  - gz-sim Physics fills that component from the engine frame data at the sensor offset; for DART this is the instantaneous `getLinearAcceleration()` of the current step.
  - gz_ros2_control does not touch IMU components. It writes the wheel `JointVelocityCmd` once per `controller_manager` cycle.
- **E1–E3 (scratch TestFixture, DART, wheel command updated every 1 ms step):** the IMU reports the true acceleration in every case.
  - Free fall: 0 against 0. Floating with a force: +0.496 against +0.489 m/s².
  - Full launch model, three drive methods (wheel velocity command, wheel torque, external force): speed-up +0.500 / +0.459 / +0.452 against true +0.500 / +0.460 / +0.451 m/s²; braking −1.003 / −0.990 / −0.972 against −1.000 / −0.991 / −0.973 m/s².
  - Unchanged by the `sensor_test.sdf` system set, by the y = −20 m spawn, and by enabling or not enabling the link acceleration component.
  - **Disproved:** an IMU configuration or attachment defect (H1); a DART acceleration-reporting limitation for constraint-driven motion (H2/H3); a frame or sign error (H5). The signs and the body x axis are correct in every run.
- **E4 (real launch):** the gz-transport `/imu` and the ROS `/imu` are identical sample by sample. Both read ≈ 0 (+0.0004 and −0.0004 m/s² against true +0.500 and −1.000 m/s²), so the bridge and the harness are excluded.
- **E5 (real `gz sim -r -s` server, `sensor_test.sdf`, runtime spawn, no gz_ros2_control):** wheels driven by the gz JointController with unsynchronized, wall-clock commands. The IMU responds: +0.68 against +0.50, and −1.19 against −0.99 m/s².
- **E6 (decisive; fixture, wheel command held for 10 ms as at the 100 Hz controller rate, phase swept 0–9 ms):**
  - Per-step physics acceleration: +4.999 m/s² on exactly one step in ten (80 of 801), about 0 on the others. The mean is still the true 0.5 m/s².
  - IMU mean at phase 0: +4.9994 m/s² (≈ 10×; it samples only the spike step).
  - IMU mean at phases 1–9: between −0.0014 and +0.0026 m/s², the TEST-M3-08 signature.
  - **Supported:** H4, a sampling (aliasing) effect.
- **E7 (bullet-featherstone):** the engine reports link acceleration 0 on every step, even with a smooth command, so its IMU never sees translational acceleration. It is not a remedy.
- **Mechanism (most likely cause; confirmed in the fixture, consistent with every launch observation, not instrumented step by step inside the launch):**
  1. `diff_drive_controller` updates the wheel velocity command every 10 ms (DEC-026, 100 Hz).
  2. DART enforces the commanded joint velocity as a constraint within one 1 ms step, so the chassis velocity changes in steps of 0.005 m/s. The acceleration is concentrated in one step per cycle (≈ 5 m/s² at the 0.5 m/s² limit) and is about 0 on the other nine.
  3. The Gazebo IMU samples that instantaneous acceleration once every 10 ms (DEC-032, 100 Hz), at a fixed phase of the same simulation-time grid. In the launch, that phase is one of the nine zero steps.
  4. The mean acceleration is physically correct; the 100 Hz samples alias it to ≈ 0.
- **Candidate corrections (scratch overlay workspaces; informal, one Task D `imu_motion` run plus one stop-profile probe each; not formal results):**

| Candidate | Accepted value changed | D11 harness | Probe speed-up (true +0.500) | Probe braking (true −1.000) | Per-sample signal |
|---|---|---|---|---|---|
| C1: IMU 1 kHz | DEC-032 (rate) | +0.5001 (+0.01 %) | +0.4998 | −0.9999 | Spike train: 0 or up to +5.5 / −7.5 m/s² (s 1.5–2.3) |
| C2: controller 1 kHz | DEC-026 (control rate) | +0.5186 (+3.72 %) | +0.5225 | −0.8335 (−17 %) | Alternating 0 / ≈ +1.0 m/s² (s 0.19–0.38) |

  - In both, D10 still passes, gravity reads +9.80 m/s², and the gyro is unaffected.
  - Neither yields a physically smooth per-sample acceleration.
  - **Not tested:**
    - C3: a continuous actuation model (wheel effort with a velocity loop or motor model; E2 shows that torque-driven motion gives a correct 100 Hz IMU). It changes the M2 control architecture (DEC-023/024).
    - C4: the IMU at 1 kHz averaged to 100 Hz, like the output-data-rate averaging of a MEMS IMU. The output rate stays 100 Hz, but the raw noise must become 0.01·√10 m/s² to keep the 0.01 m/s² output noise, and a filter node is needed.
- **Conclusion:** with every accepted value unchanged, D11 cannot pass; the aliasing is deterministic. The D11 criterion itself can be met unchanged, but only by changing another accepted engineering value or the control architecture (C1–C4), which is a my decision.

**C4 prototype and validation (2026-11-03 19:02–19:20; I selected C4 for a scratch prototype only, not production; [log](evidence/M3/TS-027_C4_validation.log)):**
- **Architecture:**
  - The Gazebo IMU runs at 1000 Hz on gz `/imu_raw`.
  - A gz-transport decimator outputs every raw stamp that is a multiple of 10 ms. Each output is the per-axis mean of the 10 raw samples in (t − 10 ms, t], with stamp t; orientation and frame are copied from the newest sample.
  - The output goes to gz `/imu`, then through the unchanged `sensor_bridge` to ROS `/imu` at 100 Hz.
  - This was tested in scratch overlay workspaces only; the M2 controller is unchanged.
- **Filter choice (offline study on recorded raw data, exact 100 Hz command hold, phases 0–9 ms):**

| Filter | D11 / braking error | Notes |
|---|---|---|
| F1: 10-sample block mean | 0.00 % noise-free; within ±0.36 % with noise, all phases | Integrated velocity exact (R0 0.0000, R2 ≤ 0.0042 m/s); outputs uncorrelated (lag-1 −0.01 to −0.03); a 100 Hz output reaches the full step 10–17 ms after the first physical step |
| F2: 20-sample sliding mean | Unbiased | Lag-1 correlation +0.46 to +0.52; about 5 ms more delay; output noise fits neither raw-noise setting |
| F3: 20 Hz first-order low-pass | −47 % to +65 % (phase-dependent) | Aliases the residual 100 Hz ripple into a bias; **rejected** |
| F0: current instantaneous sample | −100 % to +900 % | The failure being fixed |

  - F1 is a linear-phase FIR: its group delay is 4.5 ms relative to the output stamp, and it has nulls at 100 Hz and harmonics. Its output equals the mean physical acceleration of the last 10 ms.
- **Noise (rest):**
  - The raw 1 kHz samples are independent: |autocorrelation| ≤ 0.024 at lags 1–10 ms (expected about ±0.010).
  - **With the DEC-032 values applied to the raw samples (R1)**, the F1 output measures s/σ 0.30–0.33 on all six channels; S2 fails, in the fixture and in the launch (TEST-M3-07 harness).
  - **With raw σ × √10 (R2: 0.0316 m/s², 0.00316 rad/s; scratch only)**, the output measures s/σ 0.96–1.04 and S1–S4 pass (fixture and 2 launch runs).
  - Meeting DEC-032 at the output therefore needs a decision on what "noise" in DEC-032 means: the output noise, or the setting inside the simulated sensor.
- **Real launch, C4 R2 (informal):**
  - **Unchanged TEST-M3-08 harness, 3/3 runs:**
    - D11: +0.27 %, +0.18 %, +0.24 % (+0.5014 / +0.5010 / +0.5011 against +0.5001 / +0.5001 / +0.5000 m/s²).
    - D10: within 0.012 %.
  - **Stop-profile probe, 3 runs:**
    - Speed-up +0.4995 / +0.5002 / +0.4977 against ≈ +0.500 m/s².
    - Braking −0.9980 / −1.0013 / −1.0032 against −1.0002 / −1.0003 / −1.0006 m/s².
    - Cruise within ±0.0011 m/s²; gravity 9.80 m/s².
    - Per-sample ramp values track the wheel-derived 10 ms acceleration (correlation 0.63–0.96; residual s 0.011–0.035 m/s²), so the cycle-to-cycle variation is the controller's actual acceleration, not filter artefacts.
  - **Unchanged TEST-M3-07 harness, 2/2 runs:** D9 +9.7995 / +9.7997 m/s²; S1–S4 on all six channels.
  - **Unchanged TEST-M3-04 checker:** `/imu` 100.0000 Hz, stamps exactly 10 ms apart and strictly increasing; maximum |stamp − clock| 0.0010 s; `/scan` and `/joint_states` unchanged.
  - **Decimator:** 0 raw stamp gaps; every block had 10 samples except the first after start-up (9); RTF 0.999–1.000; 0 `[ERROR]` lines; 0 leftover processes.
- **Ground-truth artefact found:** a stationary link's recorded velocity is stale until motion resumes. Recorder side only; it does not affect the IMU.
- **Limits of this validation:**
  - Simulation only. The decimator is a Python prototype; the production form is undecided (a gz system plugin, a C++ node, or a sensor option).
  - The 4.5 ms group delay is stamp-relative and must be modelled or accepted by M4 fusion.
  - The IMU sensor's own update load rises 10×.
  - Encoder and LiDAR tests were not re-run on the overlay; only `/scan` and `/joint_states` were checked, by the TEST-M3-04 checker.

**Effective delay (prototype, 3 launch runs, [log](evidence/M3/TS-027_C4_delay.log)):** the controller's velocity steps fall at stamps 1 ms (150 of 200) or 2 ms (50 of 200, braking steps split over two physics steps) after each 10 ms boundary. Every run gave the same histogram. The step therefore appears in the output stamped 8–9 ms later (the 4.5 ms FIR group delay applies to evenly spread acceleration).
**Decision preparation (2026-11-03):** I finalized C4 as the preferred direction. The production decision is drafted as **DEC-038 (Proposed)**, with its design in `design/sensors.md` §8 and the conditional retest plan in `testing/test_plan.md` §7.3. Nothing is implemented.
**Verification:** DEC-038 accepted 2026-11-03 and implemented; the formal §7.3 re-run on the fixed build decides (`TEST_RESULTS.md`). The original TEST-M3-08 FAIL stays recorded.

### TS-028 — ImuDecimator refused to activate when the robot is part of the world file ("the world has no physics component")
**Symptom (2026-11-03, development run of the TEST-M3-14 (g) check):** in a minimal world that contains the robot model directly, the plugin logged `invalid configuration, NOT active (DEC-038): the world has no physics component`, and Gazebo `/imu` stayed silent. This happened in all three cases, including the valid control. In `sim.launch.py`, where the robot is spawned into a running world, the plugin was active.
**Diagnosis:** the first implementation validated in `Configure()`, which reads the world's `components::Physics` for the step size. The symptom shows that, for a model inside the world file, `Configure()` runs before that world component exists. A spawned model is configured after the world is complete, so the launch path did not show it. This is inferred from the symptom; the gz-sim source was not traced.
**Impact:** a future world that includes the robot directly would silently lose `/imu`. Nothing wrong would be published.
**Fix:** `Configure()` only reads the SDF parameters. The validation (physics step, the model's IMU sensor, rates) and the subscription happen once, at the first `PreUpdate()`, when every world and model component exists. The IMU system publishes its first sample in `PostUpdate`, so no raw sample precedes the subscription.
**Verification:**
- Development check, informal: before the fix all three cases refused ([log](evidence/M3/TS-028_dev_check_prefix.log)). After the fix ([log](evidence/M3/TS-028_dev_check_postfix.log)):
  - the valid case is active: `/imu` 400 messages from 4000 raw;
  - `raw_rate` 500 and IMU `update_rate` 100 are refused with a visible error naming the value, and `/imu` publishes 0 messages;
  - unit tests 0 failures.
- Formal: the TEST-M3-14 (g) run and the re-run of every plugin test on the fixed build are pending.

### TS-029 — Intermittent `gz sim` shutdown hang after SIGINT (sensor launches; upstream Gazebo deadlock, handled by DEC-039)
**Symptom (2026-11-03, DEC-038 pre-fix formal batch):** in 3 of 17 sensor-world launches, `gz sim -r -s --headless-rendering sensor_test.sdf` did not exit within 5 s of SIGINT. Launch escalated to SIGTERM; once (TEST-M3-04 R1) it also needed SIGKILL. The procedures require 0 `[ERROR]` lines, so TEST-M3-04 R1 and TEST-M3-14 failed, although all their measurement checks passed. In the TEST-M3-14 runs the ImuDecimator shutdown counter line was printed, so the plugin's destructor had completed.
**Investigation so far (rig [`TS-029_shutdown_rig.sh`](evidence/M3/TS-029_shutdown_rig.sh), [log](evidence/M3/TS-029_shutdown_rig.log); launch, wait 5 s after both controllers are active, SIGINT, time to `gz sim` exit; a snapshot of every thread's kernel wait channel 3 s after SIGINT):**

| Variant | Runs | Hangs |
|---|---|---|
| V1: current model (1 kHz IMU and ImuDecimator) | 12 | 0 (all exit in 0.2 s) |
| V2: 1 kHz IMU **without** the plugin (scratch overlay of `amr_description`) | 12 | 1 (run 5: 10.1 s, 3 `[ERROR]` lines) |

- **The plugin is not required for the hang.** V2 reproduced it without the plugin loaded.
- In the hung server, 48 `ruby` threads (the `gz sim` host process) waited on futexes. Also present and idle: DDS threads (the in-process ROS node of `gz_ros2_control`), GPU-driver and render-queue threads from `--headless-rendering`, and ZMQ threads. No thread was busy.
- `gdb` cannot attach: `kernel.yama.ptrace_scope` = 1, and the server is not a child of the debugger.
- Short runs (5 s of simulation after start) hang rarely. The formal runs that hung lasted 10–25 s.
**Investigation 2026-11-04 (rig 2, informal; [summary](evidence/M3/TS-029_rig2_summary.log), scripts `TS-029_rig2*.sh`):**
- Each run: the formal launch command, both controllers active, a **25 s** hold, SIGINT to the launch.
- If `gz sim` was still alive 3.5 s after SIGINT, the rig recorded a per-thread snapshot and **gdb stack traces**. The shell that started the launch `exec`s gdb, so gdb is an ancestor of `gz sim`. `kernel.yama.ptrace_scope` = 1 allows that; no system setting was changed.
- Batch 1 (V0, V1 and V2 interleaved) and batch 2 (V1S):

| Variant | Runs | Hangs |
|---|---|---|
| V0: original 100 Hz IMU, no plugin (`be788ca` xacro) | 20 | 0 |
| V1: current model (1 kHz IMU and ImuDecimator) | 20 | 0 |
| V2: 1 kHz IMU, no plugin | 20 | 1 (run 15: SIGTERM, then SIGKILL, 3 `[ERROR]` lines) |
| V1S: V1 with external ROS and gz subscribers during the hold, all exiting before SIGINT (as the formal harnesses) | 20 | 0 |

**Root cause (from the stack trace; [gdb](evidence/M3/TS-029_V2_run15_gdb.txt), [threads](evidence/M3/TS-029_V2_run15_threads.txt), [launch log](evidence/M3/TS-029_V2_run15_launch.log)): an upstream Gazebo deadlock.**
- **Main thread:** inside `SimulationRunner::Step` → `PublishStats` → `gz::transport::NodeShared::Publish` → zmq `poll`, SIGINT arrived.
  - `gz::common::SignalHandler::OnSignal` ran **on that thread** and called the server stop.
  - The stop reached `gz::sim::systems::SensorsPrivate::Stop()`, which waits in `std::thread::join()` for the render thread.
- **Render thread:** `SensorsPrivate::RenderThread` → `Manager::Remove` → `~GpuLidarSensor()` → gz-transport → `pthread_mutex_lock`, blocked.
- *Inference* (no debug symbols, so the mutex owner cannot be printed): the render thread waits for the gz-transport lock held by the interrupted `Publish` on the main thread, and the main thread waits for the render thread. SIGTERM goes through the same handler, so only SIGKILL ends it, as in TEST-M3-04 R1.
- The same class is reported upstream: [ros_gz #1011](https://github.com/gazebosim/ros_gz/issues/1011), "gz-common's signal handler stops the server while …", with rendering sensors. The proposed fix is in the server host ([ros_gz PR #1012](https://github.com/gazebosim/ros_gz/pull/1012)). Not confirmed in the installed release: gz-sim 8.15.0 (`ros-jazzy-gz-sim-vendor` 0.0.13), ros_gz_sim 1.0.24.

**Conclusions:**
- The plugin does not appear in the deadlocked stacks, and the hang occurs without it (V2, and V2 on 2026-11-03).
- The mechanism needs the `gpu_lidar` teardown and a SIGINT that lands while the main thread is inside gz-transport `Publish`. That is a race, which explains the intermittency.
- It is not fixable in project code.
- Rates: the rig gave 1 of 80. The 2026-11-03 formal batch gave 3 of 17, a higher rate that is not explained: external subscribers did not raise it (V1S 0/20). Untested factors: robot motion and longer harness runs.
- In TEST-M3-14 runs 1–2 (2026-11-03), `gz` ended on SIGTERM, not SIGKILL. That variant was not stack-traced.

**Resolution:** DEC-039 (decided 2026-11-04).
- A sensor-launch attempt whose measurements passed and whose shutdown shows only this signature is invalid and repeated within the attempt limit.
- The classifier is `evidence/M3/TEST-M3_launch_shutdown_classify.py`, tested on the run-15 log and five synthetic cases (2026-11-04, informal).
- Every other `[ERROR]` or leftover process still fails the attempt.
**Upstream check, 2026-11-04 (web search, at M3 closeout):**
- ros_gz #1011 ("gzserver segfaults or hangs on SIGINT", opened 2026-10-27, Jazzy binary 1.0.24 = this installation) is open, with no maintainer comment. Its reporter gives the same mechanism: gz-common's SIGINT handler stops the server while another thread tears it down, and with rendering sensors the Sensors system's stop waits for the render thread. The reporter's rates are higher (segfault 5 of 6 on `sensors_demo.sdf`, hangs on `shapes.sdf` 2 of 6) and its host is the `GzServer` ROS node.
- ros_gz PR #1012 (restore the ROS signal handlers so the gz-common handler is never active; stop and destroy the server on its own thread) is open and unreviewed. The author reports 8 of 8 clean exits with it. No release contains it.
- gz-sim PR #2025 ("Prevent deadlock in sensors system", merged 2023-07 into gz-sim7; presence in gz-sim 8.15.0 not checked) is a different deadlock: steady-state stepping, not shutdown.
- No other report of this exact signature was found.
- **Correction (same day): PR #1012 does not apply to this project.** Our `sim.launch.py` runs the Gazebo CLI (`gz sim -r -s --headless-rendering`, `sim.launch.py` line 62), not the ros_gz `GzServer` node that #1011/#1012 concern. #1012 works around the bug only in that node, by keeping gz-common's handler from running. In our process the handler still runs.
- **Mechanism, restated from the run-15 trace:** SIGINT is delivered to the main thread while it is inside gz-transport `Publish` (`SimulationRunner::PublishStats`, frames 17–19). gz-common runs the stop callback in that signal context (frames 8–10), and `SensorsPrivate::Stop` joins the render thread. The render thread waits in `~GpuLidarSensor` for a gz-transport mutex (Thread 62), presumably the one the interrupted `Publish` holds. The thread deadlocks on itself: heavy work in a signal handler. The fix belongs in gz-common/gz-sim (defer the stop out of signal context).
- **Candidate project-side mitigation (not tested):** gz-sim 8 offers a non-signal stop, the `/server_control` service with `stop: true` (`gz.msgs.ServerControl` field 6). A procedure could request that stop first and send SIGINT only as a fallback. Rig evidence would be required, and a procedure change needs a recorded decision (it touches the DEC-039 shutdown handling). Statistical note: at the rig rate of 1 in 80, 0 hangs in 80 runs proves nothing; a comparison needs a few hundred runs, or the formal-batch conditions (3 of 17).
**Decision (DEC-039 amendment, 2026-11-04):** keep DEC-039; defer the `/server_control` candidate, with a stated trigger; report upstream.
**Origin: upstream Gazebo, not project code.** The evidence:
- every frame of the deadlock is in Gazebo libraries (gz-common `SignalHandler`, gz-sim `SensorsPrivate`, gz-sensors `GpuLidarSensor`, gz-transport);
- no project code (the `amr_gazebo_plugins` ImuDecimator) appears in any deadlocked stack;
- the hang reproduces with the project plugin removed (rig 2 variant V2, and on 2026-11-03).
**Reported upstream:** [gazebosim/gz-sim#4173](https://github.com/gazebosim/gz-sim/issues/4173) (opened 2026-11-04 from my account, ; the exact text is [evidence/M3/TS-029_upstream_issue.md](evidence/M3/TS-029_upstream_issue.md)).
- Before posting, a Gazebo-only reproduction was tried (stock systems plus one static `gpu_lidar`, plain `gz sim`, no ROS): **0 hangs in 300** ([log](evidence/M3/TS-029_minimal_300runs.log), [world](evidence/M3/TS-029_minimal_gpu_lidar_sigint.sdf), [loop](evidence/M3/TS-029_minimal_sigint_loop.sh)). The report says so. The likely reason is the lower gz-transport traffic of that world.
- New detail from the run-15 trace, included in the report: the gz-transport discovery threads (`OnNewDisconnection`, `OnNewSrvDisconnection`) wait on the same mutex (`0x5e090185eb30`) as the render thread, and no running thread holds it. This supports the conclusion that the interrupted `Publish` on the main thread holds it.
- Follow the issue at each session start and at each environment update (Deferred). Retire DEC-039 once a fixed release is installed.
**Addendum 2026-11-13: GUI mode (TEST-M4-10 preparation).**
- A `SHOW=1` (Gazebo GUI) option was tried for the M3 sensor procedures. Smoke run `TEST-M3-D imu_rest` with the GUI ([log](evidence/M3/TS-029_gui_imu_rest_smoke.log)) passed every measurement criterion but the launch log had `process[gz-5] failed to terminate '5' seconds after receiving 'SIGINT', escalating to 'SIGTERM'` followed by `process has died [..., exit code 1, cmd 'gz sim -r .../sensor_test.sdf']`. The DEC-039 classifier accepts the TS-029 signature only with exit code −9 or −15, so it reported OTHER (attempt fails).
- Informal rig [`TS-029_gui_rig.sh`](evidence/M3/TS-029_gui_rig.sh) (launch, wait for odometry, 5 s, SIGINT): GUI + sensors 6/6 clean, GUI without sensors 4/4 clean, all stopped in under 4 s (rig logs not kept). Overall about 1 hang in 12 GUI + sensor launches, similar to the headless TS-029 rate.
- **Hypothesis (not verified; no stack trace of the hung process was captured):** the same TS-029 deadlock; in GUI mode `gz sim` (server and GUI in one command, no `-s`) exits with code 1 after SIGTERM instead of dying by the signal.
- **Decision (2026-11-13):** DEC-039 is **not** extended. Sensor procedures (TEST-M3-D, -11, -14) stay headless; only the M2 procedures, which have no sensors, get the `SHOW=1` GUI option.

**Status:** open (upstream); handled under DEC-039. Re-check upstream at each environment update.

### TS-030 — Truncated `Exception in thread Thread-1 (spin)` in harness output after the measurements (TEST-M3-09 R2, TEST-M3-14 R1; cause suspected, not reproduced; resolved by the DEC-040 (c) fix)
**Symptom (2026-11-04 formal re-run):**
- 2 of 11 Task D / TEST-M3-14 harness runs printed `Exception in thread Thread-1 (spin):` and at most the first two traceback lines: TEST-M3-09 R2 attempt 3 ([log](evidence/M3/TEST-M3-09-R2_review.log)) and TEST-M3-14 R1 attempt 3 ([log](evidence/M3/TEST-M3-14-R1_review.log)). The same truncated lines are in the scratch log `evidence/M3/TS-027_C4_delay.log` (2026-11-03).
- Both attempts passed every criterion with harness exit 0. In the TEST-M3-14 log the lines appear above the harness header only because stdout to a file is block-buffered and flushed at exit, while stderr is unbuffered.

**Diagnosis.** Established facts first, then the suspected cause. The exception type and full traceback were **never captured**, so the cause is not confirmed.
- Every harness since M2 (`TEST-M2_motion_measure.py`, `TEST-M3-D_imu_encoder_measure.py`, `TEST-M3-14_imu_decimation_check.py`) runs `SingleThreadedExecutor.spin()` in a daemon thread, then tears down with `ex.shutdown()` → `destroy_node()` → `rclpy.try_shutdown()` → `os._exit(code)`. `os._exit` is deliberate (gz-transport aborts in normal interpreter teardown, M2) and kills the thread mid-traceback, hence the truncation.
- In the installed rclpy (Jazzy), `Executor.shutdown()` sets `_is_shutdown = True` and then tests `if not self._is_shutdown:` before `_work_tracker.wait()`, so it never waits for a running `spin()`; it then destroys the executor's guard condition. Observed: in a scratch run of the unchanged TEST-M3-14 harness wrapped to report thread state, the spin thread was still alive after `main()` returned in 3 of 6 runs.
- **Suspected cause (not reproduced):** the spin thread wakes after the guard condition, node or context has been destroyed and raises. Reproduction attempts: 0 exceptions in 6 wrapped Gazebo runs and 0 in 30 minimal rclpy runs. The two facts above make it plausible, but other teardown failures in the harness thread are not excluded.
- Measurements unaffected (evidence, not the cause): had the spin thread died during recording, callbacks would have stopped and the sample counts would be short (or the harness would report INVALID for missing data). Sample counts of the affected attempts equal those of clean attempts (TEST-M3-14 R1 attempt 3: ROS imu 1961, raw 19588, vs 1963 / 19594 and 1963 / 19617), and in TEST-M3-09 R2 the line follows the harness `# result:` line. No formal criterion (harness exit code, launch-log `[ERROR]` lines, leftover processes) reads harness stderr.

**Resolution:** none in the formal batch; the runs stand as PASS and the anomaly is recorded here. Proposed harness fix, deferred to the DEC-040 test-automation step (a harness change, so it is followed by a re-run of the affected tests): spin with a stop flag (`while not stop: ex.spin_once(timeout_sec=0.05)`), set the flag, `join()` the thread, and only then shut down the executor, node and context. Before the fix, capture the full traceback (a `threading.excepthook` that writes it out before `os._exit`) to confirm or reject the suspected cause; the fix is verified only when that capture shows no spin-thread exception over the affected tests.
**Further diagnosis, 2026-11-04 (after M3 closeout; informal, scratch only, not committed):**
- Source check, `/opt/ros/jazzy/lib/python3.12/site-packages/rclpy/executors.py` lines 279–298: `shutdown()` sets `_is_shutdown = True` and then tests `if not self._is_shutdown`, which is now always false. It therefore never waits for a thread still inside `spin()`, and goes straight on to destroy the guard condition that thread may be waiting on. This confirms the window exists in the installed rclpy.
- Reproduction without Gazebo (the harness teardown order: `spin()` in a thread, then `shutdown`, `destroy_node`, `try_shutdown`, `join`): 0 thread exceptions in 300 teardowns (one 1 kHz timer), and 0 in 1000 under heavier load (4 timers at 2 kHz, 4 busy subscriptions, random stop time). The stop-flag order (`spin_once` loop, set the flag, join, then shut down) also gave 0 in 300.
- Conclusion: the race window is real, but it does not trigger easily. The two observed tracebacks need something present only in the Gazebo runs (message rate and size, CPU load from rendering, or the `os._exit` timing). The cause stays **suspected, not reproduced**. The stop-flag fix closes the window whatever the trigger is, so it stays the DEC-040 (c) action.
**Fix implemented, 2026-11-04 (DEC-040 (c), REQ-TA-01):** `M2.Spinner` in `evidence/M2/TEST-M2_motion_measure.py`, used by the four formal harnesses. TEST-TA-01 PASS (1000/1000 without Gazebo). Each formal run now prints `# TS-030 check: spin thread ...`. TS-030 is closed only if TEST-TA-04 shows "ended cleanly" in every run.
**Verification, 2026-11-04 (TEST-TA-04):** "ended cleanly" in 55 of 55 formal harness runs, 11 of them in the Task D / TEST-M3-14 harnesses where TS-030 appeared (2 of 11 before the fix). Limitation: 0 of 11 would have about an 11 % chance even without the fix ((9/11)^11), so the evidence is that the window is closed, not that the trigger was the one suspected.
**Reopen trigger:** any formal run that prints a spin-thread state other than "ended cleanly", or a thread traceback. The Spinner writes the full traceback before `os._exit`, so a recurrence would also identify the cause.
**Status:** **Resolved** 2026-11-04 by the DEC-040 (c) fix, under the pre-agreed criterion. The original cause stays suspected, not confirmed (the old order's traceback was never captured). Earlier status: open; cause suspected, not confirmed. The exception is raised in the harness's own Python thread (not in the robot model, the plugin or Gazebo), and the formal PASS verdicts rest on the criteria and the complete sample counts, not on the suspected cause. Scratch diagnostics were not committed.

### TS-031 — TEST-M2-11 R3 FAIL: the records checker counted a git-ignored `__pycache__` as an unindexed evidence file
**Symptom (2026-11-04 16:13):** TEST-M2-11 R3 (log): 111 PASS, 1 FAIL `__pycache__: listed in docs/evidence/README.md`, exit 1.
**Diagnosis:** the Task D harness loads `TEST-M2_motion_measure.py` through `importlib`, so Python writes `docs/evidence/M2/__pycache__/` (created 15:57:46, the start of TEST-M3-07 R2). The folder is git-ignored (`.gitignore`: `__pycache__/`) and never committed. The checker's section 3 lists the folder with `os.listdir` and so treated it as evidence. It never occurred before because TEST-M2-11 R2 predates the M3 harnesses. A checker defect (it measured the wrong thing), not a records inconsistency.
**Fix:** the checker skips exactly the name `__pycache__`; every other file in `docs/evidence/M2` must still be indexed. Deleting the cache was rejected: the next harness run recreates it. The R3 FAIL log is kept.
**Verification:** TEST-M2-11 R4 PASS, 111 checks (log).
**Status:** resolved.

### TS-032 — TEST-M3-12 FAIL: the TEST-M3-10 execution record did not follow the record convention
**Symptom (2026-11-04):** TEST-M3-12 (log): 231 PASS, 1 FAIL `TEST-M3-10: 1 summary row(s), executed, has no execution record`, exit 1.
**Diagnosis:** M3 execution records in `TEST_RESULTS.md` start with a bold test ID (`**TEST-M3-nn` or `- **TEST-M3-nn`), which is how a reader or the checker finds the record of a test. The new TEST-M3-10 record ended with `**Result:** TEST-M3-10 **PASS…**` instead. A records defect introduced while writing the record, caught by the checker as intended; the configuration and every other record passed.
**Fix:** the result line reads `**TEST-M3-10:** **PASS (observed by me)**.` (wording and result unchanged). The FAIL log is kept.
**Verification:** TEST-M3-12 R1 PASS (log).
**Status:** resolved.

### TS-033 — Runner suite `static` included the superseded standalone TEST-M1-08 (suite-definition defect)
**Date:** 2026-11-04   **Context:** DEC-040, TA Task 2, TEST-TA-03   **Status:** Resolved
**Symptom:** the first run of `tools/run_suite.py static TA03` ended with exit 1. Entry TEST-M1-08 exited 1 with `# overall: AT LEAST ONE STEP FAILED`. The runner classified it FAIL, correctly: its exit code and overall line agree.
**Diagnosis:**
- The failing assertion is the M1-scope source-file check "no mesh, gazebo, sensor, plugin, transmission, ros2_control elements". It fails for `amr.ros2_control.xacro` (M2) and `amr.sensors.xacro` (M3) by design (TS-016, TS-023).
- The step gave 84 PASS plus exactly those 2 FAIL, the TS-023 baseline. Every other M1-08 step exited 0.
- Standalone TEST-M1-08 is an M1-milestone procedure. Since M3 its valid content is run inside TEST-M3-02, which requires exactly these two failures.
- The plan (§5/§7) listed it as a GPU-free check without checking this. The defect is in the suite definition, not in the runner or the robot code.
**Fix:** TEST-M1-08 removed from the `static` suite, with a comment in `tools/run_suite.py`. The CI specification (plan §7) is corrected the same way: M1 byte identity and the M1 checker run through TEST-M3-02. The M1-08 procedure and checker are unchanged.
**Verification:** TEST-TA-03 R1 (`static` suite, tag TA03R1), recorded in `TEST_RESULTS.md`.

### TS-034 — First CI run: TEST-M3-02 step 2 could not find the M2 baseline commit (shallow checkout)
**Date:** 2026-11-04   **Context:** DEC-040, TA Task 4, TEST-TA-05, CI run 1 (GitHub run 41837281025, `6f4a7b0`)   **Status:** Resolved
**Symptom:** the `ci` suite (tag CI1a1) gave TEST-M3-01 and -13 PASS-candidate and TEST-M3-02 exit 1, `# overall: AT LEAST ONE STEP FAILED`; the runner classified it FAIL (exit code and overall line agree). Step 2 printed `fatal: not a valid object name: 5b9332e`, then an empty baseline URDF ([log](evidence/M3/TEST-M3-02-CI1a1_review.log)).
**Diagnosis:**
- `actions/checkout` fetches only the pushed commit by default (`fetch-depth: 1`). TEST-M3-02 step 2 compares the current M2 model with the M2 baseline `5b9332e`, extracted by `git archive`, which needs that commit in the clone.
- All other output matches the local TEST-TA-03 R1 run: the FAIL lines of steps 1 and 3 are identical (the declared expected M1/M2-scope assertions). The only difference is step 2's exit code.
- The procedure is correct; the defect is in the workflow's checkout configuration.
**Fix:** `fetch-depth: 0` in `.github/workflows/ci.yml`, so that the full history is present. The procedure is unchanged.
**Verification:** CI run 2 (GitHub run 41837931388, `477c880`): TEST-M3-02 all steps passed, step 2 identical to `5b9332e` ([log](evidence/M3/TEST-M3-02-CI2a1_review.log)). Recorded with TEST-TA-05 in `TEST_RESULTS.md`.

### TS-035 — Odometry and joint_states stamps of the same control cycle differ by 1 ms in about 7 % of the cycles
**Date:** 2026-11-13   **Context:** M4 Task A, TEST-M4-03 checker dry run (informal, scratch output, revision `557141e`)   **Status:** Resolved (checker design); cause in ros2_control not investigated
**Symptom:** the first draft of the TEST-M4-03 checker paired odometry with joint_states by equal stamps. It compared 647 of 698 messages and failed its ≥ 95 % coverage check, while every compared pose matched to 0.000000 mm.
**Diagnosis (measured, one 14 s recording):**
- joint_states arrive at 100 Hz with stamp spacings of 9, 10 and 11 ms (830/310/310 intervals); no sample was missing.
- 52 of 700 odometry stamps have no equal joint_states stamp. Each is exactly 1 ms earlier than a joint_states stamp, and the pose recomputed from that joint_states sample equals the published pose exactly (0.0 mm), while the previous sample (10 ms earlier) gives up to 2 mm. So both messages come from the same control cycle and the same wheel positions; only their stamps differ.
- Why the two controllers (`joint_state_broadcaster`, `diff_drive_controller`) stamp the same cycle 1 ms apart was not investigated (ros2_control 4.48.1, gz_ros2_control 1.2.20). It does not affect the odometry pose.
- Hypothesis, not verified: the same 1 ms offset could bias the published twist, which divides each cycle's travel by the stamp interval. The dry-run twist was +0.2 % high in both straight and rotation, and the formal TEST-M4-08 confirmed +0.17 to +0.22 % in all six cases (bound ± 2 %).
**Fix:** the checker pairs each odometry message with the first joint_states sample in [t_odom, t_odom + 1.5 ms] and prints how many pairs are shifted. The criteria are unchanged (≤ 1 mm, ≤ 0.01°, ≥ 95 % compared). A negative check with b = 0.404 m (1 % wrong) fails as expected (4.99 mm, 0.68°).
**Verification:** the dry run then compared 699 of 699 messages, max difference 0.000000 mm and 0.00000000°. Formal result: TEST-M4-03 in `TEST_RESULTS.md`.

### TS-036 — Demonstration capture: covered windows and processes left from the previous scene (2026-11-13)
**Symptoms:** (1) the TEST-M4-09 RViz screenshots were partly covered by the Gazebo window, cutting off the odometry trail; (2) in the first demo batch the RViz RobotModel and TF displays showed error status and, in one scene, no robot; (3) one scene waited indefinitely at its end.
**Diagnosis (evidence: `xwininfo -root -tree`, `pgrep -af`):**
- `xwd` and `ximagesrc` capture only the visible pixels of a window. RViz (1280 px) opened at x = 640 on the 1920 px monitor, over Gazebo (x = 50–1050), and mutter ignores a requested position (`Window Geometry X/Y`, `-qwindowgeometry`).
- The demo script lacked `set -m`. Without job control, background jobs of a non-interactive shell ignore SIGINT (as TS-011), so the M1 scene's `robot_state_publisher`, `joint_state_publisher_gui` and RViz survived the teardown. On the same ROS domain they published a second robot description and wall-clock joint states into every later scene.
- A bare `wait` in a scene without recorders waited for the launch itself.
- Recordings: the first 2.1–2.6 s of an `ximagesrc` capture of the Gazebo window repeat the window content from before the recording (a camera view set 3 s earlier appears only then, as a jump). Cause inside XWayland/ximagesrc not investigated.
**Fix:** RViz is 860 px wide and started after the Gazebo window exists, so mutter places it beside Gazebo (verified: RViz at x = 1060). `tools/demo_capture.sh` uses `set -m`, signals each process group, escalates to `gz sim` directly, refuses to start while any ROS/Gazebo process exists and exits 1 if anything is left. All pictures of the affected runs were deleted and re-captured (user instruction: no imperfect pictures). TEST-M4-09 was re-run (R1) for clean pictures. Stale start: `tools/webm_trim.py auto` finds the jump in the Gazebo video and cuts both videos there; callers wait 3 s after starting a recording before any motion.
**Verification:** the re-captured pictures were reviewed one by one; every scene ended with 0 leftover processes (`docs/gallery/README.md`).

### TS-037 — `colcon version-check` hung 10 min in TEST-M3-01 (stalled PyPI connection, 2026-11-13)
**Symptom:** TEST-M4-10 static suite, tag M410: the TEST-M3-01 entry ran 627 s instead of about 2 s. The procedure's informational line `# colcon-core <version>` runs `colcon version-check`, which was blocked (`wait_woken`) on an established IPv6 TLS connection to PyPI (`[2a04:4e42::223]:443`) that delivered no data; it reads without a timeout. `curl` to pypi.org from the same shell answered at once, so the stall was transient on the network side.
**Action:** only the hung `colcon version-check` process was ended (SIGTERM); the build itself then ran normally. The M410 log therefore shows an empty `# colcon-core` version; no criterion reads that line, and the run was repeated (M410R1, M410R2).
**Fix, first attempt:** `timeout 30 colcon version-check`. The clean re-run M410R1 hit the timeout too (the stall persisted from Python while `curl` worked), so its log again has an empty version.
**Fix:** the procedure reads the installed version locally (`python3 -c 'import colcon_core; print(colcon_core.__version__)'`, 0.21.3, the same value as earlier runs); no network access. Re-run M410R2.
**Status:** fixed (procedure); the network cause is outside the project.
