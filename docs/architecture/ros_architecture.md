# ROS Architecture and Milestone Boundaries

**Status:** `amr_ws/` and the `amr_description` package exist (TEST-M1-01 PASS). The Xacro robot model exists (TEST-M1-02 PASS, TEST-M1-03 re-test 1 PASS). The RViz display launch and configuration exist (TEST-M1-04/05 PASS). The Gazebo spawn launch exists (TEST-M1-06/07 PASS).

## 1. Workspace and packages

| Package | Build type | Responsibility | Introduced | Status |
|---|---|---|---|---|
| `amr_description` | `ament_cmake` (installs data only) | Robot model (Xacro/URDF), RViz config, M1 display and Gazebo spawn launch files. From M2: the conditional `use_ros2_control` option (`ros2_control` system, Gazebo control plugin, contact surfaces), default off (DEC-023) | M1 | Accepted (DEC-017, DEC-023); package, Xacro model, display and Gazebo launch files, and RViz config created; M2 option not yet implemented |
| `amr_bringup` | `ament_cmake` | Integration: controller configuration (`config/controllers.yaml`), the M2 simulation launch (`launch/sim.launch.py`; M3 adds the `sensors` and `world` arguments, whose defaults keep the M2 launch, plus `config/sensor_bridge.yaml` and `worlds/sensor_test.sdf`, DEC-034), and the C++ command-freshness guard `cmd_vel_guard` (DEC-029). Depends on `amr_description`; never the reverse | M2 | Accepted (DEC-023, DEC-029); created 2026-10-22 (`26a6048`) |
| `amr_gazebo_plugins` | `ament_cmake` (C++) | Gazebo Sim system plugins. `ImuDecimator` (DEC-038): the 1 kHz IMU on the Gazebo-internal `/imu_raw` becomes the 100 Hz block mean on Gazebo `/imu`, which `sensor_bridge` maps to ROS `/imu` unchanged. The Gazebo-independent `ImuBlockAverager` is unit-tested. Loaded from the model (`amr.sensors.xacro`, use_sensors only) through `GZ_SIM_SYSTEM_PLUGIN_PATH`. No ROS dependency; kept out of `amr_bringup` so that a hardware bringup need not depend on Gazebo | M3 | Accepted (DEC-038); created 2026-11-03 |

Further packages (for example a Gazebo world package) will be added only when a milestone needs them. Each addition is recorded in `DECISIONS.md`. Nothing is created in advance.

### `amr_description` layout (DEC-017, Accepted; everything below exists)
```
amr_ws/src/amr_description/
├── package.xml
├── CMakeLists.txt
├── urdf/
│   ├── amr.urdf.xacro          top level: links and joints
│   ├── amr_properties.xacro    all dimensions and masses (single source of truth for code)
│   └── inertial_macros.xacro   box / cylinder / sphere inertia macros
├── launch/
│   ├── display.launch.py       robot_state_publisher + joint_state_publisher_gui + rviz2
│   └── gazebo.launch.py        gz sim (empty world) + ros_gz_sim create from /robot_description
└── rviz/
    └── display.rviz
```

`package.xml` dependencies (planned 2026-10-19; implemented as listed in M1 step 1):
- `buildtool_depend`: `ament_cmake`
- `exec_depend`: `xacro`, `robot_state_publisher`, `joint_state_publisher`, `joint_state_publisher_gui`, `rviz2`, `ros_gz_sim`, `launch`, `launch_ros`

All of these are installed ([../environment.md](../environment.md)). `ros_gz_bridge` is not needed until M2.

## 2. M1 runtime graph

**RViz display check:**
```
amr.urdf.xacro ──xacro──▶ robot_state_publisher ──▶ /robot_description, /tf_static, /tf ──▶ rviz2
                                    ▲
joint_state_publisher_gui ──/joint_states──┘
```

**Gazebo spawn check:**
```
robot_state_publisher ──/robot_description──▶ ros_gz_sim create ──▶ Gazebo Sim (empty world)
```

There are no wheel joint states or `/clock` bridge in M1 (see [frames_and_tf.md §4](../design/frames_and_tf.md)).

## 3. Milestone boundaries

| Milestone | Adds (planned) | Explicitly not before |
|---|---|---|
| M1 | Robot description, RViz display, Gazebo spawn and rest | — |
| M2 | `ros2_control`, `gz_ros2_control`, `diff_drive_controller`, `joint_state_broadcaster`, `cmd_vel`, teleop, `/clock` bridge, friction parameters | after M1 passes |
| M3 | Simulated LiDAR, IMU, wheel-encoder data; sensor bridges; RViz sensor displays | after M2 |
| M4 | Odometry validation and quantitative tests | after M3 |
| M5 / M6 | SLAM Toolbox mapping; localization on a saved map | after M4 |
| M7 / M8 | Nav2 configuration, costmaps, planners, obstacle avoidance | after M6 |
| M9 | Factory/warehouse world | after M7 (may be prepared earlier only if needed for testing) |
| M10–M12 | Task automation, station vision, dashboard | after M8/M9 |
| M13 | Optional physical hardware | optional |

Installed packages for later milestones (Nav2, SLAM Toolbox, ros2_control) are **not integrated** and are not evidence of working functionality.
