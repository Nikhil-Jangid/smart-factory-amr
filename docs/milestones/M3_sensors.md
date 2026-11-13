# M3 — Sensors: Milestone Plan and Record

**Status:** **Complete** (2026-11-04; closed; in progress since 2026-11-03). Every exit criterion in §10 is met: TEST-M3-01 to -14 PASS. History: I finalized the revised Task breakdown (§7.1) on 2026-11-03; Task A was implemented and verified (TEST-M3-01 to -03 PASS, the last two on re-test 1; [TEST_RESULTS.md](../../TEST_RESULTS.md) § M3). Task B (world, bridge, launch) was implemented and verified the same day (TEST-M3-04 PASS). Tasks C and D ran in parallel on 2026-11-03: **Task C is complete** (TEST-M3-05, -06 PASS). Task D: TEST-M3-07 and -09 PASS, TEST-M3-08 FAIL on D11 (TS-027, the simulated accelerometer did not report the robot's acceleration). DEC-038 corrected it, and **Task D is complete** since the formal re-run of 2026-11-04 (§7.3, all PASS; one TS-029 attempt invalid under DEC-039). Task E (2026-11-04): TEST-M3-10 PASS (observed by me), -11 PASS, -12 R1 PASS.

**History:** the plan was **Proposed** first. The plan was drafted on 2026-11-03, and I decided OPEN-03 and OPEN-13 to -18 the same day (DEC-030 to DEC-036). The milestone **stays Proposed until the feasibility gate (step 1, sensors.md §6) passes** and I have reviewed its results and the Task breakdown. No sensor implementation before that. **Feasibility gate G1–G6: PASS on 2026-11-03** ([sensors.md §6.1](../design/sensors.md)). **OPEN-03 was reopened on 2026-11-03** for a low-obstacle architecture comparison (§12), and **closed the same day by DEC-037**: option 3, with DEC-030 unchanged and the depth camera assigned to M8. The revised Task breakdown (§7.1) was then presented for review.

## 1. Purpose
Give the M2 robot the simulated sensors that the later milestones need:
- a 2D LiDAR for M5 SLAM and M8 obstacle avoidance;
- an IMU for M6 localization;
- a verified wheel-encoder signal for M4 odometry.

Each sensor's data must reach ROS on the correct topic, frame and time base, and must be quantitatively checked against Gazebo ground truth. The LiDAR scan must also be visible in RViz. Background on each sensor and on how Gazebo simulates sensors: [../design/sensors.md](../design/sensors.md) §1.

## 2. Scope
Derived from `ROADMAP.md` § M3, `docs/architecture/ros_architecture.md` §3, frames_and_tf.md §5, DEC-014, DEC-019 (OPEN-03), CALC-M1-14 and the blind-zone item.

**In scope:**
| Item | Authoritative source |
|---|---|
| Simulated 2D LiDAR (`/scan`, `laser_frame`) | ROADMAP M3; frames_and_tf.md §5; DEC-014 |
| Simulated IMU (`/imu`, `imu_link`) | ROADMAP M3; frames_and_tf.md §5 |
| Wheel encoders: representation decision and quantitative check | ROADMAP M3; M2 plan §2 (deferred encoder model) |
| Sensor topics bridged to ROS on simulation time | ROADMAP M3; ros_architecture.md §3 |
| RViz visualization of the scan and the sensor frames | ROADMAP M3 |
| OPEN-03 resolution (bracket and sensor frame); blind-zone characterization (the M3 part) | DEC-019; CALC-M1-14 |
| Sensor test world with known targets | sensors.md OPEN-16 |
| M1/M2 baseline preservation and an M2 motion regression with sensors on | DEC-023 pattern |

**Out of scope (later milestones):**
- Odometry accuracy and error budgets, and fusing encoders into odometry (M4).
- SLAM (M5); IMU fusion / EKF (M6); Nav2 and the footprint (M7).
- Blind-zone *mitigation* and obstacle avoidance (M8); the factory world (M9).
- Cameras or depth sensors: the low-obstacle depth camera is an **M8** sensor (DEC-037), not an M3 Task. AprilTags (ideas list).
- Sensor bias and drift models, unless selected under OPEN-14.
- Payload, caster arm, SVG drawing, SPDX headers.
- Physical sensors and hardware (M13).

## 3. Design baseline
- Model values: `amr_properties.xacro` (owner); [../design/mechanical_geometry.md](../design/mechanical_geometry.md), [../design/mass_inertia.md](../design/mass_inertia.md), [../design/frames_and_tf.md](../design/frames_and_tf.md).
- **M3 sensor analysis (OPEN-03, OPEN-13 to -18; CALC-M3-01 to -03): [../design/sensors.md](../design/sensors.md).**
- M2 control baseline: DEC-023 to DEC-029; [../design/motion_control.md](../design/motion_control.md).
- Requirements: [../requirements.md](../requirements.md) § M3. Tests: [../testing/test_plan.md](../testing/test_plan.md) §7.
- Environment and installed sensor software: [../environment.md](../environment.md); sensors.md §2. Plugins are installed but **not yet exercised**.

## 4. Design items
| ID | Item | Status | Proposal (sensors.md §4) | Needed by |
|---|---|---|---|---|
| OPEN-03 (from M1) | LiDAR bracket and sensor frame | **Decided: DEC-030** (2026-11-03); reopened and **closed by DEC-037** (2026-11-03; DEC-030 confirmed unchanged) | Bracket unchanged; `laser_frame` +0.030 m above it; scan plane 0.230 m (CALC-M3-01); finalize after TEST-M3-06 | Step 2 |
| OPEN-13 | LiDAR model | **Decided: DEC-031** (2026-11-03) | `gpu_lidar`, 360°/360 samples, 0.12–12 m, 10 Hz, σ 0.01 m, `/scan` | Step 2 |
| OPEN-14 | IMU model and placement | **Decided: DEC-032** (2026-11-03) | `imu_link` at the `base_link` origin, 100 Hz, σ_gyro 0.001 rad/s, σ_acc 0.01 m/s² (simulation assumptions), zero bias, `/imu` | Step 2 |
| OPEN-15 | Wheel-encoder representation | **Decided: DEC-033** (2026-11-03) | `/joint_states` as the ideal encoder; quantizing node deferred (CALC-M3-03) | Step 5 |
| OPEN-16 | Integration architecture | **Decided: DEC-034** (2026-11-03) | `use_sensors` Xacro option (default off, M1 byte-identical); massless sensor links (9.4 kg unchanged); `sensor_test.sdf` world; launch args `world`/`sensors` (defaults keep M2); bridge YAML | Steps 2–3 |
| OPEN-17 | IMU visualization in RViz | **Decided: DEC-035** (2026-11-03) | No IMU plugin; LaserScan + TF only (installing `rviz_imu_plugin` is the alternative) | Step 6 |
| OPEN-18 | M3 test criteria | **Decided: DEC-036** (2026-11-03) | Deterministic checks separated from statistical noise checks; specification sensors.md §7 | Step 4 |

Decided values: DEC-030 to DEC-036 in `DECISIONS.md` (summaries in sensors.md §4; test specification sensors.md §7). DEC-032 changed the IMU noise to σ_ω 0.001 rad/s and σ_a 0.01 m/s², labelled as simulation assumptions. DEC-034 added the condition that the generated SDF has no zero-mass or zero-inertia link.

## 5. Entry criteria and dependencies
- M2 complete (2026-11-03): ✅.
- I decide OPEN-03 and OPEN-13 to -18: ✅ 2026-11-03 (DEC-030 to DEC-036).
- The feasibility gate (sensors.md §6, G1–G6) passes, or its failure is resolved. Then I review the results and the Task breakdown.

## 6. Architecture (DEC-034)
```
amr_description/urdf/amr.urdf.xacro
  └── xacro:if use_sensors → amr.sensors.xacro
        lidar_mount_link ──fixed (0,0,+0.030)──> laser_frame   [gpu_lidar → gz topic]
        base_link ──────────fixed (0,0,0)───────> imu_link      [imu → gz topic]
amr_bringup/
  worlds/sensor_test.sdf      (empty.sdf systems + sensors(ogre2) + imu; static targets)
  config/sensor_bridge.yaml   (/scan, /imu: GZ → ROS)
  launch/sim.launch.py        (+ args world, sensors; defaults reproduce M2)
  rviz/sensors.rviz           (fixed frame odom; RobotModel, TF, LaserScan)
```
Data path: Gazebo sensor → Gazebo Transport → `ros_gz_bridge` → ROS topic (sim-time stamped) → RViz / tests. The encoder path is the M2 path: `gz_ros2_control` → `joint_state_broadcaster` → `/joint_states`.

## 7. Implementation sequence and Tasks
| Step | Work | Tests | Proposed Task | Depends on |
|---|---|---|---|---|
| 1 | Feasibility probe in scratch: `gpu_lidar` headless + GUI, RTF, `gz_frame_id`, pose after lumping, gravity (sensors.md §6) | — (findings recorded) | — (done as the feasibility gate, 2026-11-03, G1–G6 PASS, sensors.md §6.1; GUI rendering left to TEST-M3-10) | Plan finalized |
| 2 | `amr.sensors.xacro` + `use_sensors` option; sensor frames | TEST-M3-01, -02, -03 | Task A | Step 1; DEC-030 (confirmed by DEC-037), DEC-031, -032, -034 |
| 3 | `sensor_test.sdf`, bridge YAML, launch args | TEST-M3-04 | Task B | Step 2 |
| 4 | LiDAR verification (range accuracy, FOV, blind zone) | TEST-M3-05, -06 | Task C | Step 3; OPEN-18 |
| 5 | IMU and encoder verification | TEST-M3-07, -08, -09 | Task D | Step 3; OPEN-15, -18 |
| 6 | RViz config (observed), M2 regression with sensors on, consistency review, closeout | TEST-M3-10, -11, -12 | Task E | Steps 4–5; OPEN-17 |

### 7.1 Revised Task breakdown (2026-11-03, after the feasibility gate and DEC-037; **finalized 2026-11-03**)
- Scope is unchanged: LiDAR, IMU and wheel encoders (DEC-030 to DEC-036).
- The depth camera is **not** an M3 Task (DEC-037, M8).
- No accepted value changes.

| Task | Objective and deliverables | Tests (test_plan §7) | Carried-in findings | Depends on |
|---|---|---|---|---|
| **A: Sensor model** | `amr_description/urdf/amr.sensors.xacro` with a `use_sensors` Xacro argument (default false) and a conditional include in `amr.urdf.xacro` (DEC-023/034 pattern). Massless `laser_frame` (DEC-030) and `imu_link` (DEC-032). `gpu_lidar` per DEC-031 and IMU per DEC-032, each with `gz_frame_id`. Sensor parameters as named Xacro properties | TEST-M3-01 build, -02 model regression (default byte-identical to M1; M2 expansion unchanged; 9.4 kg, no zero-inertia link), -03 sensor frames (D5) | `max_angle` = 3.12413936106985 rad for exact 1° steps; the `gz_frame_id` SDF warning is expected; xacro run from inside the workspace (TS-010/021). The prototype in `FEAS-M3_amr.sensors.prototype.xacro` is a reference, not code to copy unreviewed | Approval of this breakdown |
| **B: World, bridge, launch** | `amr_bringup/worlds/sensor_test.sdf` (empty-world systems, Sensors `ogre2`, IMU, static targets for C/D). `config/sensor_bridge.yaml` (`/scan`, `/imu`). `sim.launch.py` arguments `world` and `sensors`, with defaults that reproduce M2 exactly | TEST-M3-04 (D1–D4; `/joint_states` 100 Hz ± 2 %) | Headless form `gz sim -s --headless-rendering` (G1); procedures use job control and a leftover check (TS-011/021); the `gz_ros2_control` IMU "skipping" message is expected | A |
| **C: LiDAR verification** | Range accuracy and noise (S1–S4) at 1, 3 and 6 m; FOV; no self-returns; blind-zone characterization of the 0.230 m plane (the M3 part of the blind-zone item) | TEST-M3-05, -06 | Gate G2 values as expectations, not as results. TS-022 does not apply to the 0.230 m plane | B |
| **D: IMU and encoders** | IMU at rest (D9, S1–S4) and in motion (D10, D11); encoder consistency vs ground truth (D12) | TEST-M3-07, -08, -09 | Gravity is +9.80 m/s² on z (G3); the M2 harness profiles are reused | B |
| **E: Visualization, regression, closeout** | `rviz/sensors.rviz` (RobotModel, TF, LaserScan); `gpu_lidar` in the GUI, the one G1 aspect not yet covered; M2 motion regression with sensors on; M3 consistency checker (including DEC-030 to DEC-037); closure records | TEST-M3-10 (observed by me), -11, -12 | DEC-035: no IMU plugin. DEC-037 limits recorded, not tested in M3 | C, D |

## 8. Tests (PLANNED; criteria Accepted: DEC-036, specification sensors.md §7)
Procedures in [test_plan.md §7](../testing/test_plan.md). Evidence goes in `docs/evidence/M3/`.
| Test | Requirement | Summary |
|---|---|---|
| TEST-M3-01 | REQ-M3-01 | Build |
| TEST-M3-02 | REQ-M3-02 | Model regression: M1 default expansion byte-identical, M2 enabled expansion unchanged with sensors off, mass 9.4 kg with sensors on |
| TEST-M3-03 | REQ-M3-03 | Sensor TF frames and poses |
| TEST-M3-04 | REQ-M3-04 to -06 | Topics, types, rates, frames, sim-time stamps |
| TEST-M3-05 | REQ-M3-07 | LiDAR range accuracy against known targets |
| TEST-M3-06 | REQ-M3-08 | LiDAR FOV, no self-occlusion, blind-zone characterization |
| TEST-M3-07 | REQ-M3-09 | IMU at rest |
| TEST-M3-08 | REQ-M3-10 | IMU in motion vs ground truth |
| TEST-M3-09 | REQ-M3-11 | Encoder consistency vs ground truth |
| TEST-M3-10 | REQ-M3-12 | RViz visualization (observed by me) |
| TEST-M3-11 | REQ-M3-13 | M2 motion regression with sensors on |
| TEST-M3-12 | REQ-M3-14 | Documentation / configuration consistency |

## 9. Risks
- *`gpu_lidar` needs rendering.* Headless EGL on the Intel GPU may fail or be slow (A1). Mitigation: the step-1 probe before any model change, with fallback options held for review.
- *Rendering lowers the RTF.* Timing tests become noisy. Mitigation: sim-time evaluation; RTF logged; runs with RTF < 0.5 invalid (as in M2).
- *Frame-id mismatch* (scoped Gazebo names instead of `laser_frame`/`imu_link`) breaks TF lookup in RViz and SLAM. Mitigation: A2 probe; TEST-M3-04 checks `frame_id` exactly.
- *Sensor pose lost or shifted by fixed-joint lumping* (A3). Mitigation: probe plus TEST-M3-03/05 against geometry.
- *IMU conventions* (specific force vs acceleration, orientation reference). Mitigation: CALC-M3-02 expected values; TEST-M3-07/08 sign checks.
- *Noisy sensors make tests flaky.* Mitigation: criteria on means over many samples, with tolerances derived from the configured σ (OPEN-18).
- *M2 regression:* sensors must not change dynamics. Mitigation: massless sensor links (OPEN-16) and TEST-M3-11.
- *Beam floor hits under pitch* if `range_max` > 13 m (CALC-M3-01). Mitigation: `range_max` 12 m.

## 10. Exit criteria
M3 is complete only when:
- TEST-M3-01 to TEST-M3-12 are PASS with evidence in `TEST_RESULTS.md` and `docs/evidence/M3/`. Failures are kept with TS entries and re-tests.
- The M1 default expansion is byte-identical to the M1 evidence, and the M2 motion regression passes with sensors on.
- OPEN-03 and OPEN-13 to -18 are decided and recorded in `DECISIONS.md`, or provisional with a named follow-up milestone. The M3 part of the blind-zone item (characterization) is recorded.
- Configuration, Xacro properties and design documents agree (TEST-M3-12).
- Roadmap and traceability are updated; the M3 Tasks are done.

## 11. Implementation record
- 2026-11-03: plan drafted (Proposed) after the M2 closure. Inputs:
  - ROADMAP M3; OPEN-03; DEC-014; CALC-M1-14; frames_and_tf.md §5.
  - Installed-software facts checked read-only (sensors.md §2).
  - No code, model or configuration changed; no probe run.
- 2026-11-03: my decisions on OPEN-03 and OPEN-13 to -18 → DEC-030 to DEC-036; design documents, requirements and the test plan updated. The feasibility gate was decided as a throwaway test.
- 2026-11-03: feasibility gate G1–G6 **PASS**, on a throwaway prototype in scratch (the repository's `amr_ws/` unchanged). Results, findings and limits are in [sensors.md §6.1](../design/sensors.md); evidence is in `docs/evidence/M3/FEAS-M3_*`.
  - Runtime, two runs: headless `ogre2` rendering on the Intel GPU at RTF 0.998 / 1.000. `/scan` in `laser_frame` at 10 Hz with exact 1° steps; target mean errors ≤ 0.6 mm; blind-zone target not detected; no self-returns. `/imu` in `imu_link` at 100 Hz, with +9.80 m/s² on z at rest.
  - `/joint_states` **measured at 100 Hz** (DEC-036 D2).
  - Static: the default-off expansion is byte-identical to the M1 evidence. The sensors-on SDF has 9.4 kg, positive inertias, the sensor links lumped and the sensor poses correct.
  - Gate-harness defects TS-021 (SIGINT ignored, absolute xacro path) were fixed in the gate scripts. They are not model or architecture defects.
  - Findings carried into step 2: `max_angle` 179°; the `gz_frame_id` warning and the `gz_ros2_control` IMU message are expected.
  - M3 stays **Proposed** pending my review. The Tasks are not created yet.
- 2026-11-03: I reopened OPEN-03 (0.230 m blind zone). Low-obstacle investigation (§12):
  - CALC-M3-04 plus two scratch Gazebo runs; recommendation (Proposed): option 3, the upper LiDAR unchanged plus a forward depth camera, implemented in M8.
  - Found TS-022, `gpu_lidar` seeing through the robot body when mounted low.
  - No robot code, geometry or accepted specification changed.
- 2026-11-03: **DEC-037**. Option 3: DEC-030/031 unchanged; the forward depth camera is an M8 sensor, not an M3 Task. OPEN-03 closed. Limitations and eight M8 planning requirements recorded in DEC-037. Revised Task breakdown §7.1 presented for review; no Tasks created.
- 2026-11-03: I finalized §7.1 and started Task A.
- 2026-11-03: **Task A implemented and verified.**
  - New `amr_description/urdf/amr.sensors.xacro`: massless `laser_frame` (DEC-030) and `imu_link` (DEC-032), `gpu_lidar` (DEC-031) and IMU (DEC-032) with `gz_frame_id`, sensor values as named Xacro properties. `amr.urdf.xacro`: `use_sensors` argument (default false) and one conditional include (DEC-034). No camera (DEC-037). `amr_properties.xacro` unchanged.
  - TEST-M3-01 PASS; TEST-M3-02 FAIL (checker defect TS-024), re-test 1 PASS; TEST-M3-03 FAIL (harness defect TS-025, no check ran), re-test 1 PASS. Expected M1/M2-scope assertions declared before the run (TS-023). Records: [TEST_RESULTS.md](../../TEST_RESULTS.md) § M3.
  - Default expansion byte-identical to the M1 evidence; M2 expansion unchanged; 9.4 kg with sensors on. Simulation model only: no sensor output measured yet (Tasks B–D).
- 2026-11-03: **Task B implemented and verified.**
  - `amr_bringup/worlds/sensor_test.sdf`: the stock `empty.sdf` systems and 1 kHz physics, plus Sensors (`ogre2`) and IMU; five static targets (1, 2, 3, 6 m and a low box; poses in test_plan §7.1).
  - `config/sensor_bridge.yaml` (`/scan`, `/imu`, Gazebo → ROS).
  - `sim.launch.py`: `sensors` (default false) and `world` (default `empty.sdf`); with sensors headless, `--headless-rendering`; spawn world name read from the world file.
  - TEST-M3-01 re-test 1 PASS (build after the changes). TEST-M3-04 PASS: D1–D4, and the default launch equals M2 (command, world, byte-identical `robot_description`, no sensor topics). The informal dry run before it showed one `/scan` D3 value of 0.115 s: TS-026, open for monitoring; limits unchanged.
- 2026-11-03: **Tasks C and D, in parallel.** Separate test files and ROS domains; Gazebo runs serialized. No robot, world or launch change.
  - Task C: TEST-M3-05 PASS (bias ≤ 1.0 mm, s/σ 0.991–1.054 at 1, 3, 6 m); TEST-M3-06 PASS (D6–D8; blind zone of the 0.230 m plane characterized, the M3 part of the blind-zone item). **Task C complete.**
  - Task D: the spawn (0, −20) m was verified clear first (nearest model 17.1 m). TEST-M3-07 PASS (gravity 9.8008 m/s², S1–S4 on six channels); TEST-M3-09 PASS 3/3 (encoder travel within 0.006 %); TEST-M3-08 **FAIL**: D10 PASS 3/3 (gyro within 0.016 %), D11 FAIL 3/3 (accel x ≈ 0 during a 0.5 m/s² ramp). TS-027 diagnostic: the simulated accelerometer shows no response to the robot's own acceleration; cause not established. DEC-032/036 unchanged; held for review. **Task D blocked.**
  - TS-026: no recurrence; TEST-M3-05/06 do not check D3, and TEST-M3-04 is not re-run in Tasks C/D.
- 2026-11-03: **TS-027 bounded investigation** (scratch only). Cause: the 100 Hz diff-drive command hold makes the chassis acceleration a one-step spike every 10 ms, and the 100 Hz IMU samples the instantaneous acceleration at a fixed phase, so it reads ≈ 0. The IMU itself, DART, the frames, the bridge and the harness are excluded; bullet-featherstone reports no link acceleration at all. Candidates C1 (IMU 1 kHz) and C2 (controller 1 kHz) pass D11 informally, but neither gives a smooth per-sample signal, and each changes an accepted value. Decision held open; TEST-M3-08 stays FAIL.
- 2026-11-03: **TS-027 C4 scratch prototype** (selected; prototype only). The IMU runs at 1 kHz and a 10-sample block mean gives the 100 Hz output, chosen over a 20-sample mean and an IIR filter, which aliases.
  - Informal results: TEST-M3-08 harness 3/3 (D11 +0.18 to +0.27 %); braking within 0.3 %; TEST-M3-07 2/2; TEST-M3-04 checker PASS (`/imu` 100 Hz, stamp − clock ≤ 1 ms); group delay 4.5 ms.
  - The output noise meets DEC-032 only with the raw σ × √10; with the DEC-032 values applied to the raw samples, S2 fails (0.31 σ).
  - Decision held open; production, DEC-032 and TEST-M3-08 unchanged.
- 2026-11-03: **C4 chosen as the preferred direction; DEC-038 drafted (Proposed).** It specifies:
  - the IMU noise at the `/imu` output, 1 kHz internal sampling, the 10-sample block mean, and the derived raw σ = √10 · σ_out;
  - a C++ Gazebo system plugin, recommended over a standalone process or a ROS node;
  - newest-sample stamps with interval-mean values; measured controller-step delay 8–9 ms;
  - full-block startup and dropped blocks on missing samples;
  - the DEC-026 rate constraint.
  Conditional retest plan in test_plan §7.3 (TEST-M3-01 to -09 re-tests, new TEST-M3-13/-14). Not implemented; awaiting my review.
- 2026-11-03 (evening): **DEC-038 Accepted**. A dedicated implementation step (it blocks Task D).
  - New package `amr_gazebo_plugins`: ImuBlockAverager, ImuDecimator system plugin, 13 unit tests; `amr.sensors.xacro` updated (use_sensors only).
  - The rate covariances are divided by 10 (confirmed by me).
  - A pre-fix formal batch was run (TEST_RESULTS, superseded). All measurement checks passed, including D11 3/3 and braking. TEST-M3-04 R1 and TEST-M3-14 failed on a shutdown hang (TS-029, open; reproduced without the plugin).
  - TS-028 (validation timing) fixed in development.
- 2026-11-04: TS-029 diagnosed (upstream gz shutdown deadlock, gdb stack trace); **DEC-039** invalid-run rule and **DEC-040** test automation accepted. **Formal re-run on `4961817`: PASS** for TEST-M3-01 R3, -13 R1, -02 R3 (M1 identity), -03 R3, -04 R2, -05/-06 R2 (TEST-M3-06 attempt 1 INVALID, TS-029), -07 R2, -08 R2 (D11 within 0.39 %), -09 R2, -14 R1, -14 (g) R1; TEST-M2-11 R3 FAIL (checker defect TS-031), R4 PASS. TS-030 (harness teardown traceback) recorded. The plugin step and Task D complete; next Task E.
- 2026-11-04: **Task E started.** TEST-M3-11 PASS (M2 modes 3/3 each with sensors on, `sensor_test.sdf` at (0, −20); stop distance 3–6 mm longer than M2 R1, within criteria, not attributed). `amr_bringup/rviz/sensors.rviz` (RobotModel, TF, LaserScan; fixed frame `odom`; no IMU display, DEC-035) installed; TEST-M3-01 R4 PASS. TEST-M3-12 checker written. Pending: TEST-M3-10 (observed by me), TEST-M3-12, closeout.
- 2026-11-04: **TEST-M3-10 PASS (observed by me)**: the four scan lines match the targets, none for the low target; `laser_frame` and `imu_link` labelled; `gpu_lidar` runs with the Gazebo GUI (RTF 99.83 %), the last gate G1 aspect.
- 2026-11-04: TEST-M3-12 FAIL (the TEST-M3-10 record format, TS-032), **R1 PASS** (232 checks). **All TEST-M3-01 to -14 PASS; the M3 exit criteria are met.**
- 2026-11-04: **M3 closed.** OPEN-13 to -17 closed after verification; the blind-zone item stays deferred for its M8 part. Next: the DEC-040 test-automation step, before M4.

## 12. Low-obstacle architecture investigation (OPEN-03 reopened, 2026-11-03)
**Status:** investigation complete. **Decided 2026-11-03: DEC-037**. I finalized option 3, with the depth camera in M8 and not as an M3 Task F, and OPEN-03 is closed. The text below is kept as the record of the investigation; where it says Proposed, DEC-037 governs.
- After the feasibility gate, I reopened OPEN-03 because of the 0.230 m blind zone and asked for this comparison before Task A.
- DEC-030 stays as recorded, with status "reopened for review". Nothing in the robot code, the sensor geometry or the accepted sensor specifications (DEC-030 to DEC-036) was changed. The G1–G6 evidence is unchanged.
- **Method.**
  - CALC-M3-04, a reproducible 2D ray cast of the M1 body at each candidate scan-plane height, using `amr_properties.xacro` values ([script](../evidence/M3/LOWOBS_geometry.py), [log](../evidence/M3/LOWOBS_geometry.log)).
  - Two throwaway Gazebo runs on scratch copies, same harness as the gate, headless `ogre2`, Intel GPU. The world ([file](../evidence/M3/LOWOBS_world.sdf)) contains:
    - t1, a 0.03 m "dropped part" at 0.8 m;
    - t2, a 0.08 m tote at 1.2 m;
    - t3, a 0.15 m box at 1.8 m;
    - t4, a simplified EUR-pallet proxy, deck 0.100–0.144 m on 9 blocks, front face at 2.8 m;
    - t5 and t6, 0.40 m boxes behind and to the right;
    - an enclosure, so that every unblocked beam returns a range.
  - Run A ([log](../evidence/M3/LOWOBS_run_A.log)): the accepted upper LiDAR plus a **trial** forward depth camera ([xacro](../evidence/M3/LOWOBS_sensors_A_trial.xacro)).
    - Camera: 320 × 240, 87° horizontal FOV, 0.10–4.0 m, 10 Hz, at (0.135, 0, 0.190) m, pitched 25° down.
    - No depth noise was configured.
    - These are investigation values, not proposals for decision.
  - Run B ([log](../evidence/M3/LOWOBS_run_B.log)): the LiDAR alone, lowered to a front-protruding mount at (0.160, 0, 0.120) m ([xacro](../evidence/M3/LOWOBS_sensors_B_trial.xacro)).
  - Procedure: [runner](../evidence/M3/LOWOBS_run.sh), [launch](../evidence/M3/LOWOBS_launch.py), [measurement](../evidence/M3/LOWOBS_measure.py). Each run takes 5 s of simulation time after a 2 s settle, at rest.

### 12.1 Options
| | Option 1: upper LiDAR only (DEC-030 as recorded) | Option 2: lower the existing LiDAR | Option 3: upper LiDAR + a lower obstacle sensor |
|---|---|---|---|
| Variant evaluated | Plane 0.230 m on the bracket | 2a: on the chassis top, no bracket, plane ≈ 0.190 m. 2b/2c: front-protruding housing, plane 0.120 / 0.060 m. 2d: under the chassis, plane 0.035 m | Upper LiDAR unchanged, plus a forward depth camera pitched down (trial values above). A second, low 2D LiDAR is the alternative sensor |

### 12.2 Evaluation
| Criterion | Option 1 | Option 2 | Option 3 |
|---|---|---|---|
| **Floor-level boxes, totes** | Not detected below 0.230 m. **Measured (run A):** t1 0.03, t2 0.08 and t3 0.15 m all not detected | 2b detects only tops > 0.120 m. **Measured (run B):** t3 detected; t1, t2 not. 2c (0.060 m) would also catch t2 (Calculated). 2a gains only 40 mm and still misses t3 | **Measured (run A, ideal depth):** t1, t2, t3 detected in 100 % of clouds, with recovered top heights 0.030 / 0.080 / 0.150 m (matching the world) |
| **Pallet edges** (empty EUR pallet, nominal 144 mm; block / board split **Assumed**) | Not detected (t4: 0 beams) | 2b (plane in the deck band 0.100–0.144 m): detected (run B, 11 beams). A plane at 0.022–0.100 m would pass through the fork openings and hit only the blocks (Calculated from the proxy geometry) | Detected (run A: 480 points, top 0.144 m) |
| **Dropped components** (≈ 0.01–0.05 m, **Assumed**) | No | No for any practical 2D plane (2d at 0.035 m is mechanically infeasible: see mounting) | Detected at 0.03 m in ideal simulation. On hardware the limit is set by depth noise and pitch: a 1° pitch shifts the apparent floor by d · tan 1° = 0.017 d m, i.e. 0.026 m at 1.5 m (Calculated). So small parts are reliable only at short range (**Estimate**) |
| **Self-occlusion / coverage** | 360/360 beams (CALC-M3-04; run A and gate: 0 self-returns) | 2a: 360/360. 2b/2c: **203/360**; the chassis blocks bearings beyond ±102° (157°) (CALC-M3-04). 2d: 285/360 (wheels ±49–80°, caster 180°). **Simulation artifact (run B, TS-022):** `gpu_lidar` sees *through* the chassis at ±120–180°, so simulation would over-state option 2's coverage | LiDAR 360/360 unchanged. Camera: forward only, ±43.5° horizontal; floor visible from ≈ 0.11 m ahead of the camera (Calculated). No rear or side low-obstacle coverage |
| **Mounting, clearance, collision geometry** | Existing bracket; no change | 2a: removes or alters the accepted bracket. 2b/2c: housing ahead of the chassis front face, which lengthens the footprint and changes collision geometry and the Nav2 footprint (M1 geometry change, needs a decision). 2d: does not fit the 0.050 m ground clearance with a usable housing (**Assumed** housing height ≳ 0.04 m) | A small front mount on the chassis top edge. It can be modelled massless (DEC-034 pattern), so the M1 mass and geometry are unchanged |
| **Floor returns under pitch** (level beam reaches the floor at h / tan θ; `range_max` 12 m, DEC-031) | 13.18 m at 1° (no floor hits) | 2a 10.89 m, 2b 6.87 m, 2c 3.44 m, 2d 2.01 m at 1°. All are below 12 m, so a lowered plane needs a shorter `range_max` or tolerates floor hits: a DEC-031 change | Not applicable to the LiDAR. The camera sees the floor by design and needs floor segmentation (Nav2 `min_obstacle_height`) |
| **Integration** | Done (gate G1–G6) | Same sensor type, but a 360° spec with a blocked rear needs an FOV restriction (DEC-031 change) or a masking filter; plus the TS-022 artifact | Second sensor, second TF frame, `PointCloud2` bridge. **Verified:** `depth_camera` renders headless; `/depth/points` bridged in frame `depth_link`. Installed: `nav2_costmap_2d` `ObstacleLayer`/`VoxelLayer` and `depthimage_to_laserscan` |
| **Computation** | 3.6 k ranges/s | Same as option 1 | **Measured:** RTF 0.993 with LiDAR + IMU + depth camera, vs 0.998 without (runs A/B; this simple world only). 76,800 points per cloud at 10 Hz (0.77 M points/s) to filter in M8 (costmap CPU not measured) |
| **Cost / hardware** (M13 optional; **no quotes in the repository**) | No added sensor | No added sensor; mechanical redesign. Restoring 360° would need a second low LiDAR (≈ 2× LiDAR cost, **Estimate**) | One added sensor plus mount, cabling, USB bandwidth and compute. **Estimate:** an entry-level depth camera is of the same order as an entry-level 2D LiDAR (unverified, no quote) |
| **M5 mapping / M6 localization** | Best: a high plane sees walls and fixed structure; `slam_toolbox` 2.8.5 installed | Worse: 203° FOV; a low plane sees movable clutter (pallets, totes), which degrades maps (engineering judgment) | Same as option 1 (SLAM and AMCL keep using the upper `/scan`) |
| **M8 obstacle avoidance** | Unsafe alone for low obstacles | Low detection in front only above the plane; **rear blind for all obstacles** (157°), which matters when reversing (DEC-025 allows −0.25 m/s) | Standard Nav2 multi-source costmap (`observation_sources`: `/scan` + `/depth/points`). The rear and sides stay blind to low obstacles |

### 12.3 Recommendation (Proposed at the time; **accepted as DEC-037**, with the timing set to M8 by me)
- **Option 3: keep the upper 360° LiDAR exactly as DEC-030/031 and add a dedicated forward, down-tilted depth camera as the low-obstacle sensor.**
  - It is the only option that detects all four low-target classes in the evidence.
  - It keeps full 360° LiDAR coverage for mapping and localization.
  - It changes no accepted M1 geometry or M3 specification. Task A and the G1–G6 evidence stay valid.
  - The measured simulation cost is small (RTF 0.993).
- **Timing:** recommended in **M8**, behind its own default-off Xacro option (DEC-023/034 pattern), with its own decision record and feasibility/acceptance tests.
  - M8 is where its consumer (the Nav2 costmap) and its requirements exist: footprint, speeds, stopping distance, floor-filter thresholds.
  - M4–M7 do not use it.
  - The alternative is to add it to M3 as a new Task F (a sensor-milestone scope change).
- **OPEN-03 resolution, once decided:** DEC-030 confirmed unchanged, plus a new decision recording the low-obstacle architecture. The blind-zone item then becomes an M8 implementation item.
- **Not recommended:**
  - Option 2b/2c loses 157° of rear coverage, changes the M1 footprint and DEC-031, and cannot be simulated faithfully with `gpu_lidar` (TS-022).
  - Option 2a gains only 40 mm.
  - Option 2d is mechanically infeasible.
  - Option 1 alone leaves the blind zone without mitigation.

### 12.4 Assumptions, limits and risks
- **Simulation is idealized.** No depth noise was configured, the floor is perfectly flat, and the robot is at rest in a simple world. Detection results are upper bounds; a noise model and pitch effects must be included before any M8 acceptance.
- **Remaining blind zones.** Forward-only coverage leaves the rear and sides blind to low obstacles. Options: limit reversing near unknown space; costmap persistence; or a rear sensor later (M8 decision).
- **EUR-pallet details** (block height, fork openings) and dropped-part sizes are **Assumed**, not measured. The pallet proxy is simplified (no bottom boards).
- **Trial camera values** (pose, FOV, resolution, clip, rate) were chosen only to exercise the option. They are **not** proposals for decision.
- **Rendering cost** was measured in one simple world; heavier worlds may lower the RTF (M3/M8 RTF validity rule, sensors.md §7.5).
- **Data-handling note.** Run A attempt 1 ([log](../evidence/M3/LOWOBS_run_A_attempt1.log)) mis-handled ±inf points beyond the camera clip, so its frame-convention check printed NaN. The detection counts were unaffected. Fixed in the measurement script and re-run.
- **Run B attempts.** Attempt 1 ([log](../evidence/M3/LOWOBS_run_B_attempt1.log)) led to the see-through diagnosis; the final run adds a per-bearing dump.

### 12.5 Decisions needed (**answered 2026-11-03: option 3; M8; DEC-037**)
1. Low-obstacle architecture: option 3 (recommended), 1 or 2.
2. If option 3: implement in M8 (recommended) or add it to M3 as Task F.
3. Then OPEN-03 can be closed (DEC-030 confirmed or revised) and the Task breakdown (§7) finalized.
