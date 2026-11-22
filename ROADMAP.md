# Smart AMR Roadmap

Milestone plans live in [docs/milestones/](docs/milestones/); every test result is in [TEST_RESULTS.md](TEST_RESULTS.md).

## M0 — Development Environment
**Status:** ✅ Complete (2026-10-19)
- [x] Create the repository
- [x] Clone repository
- [x] Initialize documentation
- [x] Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic installed; versions verified (TEST-M0-05)
- [x] ROS 2 Jazzy communication (TEST-M0-01)
- [x] Gazebo Harmonic GUI (TEST-M0-02)
- [x] RViz2 (TEST-M0-03)
- [x] ROS–Gazebo `/clock` integration (TEST-M0-04, re-test 1)

## M1 — Custom AMR
**Status:** ✅ Complete (2026-10-21). Design review finalized on 2026-10-19 (DEC-016/017 Accepted); TEST-M1-01 to -08 PASS; OPEN-07 rest-stability thresholds kept provisional with follow-up in M2.
**Plan and criteria:** [docs/milestones/M1_custom_amr.md](docs/milestones/M1_custom_amr.md)
- [x] Design and documentation baseline reviewed and finalized (2026-10-19)
- [x] Resolve open design items OPEN-01 to OPEN-07 (DEC-019; OPEN-03 provisional until M3; OPEN-07 provisional until TEST-M1-07, then kept provisional with follow-up M2)
- [x] Accept or revise DEC-016 and DEC-017 (accepted 2026-10-19)
- [x] Create ROS 2 workspace (`amr_ws/`)
- [x] Create robot description package `amr_description` (TEST-M1-01 PASS)
- [x] Create URDF/Xacro (TEST-M1-02 PASS)
- [x] Chassis
- [x] Drive wheels
- [x] Caster
- [x] Passive LiDAR mount
- [x] Collision geometry
- [x] Inertial properties (TEST-M1-03 re-test 1 PASS)
- [x] RViz display and TF verification (TEST-M1-04 PASS, observed by me; TEST-M1-05 PASS)
- [x] Spawn in Gazebo (TEST-M1-06 PASS, observed by me)
- [x] Rest stability in Gazebo (TEST-M1-07 PASS; thresholds still provisional, OPEN-07, follow-up M2)
- [x] Documentation / code consistency review (TEST-M1-08 re-test 1 PASS)
- [x] M1 closeout (2026-10-21); OPEN-07 follow-up named (M2)

## M2 — Basic Movement
**Status:** ✅ Complete (2026-11-03). Implemented and re-tested 2026-10-22 (DEC-023 to DEC-029); TEST-M2-09 and TEST-M2-10 PASS (observed by me) and OPEN-07 finalized unchanged on 2026-11-03. Limitations: [M2 record §11](docs/milestones/M2_basic_movement.md).
**Plan and criteria:** [docs/milestones/M2_basic_movement.md](docs/milestones/M2_basic_movement.md); proposals in [docs/design/motion_control.md](docs/design/motion_control.md).
- [x] Differential-drive control
- [x] ros2_control
- [x] cmd_vel (`/cmd_vel` TwistStamped through `cmd_vel_guard`, DEC-026/029)
- [x] Manual control (TEST-M2-09 PASS, observed by me, 2026-11-03)
- [x] Forward motion (TEST-M2-05)
- [x] Reverse motion (TEST-M2-05)
- [x] Rotation (TEST-M2-06 re-test 1, DEC-028)
- [x] Stop (TEST-M2-07)
- [x] Verify motion (TEST-M2-05 to -08)
- [x] Revisit the provisional OPEN-07 rest-stability thresholds (TEST-M2-10 PASS; finalized unchanged 2026-11-03, DEC-019)
- [x] Package structure decided (OPEN-08 → DEC-023: `amr_description` + `amr_bringup`, conditional `ros2_control`)
- [x] Contact and friction parameters (DEC-024; wheel collision DEC-028)
- [x] Velocity and acceleration limits (DEC-025; TEST-M2-08)
- [x] Controller rate and command interface (DEC-026; guard DEC-029)
- [x] Motion-test criteria (DEC-027)
- [x] `joint_state_broadcaster`, wheel `/joint_states`, `odom → base_footprint` (TEST-M2-04; accuracy M4)
- [x] `/clock` bridge and simulation time (TEST-M2-04 re-test 1)

## M3 — Sensors
**Status:** ✅ Complete (2026-11-04). Task A (sensor model): TEST-M3-01 to -03 PASS. Task B (world, bridge, launch): TEST-M3-04 PASS. Task C (LiDAR): TEST-M3-05, -06 PASS. Task D (IMU, encoders): TEST-M3-08 failed D11 (TS-027) on the original model, corrected by DEC-038 (my IMU decimation plugin); the formal re-run passed TEST-M3-01 to -09, -13, -14 (TS-029 handled by DEC-039). Task E: TEST-M3-10 PASS (observed by me), TEST-M3-11 PASS (M2 regression with sensors). OPEN-03 and OPEN-13 to -18 decided by DEC-030 to DEC-036; feasibility gate G1–G6 PASS; low-obstacle detection assigned to a depth camera in M8 (DEC-037). Plan: [docs/milestones/M3_sensors.md](docs/milestones/M3_sensors.md).
- [x] LiDAR (TEST-M3-05, -06)
- [x] IMU (TEST-M3-07, -08, DEC-038: TEST-M3-13, -14)
- [x] Wheel encoders (TEST-M3-09)
- [x] Sensor topics (TEST-M3-04)
- [x] RViz visualization (TEST-M3-10, observed by me)
- [x] M2 regression with sensors (TEST-M3-11)

## Between M3 and M4 — Test automation (DEC-040)
**Status:** ✅ Complete (2026-11-04; TEST-TA-01 to -05 PASS; plan [docs/milestones/M3-M4_test_automation.md](docs/milestones/M3-M4_test_automation.md)). Done after M3 and before M4.
- [x] Local suite runner (TEST-TA-02, TEST-TA-03 R1): serial execution, leftover-process check, unique tags, exit code vs `# overall:` cross-check, summary table. Human log review before any PASS is recorded.
- [x] TS-030: the harness teardown fix in the shared pattern, with a full-traceback capture, and re-runs of every harness user (TEST-TA-01, TEST-TA-04; TS-030 resolved).
- [x] Stop-measurement timing INFO (TEST-TA-04) (DEC-040 (d)): zero-command-to-braking latency and the interpolated stop distance, to explain the TEST-M3-11 3–6 mm difference. Criteria unchanged.
- [x] GitHub Actions CI for the GPU-free checks (TEST-TA-05): build, unit tests, M1 byte identity, odometry recomputation. It runs only on pushes that change code, configuration or tests, to stay inside the free Actions minutes.

## M4 — Odometry
**Status:** ✅ Complete (2026-11-13; plan [docs/milestones/M4_odometry.md](docs/milestones/M4_odometry.md); DEC-042 to DEC-045; TEST-M4-01 to -11 PASS, [TEST_RESULTS.md](TEST_RESULTS.md) § M4)
- [x] Differential-drive kinematics (TEST-M4-03)
- [x] Wheel odometry (TEST-M4-01, -02)
- [x] TF tree (TEST-M4-02, -11)
- [x] Odometry verification (TEST-M4-04 to -09)
- [x] Quantitative testing (TEST-M4-04 to -10)

## M5 — SLAM
**Status:** ✅ Complete 2026-11-15 (plan [docs/milestones/M5_slam.md](docs/milestones/M5_slam.md); DEC-046 to DEC-055; TEST-M5-01 to -10 PASS, [TEST_RESULTS.md](TEST_RESULTS.md) § M5)
**Carried forward:** loop-closure verification in a larger or corridor environment (DEC-052); half-cell origin correction for every new map (TS-041).
- [x] SLAM Toolbox (TEST-M5-01, -02)
- [x] Map building (TEST-M5-03, -04, -06, -09)
- [x] Mapping test (TEST-M5-03, -07, -08, -10)
- [x] Save map (TEST-M5-05)

## M6 — Localization
**Status:** ✅ Complete 2026-11-21 (plan [docs/milestones/M6_localization.md](docs/milestones/M6_localization.md); DEC-056 to DEC-065; TEST-M6-01 to -11 PASS, [TEST_RESULTS.md](TEST_RESULTS.md) § M6)
**Carried forward (M6 plan §13):** a known start pose is required (global localization is unreliable in this arena, DEC-058); AMCL keeps its own map copy on `/map_amcl` (TS-045, DEC-062; reported upstream as [ros-navigation/navigation2#6833](https://github.com/ros-navigation/navigation2/issues/6833)); the wrong-start recovery margin is a known risk (DEC-065).
- [x] Localization setup (TEST-M6-01, -02)
- [x] Pose estimation (TEST-M6-03 to -07)
- [x] TF verification (TEST-M6-02, -07, -10)
- [x] Localization testing (TEST-M6-03 to -11)

## M7 — Autonomous Navigation
**Status:** ✅ Complete 2026-11-23 (plan [docs/milestones/M7_navigation.md](docs/milestones/M7_navigation.md); DEC-066 to DEC-080; TEST-M7-01 to -10 PASS, [TEST_RESULTS.md](TEST_RESULTS.md) § M7)
**Carried forward (M7 plan §13):** low obstacles below the LiDAR plane are invisible to Nav2, which leads to contact, localization loss and false successes (TS-058, an M8 input); Nav2 judges success on the estimate; a known start pose is still required; dropped lifecycle replies at start-up are watched (TS-055).
**Carried in (DEC-011, CALC-M1-05):** the Nav2 footprint must cover the wheels (width 0.435 m across the outer faces) and the caster overhang (length 0.510 m), not the chassis outline alone.
- [x] Nav2 (`navigation.launch.py`, `nav2.yaml`, behavior trees; TEST-M7-02)
- [x] Costmaps (global on `/map`, local rolling window; CALC-M7-01 footprint; TEST-M7-02)
- [x] Global planner (NavFn, DEC-068, DEC-077; TEST-M7-03, -05)
- [x] Local controller (RPP and velocity smoother, DEC-067, DEC-070; TEST-M7-03 to -06)
- [x] Goal navigation (single goals, route, cancel, RViz goals; TEST-M7-03, -04, -06, -09)
- [x] Navigation testing (TEST-M7-07 to -10)

## M8 — Obstacle Avoidance  ← next
**Status:** ⚪ Not Started
**Carried in (DEC-037, 2026-11-03):** a forward, down-tilted depth camera for low obstacles, with parameters to be decided in M8 with evidence. Planning must cover the eight DEC-037 requirements: front-only coverage behaviour, pitch sensitivity, small-part detection range, stopping distance including latency, floor-filter thresholds, an explicit depth-noise model (noise-free simulation is not hardware validation), an RTF re-check, and no change to DEC-031 without a separate decision.
- [ ] Low-obstacle depth camera (DEC-037)
- [ ] Static obstacles
- [ ] Dynamic obstacles
- [ ] Local replanning
- [ ] Avoidance testing

## M9 — Factory Environment
**Status:** ⚪ Not Started
- [ ] Warehouse/factory world
- [ ] Storage areas
- [ ] Stations
- [ ] Charging area
- [ ] Obstacles
- [ ] Navigation map

## M10 — Task Automation
**Status:** ⚪ Not Started
- [ ] Task representation
- [ ] Pickup workflow
- [ ] Delivery workflow
- [ ] Task completion state
- [ ] Multiple task handling

## M11 — Vision
**Status:** ⚪ Not Started
- [ ] Camera
- [ ] AprilTag/QR detection
- [ ] Station identification
- [ ] Vision integration

## M12 — Dashboard
**Status:** ⚪ Not Started
- [ ] Robot status
- [ ] Task status
- [ ] Navigation status
- [ ] Position
- [ ] Factory visualization
- [ ] Basic controls

## M13 — Physical Robot
**Status:** ⚪ Optional
- [ ] Mechanical design
- [ ] Electronics
- [ ] Motor control
- [ ] Sensors
- [ ] Hardware integration
- [ ] Simulation-to-real testing
