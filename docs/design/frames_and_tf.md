# Coordinate Frames, Links, Joints, and TF Design

**Status:** M1 frame design recorded 2026-10-19. DEC-016 was **accepted** by me on 2026-10-19. OPEN-04 and OPEN-05 were resolved in DEC-019, finalized on 2026-10-19. Implemented on 2026-10-21 in `amr.urdf.xacro`: structure verified by TEST-M1-02, values by TEST-M1-03 re-test 1. TF values and the wheel direction were verified in a running system on 2026-10-21 by TEST-M1-04 (wheel direction observed by me) and TEST-M1-05. The model spawned and rested in Gazebo Harmonic in TEST-M1-06/07.
**Related:** REQ-M1-02, REQ-M1-05, REQ-M1-08, REQ-M1-09 · OPEN-04, OPEN-05 · geometry in [mechanical_geometry.md](mechanical_geometry.md)

## 1. Conventions
- **REP-103** (ROS standard units and coordinate conventions): SI units; right-handed body frames with **+X forward, +Y left, +Z up**; angles in radians, with positive rotation counter-clockwise about the axis by the right-hand rule.
- **REP-105** (*Coordinate Frames for Mobile Platforms*): defines `base_link`, `odom`, `map` (and `earth`), giving the chain `map → odom → base_link`. It does **not** define `base_footprint`.
- **REP-120** (*Coordinate Frames for Humanoid Robots*; it requires REP-103 and REP-105): defines `base_footprint` as "the representation of the robot position on the floor", with zero roll and pitch relative to `odom`. This project uses that definition for a wheeled base: the ground point under the axle midpoint.
  - *Source check (2026-10-19, review finding R-06):* the raw `rep-0105.rst` and `rep-0120.rst` were read from `github.com/ros-infrastructure/rep`, branch `master` at commit `11ca24a4`. `base_footprint` appears nowhere in REP-0105; REP-0120 defines it in its frame list. The earlier text credited `base_footprint` to REP-105 and has been corrected.
- **URDF joint semantics:** a joint's `<origin>` gives the pose of the **child** link frame expressed in the **parent** link frame. For `base_footprint_joint` (parent `base_footprint`, child `base_link`), `xyz = "0 0 0.075"` therefore means `base_link` sits 0.075 m above `base_footprint`. The transform runs from parent to child.

## 2. M1 frame tree (static robot description)
Published by `robot_state_publisher` from the URDF. Fixed joints go to `/tf_static`; the continuous wheel joints go to `/tf` and require `/joint_states`.

```
base_footprint                          root; ground plane under axle midpoint; no mass
└── [base_footprint_joint: fixed, xyz(0, 0, 0.075)]
    base_link                           axle midpoint; carries chassis visual/collision/inertial
    ├── [left_wheel_joint:  continuous, xyz(0, +0.200, 0), axis(0 1 0)] → left_wheel_link
    ├── [right_wheel_joint: continuous, xyz(0, −0.200, 0), axis(0 1 0)] → right_wheel_link
    ├── [caster_joint:      fixed,      xyz(−0.360, 0, −0.050)]         → caster_link      (OPEN-01 Selected)
    └── [lidar_mount_joint: fixed,      xyz(+0.070, 0, +0.125)]         → lidar_mount_link (provisional, OPEN-03)
```

### Link inventory

| Link | Mass (kg) | Visual / collision | Inertial origin (in link) | Notes |
|---|---|---|---|---|
| `base_footprint` | — | none | — | Root. Massless, which avoids KDL's "root link has inertia" warning |
| `base_link` | 8.0 | box 0.45 × 0.35 × 0.12 at (−0.100, 0, +0.035) | (−0.100, 0, +0.035) | Chassis tensor (CALC-M1-07) about the box centroid |
| `left_wheel_link` | 0.5 | cylinder r 0.075, length 0.035, rotated so its axis lies along link Y | (0, 0, 0) | CALC-M1-08 |
| `right_wheel_link` | 0.5 | as left | (0, 0, 0) | CALC-M1-08 |
| `caster_link` | 0.2 | sphere r 0.025 | (0, 0, 0) | CALC-M1-09 |
| `lidar_mount_link` | 0.2 | box 0.08 × 0.08 × 0.03, centred 0.015 m below the link origin (provisional, OPEN-03) | (0, 0, −0.015) | Origin on the bracket top surface; the M3 sensor frame attaches here |

**OPEN-05 resolved (DEC-019):** the chassis inertial stays on `base_link`, with the offset origin above. A separate `chassis_link` was considered and not selected: it would add a link and joint (changing REQ-M1-02 and the TF tree), and Gazebo would merge it back by fixed-joint lumping (§4). Only the root `base_footprint` is massless, which is what the KDL root-inertia warning requires.

### Joint inventory
Joint origins are derived from the parameters in `amr_properties.xacro`, which are listed with their rationale in [mechanical_geometry.md §2](mechanical_geometry.md#2-parameter-table-authoritative).

| Joint | Type | Parent → child | Origin xyz (m) | Axis | Status |
|---|---|---|---|---|---|
| `base_footprint_joint` | fixed | `base_footprint` → `base_link` | (0, 0, 0.075) | — | Selected (DEC-016) |
| `left_wheel_joint` | continuous | `base_link` → `left_wheel_link` | (0, 0.200, 0) | (0, 1, 0) | Selected (OPEN-04, DEC-019); sign verified by TEST-M1-04 (PASS 2026-10-21) |
| `right_wheel_joint` | continuous | `base_link` → `right_wheel_link` | (0, −0.200, 0) | (0, 1, 0) | Selected (OPEN-04, DEC-019); sign verified by TEST-M1-04 (PASS 2026-10-21) |
| `caster_joint` | fixed | `base_link` → `caster_link` | (−0.360, 0, −0.050) | — | Selected (OPEN-01, DEC-019) |
| `lidar_mount_joint` | fixed | `base_link` → `lidar_mount_link` | (0.070, 0, 0.125) | — | Selected (DEC-030, 2026-11-03; provisional placeholder until then, OPEN-03, DEC-019) |

Expected count: **6 links, 5 joints** (checked by TEST-M1-02).

## 3. Wheel axis analysis (OPEN-04 Selected in DEC-019; sign to be verified)
With an unrotated wheel link and joint axis +Y, consider a positive joint velocity ω > 0:
- The ground-contact point sits at offset (0, 0, −r) from the wheel centre.
- Its velocity relative to the wheel centre is ω ŷ × (−r ẑ) = −ωr x̂, i.e. the contact point moves backward.
- With no slip, the wheel centre therefore moves **forward (+X)** at speed ωr.

So the same axis (0 1 0) on both wheels means "positive = forward" for both, with no sign inversion. This was an analytical result. **TEST-M1-04 confirmed it on 2026-10-21:** with each slider at a positive value, I observed both wheels rolling forward, and TF showed each wheel rotated by its joint angle about +Y with the same sign on both sides.

**Alternative convention (not selected):** rotate each wheel link about X and use joint axis (0 0 1). Rotating by θ about X maps the link Z axis to (0, −sin θ, cos θ) in `base_link`. So θ = −π/2 gives +Y and θ = +π/2 gives −Y. The sign therefore depends on the rotations, not on the convention itself:
- **Same rotation on both wheels** (e.g. −π/2 on both): both axes are +Y, positive = forward on both, and there is no sign difference. It is equivalent to the selected convention, except the inertial frame is rotated.
- **Opposite rotations** (e.g. −π/2 left, +π/2 right, a common tutorial pattern): the axes are +Y and −Y, so positive is forward on one wheel and backward on the other. A sign inversion is then needed.

If that convention were used, this section, CALC-M1-08's axis assignment (the axial moment becomes Izz in the rotated frame), and the M2 controller configuration would have to change together. *(Wording corrected 2026-10-19, review finding R-05. It previously said the alternative always flips one side.)*

## 4. Gazebo-specific behaviour
- **Fixed-joint lumping:** when sdformat converts URDF to SDF, it merges links connected by fixed joints into their parent, repeating up the chain.
  - *Probe (2026-10-19, review finding R-08):* a **generic** probe was converted with `gz sdf -p probe.urdf`, using the installed tools (`gz sdf --versions` → 14.9.0); the exit code was 0. The probe was not the AMR model. It had a massless root, then a 1 kg box on a fixed joint, then a 1 kg sphere on a fixed joint 1 m away, plus one continuous-joint child. Observed output:
    - Both fixed-joint links merged into the **root**, which kept the root's name. Their collisions were renamed `root_fixed_joint_lump__…`, and their frames survived as `<frame>` elements.
    - The merged inertial was mass 2, pose (0.5, 0, 0), Iyy = Izz = 0.7 = 0.1 + 0.1 + 2 × 1 × 0.5², i.e. combined with the parallel-axis theorem.
    - The continuous joint became `revolute` with ±inf limits, no damping, and spring stiffness 0.
  - *Evidence (review follow-up G3):* the probe input, its generated output, the procedure, and the run log are in `docs/evidence/M1/`. That covers [`R-08_sdformat_lumping_probe.urdf`](../evidence/M1/R-08_sdformat_lumping_probe.urdf), [`.sdf`](../evidence/M1/R-08_sdformat_lumping_probe.sdf), [`.sh`](../evidence/M1/R-08_sdformat_lumping_probe.sh) and [`.log`](../evidence/M1/R-08_sdformat_lumping_probe.log). The URDF is the original 17:36 probe input, copied byte-for-byte. The SDF was regenerated by the logged procedure at 18:35 (exit 0) and is byte-identical to the 17:36 output. The log also captures the installed spec's `self_collide` text.
  - *Expected for the AMR (written before testing):* `base_link`, `caster_link`, and `lidar_mount_link` merge into **`base_footprint`** (the root), not into `base_link`. The SDF then has 3 links. Expected values are in [mass_inertia.md §11](mass_inertia.md) (CALC-M1-15); TEST-M1-03 confirms them on the real model.
  - *Observed 2026-10-21:* TEST-M1-03 re-test 1 confirmed this on the AMR SDF. It has 3 links, and the lumped `base_footprint` is 8.4 kg at (−0.1021, 0, +0.1098), with the caster and bracket as lumped collisions and their frames kept as `<frame>` elements. TEST-M1-06/07 then ran the model in Gazebo.
  - If a separate Gazebo link is ever needed, URDF `<gazebo>` options exist to preserve fixed joints. Their exact usage must be checked before relying on them.
- **Self-collision and contacts (geometric clearance vs physics risk):** the installed SDFormat 1.11 specification (`gz sdf -d 1.11`) gives `self_collide` a default of `false`, and states that "links connected by a joint will never collide". Taken together with the lumping above, the expected consequences are:
  - The caster and the LiDAR bracket become collisions of the **same** link as the chassis. *Assumption:* collision shapes of one rigid link are not tested against each other. This is general rigid-body physics-engine behaviour, not text quoted from the SDFormat spec, so no contact force is expected between them.
  - Each wheel is joint-connected to that link, so wheel–chassis contact is not expected either, even if `self_collide` were enabled.
  - Therefore, the caster clearance (CALC-M1-13) and the 7.5 mm wheel gap (CALC-M1-03, OPEN-02) are **geometric-correctness requirements** in M1, not demonstrated physics or stability risks.
  - This rests on the specification text and the generic probe. It is not an observation of the AMR in Gazebo, and it is checked on the real model in TEST-M1-03 (SDF content) and TEST-M1-06 (visual). *Checked 2026-10-21:* TEST-M1-03 re-test 1 found the 3 lumped collisions in `base_footprint`, and in TEST-M1-06 I observed no wheel–chassis interpenetration.
  - Ground contacts (wheels and caster against the floor) are real physics contacts and are covered by TEST-M1-07.
- **Wheel joint states during M1:** no controller publishes `/joint_states` in Gazebo until M2 (`ros2_control` `joint_state_broadcaster`). Missing wheel TF while the robot runs in Gazebo during M1 is therefore **expected**. For RViz-only tests, `joint_state_publisher_gui` supplies the joint states.

## 5. Future frames (not part of M1)

| Frame / transform | Publisher | Milestone |
|---|---|---|
| `odom → base_footprint` | `diff_drive_controller` (ros2_control) | M2 (introduced), M4 (validated) |
| `/joint_states` for the wheels in simulation | `joint_state_broadcaster` | M2 |
| `lidar_mount_link → laser_frame` | URDF (sensor link) + Gazebo LiDAR sensor; offset (0, 0, +0.030), DEC-030 | M3 (implemented in `amr.sensors.xacro`, `use_sensors:=true`; verified by TEST-M3-03 re-test 1, 2026-11-03) |
| `base_link → imu_link` | URDF + Gazebo IMU sensor; offset (0, 0, 0), DEC-032 | M3 (implemented in `amr.sensors.xacro`, `use_sensors:=true`; verified by TEST-M3-03 re-test 1, 2026-11-03) |
| `map → odom` | SLAM Toolbox | M5 |
| `map → odom` (on a saved map) | localization (e.g. AMCL) | M6 |
| `base_link → camera_link` (+ optical frame) | URDF + Gazebo camera | M11 |

## 6. Verification
Planned on 2026-10-19; all executed and PASS on 2026-10-21 (records in [../../TEST_RESULTS.md](../../TEST_RESULTS.md)):
- TEST-M1-02: tree structure (`check_urdf`). PASS.
- TEST-M1-04: `tf2_echo` values and wheel direction. PASS (visual criteria observed by me).
- TEST-M1-05: `view_frames` diagram. PASS.

Procedures are in [../testing/test_plan.md](../testing/test_plan.md).
