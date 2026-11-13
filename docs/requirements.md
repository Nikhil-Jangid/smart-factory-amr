# Requirements, Acceptance Criteria, and Traceability

**Status:** M0 requirements were recorded retroactively on 2026-10-19 and are satisfied. M1 requirements were reviewed and finalized on 2026-10-19 as part of the M1 documentation baseline (M1 plan §5). TEST-M1-01 (PASS, 2026-10-19), TEST-M1-02 (PASS, 2026-10-21) and TEST-M1-03 (FAIL, then re-test 1 PASS, 2026-10-21), TEST-M1-04 (PASS, visual criteria observed by me), TEST-M1-05 (PASS), TEST-M1-06 (PASS, visual criteria observed by me) and TEST-M1-07 (PASS, jitter observed by me) and TEST-M1-08 (FAIL, then re-test 1 PASS) have been run, all on 2026-10-21. Every M1 test has been executed. M2 requirements (REQ-M2-01 to -17) were proposed on 2026-10-22 with the M2 plan, whose scope I finalized as the working plan on 2026-10-22 (M2 plan §2, §5); TEST-M2-01 to -11 all PASS (several on re-test; final 2026-11-03), and M2 is complete. M3 requirements (REQ-M3-01 to -14) were recorded on 2026-11-03 with the M3 plan (DEC-030 to DEC-036); M3 Task A (2026-11-03): TEST-M3-01 PASS, TEST-M3-02 and -03 PASS on re-test 1. Task B (2026-11-03): TEST-M3-01 re-test 1 and TEST-M3-04 PASS. Tasks C and D (2026-11-03): TEST-M3-05, -06, -07 and -09 PASS; TEST-M3-08 FAIL (D11, TS-027). TEST-M3-10 to -12 are PLANNED.

Traceability chain:
**Requirement → Design decision / property → Calculation (where applicable) → Implementation location (once it exists) → Test ID → Result / evidence**

Implementation paths for code that does not exist yet are marked *(planned)*.

## M0 — Development Environment (complete)

| ID | Requirement | Acceptance criterion | Decision | Test | Result |
|---|---|---|---|---|---|
| REQ-M0-01 | ROS 2 Jazzy nodes communicate | Listener receives all talker messages | DEC-003, DEC-007 | TEST-M0-01 | PASS ([evidence](evidence/M0/TEST-M0-01_talker_listener.log)) |
| REQ-M0-02 | Gazebo Harmonic GUI simulates a world | World loads; sim time advances; RTF ≈ 100 % | DEC-004, DEC-007 | TEST-M0-02 | PASS (observed by me) |
| REQ-M0-03 | RViz2 renders | Window opens with OpenGL; no fatal error | DEC-007 | TEST-M0-03 | PASS (observed by me) |
| REQ-M0-04 | ROS 2 receives Gazebo simulation time | `/clock` bridged; timestamps increase | DEC-007 | TEST-M0-04; TEST-M0-04 re-test 1 | PASS (observed by me); re-test 1 PASS ([evidence](evidence/M0/TEST-M0-04-R1_clock_bridge_headless.log)) |
| REQ-M0-05 | Environment matches the target platform | Ubuntu 24.04.x; ROS 2 Jazzy; Gazebo Sim 8.x; required packages installed (`ii`); values match `environment.md` | DEC-003, DEC-004, DEC-007 | TEST-M0-05 | PASS ([evidence](evidence/M0/TEST-M0-05_environment_inventory.log)) |

REQ-M0-01 to REQ-M0-04 were written after their tests ran (see the disclosure in [`../TEST_RESULTS.md`](../TEST_RESULTS.md#summary)). REQ-M0-05 was written before TEST-M0-05 and TEST-M0-04 re-test 1 were run.

## M1 — Custom AMR Model (reviewed and accepted 2026-10-19)

| ID | Requirement | Acceptance criterion |
|---|---|---|
| REQ-M1-01 | The description package builds | `colcon build --packages-select amr_description` exits 0 |
| REQ-M1-02 | The Xacro expands to a structurally valid URDF with a single tree | `xacro` exits 0; `check_urdf` parses successfully; root `base_footprint`; 6 links, 5 joints |
| REQ-M1-03 | Geometry matches the accepted baseline | Every dimension and joint origin in the generated URDF equals the [geometry table](design/mechanical_geometry.md) (exact to the stated decimals) |
| REQ-M1-04 | Nominal three-point ground contact | Wheel and caster bottoms at z = 0 above ground in the generated model (CALC-M1-04) |
| REQ-M1-05 | Frames follow REP-103 / REP-105 (`base_footprint` per REP-120) and the TF design | TF tree equals [frames_and_tf.md §2](design/frames_and_tf.md); `tf2_echo` values match the joint table to 1 mm |
| REQ-M1-06 | Physically valid inertial properties | Every massive link has an explicit `<inertial>`; moments > 0; triangle inequality holds; per-link values in the generated URDF match CALC-M1-07 to 10 within 4 significant figures (TEST-M1-03(a)); SDF values are checked in combined form only (CALC-M1-15) |
| REQ-M1-07 | Correct total mass | Sum of link masses in the generated model = 9.4 kg (payload excluded) |
| REQ-M1-08 | Positive wheel rotation drives forward | Positive joint position/velocity on each wheel corresponds to +X rolling (OPEN-04) |
| REQ-M1-09 | Passive LiDAR mount reserved | `lidar_mount_link` exists at the specified pose; no active sensor plugin |
| REQ-M1-10 | Primitive geometry only | No mesh files referenced |
| REQ-M1-11 | Model displays correctly in RViz | Robot model and TF render with no errors; geometry visually matches the drawing |
| REQ-M1-12 | Model spawns in Gazebo Harmonic | Spawn succeeds; no `[Err]` messages about the model |
| REQ-M1-13 | Model rests stably in Gazebo | Over 30 s of sim time: thresholds in TEST-M1-07 met (thresholds accepted as provisional, OPEN-07, DEC-019; follow-up milestone M2) |
| REQ-M1-14 | Documentation and code are consistent and evidence is complete | TEST-M1-08 finds zero mismatches; evidence files exist for each executed test |

## M1 traceability matrix

| Requirement | Design decision / property | Calculation | Implementation | Test | Result |
|---|---|---|---|---|---|
| REQ-M1-01 | DEC-008, DEC-017 | — | `amr_ws/src/amr_description/{package.xml,CMakeLists.txt}` (created) | TEST-M1-01 | PASS ([TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-02 | DEC-016 | — | `urdf/amr.urdf.xacro` | TEST-M1-02 | PASS ([TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-03 | DEC-011, DEC-012; `chassis_*`, `wheel_*`, `axle_offset_x` | CALC-M1-01, -02, -03, -05, -13, -14 | `urdf/amr_properties.xacro` | TEST-M1-03, TEST-M1-08 | TEST-M1-03 PASS (re-test 1); TEST-M1-08 PASS (re-test 1) |
| REQ-M1-04 | DEC-013, DEC-016; `caster_radius`, `caster_x`, `ground_clearance` | CALC-M1-04, -13 | `urdf/amr.urdf.xacro` | TEST-M1-03, TEST-M1-06 | TEST-M1-03 PASS (re-test 1); TEST-M1-06 PASS (observed by me) |
| REQ-M1-05 | DEC-016 | — | `urdf/amr.urdf.xacro` | TEST-M1-04, TEST-M1-05 | PASS (both; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-06 | DEC-013; mass properties | CALC-M1-07, -08, -09, -10 | `urdf/inertial_macros.xacro` | TEST-M1-03 | PASS (re-test 1; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-07 | mass properties | CALC-M1-06, -15 (SDF lumped link) | `urdf/amr_properties.xacro` | TEST-M1-03 | PASS (re-test 1; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-08 | DEC-016 (OPEN-04) | — | `urdf/amr.urdf.xacro` | TEST-M1-04 | PASS (observed by me, supported by TF readback; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-09 | DEC-014 (OPEN-03) | CALC-M1-10, -14 | `urdf/amr.urdf.xacro` | TEST-M1-02, TEST-M1-04 | TEST-M1-02 PASS (link exists; pose and no sensor also confirmed by TEST-M1-03 re-test 1); TEST-M1-04 PASS (mount at (0.070, 0, 0.200), provisional) |
| REQ-M1-10 | DEC-017 | — | all `urdf/` files | TEST-M1-08 | PASS (re-test 1: 0 `<mesh>` elements in the sources and the generated URDF; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-11 | — | — | `launch/display.launch.py`, `rviz/display.rviz` | TEST-M1-04 | PASS (observed by me; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-12 | — | — | `launch/gazebo.launch.py` | TEST-M1-06 | PASS ([TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-13 | DEC-012, DEC-013 | CALC-M1-11, -12 | `launch/gazebo.launch.py` | TEST-M1-07 | PASS (thresholds provisional at the time; OPEN-07 finalized unchanged 2026-11-03 after TEST-M2-10, DEC-019; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M1-14 | DEC-009, DEC-010 | — | `docs/` | TEST-M1-08 | PASS (re-test 1; [TEST_RESULTS.md](../TEST_RESULTS.md)) |

When a test is executed, update the "Result" column with PASS / FAIL / BLOCKED and a link to its `TEST_RESULTS.md` entry. Paths marked *(planned)* do not exist yet; remove the mark when the file is created.

## M2 — Basic Movement (complete 2026-11-03; scope accepted as the working plan 2026-10-22)

Plan: [milestones/M2_basic_movement.md](milestones/M2_basic_movement.md); proposals for DEC-024 to -12: [design/motion_control.md](design/motion_control.md). These requirements are **Proposed** (the milestone is in progress; results in the traceability below). Their values come from DEC-024 (contact), DEC-025 (limits), DEC-026 (interface) and DEC-027 (test criteria); exact procedures are in `testing/test_plan.md` §6. Odometry *accuracy* is not an M2 requirement (M4).

| ID | Requirement | Acceptance criterion |
|---|---|---|
| REQ-M2-01 | The M2 packages build | `colcon build` of the M2 package set exits 0, with no warnings for those packages |
| REQ-M2-02 | M2 additions leave the M1 robot model unchanged | Default expansion (`use_ros2_control` false): byte-identical to `TEST-M1-02_amr.urdf`, and the TEST-M1-08 procedure passes (DEC-023). Enabled expansion: `check_urdf` passes, root `base_footprint`, 6 links / 5 joints, 0 `<mesh>` elements, and every TEST-M1-03 geometry, inertial and lumped-SDF check passes, except the M1-scope "no `<gazebo>`/`<plugin>`/`filename`" assertions (replaced by REQ-M2-03) and the two M1 cylinder wheel-collision assertions (the M2 simulation model uses sphere wheel collisions, DEC-028, checked by TEST-M2-02's control check) |
| REQ-M2-03 | The `ros2_control` description covers exactly the drive wheels | One `<ros2_control>` system with hardware plugin `gz_ros2_control/GazeboSimSystem`; `left_wheel_joint` and `right_wheel_joint` each have a `velocity` command interface and `position` and `velocity` state interfaces; no other joint is listed |
| REQ-M2-04 | Controllers start in simulation without unintended motion | `joint_state_broadcaster` and the drive controller are `active` (`ros2 control list_controllers`) within the DEC-027 time; both wheel velocity command interfaces are claimed; no error lines from `controller_manager` or `gz_ros2_control` in the launch log; a command published before activation causes no motion beyond the DEC-027 bound; behaviour on controller deactivation is recorded |
| REQ-M2-05 | ROS runs on simulation time | `/clock` is bridged from Gazebo and advances; every M2 runtime node (`robot_state_publisher`, bridge, controllers, teleop) has `use_sim_time` true; every stamped command is stamped in simulation time (the test harness takes it from the Gazebo pose stamps, TS-013) |
| REQ-M2-06 | Wheel joint states are published in simulation | `/joint_states` contains `left_wheel_joint` and `right_wheel_joint` with position and velocity |
| REQ-M2-07 | Odometry frame and TF follow the frame design | The drive controller publishes `nav_msgs/Odometry` with `frame_id` `odom` and `child_frame_id` `base_footprint`, and TF `odom → base_footprint`. The TF tree is a single tree `odom → base_footprint → …` (frames_and_tf.md §2 below `base_footprint`) |
| REQ-M2-08 | Controller kinematic parameters match the model | `wheel_separation` = `wheel_track` and `wheel_radius` = `wheel_radius` in `amr_properties.xacro`, exactly |
| REQ-M2-09 | Commanded motion has the correct direction | +`linear.x`: the robot moves forward (+X of `base_footprint` in the world) and both wheel velocities are > 0. −`linear.x`: reverse, both < 0. +`angular.z`: yaw increases (counter-clockwise from above), with right wheel velocity > left |
| REQ-M2-10 | Motion quality is acceptable | Straight-line heading/lateral error and translation during in-place rotation within the DEC-027 thresholds |
| REQ-M2-11 | Odometry direction agrees with ground truth | For forward, reverse and rotation, the signs of the odometry displacement and yaw change equal those of the ground-truth world pose. Magnitude accuracy is M4 |
| REQ-M2-12 | The robot stops on command, on command loss, and ignores stale commands | Zero command brings the robot to rest; when commands stop, the robot stops after `cmd_vel_timeout` (DEC-026); a command stamped older than the timeout causes no motion; a command stamped in another clock domain (e.g. wall-clock time) causes no motion (DEC-029 guard); stop distance and times within the DEC-027 thresholds |
| REQ-M2-13 | Velocity and acceleration limits are configured and enforced | The DEC-025 limits are configured; commands above them are limited (`cmd_vel_out`); measured acceleration ≤ the limit within the DEC-027 tolerance; limits below the CALC-M1-12 tipping thresholds |
| REQ-M2-14 | Contact and friction parameters are defined and effective | The DEC-024 wheel and caster surface parameters appear in the generated SDF; TEST-M2-05, -06 and -08 pass with them; wheel slip recorded |
| REQ-M2-15 | The robot can be driven manually | Keyboard teleop drives forward, reverse, rotate and stop (observed by me) |
| REQ-M2-16 | OPEN-07 follow-up is performed | Rest stability re-measured with the M2 configuration (controllers active, zero command) by the TEST-M1-07 method with the unchanged provisional thresholds; result recorded; my decision recorded in DEC-019 |
| REQ-M2-17 | Documentation, configuration and evidence are consistent | TEST-M2-11 finds zero mismatches; every executed test has a record and indexed evidence |

## M2 traceability matrix

| Requirement | Design decision / property | Calculation | Implementation | Test | Result |
|---|---|---|---|---|---|
| REQ-M2-01 | DEC-008, DEC-023 | — | `amr_bringup` and `amr_description` *(planned)* | TEST-M2-01 | PASS (re-test 1; [TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M2-02 | DEC-016, DEC-017, DEC-023 | CALC-M1-06 to -10 | `urdf/amr.urdf.xacro` *(planned change)* | TEST-M2-02 | FAIL (TS-016), re-test 1 FAIL (TS-019), re-test 2 PASS |
| REQ-M2-03 | DEC-023; frames_and_tf.md §2 | — | `urdf/amr.ros2_control.xacro` *(planned)* | TEST-M2-02 | re-test 2 PASS (control check incl. DEC-028) |
| REQ-M2-04 | DEC-023, DEC-026, DEC-027 | — | `amr_bringup/config/controllers.yaml`, `launch/sim.launch.py` *(planned)* | TEST-M2-03 | PASS (suite 1 and re-test 1) |
| REQ-M2-05 | ros_architecture.md §3 | — | simulation launch *(planned)* | TEST-M2-04 | FAIL (TS-018), re-test 1 PASS |
| REQ-M2-06 | frames_and_tf.md §4, §5 | — | controller YAML *(planned)* | TEST-M2-04 | re-test 1 PASS (suite 1 values also met) |
| REQ-M2-07 | DEC-016; frames_and_tf.md §5 | — | controller YAML *(planned)* | TEST-M2-04 | re-test 1 PASS (suite 1 values also met) |
| REQ-M2-08 | DEC-011; `wheel_track`, `wheel_radius` | — | controller YAML *(planned)* | TEST-M2-11 | TEST-M2-11 FAIL (TS-020), re-test 1 PASS |
| REQ-M2-09 | DEC-016 (OPEN-04) | — | controller YAML *(planned)* | TEST-M2-05, TEST-M2-06 | TEST-M2-05 PASS; TEST-M2-06 FAIL (TS-014), re-test 1 PASS |
| REQ-M2-10 | DEC-027 | — | — | TEST-M2-05, TEST-M2-06 | TEST-M2-05 PASS; TEST-M2-06 FAIL (TS-014), re-test 1 PASS |
| REQ-M2-11 | frames_and_tf.md §5 | — | — | TEST-M2-05, TEST-M2-06 | PASS (odometry signs; accuracy is M4) |
| REQ-M2-12 | DEC-025, DEC-026, DEC-027, DEC-029 | CALC-M2-04 | controller YAML, `amr_bringup/src/cmd_vel_guard.cpp` | TEST-M2-07 | PASS; wall-clock hazard (TS-015) fixed by DEC-029, re-test 1 PASS |
| REQ-M2-13 | DEC-025 | CALC-M1-12, CALC-M2-03 | controller YAML *(planned)* | TEST-M2-08 | FAIL (TS-014), re-test 1 PASS |
| REQ-M2-14 | DEC-013, DEC-024 | CALC-M2-01, -02 | Gazebo surface tags in `amr.ros2_control.xacro` *(planned)* | TEST-M2-02, TEST-M2-05, TEST-M2-06, TEST-M2-08 | re-test 1 / re-test 2 PASS (DEC-024, DEC-028) |
| REQ-M2-15 | ROADMAP M2 | — | teleop launch or command *(planned)* | TEST-M2-09 | PASS 2026-11-03 (observed by me) |
| REQ-M2-16 | DEC-019 (OPEN-07) | CALC-M1-11, -12 | simulation launch *(planned)* | TEST-M2-10 | PASS 2026-11-03 (quantitative re-test 1 3/3; no jitter observed by me); OPEN-07 finalized unchanged (DEC-019) |
| REQ-M2-17 | DEC-009, DEC-010 | — | `docs/` | TEST-M2-11 | TEST-M2-11 FAIL (TS-020), re-test 1 PASS |

## M3 — Sensors (design decisions Accepted 2026-11-03, DEC-030 to DEC-037; feasibility gate passed; milestone In Progress since 2026-11-03)

Plan: [milestones/M3_sensors.md](milestones/M3_sensors.md); analysis and test specification: [design/sensors.md](design/sensors.md) (§7 = DEC-036).

| ID | Requirement | Acceptance criterion |
|---|---|---|
| REQ-M3-01 | The M3 packages build | `colcon build` of `amr_description` and `amr_bringup` exits 0, with no warnings for those packages |
| REQ-M3-02 | M3 additions preserve the M1/M2 baselines (DEC-034) | `use_sensors` off (default): expansion byte-identical to `TEST-M1-02_amr.urdf`, and the M2 enabled expansion unchanged. `use_sensors` on: M1 geometry and inertials unchanged; total mass 9.4 kg; the generated SDF contains no link with zero mass or zero inertia |
| REQ-M3-03 | Sensor frames exist at the decided poses | TF `lidar_mount_link → laser_frame` = (0, 0, +0.030) (DEC-030) and `base_link → imu_link` = (0, 0, 0) (DEC-032), identity rotation, to 1e-6 (DEC-036 D5) |
| REQ-M3-04 | LiDAR scans are published in ROS (DEC-031) | `/scan` `sensor_msgs/msg/LaserScan`, `frame_id` `laser_frame`, simulation-time stamps, 360 samples over −π to +π, 0.12–12.0 m, 10 Hz (DEC-036 D1–D4) |
| REQ-M3-05 | IMU data is published in ROS (DEC-032) | `/imu` `sensor_msgs/msg/Imu`, `frame_id` `imu_link`, simulation-time stamps, 100 Hz (DEC-036 D1–D3) |
| REQ-M3-06 | Ideal simulated encoder feedback is available (DEC-033) | `/joint_states` contains both wheel positions at the rate measured in the feasibility gate (100 Hz, sensors.md §6.1; DEC-036 D2). It is documented as ideal simulated feedback, not a hardware encoder model |
| REQ-M3-07 | LiDAR ranges are accurate and the noise model is as configured | Bias ≤ 0.010 m at the target distances; noise σ_r = 0.01 m confirmed statistically (DEC-036 S1–S4) |
| REQ-M3-08 | The LiDAR field of view is as designed (DEC-030) | 360° detection; no self-returns; the blind zone below the 0.230 m scan plane is characterized and recorded for M8 (DEC-036 D6–D8) |
| REQ-M3-09 | The IMU is correct at rest (DEC-032) | Specific force +g on +Z; bias within limits; noise σ_ω = 0.001 rad/s, σ_a = 0.01 m/s² confirmed statistically (DEC-036 D9, S1–S4) |
| REQ-M3-10 | The IMU is correct in motion | Gyro z within ±3 % of the ground-truth yaw rate; accel x sign and magnitude within ±20 % (DEC-036 D10–D11) |
| REQ-M3-11 | The encoder feedback is consistent with motion | Mean wheel travel within ±2 % of ground truth; correct signs (DEC-036 D12) |
| REQ-M3-12 | Sensors can be visualized with installed tools (DEC-035) | RViz LaserScan aligned with the world targets, and TF frames `laser_frame`/`imu_link` (observed by me); IMU validated through topics |
| REQ-M3-13 | M2 motion is preserved with sensors on | The TEST-M2-05, -06 and -07 (stop, timeout) modes pass the DEC-027 criteria with sensors enabled |
| REQ-M3-14 | Documentation, configuration and evidence are consistent | TEST-M3-12 finds zero mismatches; every executed test has a record and indexed evidence |
| REQ-M3-15 | The published IMU output is the 10-sample block mean of a 1 kHz IMU, with defined stamp, startup and missing-sample semantics (DEC-038, accepted 2026-11-03) | Output = mean of its 10 raw samples, newest raw stamp, full blocks only; counters 0; braking correct sign and within ± 20 % (TEST-M3-13, -14; `docs/design/sensors.md` §8) |

## M3 traceability matrix

| Requirement | Design decision / property | Calculation | Implementation | Test | Result |
|---|---|---|---|---|---|
| REQ-M3-01 | DEC-008, DEC-023 | — | `amr_description`, `amr_bringup` | TEST-M3-01 | PASS ([TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M3-02 | DEC-023 pattern, DEC-034 | — | `urdf/amr.sensors.xacro`, `use_sensors` in `urdf/amr.urdf.xacro` | TEST-M3-02 | FAIL (TS-024), re-test 1 PASS |
| REQ-M3-03 | DEC-016, DEC-030, DEC-032 | CALC-M3-01, -02 | `urdf/amr.sensors.xacro` (`laser_joint`, `imu_joint`) | TEST-M3-03 | FAIL (TS-025), re-test 1 PASS |
| REQ-M3-04 | DEC-031, DEC-034 | CALC-M3-01 | `amr.sensors.xacro`, `config/sensor_bridge.yaml`, `sim.launch.py sensors:=true` | TEST-M3-04 | PASS ([TEST_RESULTS.md](../TEST_RESULTS.md)) |
| REQ-M3-05 | DEC-032, DEC-034 | CALC-M3-02 | `amr.sensors.xacro`, `config/sensor_bridge.yaml`, `sim.launch.py sensors:=true` | TEST-M3-04 | PASS |
| REQ-M3-06 | DEC-033, DEC-026 | CALC-M3-03 | `controllers.yaml` (existing) | TEST-M3-04, TEST-M3-09 | PASS (TEST-M3-04; TEST-M3-09 3/3) |
| REQ-M3-07 | DEC-031, DEC-036 | CALC-M3-01 | `worlds/sensor_test.sdf` (targets, test_plan §7.1) | TEST-M3-05 | PASS |
| REQ-M3-08 | DEC-030, DEC-031, blind-zone item | CALC-M3-01 | `worlds/sensor_test.sdf` (targets, test_plan §7.1) | TEST-M3-06 | PASS |
| REQ-M3-09 | DEC-032, DEC-036 | CALC-M3-02 | `amr.sensors.xacro` (IMU) | TEST-M3-07 | PASS |
| REQ-M3-10 | DEC-032, DEC-036 | CALC-M3-02 | `amr.sensors.xacro` (IMU) | TEST-M3-08 | FAIL (D11, TS-027), kept; corrected by DEC-038, R2 PASS 2026-11-04 |
| REQ-M3-11 | DEC-033, DEC-036 | CALC-M3-03 | `/joint_states` (existing) | TEST-M3-09 | PASS (3/3) |
| REQ-M3-12 | DEC-035 | — | `amr_bringup/rviz/sensors.rviz` | TEST-M3-10 | PASS 2026-11-04 (observed by me) |
| REQ-M3-13 | DEC-024 to DEC-029, DEC-034 | — | `sim.launch.py sensors:=true` (`sensor_test.sdf`) | TEST-M3-11 | PASS 2026-11-04 (3/3 per mode) |
| REQ-M3-14 | DEC-009, DEC-010 | — | `docs/`, `docs/evidence/M3/TEST-M3-12_consistency_check.py` | TEST-M3-12 | FAIL (TS-032), R1 PASS 2026-11-04 |
| REQ-M3-15 | DEC-038 | sensors.md §8 | `amr_gazebo_plugins` (ImuBlockAverager, ImuDecimator); `amr.sensors.xacro` | TEST-M3-13, TEST-M3-14 | PASS 2026-11-04 (TEST-M3-13 R1, TEST-M3-14 R1 and (g)) |

## Between M3 and M4 — Test automation (DEC-040; scope accepted 2026-11-04)

Plan: [milestones/M3-M4_test_automation.md](milestones/M3-M4_test_automation.md). `REQ-TA` = test-automation step (not a milestone). No pass criterion of M1–M3 changes.

| ID | Requirement | Acceptance criterion |
|---|---|---|
| REQ-TA-01 | Harness threads stop before ROS shuts down (TS-030) | One helper in `TEST-M2_motion_measure.py` is used by the four formal harnesses. Order: stop flag, join, then executor/node/context shutdown. The thread-end state is printed. The Gazebo-free reproduction gives 0 thread exceptions in 1000 teardowns. |
| REQ-TA-02 | Stop distance reported with known timing (DEC-040 (d)) | Stop mode prints the zero-command-to-braking latency and the interpolated stop distance as INFO. The DEC-027 criteria are unchanged. |
| REQ-TA-03 | A milestone suite runs serially and is cross-checked | `tools/run_suite.py` as specified in the plan §5: process pre-check, no overwrite, exit-code vs `# overall:` MISMATCH flag, TS-029 count, summary table, never records PASS. |
| REQ-TA-04 | The harness changes cause no regression | The re-run set of plan §6 passes, through the runner, with the original criteria. Every run reports the spin thread "ended cleanly". |
| REQ-TA-05 | GPU-free checks run on GitHub on code changes only | `.github/workflows/ci.yml` as specified in the plan §7. It passes on a code push; a documentation-only push starts no run; minutes per run are measured. |

## Test automation traceability matrix

| Requirement | Design decision | Implementation | Test | Result |
|---|---|---|---|---|
| REQ-TA-01 | DEC-040 (c); TS-030 | `docs/evidence/M2/TEST-M2_motion_measure.py` helper and its four users | TEST-TA-01, TEST-TA-04 | TEST-TA-01 PASS 2026-11-04; TEST-TA-04 PASS 2026-11-04 (55/55 ended cleanly) |
| REQ-TA-02 | DEC-040 (d) | `mode_stop` in `TEST-M2_motion_measure.py` | TEST-TA-04 | PASS 2026-11-04 (INFO in all 6 stop runs) |
| REQ-TA-03 | DEC-040 (a), item 5 | `tools/run_suite.py` | TEST-TA-02, TEST-TA-03 | TEST-TA-02 PASS; TEST-TA-03 FAIL (TS-033), R1 PASS (2026-11-04) |
| REQ-TA-04 | DEC-040 (c); DEC-027, DEC-036, DEC-038, DEC-039 | `tools/run_suite.py` suite `regression` | TEST-TA-04 | PASS 2026-11-04 (20/20 entries, logs reviewed) |
| REQ-TA-05 | DEC-040 (b), item 3 | `.github/workflows/ci.yml`; `tools/run_suite.py` suites `ci`, `records` | TEST-TA-05 | FAIL (run 1, TS-034), then PASS 2026-11-04 |

## M4 — Odometry (plan accepted 2026-11-13; DEC-042 to DEC-045)

Plan and analysis (CALC-M4-01 to -03): [milestones/M4_odometry.md](milestones/M4_odometry.md). Criteria: DEC-044. Results only in [TEST_RESULTS.md](../TEST_RESULTS.md) (DEC-041).

| ID | Requirement | Acceptance criterion |
|---|---|---|
| REQ-M4-01 | The odometry integration matches the documented kinematics with the configured r and b | Independent recomputation from recorded `/joint_states` equals `/odom` within 1 mm and 0.01° (TEST-M4-03) |
| REQ-M4-02 | Odometry interface | `/diff_drive_controller/odom`, `odom` → `base_footprint`, 50 Hz ± 2 %, sim-time stamps; exactly one TF publisher of `odom → base_footprint`; TF equals odometry within 1 mm / 0.1° (TEST-M4-02, -11) |
| REQ-M4-03 | Linear accuracy | 2 m straight: distance error ≤ 0.5 %, heading error ≤ 0.5° (TEST-M4-04) |
| REQ-M4-04 | Rotational accuracy | 360° in place: yaw error ≤ 1.0° per turn, translation ≤ 20 mm (TEST-M4-05) |
| REQ-M4-05 | Closed-path accuracy | 1 m square CW and CCW, 1 m-radius circle: end-point position ≤ 20 mm, yaw ≤ 1.0° (TEST-M4-06, -07) |
| REQ-M4-06 | Velocity accuracy | Odometry twist mean within ± 2 % of ground truth in cruise, sign correct (TEST-M4-08) |
| REQ-M4-07 | Covariance configured and not zero | Pose and twist covariance diagonals equal the DEC-042 values (TEST-M4-02, -12) |
| REQ-M4-08 | The tests detect calibration errors | Each DEC-043 injected error fails its target test with the CALC-M4-02 prediction within ± 25 % (TEST-M4-09) |
| REQ-M4-09 | No M1–M3 regression | Build clean; M1 default expansion byte-identical; the product controller configuration differs from M2 only in the covariances; M2 suite and M3 static checks pass (TEST-M4-01, -10) |
| REQ-M4-10 | Records consistent under DEC-041 | TEST-M4-12 finds zero mismatches |
| REQ-M4-11 | Automation | `m4` suite in `tools/run_suite.py`; TEST-M4-03 and -12 run in CI (TEST-M4-12) |

## M4 traceability matrix

| Requirement | Design decision | Calculation | Implementation | Test | Result |
|---|---|---|---|---|---|
| REQ-M4-01 | DEC-016, DEC-026 | CALC-M4-01 | `diff_drive_controller` (installed); `docs/evidence/M4/TEST-M4-03_recompute.py` | TEST-M4-03 | PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task A) |
| REQ-M4-02 | DEC-016, DEC-026 | — | `controllers.yaml` | TEST-M4-02, TEST-M4-11 | TEST-M4-02 PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task B); TEST-M4-11 PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task D) |
| REQ-M4-03 | DEC-044 | CALC-M4-02, -03 | — | TEST-M4-04 | PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task C) |
| REQ-M4-04 | DEC-044 | CALC-M4-02, -03 | — | TEST-M4-05 | PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task C) |
| REQ-M4-05 | DEC-044 | CALC-M4-02, -03 | — | TEST-M4-06, TEST-M4-07 | PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task C) |
| REQ-M4-06 | DEC-044 | — | — | TEST-M4-08 | PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task C) |
| REQ-M4-07 | DEC-042 | CALC-M4-04 | `controllers.yaml` | TEST-M4-02, TEST-M4-12 | TEST-M4-02 PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task B); TEST-M4-12 PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task D) |
| REQ-M4-08 | DEC-043 | CALC-M4-02, CALC-M4-05 | `docs/evidence/M4/TEST-M4-09_procedure.sh` (run-time override copies) | TEST-M4-09 | PASS 2026-11-13; R1 PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task D) |
| REQ-M4-09 | DEC-023, DEC-045 | — | — | TEST-M4-01, TEST-M4-10 | TEST-M4-01 PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task B); TEST-M4-10 PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task D) |
| REQ-M4-10 | DEC-041 | — | `docs/evidence/M4/TEST-M4-12_consistency_check.py` | TEST-M4-12 | PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task D) |
| REQ-M4-11 | DEC-040 | — | `tools/run_suite.py`, `.github/workflows/ci.yml` | TEST-M4-12 | PASS 2026-11-13 ([TEST_RESULTS.md](../TEST_RESULTS.md) § M4 Task D) |
