# Development Environment

**Status:** The versions below were captured by TEST-M0-05 on 2026-10-19 ([evidence log](evidence/M0/TEST-M0-05_environment_inventory.log)), updated after the apt upgrade of 2026-11-18 (§ Upgrade 2026-11-18). Functional M0 verification is TEST-M0-01 to TEST-M0-04 (see [`../TEST_RESULTS.md`](../TEST_RESULTS.md)).

This is the single source of truth for environment and dependency versions. Update it whenever the toolchain changes.

## Platform

| Item | Value | Source |
|---|---|---|
| OS | Ubuntu 24.04.5 LTS (native install, not a VM or container) | `lsb_release -ds` |
| Kernel | 7.0.0-43-generic (7.0.0-38 at TEST-M0-05) | `uname -r` |
| ROS 2 | Jazzy, binary install at `/opt/ros/jazzy`, sourced from `~/.bashrc` | `$ROS_DISTRO`, `~/.bashrc` |
| Gazebo | Gazebo Sim 8.15.0 (Harmonic) | `gz sim --version` |
| Python | 3.12.3 | `python3 --version` |
| CMake | 3.28.3 | `cmake --version` |
| colcon | `python3-colcon-common-extensions` 0.3.0-100 | `dpkg -l` |

## ROS middleware and networking

| Variable | Value at M0 verification |
|---|---|
| `RMW_IMPLEMENTATION` | unset (Jazzy default Fast DDS; `ros-jazzy-rmw-fastrtps-cpp` 8.4.4 installed) |
| `ROS_DOMAIN_ID` | unset (defaults to 0) |
| `ROS_AUTOMATIC_DISCOVERY_RANGE` | `SUBNET` |

Note: with `SUBNET` discovery and domain 0, other ROS 2 machines on the same network can see this machine's topics. Revisit if that causes interference.

## Installed ROS 2 / Gazebo packages (from `dpkg -l`, 2026-10-19; upgraded rows from `dpkg-query`, 2026-11-18)

| Package | Version | First milestone that uses it |
|---|---|---|
| `ros-jazzy-demo-nodes-cpp` | 0.33.11 | M0 (verified) |
| `ros-jazzy-rviz2` | 14.1.24 | M0 (verified), M1 (verified, TEST-M1-04) |
| `ros-jazzy-ros-gz` | 1.0.25 (1.0.24 until 2026-11-18) | M0 (verified) |
| `ros-jazzy-ros-gz-bridge` | 1.0.25 (1.0.24 until 2026-11-18) | M0 (verified, TEST-M0-04 and re-test 1), M2 |
| `ros-jazzy-ros-gz-sim` | 1.0.25 (1.0.24 until 2026-11-18) | M1 (verified, TEST-M1-06/07) |
| `ros-jazzy-xacro` | 2.1.1 | M1 (verified, TEST-M1-02/08) |
| `ros-jazzy-urdf` | 2.10.1 | M1 (verified indirectly through `robot_state_publisher`, TEST-M1-04) |
| `ros-jazzy-robot-state-publisher` | 3.3.4 | M1 (verified, TEST-M1-04/05) |
| `ros-jazzy-joint-state-publisher` | 2.4.3 | M1 (verified indirectly: imported by `joint_state_publisher_gui`, TEST-M1-04) |
| `ros-jazzy-joint-state-publisher-gui` | 2.4.3 | M1 (verified, TEST-M1-04, observed by me) |
| `ros-jazzy-sdformat-urdf` | 1.0.2 | M1 (candidate; not used in M1, which loads no SDF through the URDF parser; not exercised) |
| `ros-jazzy-tf2-ros` | 0.36.23 | M1 (verified, `tf2_echo`, TEST-M1-04) |
| `ros-jazzy-tf2-tools` | 0.36.23 | M1 (verified, `view_frames`, TEST-M1-05) |
| `ros-jazzy-launch-ros` | 0.26.13 | M1 (verified, TEST-M1-04/06) |
| `ros-jazzy-ros2-control` | 4.50.0 (4.48.1 until 2026-11-18) | M2 |
| `ros-jazzy-ros2-controllers` | 4.43.1 (4.42.1 until 2026-11-18) | M2 |
| `ros-jazzy-diff-drive-controller` | 4.43.1 (4.42.1 until 2026-11-18) | M2 |
| `ros-jazzy-gz-ros2-control` | 1.2.20 | M2 |
| `ros-jazzy-teleop-twist-keyboard` | 2.4.1 | M2 |
| `ros-jazzy-slam-toolbox` | 2.8.5 | M5 |
| `ros-jazzy-navigation2` | 1.3.14 (1.3.13 until 2026-11-18) | M7 |
| `ros-jazzy-nav2-bringup` | 1.3.14 (1.3.13 until 2026-11-18) | M7 |
| `ros-jazzy-nav2-amcl`, `ros-jazzy-nav2-map-server`, `ros-jazzy-nav2-lifecycle-manager` | 1.3.14 | M5 (`map_server`, TEST-M5-05), M6 |
| `ros-jazzy-robot-localization` | 3.8.4 | M6 |
| `graphviz` | 2.42.2 | M1 (diagram generation; verified, TEST-M1-03/05 PDFs) |

Build dependencies of `amr_gazebo_plugins` (M3, DEC-038; versions from `dpkg-query`, 2026-11-03). They were already installed with ROS 2 Jazzy; nothing new was installed. Verified by TEST-M3-01 re-test 2 (build) and TEST-M3-13 (gtest):

| Package | Version | Use |
|---|---|---|
| `ros-jazzy-gz-sim-vendor` | 0.0.13 | Gazebo Sim 8 headers and `gz-sim::core` (system plugin API) |
| `ros-jazzy-gz-plugin-vendor` | 0.0.5 | `gz-plugin::register` (`GZ_ADD_PLUGIN`) |
| `ros-jazzy-gz-transport-vendor` | 0.0.9 | gz-transport 13 (`/imu_raw` subscription, `/imu` publication) |
| `ros-jazzy-gz-msgs-vendor` | 0.0.8 | gz-msgs 10 (`gz.msgs.IMU`) |
| `ros-jazzy-ament-cmake-gtest` | 2.5.7 (2.5.6 until 2026-11-18) | Unit tests (TEST-M3-13) |

The plugin is found by Gazebo through `GZ_SIM_SYSTEM_PLUGIN_PATH`. The package's environment hook prepends `<install>/amr_gazebo_plugins/lib` when `amr_ws/install/setup.bash` is sourced.

Command-line tools:
- **Captured in TEST-M0-05:** `check_urdf` and `urdf_to_graphviz` (`/opt/ros/jazzy/bin`), `gz` (`/opt/ros/jazzy/opt/gz_tools_vendor/bin/gz`), and `ros2`.
- **Observed during the 2026-10-19 M1 planning session but not captured in TEST-M0-05:**
  - `gz sdf` and `gz model`: their `--help` usage text was printed.
  - `ros_gz_sim create`: listed by `ros2 pkg executables ros_gz_sim`.
  - `tf2_tools view_frames`: listed by `ros2 pkg executables tf2_tools`.

  None of these four had been run functionally at that point. All four have since been run in M1: `gz sdf -p` (TEST-M1-03), `view_frames` (TEST-M1-05), and `ros_gz_sim create` and `gz model --list` / `-m -p` (TEST-M1-06/07, 2026-10-21).
- **2026-10-19 M1 design review:**
  - `gz sdf -p` was run functionally on a generic probe URDF, not the AMR model, with exit 0. `gz sdf --versions` reports 14.9.0, and `gz sdf -d 1.11` printed the SDFormat 1.11 specification. Details are in [design/frames_and_tf.md §4](design/frames_and_tf.md#4-gazebo-specific-behaviour).
  - `gz model --help` was re-read to check the `--list`, `-m`, and `-p` options.
- **2026-10-21:** run against a live simulation for the first time.
  - `gz model --list` prints `Available models:` with one `- <name>` line per model.
  - `gz model -m <model> -p` prints `Pose [ XYZ (m) ] [ RPY (rad) ]` to 6 decimals, without a timestamp.
  - `gz topic -e -t /world/<world>/pose/info -n 1` gives the model poses at full precision as quaternions, stamped with sim time.
  - `/world/<world>/stats` gives `sim_time`, `real_time` and `real_time_factor`.
  - The stock `empty.sdf` world is `/opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/worlds/empty.sdf`: world `empty`, 1 ms step, real-time-factor target 1.0.

**Installed is not the same as working.** Only the items marked "verified" have been exercised: the M0 items, and the M1 items as of 2026-10-21 (repository audit). Everything else has only been confirmed as installed.

## Screenshots and screen recording (gallery; verified 2026-11-13)
- Desktop: GNOME on Wayland, two monitors (HDMI-1 1920×1080 at +0+0, eDP-1 1536×864). The window manager (mutter) ignores a requested window position.
- Gazebo GUI and RViz are started as X11 (XWayland) windows with `QT_QPA_PLATFORM=xcb`, because the capture tools work on X11 windows only. A whole-screen `ximagesrc` capture of the XWayland root is black.
- Stills: Gazebo through its own `/gui/screenshot` service (GUI Screenshot plugin, in the default gz-sim 8 GUI config); RViz with `xwd` (x11-apps 7.7+11build3), converted to PNG in `tools/sim_capture.py`.
- Video: GStreamer 1.24.2 (`gstreamer1.0-plugins-good` 1.24.2-1ubuntu1.8): `ximagesrc xid=<window>` → `vp9enc` → `webmmux`, one file per window (`tools/sim_record.sh`). ffmpeg 6.1.1-3ubuntu5 (with libx264) installed by me on 2026-11-13: recordings are converted to H.264 MP4 (`tools/sim_record.sh`). Not installed: wf-recorder. A live side-by-side `compositor` pipeline failed (WebM mux rejects the caps change), so the windows are recorded separately.

## Continuous integration (GitHub Actions; DEC-040, verified by TEST-TA-05 on 2026-11-04)
- Workflow `.github/workflows/ci.yml`, job `gpu-free`: hosted `ubuntu-latest` runner, container `ros:jazzy-ros-base` (Ubuntu 24.04, ROS 2 Jazzy). Packages come from `rosdep install --from-paths amr_ws/src` (all dependency types), plus `git` and `procps`, which are installed before `actions/checkout` (`fetch-depth: 0`, TS-034).
- Runs `tools/run_suite.py ci` (TEST-M3-01, -13, -02; TEST-M4-03 from 2026-11-13) on pushes to `main` that change `amr_ws/**`, `tools/**`, `docs/evidence/**/*.py|*.sh` or `.github/workflows/**`. It can also be started by hand (`gh workflow run ci.yml`).
- No GPU: the Gazebo sensor tests stay local (DEC-040 item 4). Logs are uploaded as an artifact for 7 days; CI never records a test result.
- About 3 min per run (Measured; about 115 s of it is the dependency install). Job timeout 10 min. The account's monthly allowance is shown in GitHub Settings → Billing; the hard stop against paid usage is the account's $0 Actions budget, set on 2026-11-04 (DEC-040 amendment). No dependency cache.

## Upgrade 2026-11-18 (user, `apt-get upgrade`, 19:53–19:54 IST)
- 381 `ros-jazzy-*` packages changed. Version changes that the project uses: ros2_control / `controller_manager` / `hardware_interface` 4.48.1 → 4.50.0; ros2_controllers (`diff_drive_controller`, `joint_state_broadcaster`) 4.42.1 → 4.43.1; ros_gz (bridge, sim) 1.0.24 → 1.0.25; Nav2 (`nav2_amcl`, `nav2_map_server`, `nav2_lifecycle_manager`, `nav2_bringup`) 1.3.13 → 1.3.14; `robot_localization` 3.8.3 → 3.8.4; `rclcpp` 28.1.22 → 28.1.23; `rclpy` 7.1.12 → 7.1.13; `rmw_fastrtps_cpp` 8.4.4 → 8.4.5. Rebuilt at the same version: `gz_sim_vendor` 0.0.13 (Gazebo Sim still 8.15.0), `gz_ros2_control` 1.2.20, `slam_toolbox` 2.8.5, `xacro`, `rviz2`, `robot_state_publisher`, `tf2_ros`. Source: `/var/log/apt/history.log`.
- Re-verification: clean rebuild of `amr_ws` (exit 0), then the `static`, `regression`, `m4` and `m5` suites on the upgraded packages, results in `TEST_RESULTS.md` (§ Environment re-verification 2026-11-18). Findings: TS-043 (records checkers and the batch's own unindexed logs), TS-044 (one controller-load failure at start-up, not reproduced in 30 launches; open, monitoring).

Workspace layout: see DEC-008 in [`../DECISIONS.md`](../DECISIONS.md).
