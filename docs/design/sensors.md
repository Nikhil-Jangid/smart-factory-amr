# Sensors: M3 Design Analysis

**Status:** design items **decided** by me on 2026-11-03: DEC-030 to DEC-036 (`DECISIONS.md`). The decided values are **Selected**, and the IMU noise values are **Assumed** (simulation assumptions, DEC-032). The M3 milestone stays **Proposed** until the feasibility gate (§6) passes. **Feasibility gate G1–G6: PASS on 2026-11-03 (§6.1).** I finalized the Task breakdown on 2026-11-03, and M3 is **In Progress**; Task A (sensor model) is implemented and verified (TEST-M3-01 to -03; [M3 plan](../milestones/M3_sensors.md) §11). §4 keeps the original proposals for traceability; where the decision differs, the decision governs.
**Related:** [M3 plan](../milestones/M3_sensors.md) · OPEN-03 and the blind-zone item · OPEN-13 to OPEN-18 · DEC-014, DEC-016, DEC-019, DEC-023, DEC-026 · [frames_and_tf.md](frames_and_tf.md) §5 · [mechanical_geometry.md](mechanical_geometry.md) CALC-M1-14 · [mass_inertia.md](mass_inertia.md)

Units are SI, and frames follow REP-103 (+X forward, +Y left, +Z up). Parameter labels are defined in [../README.md](../README.md). Numeric model values are owned by `amr_properties.xacro`, and they are quoted here by property name. Since M3 Task A (2026-11-03), the sensor values of DEC-030 to DEC-032 (frame offsets, LiDAR and IMU parameters) are owned by the named properties in `amr_description/urdf/amr.sensors.xacro` (`laser_frame_z`, `imu_frame_z`, `lidar_*`, `imu_*`). They are kept out of `amr_properties.xacro` because xacro copies that file's comments into the default output, which must stay byte-identical to M1 (DEC-034).

## 1. Background: what the M3 sensors are
- **2D LiDAR.** A rotating laser rangefinder that measures the distance to the nearest surface along N beams in one horizontal plane (the *scan plane*). ROS publishes each sweep as `sensor_msgs/msg/LaserScan`:
  - `angle_min`/`angle_max`, `angle_increment`, `range_min`/`range_max` and one range per beam;
  - angles are measured counter-clockwise about +Z of the sensor frame, from +X.
  - M5 (SLAM) and M8 (obstacle avoidance) consume it.
- **IMU (inertial measurement unit).** It measures angular velocity (gyroscope) and *specific force* (accelerometer: acceleration minus gravity). An IMU at rest on level ground therefore reads about +9.8 m/s² on its +Z axis, not 0. ROS uses `sensor_msgs/msg/Imu`. M6 (localization, EKF) fuses it with wheel odometry.
- **Wheel encoders.** They measure wheel rotation. In simulation the wheel joint position from `gz_ros2_control` (`/joint_states`, M2) already is an ideal, continuous encoder reading. M3 decides whether this is enough (OPEN-15).
- **How Gazebo Harmonic simulates sensors.** Sensors are declared in SDF and run by world *system plugins*:
  - `gz-sim-sensors-system` runs rendering-based sensors such as `gpu_lidar` and needs a render engine (`ogre2`).
  - `gz-sim-imu-system` runs IMUs.
  - Gazebo publishes on Gazebo Transport, and `ros_gz_bridge` converts the messages to ROS topics (as for `/clock` in M2).

## 2. Installed-software facts (checked 2026-11-03, read-only)
| Fact | Source | Status |
|---|---|---|
| Gazebo Sim 8.15.0 | `gz sim --version` | Verified (M0) |
| `libgz-sim8-sensors-system.so` and `libgz-sim8-imu-system.so` present | `/opt/ros/jazzy/opt/gz_sim_vendor/lib/` | Installed, **not exercised** |
| `ogre2` render engine library present (`libgz-rendering8-ogre2.so`) | `/opt/ros/jazzy/opt/gz_rendering_vendor/lib/` | Installed, **not exercised** |
| `gz sim` has a `--headless-rendering` option | `gz sim --help` | Listed, **not exercised** |
| Stock `empty.sdf` loads physics, user-commands, scene-broadcaster and contact systems only, **no sensors or IMU system**; it sets no `<gravity>` element | the world file | Verified (read) |
| `ros_gz_bridge` 1.0.24, `ros_gz_sim` 1.0.24, `gz_sensors_vendor` 0.0.6, `rviz_default_plugins` 14.1.24 | `dpkg -l` | Installed (bridge verified in M2 for `/clock`) |
| `ros-jazzy-rviz-imu-plugin` **not installed**; apt candidate 2.1.6 | `apt-cache policy` | Verified (read) |
| GPU: Intel Iris Xe (Alder Lake-UP3 GT2) | `lspci` | Verified (read) |
| `gpu_lidar` (`ogre2`) and the IMU system run in `gz sim -s --headless-rendering` on this GPU, RTF 0.998 / 1.000 | feasibility gate §6.1 | **Verified** (2026-11-03, 2 runs) |
| `gz sdf` warns that `<gz_frame_id>` is "not defined in SDF" but copies it, and Gazebo then uses it as the message `frame_id` | feasibility gate §6.1 | **Verified**; the warning is expected and harmless |
| With an `<sensor type="imu">` in the model, `gz_ros2_control` logs `IMU sensor 'imu' not found in hardware_info, skipping` | feasibility gate launch logs | **Verified**; harmless: the IMU is published by the Gazebo IMU system and `ros_gz_bridge`, not by `ros2_control` (DEC-034) |
| Gazebo angle step = (max − min)/(samples − 1); exact 1° steps with 360 samples need `max_angle` = −π + 359° = 3.12413936106985 rad (179°), not +π | feasibility gate §6.1 (`angle_increment` 0.017453292 = 1.000000°) | **Verified** |

**Assumptions resolved by the feasibility gate (§6.1, 2026-11-03):**
- A1: `gpu_lidar` produces valid scans on this machine in headless runs (`-s --headless-rendering`). **Verified headless.** GUI runs were not part of the gate; the GUI check is TEST-M3-10 (observed by me).
- A2: the SDF `<gz_frame_id>` sensor element sets the `frame_id` of the bridged messages in this Gazebo version. Without it, Gazebo uses scoped names such as `amr::base_footprint::laser`. **Verified:** `/scan` `laser_frame`, `/imu` `imu_link`.
- A3: a sensor declared on a massless fixed-joint child link (`laser_frame`, `imu_link`) keeps its pose after the URDF→SDF fixed-joint lumping (frames_and_tf.md §4). **Verified:** lidar (0.070, 0, 0.230) m and IMU (0, 0, 0.075) m in `base_footprint`.
- A4: the SDFormat default gravity (0, 0, −9.8) m/s² applies to the stock world, which sets none. **Verified:** mean accel z +9.8005 / +9.7999 m/s² at rest.

## 3. Calculations

### CALC-M3-01: LiDAR scan plane, self-occlusion and blind zone (supports OPEN-03 and the blind-zone item)
**Inputs (Selected unless noted; `amr_properties.xacro`):**
- `wheel_radius` r = 0.075 m.
- `ground_clearance` c = 0.050 m.
- `chassis_height` h_c = 0.120 m; `chassis_length` 0.450 m; `chassis_width` 0.350 m.
- `axle_offset_x` 0.100 m.
- `lidar_mount_x` = +0.070 m and `lidar_bracket_z` = 0.030 m (provisional, OPEN-03).
- **Proposed:** laser optical-centre offset d_L = +0.030 m above the bracket top (OPEN-03).

**Heights above flat ground:**
- Wheel top: 2r = **0.150 m**.
- Chassis top: c + h_c = **0.170 m**.
- Bracket top (`lidar_mount_link` origin): 0.170 + 0.030 = **0.200 m** (matches CALC-M1-14).
- Scan plane: h_s = 0.200 + d_L = **0.230 m** (Calculated from the Proposed d_L).

**Self-occlusion:** no robot body part extends above 0.200 m, so a horizontal scan plane at 0.230 m intersects no part of the robot. A full 360° field of view is unobstructed (Calculated; verified by TEST-M3-06).

**Footprint relative to the laser** (in x/y; for orientation only, since the plane clears the body):
- Chassis front edge +0.055 m ahead; rear edge −0.395 m.
- Rear corners at (−0.395, ±0.175) m, i.e. 0.432 m from the laser.

**Ground clearance of the beams under pitch:**
- A beam that is level at h_s reaches the floor at range h_s / tan θ when the robot pitches by θ.
- M2's attitude criterion is < 1° (DEC-027), giving 0.230 / tan 1° = **13.18 m**.
- With the proposed `range_max` 12.0 m, a 1° pitch lowers the far end of a beam by 12 · tan 1° = **0.2095 m**. That stays 0.020 m above the floor.
- *Reasonableness:* the margin is small. Raising `range_max` above about 13 m, or pitch above 1°, would create floor returns. The measured M2 pitch at rest was ~0°.

**Blind zone (consequence for M8):** obstacles lower than h_s = 0.230 m are **not detected**, and neither are overhangs above the plane. M3 records and characterizes this blind zone (TEST-M3-06); mitigation (e.g. a depth camera or a lower plane) is out of scope until M8. The options were compared on 2026-11-03 in [M3 plan §12](../milestones/M3_sensors.md) (CALC-M3-04 self-occlusion per plane height, plus scratch Gazebo runs). Decided by DEC-037: a forward depth camera in M8; the 0.230 m plane is unchanged.

**Angular resolution at range:** 1.0° spacing gives 0.052 m between adjacent beams at 3 m. A 0.10 m-wide target at 3 m is hit by at least 1 beam.

### CALC-M3-02: IMU placement kinematics (supports OPEN-14)
- Proposed placement: `imu_link` at the `base_link` origin with identity rotation, i.e. the midpoint of the wheel axle, 0.075 m above ground and inside the chassis volume (chassis z range −0.025 to +0.095 m in `base_link`).
- **Pure rotation:** a differential drive rotates in place about the vertical axis through the axle midpoint. At that point the centripetal (ω²·ρ) and tangential (α·ρ) accelerations are **zero** (ρ = 0). The IMU then reads only gravity and the rotation rate, which makes TEST-M3-08 a clean check.
- **Straight acceleration:** the accelerometer x reads the commanded acceleration, ≤ 0.5 m/s² (DEC-025).
- **Expected values** (with gravity g = 9.8 m/s², A4):
  - at rest: a = (0, 0, +9.8) m/s², ω = (0, 0, 0);
  - in-place rotation at ω_z = 0.5 rad/s: ω_z = +0.5 rad/s for counter-clockwise rotation (REP-103: +Z up, CCW positive).

### CALC-M3-03: wheel-encoder signal (supports OPEN-15)
- The wheel angle change for a travel s is Δθ = s / r. The TEST-M2-05 travel of 0.980 m gives 13.07 rad (2.08 rev) per wheel.
- `/joint_states` positions are float64 with no quantization, so they are an ideal encoder.
- For comparison, a typical 4096-count/rev quadrature encoder resolves 2π/4096 = 0.00153 rad, or 0.115 mm of wheel travel at r = 0.075 m. That is far below the M2 motion tolerances (±5 %, ≤ 20 mm).
- The real-world effect is therefore not quantization but noise, slip and bias. Slip is already measured: < 0.01 % in TEST-M2-05.

## 4. Design items (Proposed; I decide)

### OPEN-03 (from M1) + blind zone: LiDAR mount and scan plane → **DEC-030 (Accepted as proposed; reopened for review by me 2026-11-03 (low-obstacle comparison in [M3 plan §12](../milestones/M3_sensors.md)); closed by DEC-037: DEC-030 confirmed unchanged, low-obstacle depth camera in M8)**
- **Proposal:**
  - Keep the bracket unchanged (0.080 × 0.080 × 0.030 m at x = +0.070 m).
  - Add `laser_frame` as a fixed child of `lidar_mount_link` at (0, 0, +0.030) with identity rotation, giving a scan plane at 0.230 m (CALC-M3-01).
  - Finalize OPEN-03 with these values once TEST-M3-06 confirms no self-occlusion.
  - Blind-zone mitigation stays deferred to M8 for mitigation; M3 only characterizes the blind zone.
- **Alternatives:** (a) a lower plane, by moving the sensor into a front cut-out, which loses the rear 180° to chassis occlusion; (b) a higher mast, which adds blind height; (c) re-sizing the bracket, which changes the M1 geometry and needs a recorded decision.

### OPEN-13: LiDAR sensor model → **DEC-031 (Accepted as proposed; `gpu_lidar` subject to the feasibility gate)**
- **Proposal** (a generic indoor 2D LiDAR *class*, not a specific product datasheet; all values **Proposed**):
  - SDF type `gpu_lidar`, 360° horizontal (−π to +π), 360 samples (1.0°), 1 vertical ray;
  - range 0.12 to 12.0 m, 10 Hz update rate;
  - Gaussian range noise with mean 0 and σ = 0.01 m;
  - ROS topic `/scan`, `frame_id` `laser_frame`.
- **Rationale:**
  - 12 m covers a factory-aisle scale and stays below the 13.18 m pitch limit (CALC-M3-01).
  - 1° resolution and 10 Hz are adequate for 2D SLAM at ≤ 0.5 m/s (DEC-025): 0.05 m of travel per scan.
  - Noise makes the downstream SLAM/localization tests meaningful; a noise-free sensor hides tuning problems.
- **Alternatives:** (a) a 3D LiDAR (unneeded for 2D SLAM in M5, and costlier to render); (b) a 270° front-only FOV (loses rear coverage; the rear is a blind zone when reversing at −0.25 m/s); (c) no noise (simpler tests, less realism); (d) CPU ray-cast LiDAR, if A1 fails (whether this Gazebo version offers one is unverified).

### OPEN-14: IMU model and placement → **DEC-032 (Accepted with specification: σ_gyro 0.001 rad/s, σ_acc 0.01 m/s², zero bias, simulation assumptions)**
- **Proposal (Proposed):**
  - `imu_link` at the `base_link` origin with identity rotation (CALC-M3-02); 100 Hz, matching the controller rate (DEC-026).
  - Gaussian noise with mean 0: gyroscope σ = 0.002 rad/s and accelerometer σ = 0.02 m/s² per axis (*proposal; **decided: 0.001 rad/s and 0.01 m/s², DEC-032**, simulation assumptions, not hardware specifications*); **no bias or bias drift** in M3.
  - Orientation output left at the Gazebo default, but documented as simulator-derived and not used as ground truth.
  - ROS topic `/imu`, `frame_id` `imu_link`.
- **Alternatives:** (a) IMU at the chassis centre of mass (realistic mounting, but adds lever-arm accelerations); (b) 200 Hz; (c) bias and random walk now (better M6 realism, harder M3 acceptance; can be added in M6 with evidence).

### OPEN-15: wheel-encoder representation → **DEC-033 (Accepted: option (a), ideal simulated encoder feedback, not a hardware encoder model)**
- **Proposal:** (a) use `/joint_states` wheel positions from `gz_ros2_control` as the simulated encoders: no new node, and the signal M2 already verified for presence. M3 adds a quantitative consistency test (TEST-M3-09).
- **Alternative:** (b) an encoder-emulation node that quantizes to N counts/rev and adds noise or slip. It is more realistic, but it adds a node and parameters whose effect is negligible at the M3/M4 tolerances (CALC-M3-03). It can be revisited in M4 if the odometry error budget needs it.

### OPEN-16: sensor integration architecture → **DEC-034 (Accepted with conditions: default-off byte-identical M1 output; 9.4 kg; no zero-mass or zero-inertia link in the generated SDF; dedicated test world)**
- **Proposal:**
  - **Model:** a new `urdf/amr.sensors.xacro` in `amr_description`, included only when a new Xacro argument `use_sensors` is true. The default is false, so the default (M1) expansion stays byte-identical to the M1 evidence, as with DEC-023.
  - **Mass:** `laser_frame` and `imu_link` are **massless** fixed links, so the total stays 9.4 kg. The existing 0.2 kg `lidar_bracket_mass` is re-interpreted as the bracket-plus-LiDAR assembly (Assumed). M2 dynamics are then unchanged.
  - **World:** a new `amr_bringup/worlds/sensor_test.sdf`:
    - the stock `empty.sdf` systems plus `gz-sim-sensors-system` (`ogre2`) and `gz-sim-imu-system`, 1 kHz physics;
    - static box targets at known poses for the LiDAR range and FOV tests (positions defined with the test procedures).
  - **Launch:** `sim.launch.py` gains `world` (default: stock `empty.sdf`, so the M2 behaviour is unchanged) and `sensors` (default false). M3 tests set both.
  - **Bridge:** `amr_bringup/config/sensor_bridge.yaml` for `/scan` (`gz.msgs.LaserScan` → `sensor_msgs/msg/LaserScan`) and `/imu` (`gz.msgs.IMU` → `sensor_msgs/msg/Imu`), Gazebo → ROS only.
- **Alternatives:**
  - (a) Sensors always on in the model. Simpler, but it breaks the M1 byte comparison and needs a re-baseline decision.
  - (b) Sensor masses added (e.g. a sensor link with its own mass). This changes the 9.4 kg total and M2 dynamics, so it needs a recorded decision and an M2 regression.
  - (c) Make sensors the launch default now. M5+ will need them on; flipping the default at M3 closeout or in M5 is a separate, later decision.

### OPEN-17: IMU visualization in RViz → **DEC-035 (Accepted: option (b), no plugin)**
- **Proposal:** (b) no IMU display plugin in M3. RViz shows `/scan` (LaserScan display) and the TF frames `laser_frame` and `imu_link`. IMU data is verified numerically (TEST-M3-07/08). No new dependency.
- **Alternative:** (a) install `ros-jazzy-rviz-imu-plugin` (apt candidate 2.1.6) for an IMU orientation and acceleration display. This is an environment change (`docs/environment.md`) and needs a recorded decision.

### OPEN-18: M3 test acceptance criteria → **DEC-036 (Accepted with specification; the governing specification is §7 below; the proposal here is superseded)**
- **Proposal (Proposed):**
  - **Rate:** measured in simulation time over ≥ 10 s:
    - `/scan` 10 Hz ± 5 %;
    - `/imu` 100 Hz ± 5 %;
    - `/joint_states` 100 Hz ± 5 % (*expected*: `controllers.yaml` sets no rate for `joint_state_broadcaster`, so it is assumed to publish every controller-manager update at `update_rate` 100 Hz, DEC-026; first measured in TEST-M3-04).
  - **Message fields:** `frame_id` exactly `laser_frame` / `imu_link`; stamps in simulation time, within 0.1 s of `/clock`; LaserScan angle and range fields equal the OPEN-13 configuration to 1e-6.
  - **LiDAR range accuracy:**
    - targets at 1.0, 3.0 and 6.0 m; mean of the beams on the target face over 20 scans;
    - |mean error| ≤ 0.02 m;
    - per-beam |error| ≤ 0.05 m (5σ) in ≥ 99 % of samples.
  - **LiDAR FOV:** valid returns from targets at 0°, ±90° and 180°. No return below `range_min` and no robot self-return (0 beams < 0.45 m in an open area). A target lower than the scan plane is **not** detected (blind-zone characterization).
  - **IMU at rest (≥ 10 s):**
    - mean accel z = 9.8 ± 0.1 m/s²; |mean accel x|, |mean accel y| ≤ 0.1 m/s²;
    - |mean gyro| ≤ 0.005 rad/s per axis;
    - sample σ within ±50 % of the configured σ.
  - **IMU in motion:**
    - in-place rotation at ±0.5 rad/s: mean gyro z within ±5 % of the ground-truth yaw rate, with the correct sign;
    - straight acceleration: the accel x sign matches the commanded acceleration sign.
  - **Encoders:**
    - for forward/reverse travel, (Δθ_left + Δθ_right)/2 · r within ±2 % of the ground-truth distance, with the correct signs;
    - in-place rotation: opposite-sign increments.
  - **Runs:** 3 per motion test (as DEC-027); a run with RTF < 0.5 is invalid.
  - **M2 regression with sensors on:** TEST-M2-05, -06 and -07 (stop, timeout) modes still pass the DEC-027 criteria.
- **Rationale:** the tolerances follow from the configured noise: 0.02 m is 2σ for a single beam, and much more than 2σ for a mean of ≥ 20 samples. The M2 criteria are reused where possible.

## 5. Interfaces (DEC-031 to DEC-034)
| Topic | Type | Frame | Rate | Producer |
|---|---|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | `laser_frame` | 10 Hz | Gazebo `gpu_lidar` → `ros_gz_bridge` |
| `/imu` | `sensor_msgs/msg/Imu` | `imu_link` | 100 Hz | Gazebo IMU → `ros_gz_bridge` |
| `/joint_states` | `sensor_msgs/msg/JointState` | — | 100 Hz (**Measured**, gate G4: 100.01 / 100.00 Hz) | `joint_state_broadcaster` (M2) |

TF additions (static, `robot_state_publisher`): `lidar_mount_link → laser_frame` and `base_link → imu_link` (frames_and_tf.md §5 already reserves both for M3).

**Implemented (2026-11-03):** model in Task A (`amr.sensors.xacro`); world `amr_bringup/worlds/sensor_test.sdf`, bridge `config/sensor_bridge.yaml` and the `sim.launch.py` options `sensors` / `world` in Task B. TEST-M3-04 verified the three topics (D1–D4) and that the default launch is unchanged from M2.

## 6. Feasibility gate (step 1; decided by me 2026-11-03; throwaway prototype, M3 stays Proposed until it passes)
Before any model change, a scratch SDF world checks the following, using a minimal model:
- **A1:** a `gpu_lidar` runs headless (`-s --headless-rendering`) and in the GUI, and the RTF with rendering is ≥ 0.5.
- **A2:** `<gz_frame_id>`.
- **A3:** the sensor pose after fixed-joint lumping, through the URDF path.
- **A4:** gravity.

The findings go to troubleshooting/design notes. If A1 fails, the LiDAR approach returns for review with options (OPEN-13 alternative d, or GUI-only LiDAR tests).
- Gate checks requested by me (2026-11-03):
  - G1: rendering on the Intel GPU in the intended headless configuration (A1);
  - G2: LiDAR scan publication and `frame_id` (A2);
  - G3: IMU messages and gravity (A4);
  - G4: the actual `/joint_states` publication frequency;
  - G5: with the sensor option disabled, the model output is byte-identical to the M1 evidence;
  - G6 (DEC-034 condition): with sensors on, the generated SDF has no zero-mass or zero-inertia link, the total mass is 9.4 kg, and the sensor poses survive lumping (A3).
- If G1 or any critical check fails: stop, record the evidence, and review the alternatives. The architecture is not changed silently.

### 6.1 Gate results (2026-11-03): G1–G6 PASS
**Set-up.**
- Throwaway prototype on a scratch copy of `amr_description`. The repository's `amr_ws/` was **not** modified.
  - The prototype adds a `use_sensors` Xacro argument (default false) and a conditional include ([diff](../evidence/M3/FEAS-M3_amr.urdf.xacro.prototype.diff)).
  - It adds a prototype `amr.sensors.xacro` with the DEC-030 to DEC-032 values ([file](../evidence/M3/FEAS-M3_amr.sensors.prototype.xacro)).
- Scratch world ([file](../evidence/M3/FEAS-M3_gate_world.sdf)): `empty.sdf` plus the Sensors (`ogre2`) and IMU systems, with four static boxes (1.0 m wide, 0.20 m thick, so each face is 0.10 m from the box centre) as targets:
  - front: face at x = 2.40 m;
  - rear: face at x = −2.90 m;
  - right: face at y = −1.90 m;
  - low left: 0.15 m high, below the scan plane.
- Launch mirroring `sim.launch.py`: `gz sim -r -s --headless-rendering`, bridges for `/clock`, `/scan` and `/imu`, and the M2 controllers.
- Isolation: `ROS_DOMAIN_ID=83`, `GZ_PARTITION=feas_m3_gate`.
- Software: Gazebo Sim 8.15.0; Intel Iris Xe (Alder Lake-UP3 GT2).
- Measurement window: settle 2 s after the first scan, then 10 s of simulation time at rest.
- Procedures: [runtime](../evidence/M3/FEAS-M3_gate_run.sh) ([launch](../evidence/M3/FEAS-M3_gate_launch.py), [measurement](../evidence/M3/FEAS-M3_gate_measure.py)) and [static](../evidence/M3/FEAS-M3_gate_static.sh) ([SDF check](../evidence/M3/FEAS-M3_sdf_check.py)).

| Gate | Check | Run 1 ([log](../evidence/M3/FEAS-M3_runtime_gate_run1.log)) | Run 2 ([log](../evidence/M3/FEAS-M3_runtime_gate_run2.log)) | Result |
|---|---|---|---|---|
| G1 | Headless rendering (`-s --headless-rendering`, `ogre2`) on the Intel GPU; 100 scans in 10 s; RTF ≥ 0.5 | RTF 0.998 | RTF 1.000 | PASS |
| G2 | `/scan` `frame_id` | `laser_frame` | `laser_frame` | PASS |
| G2 | `/scan` rate from stamps | 10.0000 Hz | 10.0000 Hz | PASS |
| G2 | LaserScan fields | `angle_min` −3.141593, `angle_increment` 1.000000°, 360 samples, range 0.12–12.0 m | same | PASS |
| G2 | Target range: mean error / SD (n) | front +0.14 / 10.07 mm (2000); rear −0.36 / 10.01 mm (1600); right +0.04 / 10.01 mm (2400) | front −0.07 / 10.05 mm; rear −0.60 / 9.85 mm; right −0.01 / 10.08 mm | PASS (≤ 10 mm; SD matches σ = 0.01 m) |
| G2 | Low target (0.15 m) below the 0.230 m scan plane | 0 finite returns | 0 | PASS (blind zone, DEC-030) |
| G2 | Self-returns closer than 0.45 m | 0 | 0 | PASS |
| G3 | `/imu` `frame_id`, rate | `imu_link`, 100.0000 Hz | same | PASS |
| G3 | Gravity: mean accel z at rest (+g, specific force) | +9.80052 m/s² | +9.79992 m/s² | PASS (9.8 ± 0.05) |
| G3 | IMU noise SD (accel x/y/z; gyro x/y/z) | 0.01016 / 0.01039 / 0.01014 m/s²; 0.001016 / 0.000974 / 0.000954 rad/s | 0.00993 / 0.01030 / 0.00979 m/s²; 0.000993 / 0.000977 / 0.000982 rad/s | consistent with DEC-032 (informational; formal S1–S4 in TEST-M3-07) |
| G4 | `/joint_states` rate from stamps | 100.0100 Hz | 100.0000 Hz | **Measured: 100 Hz** → DEC-036 D2 |
| G5 | Default-off expansion vs `TEST-M1-02_amr.urdf`; M2 expansion with sensors off vs the repository expansion | — | — | PASS: both byte-identical (SHA-256 061c22ca…) ([log](../evidence/M3/FEAS-M3_static_gate.log)) |
| G6 | Sensors-on SDF | — | — | PASS: 3 links (`base_footprint` 8.4 kg, wheels 0.5 kg each), total 9.400000 kg; all inertia diagonals > 0; `laser_frame` and `imu_link` lumped; lidar at (0.070, 0, 0.230) m and IMU at (0, 0, 0.075) m in `base_footprint`; inertial blocks identical with sensors off and on |

**Findings that M3 step 2 must carry over:**
- `max_angle` = 3.12413936106985 rad (179°), not +π. Gazebo spaces 360 samples over (max − min)/(samples − 1); with +π the step would be 1.0028°, and the first and last beams would coincide.
- The `gz sdf` warning for `<gz_frame_id>` and the `gz_ros2_control` "IMU sensor … skipping" message are expected (§2). TEST-M3 procedures should not count them as failures.
- The IMU orientation was the identity quaternion at rest in both runs. The orientation output is simulator-derived and is not used as ground truth (DEC-032).
- Not covered by the gate: `gpu_lidar` in the GUI (TEST-M3-10), motion (TEST-M3-08/09/11), and the formal statistical checks S1–S4 (TEST-M3-05/07). The gate's tolerances were feasibility checks, not the DEC-036 acceptance criteria.

**Gate harness defects (not model or architecture defects; TS-021):**
- Run 1 shutdown: `gate_run.sh` lacked job control, so the background launch ignored SIGINT, which is the TS-011 cause. The launch got SIGTERM, and `gz sim`, `robot_state_publisher` and `parameter_bridge` from run 1 had to be stopped afterwards (SIGINT).
  - Fixed with `set -m`. In run 2 the launch's SigIgn is 0 and no processes were left over.
  - The run-1 measurements were complete before shutdown, so they remain valid.
- First static-gate attempt: G5 `cmp` reported a difference in line 3 only, xacro's "autogenerated from <path>" header comment, because the script called xacro with absolute paths (the TS-010 cause). The script now runs xacro from inside each workspace, as TEST-M1-02/TEST-M2-02 do. The recorded log is from the corrected script; the failed attempt's output was not kept.

## 7. M3 test specification (DEC-036): deterministic checks vs statistical noise checks

### 7.1 Principle
- **Deterministic checks** test properties that the simulation either has or does not have: names, frames, configuration fields, rates in simulation time, poses, signs, detection or non-detection. Their limits are tight, or exact where the property is exact.
- **Statistical checks** test the *noise model* (DEC-031: range σ_r = 0.01 m; DEC-032: σ_ω = 0.001 rad/s, σ_a = 0.01 m/s²; all zero-mean Gaussian).
  - They use summary statistics over many samples, never "every sample within a narrow band".
  - Each limit is chosen so that a correctly configured sensor fails with negligible probability, while a wrong σ, a biased or non-Gaussian distribution, or spurious returns still fail.

### 7.2 Sampling windows
| Data | Settle before window | Window (simulation time) | Samples per statistic |
|---|---|---|---|
| Rates, stamps, frames (`/scan`, `/imu`, `/joint_states`) | 2.0 s after the controllers are active (`/scan`, `/imu` from the first message) | 10.0 s | all messages |
| LiDAR static range (targets) | 2.0 s | ≥ 20 scans, extended until **n ≥ 1000** target-face samples per target distance | ≥ 1000 |
| IMU at rest | 2.0 s, zero command | 10.0 s at 100 Hz | 1000 per axis |
| IMU / encoders in motion | M2 harness profiles (test_plan §6.1) | steady-state part of each profile (constant commanded velocity, after the acceleration ramp) | per run |

- Beams that pass within 1 beam (1°) of a target edge are excluded: their returns mix target and background.
- Error definitions:
  - LiDAR: e_i = r_i − r_true, with r_true the geometric distance from the `laser_frame` origin to the target plane along beam i.
  - IMU: e_i = sample − expected (expected: CALC-M3-02).

### 7.3 Deterministic checks (pass/fail)
| ID | Check | Limit |
|---|---|---|
| D1 | Topic name, message type, `frame_id` (`/scan` `laser_frame`; `/imu` `imu_link`) | exact |
| D2 | Rate from header stamps: (N − 1) / (t_last − t_first) | nominal ± 2 %: `/scan` 10 Hz, `/imu` 100 Hz, `/joint_states` 100 Hz (the value measured in the feasibility gate G4, §6.1) |
| D3 | Stamps strictly increasing; stamp within 0.1 s of the latest `/clock` at receipt | all messages |
| D4 | LaserScan `angle_min`, `angle_max`, `angle_increment`, `range_min`, `range_max`; `len(ranges)` = 360 | DEC-031 values to 1e-6 (rad, m); count exact |
| D5 | TF `lidar_mount_link → laser_frame` and `base_link → imu_link` | DEC-030 / DEC-032 offsets to 1e-6 m / rad |
| D6 | FOV: targets at 0°, ±90°, 180° each give ≥ 3 finite returns with median within 0.05 m of r_true | all 4 bearings |
| D7 | No self-returns: finite returns closer than 0.45 m in an open-area scan | 0 |
| D8 | Blind zone: a target whose top is below the 0.230 m scan plane | 0 finite returns in its bearing range (non-detection recorded) |
| D9 | IMU gravity sign and axis: mean specific force z | positive (+g up); see S1 for magnitude |
| D10 | IMU in-place rotation at ±0.5 rad/s: mean gyro z over the steady window vs mean ground-truth yaw rate | correct sign; within ± 3 % |
| D11 | IMU straight acceleration: mean accel x over the ramp vs the ground-truth acceleration | correct sign; within ± 20 % (TEST-M3-08, 2026-11-03: **FAIL**; the simulated accel x does not respond to the robot's acceleration, TS-027: aliasing between the 100 Hz controller command hold and the 100 Hz instantaneous IMU sample; criterion unchanged, awaiting my decision) |
| D12 | Encoders: (Δθ_L + Δθ_R)/2 · r vs ground-truth travel; in-place rotation gives opposite-sign Δθ | within ± 2 %; signs correct |

### 7.4 Statistical noise checks (per noisy channel: LiDAR range per target distance; IMU accel x/y/z and gyro x/y/z at rest)
With n samples, sample mean ē and sample standard deviation s:

| ID | Statistic | Pass limit | Basis |
|---|---|---|---|
| S1 | Bias \|ē\| | LiDAR ≤ 0.010 m per target distance; IMU accel \|ē\| ≤ 0.02 m/s² (z relative to g = 9.8); IMU gyro \|ē\| ≤ 0.001 rad/s | Engineering limits. The noise contribution is 3σ/√n ≤ 0.00095 m, 0.00095 m/s² and 0.000095 rad/s at n = 1000, so the limits test geometry and bias, not noise |
| S2 | Spread: s / σ_config | 0.8 ≤ s/σ ≤ 1.2 | For a Gaussian, SE(s) ≈ σ/√(2(n−1)) = 0.022σ at n = 1000, so ±0.2σ is about 9 SE (false-fail probability ≪ 1e-6) |
| S3 | Shape: fraction of samples with \|e_i − ē\| ≤ 2s | 0.93 to 0.98 | Gaussian expectation 0.9545; binomial SD at n = 1000 is 0.0066, so the band is −3.7 / +3.9 SD |
| S4 | Gross outliers: \|e_i − ē\| > 6σ_config | 0 samples | Gaussian probability 2.0e-9 per sample, about 2e-6 per 1000 samples |

- S1–S4 run on the static and at-rest windows only; motion tests use the deterministic D10–D12 on means.
- A failure of S2–S4 means the configured noise model is not what DEC-031/032 specify. That is a defect to diagnose, not a reason to widen the band.

### 7.5 Runs and validity
- Static and rest tests: 1 run each, provided n meets §7.2.
- Motion tests (D10–D12, M2 regression): 3 valid runs, each passing.
- A run with RTF < 0.5 is rejected and repeated (as in M2).
- A sensor-launch run whose measurement checks passed but whose shutdown shows only the TS-029 signature (upstream Gazebo shutdown deadlock) is invalid and repeated within the same attempt limit (DEC-039; classifier `../evidence/M3/TEST-M3_launch_shutdown_classify.py`).

## 8. IMU output decimation (C4; DEC-038 **Accepted**, implemented in `amr_gazebo_plugins`)
TS-027 background and evidence: [troubleshooting TS-027](../troubleshooting.md); prototype logs `../evidence/M3/TS-027_C4_validation.log` and `TS-027_C4_delay.log`. DEC-038 was accepted on 2026-11-03 and implemented as a dedicated M3 step. It amends DEC-032 only for the internal sampling rate and the definition of noise at the published output; DEC-036 is unchanged. §8.2–§8.5 are kept as written for the decision; §8.6 records the implementation as built.

### 8.1 Background: why a 100 Hz IMU misses the robot's acceleration
- A *zero-order-hold* command keeps one value until the next update. `diff_drive_controller` updates the wheel velocity every 10 ms (DEC-026). DART enforces the new value within one 1 ms step, so the chassis acceleration is concentrated in one step per cycle, with about 0 on the other nine.
- A Gazebo IMU reports the acceleration of the current step only, an instantaneous sample with no anti-alias filter.
- At 100 Hz on the same 10 ms grid, the IMU always samples the same phase of the cycle. In the launch, the velocity steps fall 1–2 ms after each boundary, so the IMU never samples them. This is *aliasing*.
- Real MEMS IMUs low-pass filter and average internally before publishing at their output rate. C4 reproduces that with a 10-sample block mean.

### 8.2 Production architecture comparison (decision item 5)
| Criterion | A. Gazebo system plugin (C++), recommended | B. Standalone gz-transport C++ process | C. ROS 2 C++ node in `amr_bringup` |
|---|---|---|---|
| Where it runs | Inside `gz sim`, loaded with the robot model (`<plugin>` in `amr.sensors.xacro`, use_sensors only) | Separate process started by `sim.launch.py` | Separate ROS process; `/imu_raw` must be bridged to ROS at 1 kHz |
| Timing determinism | Output values deterministic: blocks are formed from raw stamps, not arrival time. Publication is asynchronous (gz-transport callback); prototype stamp − clock ≤ 1 ms | Same as A | Values the same. Arrival depends on 1 kHz bridge and DDS delivery; the reliable QoS depth must cover bursts; not measured |
| Timestamp preservation | Raw gz stamps used directly | Same as A | Stamps survive the bridge conversion; one extra conversion step |
| Overhead | No extra process; in-process transport | One extra process, transport traffic as the prototype | 1 kHz bridge conversion and DDS traffic (10× the current `/imu`), plus the node; not measured |
| Gazebo / ROS integration | ROS interface unchanged (bridge YAML, `/imu`, 100 Hz). The sim-only component stays inside the simulator, so the ROS graph matches a future hardware IMU at 100 Hz (M13) | ROS interface unchanged | A sim-only `/imu_raw` topic and node in the ROS graph; on hardware the node would not run |
| Build | Needs gz-sim 8, gz-transport 13, gz-msgs 10 headers (installed: `gz_sim_vendor`, `gz_transport_vendor`, `gz_msgs_vendor`) and a `GZ_SIM_SYSTEM_PLUGIN_PATH` environment hook (the pattern `gz_ros2_control` uses) | gz-transport and gz-msgs only | `rclcpp` only; same pattern as `cmd_vel_guard` |
| Testability | The averaging class is Gazebo-independent and unit-tested with gtest. Integration through the existing harnesses plus a raw-vs-output check | Same as A | gtest plus `launch_testing`; integration as A |
| Maintainability | Small: one class and a thin `System` wrapper. Plugin ABI tied to gz-sim 8 (Harmonic target) | Small; transport API only | Small; most familiar ROS idiom |
| Startup / shutdown | Created and destroyed with the model; no orphan process (TS-009/TS-021 history) | Must start only with sensors on, in the same `GZ_PARTITION`; needs leftover checks | Launch-managed; depends on the bridge being up |
| Failure isolation | A crash in the plugin stops the server; mitigated by the small, unit-tested core | Isolated | Isolated |
| Missing raw samples | Same block rule (§8.4) in all three. In C, losses can also occur on the 1 kHz ROS path | — | — |

**Recommendation: A.**
- A is the cleanest fit: the decimation is part of the simulated *sensor model*, and the ROS-facing interface stays identical to DEC-032/DEC-034.
- It adds no process or topic to the ROS graph, carries no 1 kHz traffic through the bridge, and its lifetime is tied to the model.
- B is the fallback if loading a plugin proves troublesome. C is not recommended, because it moves sim-only internals into the ROS graph and adds unmeasured 1 kHz DDS load.
- The Python prototype is not retained: no compiled tests, an extra interpreter process, and no strong reason to keep it.

### 8.3 Signal specification
- **Input:** Gazebo IMU at 1000 Hz on `/imu_raw` (gz.msgs.IMU). It has DEC-032 conventions and the derived raw noise (§8.5); its stamps are on the 1 ms grid.
- **Block:** the raw samples with stamps t − 9, …, t ms, where t is a multiple of 10 ms (aligned to the simulation clock). There is no overlap between blocks.
- **Output (gz `/imu`, then ROS `/imu`, 100 Hz):**
  - `linear_acceleration` and `angular_velocity`: the per-axis arithmetic mean of the 10 samples;
  - `orientation`, its covariance and the frame: copied from the sample at t;
  - `angular_velocity_covariance` and `linear_acceleration_covariance`: the sample at t's values ÷ N, i.e. σ_out², which equals the DEC-032 values (DEC-038 item 8, implementation clarification);
  - `header.stamp`: t.
- **Timestamp versus measurement interval:** the stamp t is the **end** of the measured interval (t − 10 ms, t]. The rates describe the whole interval; the orientation describes the instant t.
- **Effective delay**, measured with the prototype (`TS-027_C4_delay.log`, 3 runs, identical):

| Measure | Value | Meaning |
|---|---|---|
| FIR group delay | 4.5 ms | Theory: (N − 1)/2 samples, for acceleration spread evenly through the block |
| Interval centre | 5.0 ms | t − 5 ms is the midpoint of (t − 10, t] |
| Controller-step delay | **8 ms (25 %) / 9 ms (75 %)** | Measured: the controller velocity steps fall 1–2 ms after the block start, so a step reaches `/imu` with the stamp 8–9 ms later. Repeatable: the same histogram in all 3 runs |
| Transient | One output | The first output whose block contains the step shows the full new acceleration (fixture: 95 % within the first output, 10–17 ms after the step) |

- **For M4 (guidance, not validated):**
  - treat each sample as the mean acceleration over (t − 10 ms, t]; integrating v(t) = v(t − 10 ms) + a·10 ms is exact;
  - a filter that treats the sample as instantaneous at t lags by 5 ms (interval centre) to 9 ms (controller steps). At the 0.5 m/s² limit this is at most ≈ 0.005 m/s of velocity at an acceleration transition;
  - M4 decides whether to compensate. No fusion is claimed here.

### 8.4 Startup, missing samples and shutdown
| Situation | Behaviour |
|---|---|
| Startup or after a reset | Publish nothing until the first complete aligned block (10 distinct stamps t − 9 … t). Never publish a partial block |
| Missing raw sample in a block | Do not publish that block (consumers see a 20 ms stamp gap); increment `blocks_dropped`; rate-limited warning |
| Duplicate raw stamp | Ignore the repeat; increment `duplicates` |
| Non-monotonic stamp (time moved backwards, e.g. a world reset) | Clear the buffer, increment `resets`, restart with the startup rule |
| Inconsistent configuration (raw rate × block ≠ output period, block not a multiple of the physics step) | Refuse at load with an error naming the values |
| Shutdown | Discard the partial block; publish nothing further |

### 8.5 Noise definition and derived raw setting (decision items 1, 4)
- **Published output (requirement, DEC-032, unchanged):** σ_a = 0.01 m/s², σ_ω = 0.001 rad/s per axis, at ROS `/imu`.
- **Derived raw setting (Calculated):** σ_raw = √10 · σ_out = 0.0316227766 m/s² and 0.00316227766 rad/s, with 10 samples averaged.
- **Evidence (prototype, informal):**

| Raw setting | Output s/σ | Raw autocorrelation (lags 1–10 ms) | Output lag-1 correlation | S1–S4 |
|---|---|---|---|---|
| Raw = DEC-032 values | 0.30–0.33 | — | — | **S2 fails** |
| Raw = √10 × DEC-032 | 0.96–1.04 (fixture and 2 launch runs) | \|r\| ≤ 0.024 | −0.01 to −0.03 | Pass |

- If a formal TEST-M3-07 after implementation fails S2, the raw value is re-derived; the published requirement is not relaxed.

### 8.6 Implementation (as built)
1. **Package:** `amr_ws/src/amr_gazebo_plugins` (ament_cmake, C++17). I chose this over adding the plugin to `amr_bringup`. Dependencies: `gz_sim_vendor`, `gz_plugin_vendor`, `gz_transport_vendor`, `gz_msgs_vendor` (Gazebo Sim 8, gz-transport 13, gz-msgs 10); `ament_cmake_gtest` for tests.
2. **Core class `ImuBlockAverager`** (`include/amr_gazebo_plugins/imu_block_averager.hpp`, `src/imu_block_averager.cpp`). It is pure C++ with no Gazebo types, built as a static library.
   - Sample index k = round(stamp / raw period); a stamp more than 1 % of a period off the grid is ignored and counted.
   - The block containing k is b = ⌊(k − 1)/N⌋ + 1. Block b holds the indices bN − N + 1 … bN.
   - A block is emitted when sample bN arrives and all N indices were seen. A block missing any index is closed, without output, when it ends or when the next block starts.
   - Counters: samples, published, dropped_incomplete (after the first complete block), discarded_partial (startup, reset, shutdown), missing_samples, duplicates, off_grid, resets.
   - `ValidateConfig()` and `ValidateControllerRate()` hold the DEC-038 item 9 rules.
3. **Plugin `amr_gazebo_plugins::ImuDecimator`** (`src/imu_decimator.cpp`, library `libamr_imu_decimator_system.so`, SDF file name `amr_imu_decimator_system`): a `gz::sim::System` with `ISystemConfigure` and `ISystemReset`, attached to the model.
   - SDF parameters: `input_topic` `/imu_raw`, `output_topic` `/imu`, `block_size` 10, `raw_rate` 1000, `output_rate` 100.
   - `Configure()` only reads the SDF parameters. At the **first `PreUpdate()`** it reads the world's physics step (`components::Physics`) and the update rate of the model's IMU sensor that publishes `input_topic` (`components::Imu`, exactly one required). It validates them and only then subscribes and advertises.
   - Validating in `Configure()` failed when the robot is part of the world file (TS-028). The IMU system publishes its first sample in `PostUpdate`, so no sample is missed.
   - **"Refuse to load" semantics.** Gazebo Sim 8's `Configure()` returns nothing, so a system cannot fail its own load. On an invalid configuration the plugin logs `gzerr` "invalid configuration, NOT active" with the offending values, and neither subscribes nor publishes.
     - Gazebo, the robot and the controllers keep running, but Gazebo `/imu`, and therefore ROS `/imu`, stays **silent**. Any consumer or test sees no IMU data; it never sees wrong data.
     - The error is printed at Gazebo's default verbosity (errors only), so it appears in the launch log.
     - TEST-M3-14 (g) proves this in a real server, and TEST-M3-04 (D2 rate) would fail on a silent `/imu`.
   - Delivery is in-process gz-transport, behind a mutex. `Reset()` (world reset) clears the averager.
   - Its destructor unsubscribes, discards the partial block, and prints the counters on standard output, which the launch log records (used by TEST-M3-14 (b)). A dropped block also gives a `gzwarn`, at most once per 5 s.
   - **Known limitation:** `sim.launch.py` starts `gz sim` without `-v`, so warnings are not shown and the dropped-block `gzwarn` is invisible in a normal launch. Drops are still recorded:
     - the shutdown counter line, which TEST-M3-14 (b) checks in every run;
     - the 20 ms stamp gap on `/imu`, which TEST-M3-14 (b) and TEST-M3-04 check.
     - Running with `gz sim -v 2` or higher shows the warnings live.
4. **`amr.sensors.xacro`** (use_sensors only): properties `imu_output_rate` 100, `imu_block_size` 10, `imu_raw_rate` = product (1000), `imu_gyro_stddev` 0.001 and `imu_accel_stddev` 0.01 (output, DEC-032), and the derived `imu_*_stddev_raw` = output × `sqrt(imu_block_size)`. The IMU publishes `/imu_raw` at `imu_raw_rate`; a model-level `<gazebo><plugin>` element carries the parameters. The default-off expansion stays byte-identical to M1.
5. **Environment hook** `env-hooks/amr_gazebo_plugins.dsv.in`: `prepend-non-duplicate;GZ_SIM_SYSTEM_PLUGIN_PATH;lib`, the `gz_ros2_control` pattern. `sensor_bridge.yaml`, `sim.launch.py` and the harnesses are unchanged.
6. **Verification:** `docs/testing/test_plan.md` §7.3. Results in `TEST_RESULTS.md`.
