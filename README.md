# Smart Factory AMR

[![ROS 2 Jazzy](https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros)](https://docs.ros.org/en/jazzy/)
[![Gazebo Harmonic](https://img.shields.io/badge/Gazebo-Harmonic-F58113)](https://gazebosim.org/docs/harmonic)
[![Ubuntu 24.04](https://img.shields.io/badge/Ubuntu-24.04-E95420?logo=ubuntu&logoColor=white)](https://releases.ubuntu.com/24.04/)
![C++ | Python](https://img.shields.io/badge/code-C%2B%2B%20%7C%20Python-3776AB)
[![ci](https://github.com/Nikhil-Jangid/smart-factory-amr/actions/workflows/ci.yml/badge.svg)](https://github.com/Nikhil-Jangid/smart-factory-amr/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

I am building an autonomous mobile robot (AMR) for a smart-factory setting, from an empty workspace up to
navigation and task automation, in simulation first. The robot model, controllers, sensor plugins, test harnesses
and CI are my own. I treat it as an engineering project rather than a tutorial: every parameter has a recorded source,
every decision has a recorded rationale, and every result is backed by a log in this repository.

<table>
  <tr>
    <td><a href="docs/gallery/M6/TEST-M6-05/TEST-M6-05-forward_a1_gazebo.mp4"><img src="docs/gallery/M6/TEST-M6-05/TEST-M6-05-forward_a1_gazebo.png" alt="Gazebo: the AMR driving the test route in the arena"></a></td>
    <td><a href="docs/gallery/M6/TEST-M6-05/TEST-M6-05-forward_a1_rviz.mp4"><img src="docs/gallery/M6/TEST-M6-05/TEST-M6-05-forward_a1_rviz.png" alt="RViz: AMCL localizing the robot on the saved map while the odometry drifts"></a></td>
  </tr>
  <tr>
    <td align="center"><sub>Gazebo: the true motion on the 28.8 m test route (TEST-M6-05). Click for the video.</sub></td>
    <td align="center"><sub>RViz: AMCL keeps the robot on the saved map although its wheel odometry is deliberately miscalibrated.</sub></td>
  </tr>
</table>

---

## Contents
[Status](#status) · [Highlights](#highlights) · [Gallery](#gallery) · [The robot](#the-robot) · [Architecture](#architecture) ·
[Milestones](#milestones-in-detail) · [Key decisions](#key-decisions) · [How I test](#how-i-test) ·
[Problems I solved](#problems-i-solved) · [Repository layout](#repository-layout) · [Quick start](#quick-start) ·
[Project tracking](#project-tracking)

## Status

| Milestone | What | Status |
|---|---|---|
| M0 | Development environment (Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic) | ✅ Done |
| M1 | Custom differential-drive robot model (URDF/Xacro, RViz, Gazebo) | ✅ Done |
| M2 | Basic movement (`ros2_control`, diff drive, command guard) | ✅ Done |
| M3 | Sensors (2D LiDAR, IMU, wheel encoders) | ✅ Done |
| — | Test automation (suite runner, GitHub Actions CI) | ✅ Done |
| M4 | Wheel odometry, verified against Gazebo ground truth | ✅ Done |
| M5 | SLAM (`slam_toolbox`), map verified against the world file | ✅ Done |
| M6 | Localization (AMCL on the saved map, optional wheel + IMU fusion) | ✅ Done |
| M7 | Autonomous navigation (Nav2) | ⏭️ Next |
| M8 | Obstacle avoidance (incl. a low-obstacle depth camera) | ⚪ Planned |
| M9 | Factory environment | ⚪ Planned |
| M10 | Task automation (pickup and delivery) | ⚪ Planned |
| M11 | Vision (AprilTag / station identification) | ⚪ Planned |
| M12 | Dashboard | ⚪ Planned |
| M13 | Physical robot | ⚪ Optional |

Full checklist: [ROADMAP.md](ROADMAP.md). Every executed test, including the failures: [TEST_RESULTS.md](TEST_RESULTS.md).

```mermaid
flowchart LR
  M0[M0 Environment] --> M1[M1 Model] --> M2[M2 Movement] --> M3[M3 Sensors] --> TA[Test automation] --> M4[M4 Odometry]
  M4 --> M5[M5 SLAM] --> M6[M6 Localization] --> M7[M7 Nav2] --> M8[M8 Obstacles] --> M9[M9 Factory] --> M10[M10 Tasks]
  M10 --> M11[M11 Vision] --> M12[M12 Dashboard] -.-> M13[M13 Hardware]
  classDef done fill:#2e7d32,color:#fff,stroke:#1b5e20;
  classDef next fill:#f9a825,color:#000,stroke:#f57f17;
  class M0,M1,M2,M3,TA,M4,M5,M6 done;
  class M7 next;
```

## Highlights

- **My own robot, not a stock model.** I designed a 9.4 kg differential-drive base with a rear caster and a LiDAR
  bracket. Its masses and inertias are calculated by hand and checked against the generated URDF and SDF
  ([mass_inertia.md](docs/design/mass_inertia.md), [mechanical_geometry.md](docs/design/mechanical_geometry.md)).
- **A custom Gazebo system plugin in C++.** Gazebo's IMU missed the robot's own acceleration (aliasing: the 100 Hz
  drive command reaches the chassis as one-step spikes). I wrote `ImuDecimator`, which samples at 1 kHz and publishes
  10-sample block means at 100 Hz, with correctly scaled noise and covariance and 13 unit tests. Braking deceleration is
  now within 0.39 % of ground truth ([DEC-038](DECISIONS.md), [TS-027](docs/troubleshooting.md)).
- **An upstream Gazebo bug, found and reported.** An intermittent `gz sim` shutdown deadlock, diagnosed from a gdb stack
  trace and reported as [gazebosim/gz-sim#4173](https://github.com/gazebosim/gz-sim/issues/4173). Until it is fixed, a
  narrow, documented invalid-run rule keeps my tests honest ([DEC-039](DECISIONS.md)).
- **Wheel odometry verified against ground truth, with injected-error sensitivity tests.** The errors on straight
  lines, in-place turns, squares and circles are 100–1000× below their bounds. To prove the bounds are not vacuous, I
  inject 1 % radius, 2 % track and 0.5 % single-wheel calibration errors. Each is detected, at the size the kinematics
  predicts, within 1 % ([TEST-M4-09](TEST_RESULTS.md)).
- **SLAM maps checked against the world, not by eye.** An offline checker compares each saved map with the walls
  and obstacles in the world file: 95 % of the wall cells lie within 0.07 m of the true surface, no ghost walls, the
  arena within 0.02 m of its true size, and the SLAM pose within 13.5 mm of ground truth at every stop
  ([TEST-M5-03/-04](TEST_RESULTS.md)). With deliberately wrong odometry (0.20 m and 3.5° of drift) SLAM still keeps
  the pose within 36 mm ([TEST-M5-06](TEST_RESULTS.md)), and the checker itself is shown to fail rotated, shifted,
  scaled, erased and ghosted maps ([TEST-M5-07](TEST_RESULTS.md)). Along the way I found that SLAM Toolbox saves its
  maps half a cell (0.025 m) off ([TS-041](docs/troubleshooting.md), [DEC-055](DECISIONS.md)).
- **Localization verified against ground truth, plus a second upstream bug.** AMCL localizes the robot on the saved
  map within 13.2 mm and 0.14° at every stop of the route, in both directions (bound 50 mm / 1°,
  [TEST-M6-03](TEST_RESULTS.md)). It holds within 34 mm while the wheel odometry drifts 0.44 m from injected calibration
  errors ([TEST-M6-05](TEST_RESULTS.md)) and within 12 mm with unmapped boxes in the arena ([TEST-M6-06](TEST_RESULTS.md)).
  An optional EKF fuses the wheel odometry with the IMU yaw rate and cuts the drift from 400 mm to under 10 mm
  ([TEST-M6-07](TEST_RESULTS.md)). From the source code I found that Nav2 AMCL reads the map origin differently from
  the rest of ROS (half a cell off), gave AMCL its own corrected map copy, and reported it as
  [ros-navigation/navigation2#6833](https://github.com/ros-navigation/navigation2/issues/6833) ([TS-045](docs/troubleshooting.md), [DEC-062](DECISIONS.md)).
- **A safety guard for commands.** `cmd_vel_guard` (C++) drops velocity commands whose stamp is stale in *simulation*
  time. I found that wall-clock-stamped commands would otherwise never time out ([TS-015](docs/troubleshooting.md),
  [DEC-029](DECISIONS.md)).
- **Reproducible testing.** 77 test IDs with written procedures, pass criteria fixed *before* each run, a suite runner
  that refuses unsafe runs, and GitHub Actions for the GPU-free checks. Failures are kept, not hidden.

## Gallery

Stills link to the videos (MP4). The test-run captures come from formal test runs; the demonstrations re-create what
an earlier, headless test covered. Details: [docs/gallery/README.md](docs/gallery/README.md).

| | Gazebo (true motion) | RViz (robot's view) |
|---|---|---|
| **M1:** the model and its TF frames | [<img src="docs/gallery/M1/TEST-M1-06/m1_gazebo_spawn_demo_gazebo.png" width="380">](docs/gallery/M1/TEST-M1-06/m1_gazebo_spawn_demo_gazebo.png) | [<img src="docs/gallery/M1/TEST-M1-04/m1_rviz_model_demo_rviz.png" width="380">](docs/gallery/M1/TEST-M1-04/m1_rviz_model_demo_rviz.png) |
| **M2:** forward, stop, reverse | [<img src="docs/gallery/M2/TEST-M2-05/m2_linear_demo_gazebo.png" width="380">](docs/gallery/M2/TEST-M2-05/m2_linear_demo_gazebo.mp4) | [<img src="docs/gallery/M2/TEST-M2-05/m2_linear_demo_rviz.png" width="380">](docs/gallery/M2/TEST-M2-05/m2_linear_demo_rviz.mp4) |
| **M2:** in-place rotation, both ways | [<img src="docs/gallery/M2/TEST-M2-06/m2_rotate_demo_gazebo.png" width="380">](docs/gallery/M2/TEST-M2-06/m2_rotate_demo_gazebo.mp4) | [<img src="docs/gallery/M2/TEST-M2-06/m2_rotate_demo_rviz.png" width="380">](docs/gallery/M2/TEST-M2-06/m2_rotate_demo_rviz.mp4) |
| **M3:** LiDAR scan of the test targets | [<img src="docs/gallery/M3/TEST-M3-10/m3_lidar_demo_gazebo.png" width="380">](docs/gallery/M3/TEST-M3-10/m3_lidar_demo_gazebo.mp4) | [<img src="docs/gallery/M3/TEST-M3-10/m3_lidar_demo_rviz.png" width="380">](docs/gallery/M3/TEST-M3-10/m3_lidar_demo_rviz.mp4) |
| **M4:** 1 m square, odometry trail | [<img src="docs/gallery/M4/TEST-M4-06/m4_square_demo_gazebo.png" width="380">](docs/gallery/M4/TEST-M4-06/m4_square_demo_gazebo.mp4) | [<img src="docs/gallery/M4/TEST-M4-06/m4_square_demo_rviz.png" width="380">](docs/gallery/M4/TEST-M4-06/m4_square_demo_rviz.mp4) |
| **M4:** circle, v 0.2 m/s, ω 0.2 rad/s | [<img src="docs/gallery/M4/TEST-M4-07/m4_circle_demo_gazebo.png" width="380">](docs/gallery/M4/TEST-M4-07/m4_circle_demo_gazebo.mp4) | [<img src="docs/gallery/M4/TEST-M4-07/m4_circle_demo_rviz.png" width="380">](docs/gallery/M4/TEST-M4-07/m4_circle_demo_rviz.mp4) |
| **M5:** mapping the arena with SLAM Toolbox | [<img src="docs/gallery/M5/TEST-M5-09/TEST-M5-09_a1_gazebo.png" width="380">](docs/gallery/M5/TEST-M5-09/TEST-M5-09_a1_gazebo.mp4) | [<img src="docs/gallery/M5/TEST-M5-03/TEST-M5-03_a1_rviz.png" width="380">](docs/gallery/M5/TEST-M5-03/TEST-M5-03_a1_rviz.mp4) |
| **M5:** SLAM corrects deliberately wrong odometry | [<img src="docs/gallery/M5/TEST-M5-06/TEST-M5-06_a1_gazebo.png" width="380">](docs/gallery/M5/TEST-M5-06/TEST-M5-06_a1_gazebo.mp4) | [<img src="docs/gallery/M5/TEST-M5-06/TEST-M5-06_a1_rviz.png" width="380">](docs/gallery/M5/TEST-M5-06/TEST-M5-06_a1_rviz.mp4) |
| **M6:** AMCL localization on the saved map | [<img src="docs/gallery/M6/TEST-M6-03/TEST-M6-03-forward_a1_gazebo.png" width="380">](docs/gallery/M6/TEST-M6-03/TEST-M6-03-forward_a1_gazebo.mp4) | [<img src="docs/gallery/M6/TEST-M6-03/TEST-M6-03-forward_a1_rviz.png" width="380">](docs/gallery/M6/TEST-M6-03/TEST-M6-03-forward_a1_rviz.mp4) |
| **M6:** recovery from a wrong start (0.5 m, 15°) | [<img src="docs/gallery/M6/TEST-M6-10/TEST-M6-10-wrongstart_a1_gazebo.png" width="380">](docs/gallery/M6/TEST-M6-10/TEST-M6-10-wrongstart_a1_gazebo.mp4) | [<img src="docs/gallery/M6/TEST-M6-10/TEST-M6-10-wrongstart_a1_rviz.png" width="380">](docs/gallery/M6/TEST-M6-10/TEST-M6-10-wrongstart_a1_rviz.mp4) |
| **M6:** wheel odometry + IMU fused by an EKF | [<img src="docs/gallery/M6/TEST-M6-07/TEST-M6-07-R1_a1_gazebo.png" width="380">](docs/gallery/M6/TEST-M6-07/TEST-M6-07-R1_a1_gazebo.mp4) | [<img src="docs/gallery/M6/TEST-M6-07/TEST-M6-07-R1_a1_rviz.png" width="380">](docs/gallery/M6/TEST-M6-07/TEST-M6-07-R1_a1_rviz.mp4) |
| **M4:** injected 2 % track error: the odometry over-turns | [<img src="docs/gallery/M4/TEST-M4-09/TEST-M4-09-R1_L_square_ccw_a1_gazebo.png" width="380">](docs/gallery/M4/TEST-M4-09/TEST-M4-09-R1_L_square_ccw_a1_gazebo.mp4) | [<img src="docs/gallery/M4/TEST-M4-09/TEST-M4-09-R1_L_square_ccw_a1_rviz.png" width="380">](docs/gallery/M4/TEST-M4-09/TEST-M4-09-R1_L_square_ccw_a1_rviz.mp4) |

## The robot

<p align="center"><img src="docs/design/amr_geometry_drawing.svg" alt="Dimensioned top and side views of the AMR (mm)" width="640"></p>

I didn't draw this by hand: I wrote [`tools/geometry_drawing.py`](tools/geometry_drawing.py) to generate it from the
same Xacro properties that build the simulated robot, so every dimension shown is the one the model actually uses, and
`--check` tells me if the drawing or the design table ever drifts from the model.

| Property | Value | Source |
|---|---|---|
| Drive | Differential drive, two wheels + rear caster | DEC-005, DEC-013 |
| Chassis (L × W × H) | 0.450 × 0.350 × 0.120 m, 0.050 m ground clearance | `amr_properties.xacro` |
| Wheels | radius 0.075 m, width 0.035 m, track 0.400 m | `amr_properties.xacro` |
| Total mass | 9.4 kg (chassis 8.0, wheels 2 × 0.5, caster 0.2, LiDAR bracket 0.2) | CALC-M1-11 |
| Speed limits | +0.5 / −0.25 m/s, ±1.0 rad/s | DEC-025, `controllers.yaml` |
| Acceleration limits | 0.5 m/s² (braking 1.0 m/s²), 2.0 rad/s² | DEC-025 |
| Control rate | 100 Hz controller, 1 ms physics step, odometry at 50 Hz | DEC-026 |
| Command timeout | 0.5 s, in simulation time (guard + controller) | DEC-026, DEC-029 |
| LiDAR | 360°, 360 samples, 10 Hz, 0.12–12 m, σ 0.01 m, scan plane 0.230 m | DEC-030, DEC-031 |
| IMU | 1 kHz raw, 100 Hz output (10-sample block mean), σ gyro 0.001 rad/s, σ accel 0.01 m/s² | DEC-032, DEC-038 |
| Encoders | wheel joint positions via `joint_state_broadcaster` | DEC-033 |
| Odometry covariance | from an assumed 1 % distance / 2 % rotation error model | DEC-042, CALC-M4-04 |
| SLAM | `slam_toolbox` online asynchronous mode, 0.05 m map cells | DEC-048, `slam_toolbox.yaml` |
| Localization | `nav2_amcl` on the saved map, motion noise from the odometry error model; optional `robot_localization` EKF | DEC-056, DEC-057, DEC-061, `amcl.yaml`, `ekf.yaml` |

Values are owned by the Xacro properties and the controller configuration; the documents name them, and checkers
compare the two. Every parameter is labelled **Selected**, **Proposed**, **Assumed**, **Calculated**, **Measured** or
**Verified** ([docs/README.md](docs/README.md)).

## Architecture

```mermaid
flowchart LR
  subgraph Gazebo[Gazebo Harmonic]
    phys[DART physics, 1 ms]
    lidar[gpu_lidar 10 Hz]
    imu[IMU 1 kHz + ImuDecimator plugin]
    gzrc[gz_ros2_control]
  end
  teleop[teleop / test harness] -- /cmd_vel TwistStamped --> guard[cmd_vel_guard]
  guard -- fresh commands only --> ddc[diff_drive_controller]
  ddc --> gzrc
  gzrc --> jsb[joint_state_broadcaster]
  jsb -- /joint_states --> rsp[robot_state_publisher]
  ddc -- /diff_drive_controller/odom + TF odom→base_footprint --> rviz[RViz]
  rsp -- TF --> rviz
  lidar -- ros_gz_bridge /scan --> rviz
  imu -- ros_gz_bridge /imu --> ekf[optional EKF]
  ddc -- odometry --> ekf
  phys -- /clock --> bridge[ros_gz_bridge /clock]
  lidar -- /scan --> slam[slam_toolbox]
  slam -- /map + TF map→odom --> rviz
  mapsrv[map_server: saved map] -- /map_amcl --> amcl[AMCL]
  lidar -- /scan --> amcl
  amcl -- TF map→odom, /amcl_pose --> rviz
```

SLAM (mapping) and AMCL (localization on the saved map) are alternatives: only one of them publishes `map → odom`.

```mermaid
flowchart TD
  map --> odom --> base_footprint --> base_link
  base_link --> left_wheel_link
  base_link --> right_wheel_link
  base_link --> caster_link
  base_link --> lidar_mount_link --> laser_frame
  base_link --> imu_link
```

Frames follow REP-103/REP-105 ([frames_and_tf.md](docs/design/frames_and_tf.md)); nodes and packages:
[ros_architecture.md](docs/architecture/ros_architecture.md).

## Milestones in detail

<details>
<summary><b>M1: Custom AMR model</b> (✅ 2026-10-21)</summary>

- **Built:** package `amr_description`: a properties file, inertia macros, the URDF/Xacro model, an RViz display
  launch and a Gazebo spawn launch. Primitive geometry only.
- **Tests:** TEST-M1-01 to -08: build, Xacro expansion, generated-model properties (52 checks on URDF and SDF), RViz TF
  values and wheel direction, TF tree, Gazebo spawn, rest stability, and a documentation/code consistency review
  (84 checks, 0 mismatches).
- **Failures kept:** TEST-M1-03 first run (a check script that matched XML comments, TS-007) and TEST-M1-08 first run
  (xacro's header path broke a byte comparison, TS-010).
- Plan and record: [M1_custom_amr.md](docs/milestones/M1_custom_amr.md) · evidence: [docs/evidence/M1](docs/evidence/M1)
</details>

<details>
<summary><b>M2: Basic movement</b> (✅ 2026-11-03)</summary>

- **Built:** package `amr_bringup`: `ros2_control` hardware via `gz_ros2_control`, `diff_drive_controller`,
  `joint_state_broadcaster`, the `/clock` bridge, the `cmd_vel_guard` node and `sim.launch.py`.
- **Tests:** TEST-M2-01 to -11: forward/reverse, rotation, stop, timeout, limits, manual teleop (observed by me) and
  rest stability (Δz 0.000 mm, drift 0.000 mm over 30 s).
- **Failures kept:** in-place rotation was 9 % larger than commanded with cylinder wheels in DART; fixed with sphere
  wheel collisions (TS-014, DEC-028). Reverse braking used the wrong limit until the reverse parameters were set
  explicitly (TS-012).
- Plan and record: [M2_basic_movement.md](docs/milestones/M2_basic_movement.md) · criteria:
  [motion_control.md](docs/design/motion_control.md)
</details>

<details>
<summary><b>M3: Sensors</b> (✅ 2026-11-04)</summary>

- **Built:** `amr.sensors.xacro` (LiDAR, IMU, sensor frames), a sensor test world with targets at 1, 3 and 6 m, the
  `ros_gz_bridge` configuration, and package `amr_gazebo_plugins` with the `ImuDecimator` system plugin.
- **Tests:** TEST-M3-01 to -14: LiDAR range bias ≤ 1.0 mm with the specified noise at 1, 3 and 6 m; field of view and
  the characterized 0.230 m blind zone; IMU noise, gravity and braking; encoder distance; RViz (observed by me); the M2
  regression with sensors on.
- **Failures kept:** TEST-M3-08 failed on braking acceleration before the plugin (TS-027); several harness defects
  are recorded with their fixes.
- Plan and record: [M3_sensors.md](docs/milestones/M3_sensors.md) · design: [sensors.md](docs/design/sensors.md)
</details>

<details>
<summary><b>Test automation</b> (✅ 2026-11-04)</summary>

- **Built:** [`tools/run_suite.py`](tools/run_suite.py) (serial suites, leftover-process check, unique run tags,
  exit-code vs `# overall:` cross-check, summary tables) and [GitHub Actions CI](.github/workflows/ci.yml) in the
  official `ros:jazzy-ros-base` container.
- **Tests:** TEST-TA-01 to -05, including a full formal regression re-run through the runner.
- **Failure kept:** the first CI run failed on a shallow checkout (TS-034).
- Plan and record: [M3-M4_test_automation.md](docs/milestones/M3-M4_test_automation.md)
</details>

<details>
<summary><b>M4: Odometry</b> (✅ 2026-11-13)</summary>

- **Built:** the odometry covariance model, an odometry test harness with ground truth from Gazebo, an offline
  recomputation checker for the controller's integration rule, the `m4` suite, and an RViz odometry view.
- **Tests:** TEST-M4-01 to -11: recomputation of the controller's integration (700 of 700 messages, max difference 0.000000 mm), TF consistency,
  straight/rotate/square/circle accuracy, twist accuracy, injected-error sensitivity, regression of M2 and M3
  (20 of 20 entries), and the RViz trail (observed by me).
- **Found:** the published twist is about 0.2 % high (systematic; the pose is not affected), and a 1 ms stamp offset
  between odometry and joint states in about 7 % of the cycles (TS-035).
- Plan and record: [M4_odometry.md](docs/milestones/M4_odometry.md)
</details>

<details>
<summary><b>M5: SLAM</b> (✅ 2026-11-15)</summary>

- **Built:** a purpose-built 10 × 8 m mapping arena with asymmetric features at known positions, `slam.launch.py`
  with SLAM Toolbox in online asynchronous mode, an RViz mapping view, a route follower steered by Gazebo ground truth
  (so every run drives the same path), an offline map checker that reads the world file, and the committed reference
  map with its pose graph.
- **Tests:** TEST-M5-01 to -10: build and regression identity, the SLAM interface, map accuracy and pose accuracy
  (three runs), save and reload with Nav2 `map_server`, mapping with injected odometry error, checker sensitivity,
  regression of M2–M4, live mapping in RViz (observed by me), and records and CI.
- **Failures kept:** TEST-M5-02 failed once on a `gz sim` exit code after shutdown with the GUI (TS-039, re-run clean).
  **Found:** SLAM Toolbox writes the centre of the first map cell where ROS expects its corner, so its maps are
  shifted 0.025 m (TS-041; the reference map is corrected, DEC-055).
- **Limitation, stated:** in a 10 × 8 m arena with a 12 m LiDAR, scan matching removes the drift continuously, so
  loop closure is not exercised; it is verified later in a larger environment (DEC-052).
- Plan and record: [M5_slam.md](docs/milestones/M5_slam.md)
</details>

<details>
<summary><b>M6: Localization</b> (✅ 2026-11-21)</summary>

- **Built:** `localization.launch.py` with Nav2 AMCL on the M5 reference map (two map servers, see below), AMCL motion
  noise derived from the odometry error model instead of the defaults, an optional `robot_localization` EKF
  (`ekf:=true`) that fuses wheel odometry with the IMU yaw rate, an RViz localization view, a test-only arena with
  unmapped boxes, an offline pose checker and the `m6` suite.
- **Tests:** TEST-M6-01 to -11: build and regression identity, the localization interface, accuracy on the route in
  both directions, recovery from a wrong start, deliberately wrong odometry, unmapped obstacles, EKF fusion, checker
  sensitivity, regression of M1–M5, RViz (observed by me), and records and CI.
- **Failures kept:** TEST-M6-07 once failed on a dropped parameter reply (a checker defect, TS-047); TEST-M6-04 failed
  in the suite run when one wrong-start run needed 4.84 m to recover against a 4.0 m bound. I measured 10 more runs
  before changing anything and restated the bound from 21 runs (DEC-065).
- **Found:** Nav2 AMCL reads the map origin as the centre of the first cell, ROS as its corner; AMCL gets its own
  copy of the map, shifted half a cell, while every other consumer keeps the correct map (TS-045, DEC-062, reported
  upstream).
- **Limitations, stated:** a known start pose is required, because global localization locks onto a pose turned by a
  half turn in this nearly symmetric arena (DEC-058); a wrong start may take up to 6 m to correct (DEC-065).
- Plan and record: [M6_localization.md](docs/milestones/M6_localization.md)
</details>

## Key decisions

All decisions, with the alternatives and trade-offs: [DECISIONS.md](DECISIONS.md).

| ID | Decision | Why |
|---|---|---|
| DEC-005 | My own AMR instead of a stock robot (TurtleBot3) | The design work is part of the project |
| DEC-011 | Wheel track 0.400 m, wheels outside the chassis | A single-box chassis without wheel wells |
| DEC-023 | `amr_description` + `amr_bringup`; `ros2_control` included only on request | M1 model stays byte-identical; checked in CI |
| DEC-028 | Sphere wheel collisions | Cylinder–plane contact in DART turned 9 % too far |
| DEC-029 | `cmd_vel_guard` with a simulation-time timeout | Wall-clock stamps never expire in simulation |
| DEC-030/031 | 360° LiDAR, scan plane at 0.230 m | 30 mm above the highest robot part, so the view is unobstructed; the low blind zone is measured and handed to M8 |
| DEC-037 | A forward depth camera for low obstacles, in M8 | The LiDAR alone cannot see below its plane |
| DEC-038 | IMU at 1 kHz, block mean to 100 Hz | Fixes the acceleration aliasing at its source |
| DEC-039 | Narrow invalid-run rule for the upstream shutdown deadlock | Open and recorded, instead of quietly re-running |
| DEC-040 | Suite runner + CI for GPU-free checks | Cheap checks run on every code push |
| DEC-042 | Odometry covariance from an error model | Downstream fusion (M6) gets honest uncertainty |
| DEC-044 | Odometry bounds: straight 0.5 % / 0.5°, turns 1°, closed paths 20 mm / 1° | 30–50× margin over the simulated error, yet the injected errors exceed them 2–7× |
| DEC-046 | A purpose-built mapping arena with features at known positions | The map can be checked cell by cell against the world file |
| DEC-049 | The test route is driven on ground truth, not odometry | The system under test is SLAM; the same path makes runs comparable |
| DEC-052 | Loop closure not claimed in M5 | The small arena cannot exercise it; a test should not claim what it cannot observe |
| DEC-056 | AMCL for localization | Nav2 is built around it, and it checks the M5 map with a second method |
| DEC-061 | AMCL motion noise from the odometry error model, not the defaults | The defaults gave up to 140 mm of error at rest; the derived values keep it near 10 mm |
| DEC-062 | AMCL gets its own half-cell-shifted map copy | Fixes an upstream origin mismatch without moving the map for RViz and Nav2 |
| DEC-065 | Wrong-start recovery bound restated from 21 measured runs | A failed bound is re-measured before it is changed |

## How I test

1. **Criteria first.** Each test has a written procedure and pass criteria in
   [test_plan.md](docs/testing/test_plan.md) *before* it runs; criteria are not changed to get a pass.
2. **Static checks, then simulation.** Xacro, URDF/SDF and configuration checks run without a GUI; Gazebo tests
   measure against ground truth (the world pose from Gazebo), at least three runs each.
3. **Ground truth, not self-agreement.** Odometry is compared with Gazebo's pose, the IMU with the true acceleration,
   and the LiDAR with known target distances.
4. **Sensitivity checks.** Test bounds are shown to catch real faults (injected calibration errors, mutation checks
   on checkers).
5. **Honest records.** Test states are only `PLANNED`, `NOT RUN`, `PASS`, `FAIL` and `BLOCKED`. Failures stay in the
   record with a diagnosis and a re-test. GUI checks are recorded as "observed by me".
6. **Automation.** `tools/run_suite.py` runs suites serially and refuses to start when a simulation is still running;
   CI runs the build, the unit tests, the model regression (including M1 byte identity), the odometry recomputation
   and the map- and pose-checker sensitivity tests.
   Gazebo sensor tests stay local, because hosted runners have no GPU.

## Problems I solved

| Problem | Diagnosis | Fix |
|---|---|---|
| Robot rotated 196° for a 180° command | Cylinder–plane contact in DART | Sphere wheel collisions (TS-014, DEC-028) |
| Commands never timed out | `cmd_vel` stamped in wall time vs simulation time | `cmd_vel_guard` (TS-015, DEC-029) |
| `/gz_ros_control` ran on wall time | The plugin's own node had no `use_sim_time` entry | `use_sim_time` for that node in `controllers.yaml` (TS-018) |
| IMU read ≈ 0 m/s² while the robot braked | Sampling aliasing of one-step acceleration spikes | `ImuDecimator` plugin (TS-027, DEC-038) |
| Plugin refused to start in a world file | It validated in `Configure()`, before the world's physics component existed | Validation moved to the first `PreUpdate()` (TS-028) |
| Rare `gz sim` hang on shutdown | Upstream deadlock (gdb trace) | Reported upstream, invalid-run rule (TS-029, DEC-039) |
| A low LiDAR "saw" through the chassis | `gpu_lidar` is rendering-based: near clip and back-face culling | Scan plane kept above the body; lower mounts need a masked sector (TS-022) |
| Saved SLAM maps were 0.025 m off | SLAM Toolbox writes the first cell's centre as the map origin, ROS expects its corner | Reference map origin corrected and re-verified (TS-041, DEC-055) |
| AMCL saw every wall 0.025 m off on a correct map | Nav2 AMCL reads the map origin as the centre of cell 0 (found in its source) | Separate half-cell-shifted map copy for AMCL; reported upstream (TS-045, DEC-062) |
| Regression of a closed milestone failed on the next milestone's approved changes | The build-identity test compared against the working tree | Each identity test checks only its own milestone's increment (TS-049, DEC-064) |
| Test harness fell up to 0.7 s behind simulation time | rclpy processing every 1 kHz `/clock` message | Simulation time taken from the Gazebo pose stream (TS-013) |

All 48 entries, including the small ones: [docs/troubleshooting.md](docs/troubleshooting.md).

## Repository layout

```
amr_ws/src/
  amr_description/        robot model: properties, inertia macros, URDF/Xacro, sensors, display/spawn launches
  amr_bringup/            simulation bring-up: sim.launch.py, slam.launch.py, localization.launch.py, controllers,
                          AMCL and EKF configuration, bridge, worlds, maps, RViz configs, cmd_vel_guard
  amr_gazebo_plugins/     ImuDecimator Gazebo system plugin + unit tests
tools/                    suite runner, capture and demo scripts, geometry drawing generator
docs/
  design/                 geometry, mass/inertia, frames/TF, motion control, sensors
  architecture/           ROS architecture and milestone boundaries
  milestones/             plan and implementation record per milestone
  testing/test_plan.md    procedures and criteria for every test
  evidence/               logs, check scripts and summaries behind every result
  gallery/                screenshots and videos per milestone and test
  requirements.md         requirements and traceability
  troubleshooting.md      every significant issue: symptom, diagnosis, fix, verification
DECISIONS.md              engineering decisions (context, alternatives, rationale, consequences)
TEST_RESULTS.md           every executed test, including failures
ROADMAP.md                milestones M0–M13
```

## Quick start

Requirements: Ubuntu 24.04, ROS 2 Jazzy and Gazebo Harmonic (exact versions:
[docs/environment.md](docs/environment.md)).

```bash
git clone https://github.com/Nikhil-Jangid/smart-factory-amr.git
cd smart-factory-amr
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths amr_ws/src --ignore-src -y
cd amr_ws && colcon build --symlink-install && source install/setup.bash && cd ..

# The model in RViz
ros2 launch amr_description display.launch.py

# Simulation with controllers (add sensors:=true world:=sensor_test.sdf for the sensor world)
ros2 launch amr_bringup sim.launch.py
# Mapping instead: the arena with sensors, SLAM (second terminal) and the mapping view (third terminal)
#   ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf
#   ros2 launch amr_bringup slam.launch.py
#   rviz2 -d $(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz/mapping.rviz --ros-args -p use_sim_time:=true
# Localization on the saved map instead of SLAM (add ekf:=true, with the fusion controllers file, for the EKF):
#   ros2 launch amr_bringup sim.launch.py sensors:=true world:=mapping_arena.sdf
#   ros2 launch amr_bringup localization.launch.py
#   rviz2 -d $(ros2 pkg prefix amr_bringup)/share/amr_bringup/rviz/localization.rviz --ros-args -p use_sim_time:=true
# Drive it (another terminal)
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true -p frame_id:=base_footprint -p use_sim_time:=true -r cmd_vel:=/cmd_vel

# The GPU-free test suite (what CI runs)
python3 -I tools/run_suite.py ci local1
```

## Project tracking

I plan and track the work in a private Jira project (milestones as epics, bounded tasks with acceptance criteria).
The engineering facts (parameters, decisions, results and evidence) all live in this repository.

A note on the records: this repository is a clean copy of my development history, so the revision hashes quoted in
the test records and logs refer to my development repository. The records-consistency checkers (TEST-M2-11,
TEST-M3-12, TEST-M4-12, TEST-M5-10, TEST-M6-11) also check private planning files, so their scripts and logs are not included.

## License and contact

Code and documentation: [Apache License 2.0](LICENSE).
Nikhil Jangid · [GitHub @Nikhil-Jangid](https://github.com/Nikhil-Jangid)
