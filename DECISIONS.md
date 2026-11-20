# Engineering Decisions

This file records the important technical decisions of the project: context, the alternatives I considered, the rationale and the consequences. Decisions that only concern my private project administration are not included, so the numbering has gaps.

Status values: **Proposed** (awaiting review), **Accepted**, **Accepted (provisional)** (accepted for the current baseline but may change after review or verification), **Superseded by DEC-nnn**. Do not delete decisions; supersede them.

From DEC-009 onward, each record uses this format:
```
## DEC-nnn — Title
**Date:** YYYY-MM-DD   **Status:**
**Context:** problem being solved
**Decision:**
**Alternatives considered:**
**Rationale and trade-offs:**
**Consequences:**
**Follow-up / open questions:**
```
DEC-001 to DEC-008 predate this format and are kept as originally recorded.

## DEC-001 — Project Type
**Decision:** Build a custom differential-drive AMR for smart-factory material handling.
**Status:** Accepted

## DEC-002 — Simulation First
**Decision:** Develop and validate the majority of the robotics architecture in simulation before attempting physical hardware.
**Reason:** Faster iteration, safer experimentation, and easier debugging.
**Status:** Accepted

## DEC-003 — ROS 2 Distribution
**Decision:** Target ROS 2 Jazzy.
**Reason:** Target development environment is Ubuntu 24.04.
**Status:** Accepted

## DEC-004 — Simulation Platform
**Decision:** Target Gazebo Harmonic.
**Status:** Accepted

## DEC-005 — Final Robot
**Decision:** The final simulated robot will be our own AMR rather than using TurtleBot3 as the final project robot.
**Status:** Accepted

## DEC-007 — Development Environment
**Decision:** Develop on native Ubuntu 24.04.5 LTS with ROS 2 Jazzy and Gazebo Harmonic (Gazebo Sim 8.15.0), installed from binary packages.
**Reason:** Ubuntu 24.04 is the Tier 1 platform for ROS 2 Jazzy and the paired platform for Gazebo Harmonic. Replaces the earlier assumption of a macOS host. Platform and package versions verified by TEST-M0-05. ROS 2 communication, Gazebo, RViz2, and ROS–Gazebo time integration verified by TEST-M0-01 to TEST-M0-04 (including TEST-M0-04 re-test 1).
**Status:** Accepted

## DEC-008 — Workspace Layout
**Decision:** Use a colcon workspace named `amr_ws/` at the repository root, with packages under `amr_ws/src/`. Build outputs (`build/`, `install/`, `log/`) are ignored by Git.
**Reason:** Keeps source and project documentation in one repository while excluding generated files. The name reflects the project rather than a generic `ros2_ws`.
**Status:** Accepted (workspace `amr_ws/` created on 2026-10-19; verified by TEST-M1-01)

## DEC-009 — Documentation-First Engineering Policy
**Date:** 2026-10-19   **Status:** Accepted
**Context:** The project must be reproducible and explainable for academic presentation and technical interviews, and must be possible to continue from the repository alone.
**Decision:** Engineering documentation is a required deliverable for every milestone. That covers requirements with IDs, traceability, design rationale, calculations, exact procedures, results, and evidence. Design and documentation baselines are reviewed before implementation begins.
**Alternatives considered:** (a) Document after implementation. (b) Keep everything in the root files only.
**Rationale and trade-offs:** Writing the design first exposes errors before code exists; for example, the 0.30 m track conflict (DEC-011) was found this way. Focused documents keep the root files short. The cost is more upfront effort and more files to keep consistent.
**Consequences:** One source of truth per fact; root files link to `docs/`. TEST-M1-08 checks consistency between docs and code.
**Follow-up / open questions:** None.

## DEC-010 — Evidence Policy
**Date:** 2026-10-19   **Status:** Accepted
**Context:** Test claims need supporting evidence, but the repository must not fill up with bulky or sensitive files.
**Decision:** Commit genuine, reasonably sized evidence (logs, screenshots, diagrams, plots) under `docs/evidence/<milestone>/`. Exclude bag files, caches, build outputs, and redundant dumps; record their location if they matter. Policy details are in `docs/evidence/README.md`.
**Alternatives considered:** (a) No committed evidence (only text summaries). (b) Commit everything, including bags.
**Rationale and trade-offs:** Committed evidence makes results auditable; excluding bulky files keeps clones small. The cost is a small, deliberate increase in repository size.
**Consequences:** Every `TEST_RESULTS.md` entry links its evidence or says "observed by me".
**Follow-up / open questions:** Revisit the ~5 MB per-file guideline if screenshots or plots need more.

## DEC-011 — Wheel Track 0.400 m
**Date:** 2026-10-19   **Status:** Accepted (M1 design review, 2026-10-19; was Accepted (provisional))
**Context:** The selected chassis width is 0.350 m (half-width 0.175 m). An earlier proposed 0.300 m track would place the 0.035 m-wide wheels at ±0.1325 … ±0.1675 m, inside the chassis outline, so a single-box chassis would overlap the wheels.
**Decision:** Wheel track (centre-to-centre) = **0.400 m**, with the wheels outside the chassis sides.
**Alternatives considered:** (a) 0.300 m track with wheel wells cut into the chassis. (b) Raise the chassis above the wheel tops (≥ 0.15 m ground clearance). (c) Narrow the chassis (rejected: the width is selected).
**Rationale and trade-offs:** A single-box chassis is the simplest to model, explain, and compute inertia for. The trade-off is overall width: 0.435 m instead of 0.350 m, which enlarges the future Nav2 footprint. The nominal wheel-to-chassis gap is only 7.5 mm per side.
**Consequences:** Wheel joint origins at y = ±0.200 m. The M7 footprint must include the wheels. The wider track gives a larger lateral stability margin (CALC-M1-12).
**Follow-up / open questions:** OPEN-02 resolved by DEC-019: the 7.5 mm gap is accepted as a Calculated geometric clearance, checked by dimensions in TEST-M1-03 and visually in TEST-M1-06.

## DEC-012 — Drive Axle 0.100 m Forward of Chassis Centre
**Date:** 2026-10-19   **Status:** Accepted (M1 design review, 2026-10-19; was Accepted (provisional))
**Context:** With one rear caster, the centre of gravity must lie inside the support triangle formed by the two wheel contacts and the caster contact. If the axle passed through the chassis centre, the CG would sit on the forward tipping line.
**Decision:** Place the drive axle **0.100 m forward** of the chassis geometric centre, with the caster near the rear.
**Alternatives considered:** (a) Axle at the centre with front and rear casters (rejected: the drive arrangement specifies one caster). (b) Rear-wheel drive with a front caster.
**Rationale and trade-offs:** With the caster at x = −0.360 m (Selected, DEC-019), the CG is 0.091 m behind the axle and the caster carries ~25 % of the weight. That leaves most of the load on the drive wheels for traction while still giving a forward-tip margin (CALC-M1-11, -12; provisional until 2026-11-03, when OPEN-03 was finalized unchanged by DEC-030 and confirmed by DEC-037, so they are final for current inputs). The trade-off is that rotation in place sweeps the long rear of the robot.
**Consequences:** `base_link` (the axle midpoint) is offset from the chassis centre. The chassis spans x = −0.325 … +0.125 m in `base_link`.
**Follow-up / open questions:** The caster x position (OPEN-01) affects these margins; OPEN-01 is resolved by DEC-019 (x = −0.360 m Selected).

## DEC-013 — Rigid Spherical Caster Approximation
**Date:** 2026-10-19   **Status:** Accepted (M1 design review, 2026-10-19; was Accepted (provisional))
**Context:** The passive rear support needs to be modelled in simulation.
**Decision:** Model the caster as a **rigid sphere on a fixed joint**, with the 0.2 kg caster assembly mass lumped into the sphere. Low-friction contact parameters are deferred to M2.
**Alternatives considered:** A swivel caster (vertical swivel joint plus wheel joint).
**Rationale and trade-offs:** It is simple and has no extra degrees of freedom; swivel casters are a common source of simulation jitter. The trade-off is that it does not reproduce caster flutter or the swivel offset.
**Consequences:** One fixed joint (`caster_joint`); inertia is a solid sphere (CALC-M1-09). With the selected position (DEC-019), the caster overhangs the chassis rear by 0.060 m, so the overall length is 0.510 m (CALC-M1-05). A mounting arm is implied but not modelled.
**Follow-up / open questions:** OPEN-01 resolved by DEC-019: r = 0.025 m at (−0.360, 0, −0.050) in `base_link` is Selected, behind the chassis with 18.0 mm clearance (CALC-M1-13). It replaced an earlier candidate at x = −0.280 m whose top touched the chassis underside. The implied mounting arm is not modelled and has not been validated physically.

## DEC-014 — Passive LiDAR Mount in M1
**Date:** 2026-10-19   **Status:** Accepted (M1 design review, 2026-10-19; was Accepted (provisional)). The bracket dimensions were provisional under OPEN-03 / DEC-019 until 2026-11-03, when DEC-030 finalized them unchanged (Selected); DEC-037 confirmed DEC-030.
**Context:** The LiDAR position affects mapping later, but an active sensor belongs to M3.
**Decision:** Reserve a **passive bracket** (0.2 kg assumed), laterally centred near the front of the top platform, with a `lidar_mount_link` frame for M3. No sensor plugin in M1.
**Alternatives considered:** (a) Centre-top mount (better 360° coverage, but more of the payload area is blocked). (b) Front-face mount (limited field of view). (c) No mount until M3.
**Rationale and trade-offs:** Reserving the mount now fixes the mass budget and frame tree early. A front position keeps most of the platform free, but a future payload may block rear rays.
**Consequences:** `lidar_mount_joint` (fixed) in the M1 frame tree; the bracket is included in the 9.4 kg total.
**Follow-up / open questions:** OPEN-03 accepted as provisional by DEC-019: the 0.080 × 0.080 × 0.030 m bracket at x = +0.070 m is a placeholder until M3 selects the sensor, scan-plane height, and field of view. *Update 2026-11-03:* M3 selected them (DEC-030, DEC-031); the bracket is finalized unchanged by DEC-030 and confirmed by DEC-037. Verification: TEST-M3-03 and -06 (PASS).

## DEC-015 — Payload Excluded from M1
**Date:** 2026-10-19   **Status:** Accepted
**Context:** A 2.0 kg virtual payload was proposed as a candidate.
**Decision:** Exclude the payload from the M1 model. It is deferred to the milestone that introduces material handling.
**Alternatives considered:** Include the payload permanently, or behind a Xacro argument, in M1.
**Rationale and trade-offs:** It keeps M1 focused on the base robot and makes its mass checks unambiguous (9.4 kg). The CG and stability effects will be recalculated when the payload is added.
**Consequences:** The M1 mass budget excludes payload; there is no payload link in M1.
**Follow-up / open questions:** Decide the payload representation (fixed link, Xacro argument, or Gazebo-attached model) in the relevant milestone.

## DEC-016 — M1 Frame Conventions and Origins
**Date:** 2026-10-19   **Status:** Accepted (2026-10-19 as the M1 baseline; was Proposed)
**Context:** The frame layout affects kinematics (M4), TF (all later milestones), and Nav2 (M7).
**Decision:**
- Follow REP-103 (units, axes) and REP-105 (`map → odom → base_link`). The `base_footprint` definition comes from REP-120 (see `docs/design/frames_and_tf.md` §1; REP-105 does not define `base_footprint`).
- `base_footprint` is the massless root on the ground, below the axle midpoint.
- `base_link` is at the axle midpoint, 0.075 m above `base_footprint` (fixed joint, parent `base_footprint`, child `base_link`, xyz (0, 0, 0.075)).
- The wheels are unrotated links with continuous joints on axis (0 1 0).
**Alternatives considered:** (a) `base_link` at the chassis geometric centre. (b) `base_link` as the root with no `base_footprint`. (c) Wheel links rotated ±π/2 about X with axis (0 0 1).
**Rationale and trade-offs:** The axle midpoint is the rotation centre of a differential drive, which simplifies odometry and in-place rotation. A massless root avoids KDL's root-inertia warning. The same wheel axis on both sides gives "positive = forward" for both wheels. The cost is that the chassis inertia must be offset from the `base_link` origin.
**Consequences:** See `docs/design/frames_and_tf.md`.
**Follow-up / open questions:** OPEN-04, OPEN-05, and OPEN-06 were resolved by DEC-019 consistently with this proposal. I accepted this decision on 2026-10-19 as the proposed M1 baseline. If it is ever revised, DEC-019's OPEN-04/05/06 selections must be revisited. The `base_link` height is not an independent parameter: it follows from this decision and the Selected `wheel_radius`.

## DEC-017 — Single `amr_description` Package with Primitive Geometry
**Date:** 2026-10-19   **Status:** Accepted (2026-10-19 as the M1 baseline; was Proposed)
**Context:** M1 needs a robot description, RViz display support, and a Gazebo spawn.
**Decision:** One `ament_cmake` package `amr_description` in `amr_ws/src/` contains the Xacro files, RViz config, and both M1 launch files. Geometry uses primitive shapes only (no meshes).
**Alternatives considered:** Separate `amr_gazebo` / `amr_bringup` packages from the start; mesh-based visuals.
**Rationale and trade-offs:** It is the minimum structure for M1, and primitives avoid mesh resource-path problems and keep the inertia models exact. The visuals are less realistic.
**Consequences:** Package split is deferred until M2 adds controller configuration (to be recorded as a new decision).
**Follow-up / open questions:** None.
*Update 2026-10-22:* the deferred package-split decision is recorded as DEC-023 (`amr_description` + new `amr_bringup`; conditional `ros2_control` option). This decision stays valid for the M1 baseline, which DEC-023 preserves byte-for-byte.

## DEC-019 — M1 Design Review Resolutions (OPEN-01 to OPEN-07)
**Date:** 2026-10-19   **Status:** Accepted; every OPEN item resolved as of 2026-11-03 (OPEN-07 finalized after TEST-M2-10; OPEN-03 finalized by DEC-030, confirmed by DEC-037). *History:* Accepted (provisional): the OPEN-item selections were finalized from the M1 Engineering Decision Report; final after my diff review. OPEN-03 stays provisional until M3. OPEN-07 was provisional until TEST-M1-07. After TEST-M1-07 passed, I kept it provisional, with **M2** named as its follow-up milestone (2026-10-21). *Update 2026-11-03:* OPEN-07 **finalized unchanged** (decided after TEST-M2-10). DEC-016 and DEC-017 are separate decisions, accepted in their own records.
**Context:** The M1 baseline had seven unresolved design items (`docs/milestones/M1_custom_amr.md` §4). The review recomputed CALC-M1-01 to -14 independently, and every recorded value reproduced. It also found documentation and test-design inconsistencies R-01 to R-08, which are corrected in the same change.
**Decision:**
- **OPEN-01:** caster sphere r = 0.025 m, centre (−0.360, 0, −0.050) in `base_link`: **Selected**. The mounting arm is implied, not modelled, and not physically validated.
- **OPEN-02:** nominal wheel-to-chassis gap of 7.5 mm per side: **Calculated** from Selected values. Checked by dimensions in TEST-M1-03 and visually in TEST-M1-06.
- **OPEN-03:** bracket 0.080 × 0.080 × 0.030 m at x = +0.070 m, mount frame on the bracket top: **accepted as a provisional placeholder** until M3. *Update 2026-11-03:* finalized unchanged by DEC-030 (Selected), confirmed by DEC-037.
- **OPEN-04:** unrotated wheel links, joint axis (0 1 0) on both wheels, cylinder geometry rpy (π/2, 0, 0), unrotated inertial frame with Iyy as the axial moment: **Selected**. The sign was analytical until TEST-M1-04. *Verified 2026-10-21 (TEST-M1-04 PASS):* with a positive slider I observed both wheels rolling forward, and TF showed each wheel rotated about +Y with the same sign.
- **OPEN-05:** chassis inertial on `base_link`, with inertial origin (−0.100, 0, +0.035); no separate `chassis_link`: **Selected**.
- **OPEN-06:** ground clearance 0.050 m: **Selected**. The `base_link` height (0.075 m) is **Calculated** from DEC-016 and `wheel_radius`.
- **OPEN-07:** rest-stability thresholds \|Δz\| < 2 mm, \|roll\| and \|pitch\| < 0.5°, drift < 5 mm over 30 s: **accepted as provisional**. The procedure is refined in TEST-M1-07; the numbers are unchanged. *Update 2026-10-21:* TEST-M1-07 passed with these unchanged thresholds. I kept them **provisional** and named **M2** as the follow-up milestone in which they are revisited; the values are not finalized or revised. *Update 2026-11-03:* finalized unchanged after TEST-M2-10 (Selected (final); see Follow-up).
**Alternatives considered:**
- OPEN-01: (a) r = 0.020 m sphere under the chassis (10 mm gap; every dependent calculation redone); (b) more ground clearance; (c) the tangent caster at x = −0.280 m (zero clearance).
- OPEN-04: rotated wheel links with axis (0 0 1).
- OPEN-05: a separate `chassis_link`.
**Rationale and trade-offs:**
- OPEN-01: the only candidate with positive clearance and a complete calculation chain. It puts 34.4 N on each drive wheel (vs 31.4 N at x = −0.280 m) and gives a 12.1 m/s² lateral tipping margin (vs 10.2). The swept radius about `base_link` grows only from 0.369 m to 0.385 m (CALC-M1-13).
- OPEN-04: both joints are defined identically, positive means forward on both, and CALC-M1-08 already uses this convention.
- OPEN-05: an offset `<inertial><origin>` is standard URDF, and the KDL root-inertia warning only concerns the massless root. A `chassis_link` would change the 6-link / 5-joint tree for no benefit.
- OPEN-06: 0.050 m is inside the feasible window 0.030 ≤ c < 0.075 m (CALC-M1-02).
- OPEN-03 and OPEN-07: they cannot be finalized without M3 sensor data and simulation results, respectively.
**Consequences:** The parameter labels are updated in `docs/design/mechanical_geometry.md` §2. CALC-M1-09 is final for current inputs. CALC-M1-10, -11, and -12 stay provisional only because of OPEN-03. CALC-M1-15 (expected SDF lumped link) was added for TEST-M1-03. *Update 2026-11-03:* OPEN-03 was finalized with the bracket unchanged (DEC-030, DEC-037), so CALC-M1-10, -11, -12 and -15 are final for current inputs; no value changed.
**Follow-up / open questions:**
- DEC-016 and DEC-017 were accepted on 2026-10-19 as the proposed M1 baseline (separate records).
- OPEN-03 is revisited in M3. *(Done 2026-11-03: DEC-030, confirmed by DEC-037.)*
- OPEN-07 was revisited after TEST-M1-07 (2026-10-21) and stays provisional; its named follow-up milestone is **M2** (decided 2026-10-21).
- *M2 review 2026-10-22 (no values changed):* the existing evidence (TEST-M1-07: Δz 0 mm, pitch 0.000098°, drift 0 mm) does not justify revising or finalizing the thresholds. M2 changes the rest conditions: OPEN-09 caster contact, and wheels held by active controllers. The thresholds therefore stay **provisional** until TEST-M2-10 has run. A proposed evaluation rule for my decision after TEST-M2-10 is in `docs/design/motion_control.md` §7.
- *Update 2026-11-03: OPEN-07 finalized unchanged.*
  - Evidence: TEST-M2-10 PASS. Re-test 1 on `7b90453` met the quantitative criteria in 3/3 runs: Δz 0.000000 mm, roll 0.000000°, pitch 0.000001° and drift 0.000000 mm, each far below 50 % of its threshold. I observed no visible jitter in the 2026-11-03 GUI session.
  - Under the motion_control.md §7 rule this recommends finalizing unchanged, and I chose that option.
  - The thresholds \|Δz\| < 2 mm, \|roll\| and \|pitch\| < 0.5° and drift < 5 mm over 30 s are now **Selected (final)**. The values did not change.
  - OPEN-03 stays provisional until M3.
- *Update 2026-11-03 (M3):* OPEN-03 **finalized** by DEC-030. The bracket is unchanged, `laser_frame` is +0.030 m above it, and the scan plane is at 0.230 m. Every OPEN item of DEC-019 is now resolved. DEC-037 (2026-11-03) confirmed DEC-030 unchanged after the low-obstacle review.

## DEC-020 — Project Licence: Apache License 2.0
**Date:** 2026-10-21   **Status:** Accepted (decided 2026-10-21)
**Context:** The `amr_description` manifest created in M1 needed a `<license>` value, and the repository had no licence file. The code is intended for reuse as part of a robotics portfolio.
**Decision:** License the project under the Apache License 2.0. The root `LICENSE` holds the complete, unmodified official text, and every ROS package declares `<license>Apache-2.0</license>` in `package.xml`.
**Alternatives considered:** (a) MIT or BSD-3-Clause: permissive, but no express patent grant. (b) GPL-3.0 (copyleft): would restrict reuse in proprietary or mixed-licence projects. (c) No licence: legally all rights reserved, so others could not reuse the code.
**Rationale and trade-offs:** Apache-2.0 allows permissive reuse and adds an express patent grant with patent-retaliation terms. It is also the licence used by most ROS 2 core packages. The trade-off is a longer licence text and the requirement that redistributors mark files they modify.
**Consequences:** New packages use `Apache-2.0`. No `NOTICE` file and no per-file licence headers have been added.
**Follow-up / open questions:** Decide whether to add SPDX headers to source files when code files (launch, Xacro) are created. Check that any third-party asset added later is compatible with Apache-2.0.
*Update 2026-10-22 (SPDX review, no files changed):* the launch, Xacro, CMake, `package.xml`, RViz and evidence-script files exist and none has a licence or SPDX header. Apache-2.0 does not require per-file headers; the root `LICENSE` and `package.xml` already declare the licence. Adding a comment header to an Xacro source changes the generated URDF (xacro copies comments), so the M1 byte comparison in TEST-M1-08 would no longer match its evidence; committed evidence scripts must stay byte-for-byte. The header decision is still open (my decision; see `docs/milestones/M2_basic_movement.md` §9).

## DEC-023 — M2 Package Architecture: `amr_description` + `amr_bringup`, Conditional `ros2_control` (OPEN-08)
**Date:** 2026-10-22   **Status:** Accepted (direction finalized on 2026-10-22, subject to validation; validation passed the same day, see below)
**Context:** DEC-017 deferred the package split until M2 adds controller configuration. M2 needs a `ros2_control` hardware description and the Gazebo control plugin in the robot model, a controller configuration, and simulation and teleop launch files. The M1 display and spawn workflows, and the frozen M1 evidence, must keep working.
**Decision:**
- `amr_description` stays responsible for the robot description. `amr.urdf.xacro` gains two Xacro arguments, `use_ros2_control` (default `false`) and `controllers_file` (default empty), and a conditional include of a new `urdf/amr.ros2_control.xacro`. That file holds the `<ros2_control>` system (`gz_ros2_control/GazeboSimSystem`, the two wheel joints), the Gazebo `gz_ros2_control-system` plugin tag, and the M2 contact/friction surfaces (OPEN-09). All of it is emitted only when `use_ros2_control:=true`.
- A new package `amr_bringup` (`ament_cmake`, Apache-2.0) owns integration: `config/controllers.yaml` and the M2 simulation and teleop launch files. It depends on `amr_description`; `amr_description` does not depend on it. The controller file path reaches the plugin through the `controllers_file` argument, so there is no reverse dependency.
- The M1 launch files and their Xacro call (no arguments) are unchanged.
- **Rule:** nothing may be added to `amr.urdf.xacro` outside the conditional except the two `xacro:arg` lines. Xacro copies comments into its output, so any other edit would change the default URDF.
**Validation (2026-10-22, [`docs/evidence/M2/OPEN-08_xacro_option_check.log`](docs/evidence/M2/OPEN-08_xacro_option_check.log), script `OPEN-08_xacro_option_check.sh`, prototype on a temporary copy, `amr_ws/` untouched):**
- Default and explicit-`false` expansions are **byte-identical** to `TEST-M1-02_amr.urdf`.
- The enabled expansion passes `check_urdf`: 6 links, 5 joints, one `ros2_control` system on exactly the two wheel joints, and the controller path passed through. `gz sdf -p` keeps the plugin.
- The TEST-M1-03 property check passes in full on the default variant. On the enabled variant only the two M1-scope assertions fail (REQ-M1-09 "no `<gazebo>`/`<plugin>`", REQ-M1-10 "no `filename`"), as intended.
- Every intended `amr_bringup` dependency resolves in the installed environment (`ros2 pkg prefix`): `ros_gz_sim`, `ros_gz_bridge`, `controller_manager`, `diff_drive_controller`, `joint_state_broadcaster`, `gz_ros2_control`, `robot_state_publisher`, `xacro`, `teleop_twist_keyboard`, `launch`, `launch_ros`. The installed `spawner` supports `--controller-ros-args`, which applies the planned `/cmd_vel` remap. *(The remap was later removed by DEC-029.)*
**Alternatives considered:**
- (a) Everything in `amr_description`: fewest packages, but runtime and controller configuration would live in the description package, which M13 hardware would have to work around.
- (c) Separate `amr_gazebo` and `amr_control` packages: more structure than M2 needs.
- Unconditional `ros2_control` tags: rejected, because they would change the M1 model and break the M1 display/spawn reproduction and the evidence comparison.
**Rationale and trade-offs:** the description stays a pure model that hardware (M13) can reuse with a different hardware plugin, and integration concerns gain one clear home. The M1 baseline remains reproducible bit-for-bit, so the existing TEST-M1-08 byte comparison stays a valid regression check. The cost is one more package and two Xacro arguments that callers must pass correctly. A wrong or empty `controllers_file` fails at plugin load, and TEST-M2-03 catches it.
**Consequences:**
- TEST-M2-02 runs the M1 checks on the default variant (including the byte comparison) plus an M2-specific check on the enabled variant. The M1-scope assertions are replaced, not ignored.
- `docs/architecture/ros_architecture.md` §1 lists `amr_bringup` as Accepted (not yet created). *Update:* created on 2026-10-22 in `26a6048`, and §1 records it.
**Migration steps (M2 step 1–2, not started):** create `amr_bringup`; add the two arguments and the conditional include to `amr.urdf.xacro`; add `amr.ros2_control.xacro`; re-run TEST-M1-08 (expected to pass unchanged) and TEST-M2-01/02. *Update:* completed on 2026-10-22 (M2 steps 1–2). The M1 byte comparison runs inside TEST-M2-02 (re-test 2 PASS), and TEST-M2-01 passed (`TEST_RESULTS.md`).
**Follow-up / open questions:** none for the structure. The values inside the new files depend on OPEN-09 to OPEN-11.

## DEC-024 — M2 Contact and Friction Parameters (OPEN-09)
**Date:** 2026-10-22   **Status:** Accepted (decided 2026-10-22)
**Context:** DEC-013 deferred the caster contact to M2. With the defaults, the fixed caster sphere has μ = 1 and drags with 23.4 N, giving 8.42 N·m of in-place yaw resistance (CALC-M2-01). The OPEN-09 probe measured that the installed Gazebo/DART uses μ_eff = min(μ₁, μ₂) ([probe log](docs/evidence/M2/OPEN-09_friction_probe.log)).
**Decision:**
- Wheel collision `mu` = `mu2` = **1.0**.
- Caster collision `mu` = `mu2` = **0.01**.
- No torsional friction, rolling friction, contact stiffness/damping (`kp`, `kd`), `max_vel`, `min_depth`, `fdir1` or slip parameters: the installed DART plugin ignores the first group, and the rest are not needed.
- The surfaces are emitted only with `use_ros2_control:=true` (DEC-023).
**Alternatives considered:** wheel μ 0.7; caster μ 0 or 0.05 (`docs/design/motion_control.md` §3).
**Rationale and trade-offs:**
- With the stock ground at μ = 1, the robot's μ is the effective μ. Wheel μ 1.0 is ≥ 7× the friction the selected limits require (CALC-M2-02).
- Caster μ 0.01 removes the artificial sliding drag of the rigid sphere. It is an **initial simulation-modelling choice**, not a measured property of a real caster.
**Consequences:** verified by TEST-M2-02 (values present on the wheel and lumped caster collisions), TEST-M2-05/06/08 (motion, slip, attitude) and TEST-M2-10 (rest). If these settings cause unexplained instability, the affected test stops and the evidence is reported; no other values are selected silently.
**Follow-up / open questions:** real-floor and real-caster friction are unknown until hardware (M13).

## DEC-025 — M2 Velocity and Acceleration Limits (OPEN-10)
**Date:** 2026-10-22   **Status:** Accepted (decided 2026-10-22)
**Context:** the installed `diff_drive_controller` (4.42.1) has no limits by default; every limit is NaN. The CALC-M1-12 tipping values (8.4 / 12.1 m/s²) are reference values only. Traction at a design μ of 0.5 limits forward acceleration to 3.19 m/s² and braking to 4.29 m/s² (CALC-M2-03).
**Decision (operating assumption: indoor, low-speed simulation and development):**

| Limit | Value | Installed parameter (sign convention verified from the installed validators) |
|---|---|---|
| Forward speed | 0.5 m/s | `linear.x.max_velocity: 0.5` (must be ≥ 0) |
| Reverse speed | 0.25 m/s | `linear.x.min_velocity: -0.25` (must be ≤ 0) |
| Linear acceleration | 0.5 m/s² | `linear.x.max_acceleration: 0.5` (≥ 0); reverse uses the default −max_acceleration |
| Linear deceleration | 1.0 m/s² | `linear.x.max_deceleration: -1.0` (must be **≤ 0**); reverse uses the default −max_deceleration |
| Angular speed | 1.0 rad/s | `angular.z.max_velocity: 1.0`, `angular.z.min_velocity: -1.0` |
| Angular acceleration | 2.0 rad/s² | `angular.z.max_acceleration: 2.0`, `angular.z.max_deceleration: -2.0` |
| Jerk | none | jerk limits left at NaN (disabled) |

**Alternatives considered:** symmetric reverse speed; higher speeds (no requirement exists).
**Rationale and trade-offs:**
- Every acceleration limit is at least 3× below the traction bound at μ 0.5 and the tipping bounds.
- Reverse is capped lower because the LiDAR is front-mounted (DEC-014).
- These are **simulation development limits, not certified hardware safety limits**; simulation results do not establish hardware readiness.
**Consequences:** configured in `amr_bringup/config/controllers.yaml`; verified by TEST-M2-08 (configured limits and measured behaviour) and TEST-M2-07 (stopping).
**Follow-up / open questions:** revisit with evidence for M7 navigation tuning and M13 hardware.

## DEC-026 — M2 Controller Rate and Command Interface (OPEN-11)
**Date:** 2026-10-22   **Status:** Accepted (decided 2026-10-22); command routing **amended by DEC-029** (2026-10-22): the spawner remap below is replaced by `cmd_vel_guard`.
**Decision:**
- `controller_manager` `update_rate` **100 Hz**.
- `diff_drive_controller` `publish_rate` **50 Hz**, `cmd_vel_timeout` **0.5 s**.
- Command topic **`/cmd_vel`** of type **`geometry_msgs/msg/TwistStamped`**, the controller's `~/cmd_vel` remapped through the spawner's `--controller-ros-args`. *Superseded by DEC-029:* the remap is removed; `cmd_vel_guard` subscribes to `/cmd_vel` and is the only publisher to `/diff_drive_controller/cmd_vel`. The public topic and type are unchanged.
- `odom_frame_id: odom`, `base_frame_id: base_footprint`, `enable_odom_tf: true`, `publish_limited_velocity: true`.
- Keyboard teleop publishes stamped commands (`stamped:=true`) on simulation time (`use_sim_time:=true`).
**Rationale:** 100 Hz divides the 1 kHz physics step evenly. The message type and parameters match the installed controller; the frames follow DEC-016.
**Consequences:**
- Every publisher of stamped commands must use simulation time.
- TEST-M2-07 checks that commands stop being applied after the timeout, the handling of stale and wall-clock stamps, and publisher/controller clock consistency.
- TEST-M2-03 checks that there is no motion before the controllers are active.
**Follow-up / open questions:** the teleop key-repeat interaction with the 0.5 s timeout is recorded in TEST-M2-09.

## DEC-027 — M2 Motion-Test Acceptance Criteria (OPEN-12)
**Date:** 2026-10-22   **Status:** Accepted (decided 2026-10-22)
**Decision:** the formal M2 motion tests use these criteria. Exact profiles, initial conditions, measurement windows and calculations are in `docs/testing/test_plan.md` §6.
- Three valid runs per test.
- Distance and turn angle within ±5 % of the stated targets (0.980 m; 180°).
- Sideways drift and translation during an in-place spin ≤ 20 mm; heading change during a straight run ≤ 1°.
- Stop from 0.5 m/s within 0.70 s and 0.150 m; stop after commands cease within 0.90 s.
- Controller startup within 10 s of simulation time, with no motion before activation.
- Tilt during motion < 1°.
- Odometry direction correct and magnitude within 0.5–1.5× ground truth (gross-fault check only; accuracy is M4).
- A run with RTF < 0.5 is rejected and repeated.
**Rationale:** `docs/design/motion_control.md` §6.
**Consequences:** thresholds are not changed to make a failing test pass. Failures are recorded with TS entries and re-tests.
**Follow-up / open questions:** M4 defines the odometry accuracy criteria.

## DEC-028 — M2 Simulation Wheel Collision: Sphere of the Wheel Radius (TS-014)
**Date:** 2026-10-22   **Status:** Accepted (preferred option (a); validated 2026-10-22 by TEST-M2 re-test 1 on `7b90453`: rotation +179.90 to +180.20° and −179.90 to −180.19°, yaw rate 1.0000 rad/s, with no regression in TEST-M2-02 (re-test 2), -03, -05, -07, -08, -10)
**Context:**
- Formal TEST-M2-06 (revision `26a6048`, cylinder wheel collision) turned +196.63° / −196.40° for a 180° command in all 3 runs, while odometry and the wheels behaved as commanded.
- TEST-M2-08 measured a yaw rate of 1.096 rad/s for 1.0 rad/s commanded, an effective track of ≈ 0.3665 m against `wheel_track` 0.400 m.
- A diagnostic changing only the wheel collision to a sphere gave 180.18° / −179.87° (TS-014).
- *Hypothesis, not established:* DART's cylinder–plane contact acts near the inner wheel rims during rotation. The contact-point locations were not measured.
**Decision:**
- When `use_ros2_control:=true` (the M2 simulation model), each wheel collision is a sphere of radius `wheel_radius`, centred on the wheel origin.
- The cylinder visual, the inertia (CALC-M1-08), the joints, the DEC-024 surface (μ 1.0), the controller track (0.400 m) and the odometry are unchanged.
- The default (M1) model keeps the cylinder collision and stays byte-identical to the M1 evidence. The selection sits inside the wheel macro with `xacro:if`/`xacro:unless`, which DEC-023's rule did not foresee; byte identity, the rule's purpose, was verified.
**Validation evidence (pre-formal, 2026-10-22):**
- Contact height z = 0 (same rolling radius) and μ = 1 applied to the sphere in the generated SDF.
- Preliminary rotation: +180.21° / −179.90°, odometry ratio 1.000, translation 0.00 mm.
- Formal acceptance: TEST-M2-02, -03, -05, -06, -07, -08, -10 re-test 1.
**Alternatives considered:**
- (b) Calibrating the controller (`wheel_separation_multiplier` ≈ 0.916): it would make odometry agree with a simulation artifact rather than with the designed geometry.
- (c) Accepting the deviation and revising DEC-027: rejected without an independent justification.
- A narrower cylinder or a capsule were not tested.
**Rationale and trade-offs:** a sphere touches a flat floor at a single point on the wheel mid-plane, which is the contact a thin real tyre has, so the kinematic track equals the designed 0.400 m.
**Limitations:**
- The sphere is wider than the tyre: the collision reaches |y| = 0.275 m against 0.2175 m for the cylinder (+57.5 mm per side), and it overlaps the chassis volume inwards. There are no forces between them, because joint-connected links do not collide (SDFormat 1.11).
- This matters for contact with obstacles and kerbs (M8) and for uneven floors, not for the flat M2 world.
- The real wheel's contact patch and its scrub during rotation are not modelled.
- Simulation only; no hardware conclusion.
**Consequences:** TEST-M2-02's control check expects sphere wheel collisions. TS-014 is resolved if re-test 1 passes. *Update 2026-10-22:* re-test 1 passed (TEST-M2-06 and -08 re-test 1 PASS, recorded in `bb3f4fb`); TS-014 is resolved (`docs/troubleshooting.md`).
**Follow-up / open questions:** revisit before M8 obstacle work: the collision width, and whether a different geometry (capsule, narrower cylinder) would avoid both the DART artifact and the width.

## DEC-029 — Command-Freshness Guard on `/cmd_vel` (TS-015)
**Date:** 2026-10-22   **Status:** Accepted (self-directed safeguard; validated 2026-10-22 by TEST-M2-03, -05 and -07 re-test 1: stale, wall-clock and domain-switch cases rejected; stop after the last valid command ≤ 0.726 s)
**Context:**
- Formal TEST-M2-07 characterized a hazard: commands stamped in wall-clock time, while the controller runs on simulation time, were accepted and never timed out. The robot kept moving 0.598 m in the 3 s after the last command.
- Introspection of the installed `diff_drive_controller` 4.42.1 (strings of `libdiff_drive_controller.so`) shows how it treats stamps:
  - on receipt, a zero stamp is replaced by the current time;
  - a message "older than the current time by … which exceeds the allowed timeout" is ignored;
  - the update loop brakes when the stored stamp is older than `cmd_vel_timeout`.
- A future stamp therefore has negative age, passes both checks, and never expires. No controller parameter bounds future stamps (installed parameter list).
- The controller cannot detect the mismatch by itself, so the narrowest reliable place is the command interface in front of it.
**Decision:**
- A C++ node `amr_bringup/cmd_vel_guard` (on simulation time) subscribes to `/cmd_vel` and is the only publisher to the controller input `/diff_drive_controller/cmd_vel`. The spawner remap of DEC-026 is removed; the public command topic stays `/cmd_vel`.
- It forwards a command only if |now − stamp| ≤ `cmd_vel_timeout`. That is the controller's own freshness window (DEC-026, 0.5 s) applied symmetrically, not a new tuning value; a wall-clock stamp differs by about 1.8·10⁹ s.
- It rejects zero stamps and every command received before its clock is valid, because freshness cannot be established then.
- It forwards with stamp = min(stamp, now), so a forwarded command can never stay fresh longer than `cmd_vel_timeout` after it arrives.
- A rejected command is dropped (throttled warning with a count). The controller then sees no fresh command and brakes through its own timeout and the DEC-025 limits.
- Its `cmd_vel_timeout` lives in `controllers.yaml` and must equal the controller's (TEST-M2-11).
**Alternatives considered:**
- A zero-stamp relay (the controller re-stamps on receipt): it loses the publisher's age information.
- A Python guard: rejected, because Python could not keep up with the 1 kHz `/clock` (TS-013).
- Fixing only the publishers: rejected, because it does not protect the interface.
- A controller fork: too large.
**Rationale and trade-offs:**
- This is the smallest component that enforces the DEC-026 contract at the interface, independent of each publisher's correctness.
- It adds one hop of latency, sub-millisecond in the same machine; measured indirectly by TEST-M2-07.
- Up to 0.5 s of future clock skew is tolerated, but bounded by the clamp.
**Residual limitations:**
- Publishers that bypass the guard by writing to `/diff_drive_controller/cmd_vel` directly are not protected.
- If the guard process dies, no command reaches the controller, which brakes (fail-safe), but nothing reports the guard's death.
- Simulation only; on hardware, cross-machine clock synchronization still matters.
- Not a certified safety function.
**Consequences:** TEST-M2-07's wall-clock mode becomes pass/fail (no motion). The DEC-026 interface is unchanged for publishers.
**Follow-up / open questions:** M7 (Nav2) must publish to `/cmd_vel` with stamped simulation-time commands (Nav2's `enable_stamped_cmd_vel`).

## DEC-030 — M3 LiDAR Mount and Scan Plane (OPEN-03 finalized)
**Date:** 2026-11-03   **Status:** Accepted (decided 2026-11-03); verification by TEST-M3-03 and TEST-M3-06. **Reopened for review by me on 2026-11-03** (after the feasibility gate) because of the 0.230 m low-obstacle blind zone. The low-obstacle comparison and its recommendation are in `docs/milestones/M3_sensors.md` §12. Until that review, OPEN-03 stayed unresolved; the values below were never changed. **Closed 2026-11-03 by DEC-037** (decided option 3): DEC-030 is confirmed unchanged, and low-obstacle detection is assigned to a forward depth camera in M8.
**Context:** DEC-014 reserved a passive bracket; DEC-019 kept its size and position provisional (OPEN-03) until M3 chose the sensor and scan plane. Analysis: `docs/design/sensors.md` CALC-M3-01.
**Decision:**
- The existing bracket is kept unchanged (`lidar_bracket_*` 0.080 × 0.080 × 0.030 m, `lidar_mount_x` +0.070 m).
- `laser_frame` is a fixed child of `lidar_mount_link` at (0, 0, +0.030) m with identity rotation.
- The scan plane is therefore at 0.230 m above flat ground, 30 mm above the robot's highest point (the bracket top at 0.200 m).
- OPEN-03 is **finalized** with these values; the bracket values change from Proposed to Selected.
**Alternatives considered:** a lower plane in a front cut-out (loses rear coverage to chassis occlusion); a higher mast (larger blind height); re-sizing the bracket (changes the M1 geometry).
**Rationale and trade-offs:**
- No robot part rises above 0.200 m, so the 360° field of view is unobstructed (CALC-M3-01).
- The cost is a **low-obstacle blind zone**: obstacles lower than 0.230 m are not detected.
**Consequences:**
- The blind zone is documented for M8 and characterized by TEST-M3-06; mitigation is M8 scope.
- With `range_max` 12 m, a 1° pitch keeps the beams 0.020 m above the floor (limit 13.18 m, CALC-M3-01).
- DEC-019 is updated.
**Follow-up / open questions:** confirm no self-returns in TEST-M3-06.

## DEC-031 — M3 LiDAR Sensor Model (OPEN-13)
**Date:** 2026-11-03   **Status:** Accepted (decided 2026-11-03); sensor type subject to the M3 feasibility gate
**Decision** (simulation baseline of a generic indoor 2D LiDAR class, not a product datasheet):
- 360° horizontal field of view (−π to +π), 1° angular resolution (360 samples), 1 vertical ray.
- Range 0.12 to 12.0 m; update rate 10 Hz.
- Gaussian range noise with mean 0 and σ = 0.01 m.
- ROS topic `/scan` (`sensor_msgs/msg/LaserScan`), `frame_id` `laser_frame`.
- Gazebo sensor type `gpu_lidar` (rendering-based), provided the feasibility gate shows it works headless on the development machine.
**Rationale:** `docs/design/sensors.md` §4 (OPEN-13): aisle-scale range below the 13.18 m pitch limit; 0.05 m of travel per scan at 0.5 m/s; noise so that M5/M6 are tested against realistic data.
**Consequences:** if `gpu_lidar` fails the feasibility gate, the sensor type returns for review with alternatives. The architecture is not changed silently.
**Follow-up / open questions:** verified by TEST-M3-04, -05, -06.

## DEC-032 — M3 IMU Model and Placement (OPEN-14)
**Date:** 2026-11-03   **Status:** Accepted with specification (decided 2026-11-03); **amended by DEC-038** (2026-11-03). The text below is kept as originally recorded. DEC-038 changes only two points: the internal sampling rate (the sensor samples at 1000 Hz and publishes `/imu` at 100 Hz), and where the noise values apply (they are defined at the published `/imu` output). All other content is unchanged.
**Decision:**
- `imu_link` is a fixed child of `base_link` at (0, 0, 0) with identity rotation (axle midpoint; CALC-M3-02). Update rate 100 Hz.
- Noise: Gaussian with mean 0. Angular velocity σ = **0.001 rad/s** and linear acceleration σ = **0.01 m/s²** per axis; **zero bias**, no bias drift.
- These noise values are **simulation assumptions** (label: Assumed). They are **not hardware specifications** and do not describe any physical IMU.
- Conventions:
  - axes follow `imu_link` (REP-103: +X forward, +Y left, +Z up);
  - angular velocity is positive counter-clockwise about each axis;
  - linear acceleration is **specific force**, so at rest on level ground the IMU reads +g ≈ +9.8 m/s² on +Z, not 0. Gravity is taken from the world (SDFormat default (0, 0, −9.8) m/s² unless the world sets it; confirmed in the feasibility gate).
  - The orientation field is simulator-derived and is not used as ground truth.
- ROS topic `/imu` (`sensor_msgs/msg/Imu`), `frame_id` `imu_link`.
**Alternatives considered:** the proposed σ 0.002 rad/s / 0.02 m/s² (I chose the lower values); IMU at the chassis centre of mass (adds lever-arm accelerations); bias models now (deferred to M6 if evidence requires).
**Consequences:** the DEC-036 statistical checks use these σ values. Bias and drift, if needed for M6 realism, need a new decision.
**Follow-up / open questions:** verified by TEST-M3-03, -04, -07, -08.

## DEC-033 — M3 Wheel-Encoder Feedback (OPEN-15)
**Date:** 2026-11-03   **Status:** Accepted (decided 2026-11-03)
**Decision:**
- The wheel positions on `/joint_states`, published by `joint_state_broadcaster` from `gz_ros2_control` (M2), are the **ideal simulated encoder feedback**: continuous, without quantization, noise or bias.
- This is **not a physical hardware encoder model**, and the documentation does not describe it as one.
- No encoder-emulation node in M3.
**Rationale:** CALC-M3-03. A 4096-count encoder would resolve 0.115 mm of travel, far below the M3/M4 tolerances; slip is already measured (< 0.01 %, TEST-M2-05).
**Consequences:** M4 may revisit quantization or noise if its odometry error budget needs it (new decision). The `/joint_states` rate is measured, not assumed (feasibility gate; TEST-M3-04).
**Follow-up / open questions:** verified by TEST-M3-04 and -09.

## DEC-034 — M3 Sensor Integration Architecture (OPEN-16)
**Date:** 2026-11-03   **Status:** Accepted with conditions (decided 2026-11-03)
**Decision:**
- **Sensor option:** sensors are added through a Xacro argument `use_sensors`, **default false**, in a new `amr_description/urdf/amr.sensors.xacro`. With the option off, the model output must stay **byte-identical** to the M1 evidence (`TEST-M1-02_amr.urdf`), as with DEC-023.
- **Mass:**
  - the total robot mass stays **9.4 kg**;
  - `laser_frame` and `imu_link` are URDF links with **no `<inertial>` element**, attached by fixed joints, so that SDFormat lumps them into their parent body;
  - the generated SDF must contain **no link with zero mass or zero inertia**;
  - the 0.2 kg bracket mass represents the bracket plus LiDAR assembly (Assumed);
  - masses and inertias are otherwise unchanged.
- **World:** a dedicated sensor test world `amr_bringup/worlds/sensor_test.sdf`, containing the stock `empty.sdf` systems plus the Sensors (`ogre2`) and IMU systems, 1 kHz physics, and static targets at known poses.
- **Launch and bridge:**
  - `sim.launch.py` gains `world` and `sensors` arguments whose defaults reproduce the M2 behaviour;
  - `amr_bringup/config/sensor_bridge.yaml` bridges `/scan` and `/imu`, Gazebo → ROS.
**Alternatives considered:** sensors always on (breaks the M1 byte comparison); separate sensor masses (changes the 9.4 kg total and M2 dynamics); sensors as the launch default now (deferred).
**Consequences:**
- The conditions are acceptance criteria of TEST-M3-02.
- The lumped-link behaviour (sensor pose kept, no zero-inertia link) is checked first in the feasibility gate.
**Follow-up / open questions:** verified by TEST-M3-02, -04, -11.

## DEC-035 — M3 IMU Visualization (OPEN-17)
**Date:** 2026-11-03   **Status:** Accepted (decided 2026-11-03)
**Decision:**
- `rviz_imu_plugin` is **not installed** for M3.
- IMU messages are validated through ROS topics: `ros2 topic echo` / `hz` and the M3 test harness statistics.
- Visualization uses installed, supported tools only: RViz `TF` (the `imu_link` axes) and RViz `LaserScan` for the LiDAR. Any other tool is used only after confirming it is installed.
**Consequences:** no environment change. A plugin is reconsidered only if a real visualization requirement emerges (new decision).
**Follow-up / open questions:** TEST-M3-10 checks the LaserScan and frames (observed by me).

## DEC-036 — M3 Sensor Test Acceptance Criteria (OPEN-18)
**Date:** 2026-11-03   **Status:** Accepted with specification (decided 2026-11-03)
**Decision:**
- **Deterministic checks are separated from statistical noise checks.** Noisy samples are never required to fall individually inside a narrow tolerance.
- Full specification (sampling windows, rates, frames, noise distributions, statistical method, pass/fail limits): `docs/design/sensors.md` §7 and `docs/testing/test_plan.md` §7.
- Summary:
  - *Deterministic:* exact topic, type and `frame_id`; rates from simulation-time header stamps within ±2 %; stamps strictly increasing and within 0.1 s of `/clock`; LaserScan configuration fields to 1e-6; TF offsets to 1e-6; signs; FOV detection; no self-returns; blind-zone non-detection; encoder travel within ±2 %; IMU gyro z within ±3 % of the ground-truth yaw rate.
  - *Statistical* (n ≥ 1000 samples per statistic, Gaussian noise per DEC-031/032):
    - bias |mean error| within a fixed engineering limit;
    - sample standard deviation within 0.8–1.2 × the configured σ;
    - fraction of samples within ±2s of the mean in [0.93, 0.98], where s is the sample standard deviation (S3, sensors.md §7.4);
    - no sample beyond 6σ of the mean.
  - 3 runs for motion tests; RTF ≥ 0.5.
**Rationale:**
- For Gaussian noise with n ≥ 1000, the sample-σ band is more than 6 standard errors wide and the ±2σ fraction band is more than 3.7 binomial standard deviations wide, so a correct sensor fails with negligible probability. A wrong noise model (wrong σ, wrong distribution, bias, spurious returns) still fails.
- Derivation: sensors.md §7.
**Consequences:** thresholds are not changed to make a failing test pass (as DEC-027).
**Follow-up / open questions:** none.

## DEC-037 — Low-Obstacle Sensing Architecture (OPEN-03 closed)
**Date:** 2026-11-03   **Status:** Accepted (decided 2026-11-03)
**Context:**
- After the M3 feasibility gate, I reopened OPEN-03 (DEC-030) because the 0.230 m scan plane cannot see obstacles lower than 0.230 m.
- Three architectures were compared in `docs/milestones/M3_sensors.md` §12: (1) upper LiDAR only; (2) a lowered LiDAR; (3) the upper LiDAR plus a lower obstacle sensor.
- Basis: CALC-M3-04 (self-occlusion ray cast) and two scratch Gazebo runs; evidence `docs/evidence/M3/LOWOBS_*`.

**Decision:**
- **Option 3.** The accepted 360° LiDAR stays **unchanged**:
  - DEC-030: bracket 0.080 × 0.080 × 0.030 m at x = +0.070 m, `laser_frame` +0.030 m above it, scan plane 0.230 m;
  - DEC-031: 360°, 1°, 0.12–12 m, 10 Hz, σ 0.01 m.
- Low-obstacle detection is done by a **forward-facing, down-tilted depth camera**, which is an **M8 sensor**. It is not part of M3, and there is no M3 Task F.
- M3 scope stays the LiDAR, the IMU and the wheel encoders (DEC-030 to DEC-036).
- The camera's parameters are **not decided here**: pose, tilt, FOV, resolution, range, rate, noise model and filtering. They need a separate, evidence-backed M8 decision. The LOWOBS trial values (`LOWOBS_sensors_A_trial.xacro`) were investigation values only.
- OPEN-03 is **closed** with DEC-030 confirmed unchanged. Blind-zone mitigation becomes an M8 implementation item.

**Alternatives considered:**
- Option 1 alone: no low-obstacle mitigation.
- Option 2:
  - 2a, on the chassis top, gains 40 mm only.
  - 2b/2c, a front-protruding plane at 0.120 / 0.060 m, lose 157° at the rear to the chassis (203/360 beams). They also change the M1 footprint, and floor hits at a 1° pitch fall within `range_max` (6.87 / 3.44 m), which would force a DEC-031 change. They also cannot be simulated faithfully with `gpu_lidar` (TS-022).
  - 2d, under the chassis, does not fit the 0.050 m clearance.
- Adding the camera to M3 as Task F: rejected; the camera belongs with its consumer in M8.

**Rationale (evidence, M3 plan §12):**
- Option 3 is the only option that detected all four low targets in simulation:
  - 0.03 m part, 0.08 m tote, 0.15 m box and 0.144 m pallet proxy;
  - recovered top heights 0.030 / 0.080 / 0.150 / 0.144 m (`LOWOBS_run_A.log`).
- It keeps 360° LiDAR coverage with 0 self-returns, the best basis for mapping (M5) and localization (M6).
- It changes no accepted geometry, mass or specification. The G1–G6 feasibility evidence and the planned M3 Tasks stay valid.
- Measured simulation cost was small in the test world: RTF 0.993 with the camera, vs 0.997–0.998 without.

**Limitations (recorded from the investigation; not resolved by this decision):**
- **Noise-free simulation.** The trial camera had no depth noise, and the floor was perfectly flat with the robot at rest. The detection results are upper bounds. **Noise-free simulation results are not hardware validation**; any hardware claim needs M13 measurements.
- **Front-only coverage.** About ±43.5° horizontally in the trial; the rear and sides remain blind to obstacles lower than 0.230 m.
- **Pitch sensitivity.** A pitch θ shifts the apparent floor at distance d by d · tan θ: 0.017 d m per 1°, i.e. 0.026 m at 1.5 m (Calculated). That is comparable to the height of small dropped parts.
- **Small dropped parts** are expected to be reliable only at short range (Estimate). The range must be established with a noise model.
- **Assumed inputs.** EUR-pallet details and dropped-part sizes are Assumed; the pallet proxy is simplified.
- **Rendering cost** was measured in one simple world only.

**Requirements carried into M8 planning.** These are planning inputs. M8 turns them into REQ-M8 IDs with acceptance criteria and tests:
1. **Front-only coverage.** Define the behaviour for reversing and in-place rotation near low obstacles, and justify it by analysis or test. Examples: restricted reversing, costmap persistence, an additional sensor.
2. **Pitch sensitivity.** Quantify the apparent floor shift over the camera's working range, for the expected pitch (M2 attitude limit < 1°, DEC-027) and floor unevenness. Size the floor filter from it.
3. **Short-range reliability for small dropped parts.** Specify and verify the range within which a stated minimum object height is detected. Make no claim beyond the verified range.
4. **Stopping distance.** Define it from the speed limits and include detection and control latency. Reference (Calculated, DEC-025): braking only, v² / 2a = 0.5² / (2 · 1.0) = 0.125 m forward and 0.25² / 2 = 0.031 m in reverse. The detection range must exceed stopping distance plus margin, and the camera's near limit must be covered.
5. **Floor-filter thresholds.** Define the minimum and maximum obstacle height and the clearing behaviour (e.g. Nav2 `min_obstacle_height`), with evidence.
6. **Noise model.** M8 simulation must include an explicit depth-noise model. Results without noise are labelled as idealized and are not used as acceptance evidence for detection limits.
7. **Rendering cost.** Re-verify the RTF in the M8/M9 worlds (RTF < 0.5 invalidates runs).
8. **Specification stability.** DEC-031 and the other accepted specifications are not changed without a separate evidence-backed decision.

**Consequences:**
- DEC-030 is confirmed (its "reopened" note is closed by this decision); OPEN-03 is closed.
- Blind-zone mitigation stays deferred with M8 as the implementation milestone; its scope is this decision's camera and requirements.
- M3 Tasks and tests are unaffected. TEST-M3-06 still characterizes the 0.230 m blind zone. TS-022 applies to any future low-mounted `gpu_lidar`.

**Follow-up / open questions:**
- M8 planning: the camera parameter decision, REQ-M8 and tests, covering requirements 1–8 above.

## DEC-038 — M3 IMU Output Decimation: 1 kHz Sampling, 100 Hz Block-Mean Output (TS-027, correction C4)
**Date:** 2026-11-03   **Status:** **Accepted** (decided 2026-11-03), with the clarifications below; implemented and verified in M3. *History:* first recorded as Proposed in `349064c` after I finalized C4 as the preferred direction. The rationale and prototype evidence below are kept as recorded.

**Acceptance clarifications (2026-11-03):**
- Delays:
  - 4.5 ms is the theoretical FIR group delay for acceleration spread evenly over a block.
  - 5 ms is the interval centre.
  - **8–9 ms** is the measured response delay to a controller velocity step.
- The published noise requirements (DEC-032) are unchanged. The raw settings stay *derived* values (√10 × published), not independently specified tolerances. The output noise is verified experimentally (TEST-M3-07 re-test 1).
- M4 must respect the interval-mean timestamp semantics (item 6).
- The DEC-036 D11 tolerances are unchanged. The braking ± 20 % criterion and the 10 ms stamp-grid check (TEST-M3-14, TEST-M3-04 re-test 1) are added as new criteria. TEST-M3-13 also covers pause/resume and world reset.
- The package is a new `amr_gazebo_plugins` (sensors.md §8.6, item 1). The Python prototype stays historical evidence only.

**Context:**
- TEST-M3-08 D11 failed 3/3: the 100 Hz IMU reads ≈ 0 m/s² while the robot accelerates at 0.5 m/s² (TS-027).
- Cause, from the bounded investigation (`TS-027_investigation.log`):
  - `diff_drive_controller` holds each wheel command for 10 ms (DEC-026), so the chassis velocity changes in one physics step per cycle.
  - The Gazebo IMU reports the acceleration of a single step at 100 Hz, at a fixed phase that never holds that step.
  - In the launch the steps fall 1–2 ms after each 10 ms boundary (`TS-027_C4_delay.log`).
- The installed SDFormat IMU element has no averaging or filter option, only noise, bias and orientation settings (`gz sdf -d`).
- The C4 scratch prototype (`TS-027_C4_validation.log`, `TS-027_C4_delay.log`; informal) showed:
  - the unchanged TEST-M3-08 harness passes 3/3 (D11 +0.18 to +0.27 %);
  - braking is within 0.3 %, steady state ≈ 0, gravity and gyro unchanged;
  - `/imu` runs at 100.0000 Hz with stamps on the 10 ms grid;
  - the output noise meets DEC-032 only when the raw noise is set to √10 × the output value.

**Decision:**
1. **Noise is specified at the published ROS `/imu` output.**
   - The DEC-032 values stay the published-output requirements: σ_ω 0.001 rad/s and σ_a 0.01 m/s² per axis, Gaussian, mean 0, zero bias.
   - The DEC-036 S1–S4 checks and the D9–D11 tolerances apply to `/imu`, unchanged.
2. **Internal sampling.**
   - The Gazebo IMU sensor runs at **1000 Hz**, one sample per 1 ms physics step (the stock step, sensor_test.sdf §7.1).
   - It publishes on an internal Gazebo topic, **`/imu_raw`**, which is not bridged to ROS.
3. **Output: a non-overlapping block mean.**
   - Each complete group of **10 consecutive raw samples** produces one output.
   - Linear acceleration and angular velocity are each averaged per axis (arithmetic mean).
   - The output rate is 100 Hz on ROS `/imu` (`sensor_msgs/msg/Imu`, `frame_id` `imu_link`), unchanged for consumers.
4. **Raw noise is a derived configuration value, not a published tolerance:** σ_raw = √10 · σ_output, i.e. **0.0316227766 m/s²** and **0.00316227766 rad/s** (label: Calculated).
   - Basis: the mean of 10 independent samples has σ/√10.
   - The raw samples were measured to be independent (|autocorrelation| ≤ 0.024 at 1–10 ms).
   - The prototype output measured s/σ 0.96–1.04 on all six channels.
   - The value is re-verified at the output by TEST-M3-07; if the output fails S2, this derivation is revised, not the output requirement.
5. **Location and technology: a C++ Gazebo system plugin** (`gz::sim::System`), attached to the robot model in `amr.sensors.xacro` and emitted only with `use_sensors:=true`.
   - It subscribes to `/imu_raw` in the server process and publishes Gazebo `/imu`. The existing `sensor_bridge` maps that to ROS `/imu` unchanged.
   - The averaging logic is a Gazebo-independent C++ class with unit tests.
   - Comparison in `docs/design/sensors.md` §8.2; the package placement is §8.6, item 1.
   - The Python prototype is not retained.
6. **Timestamp semantics.**
   - The output `header.stamp` is the stamp of the **newest** raw sample in its block, t. It lies on the 10 ms grid.
   - The acceleration and angular velocity are the **mean over the interval (t − 10 ms, t]**. The stamp marks the end of that interval, not an instant.
   - Effective delay relative to the stamp:
     - 4.5 ms is the FIR group delay for acceleration spread evenly over the block;
     - 5.0 ms is the centre of the interval;
     - **8–9 ms (measured, repeatable)** for the controller's velocity steps, which fall 1–2 ms after the block start.
   - Integrating Σ a·10 ms reproduces the velocity change exactly (prototype fixture).
   - M4 must use these semantics. This decision does not validate any fusion.
7. **Startup and incomplete blocks.**
   - Blocks are aligned to the 10 ms grid: stamps t − 9 … t ms, with t a multiple of 10 ms.
   - An output is published **only** when all 10 stamps are present exactly once.
   - The first output after start (or after a reset) waits for the first complete aligned block. The prototype's 9-sample first block would not be published.
   - Error handling:
     - **Missing sample:** that block is not published (consumers see a 20 ms stamp gap). A counter is incremented and a rate-limited warning is logged.
     - **Duplicate stamp:** the repeated sample is ignored and counted.
     - **Non-monotonic stamp (time moved backwards, e.g. a world reset):** the buffer is cleared, the counter is incremented, and the plugin restarts with the full-block rule.
     - **Shutdown:** a partial block is discarded, never published.
8. **Orientation**, its covariance fields and the frame are copied from the newest sample. The orientation is therefore at instant t, while the rates are interval means.
   - The orientation stays simulator-derived and is not ground truth (DEC-032). Averaging quaternions over 10 ms is not done: at 0.5 rad/s the rotation is 0.005 rad.
   - **Covariance propagation** (implementation clarification found during the plugin implementation; **confirmed by me 2026-11-03**). The output rates are the mean of N = 10 raw samples. If those samples are **independent**, the covariance of the mean is the per-sample covariance ÷ N.
     - The plugin divides `angular_velocity_covariance` and `linear_acceleration_covariance` of the newest sample by 10. This publishes σ_out², the DEC-032 values 1e-6 (rad/s)² and 1e-4 (m/s²)², as `/imu` did before DEC-038.
     - `orientation_covariance` is copied unchanged: the orientation is not averaged.
     - Copying the rate covariances unchanged would publish σ_raw² = 10 σ_out², overstating the actual output noise 10×. This was observed in the first development launch.
     - **Independence assumption, stated explicitly:** Gazebo draws the raw noise independently per sample. The prototype measured \|r\| ≤ 0.024 at lags 1–10 ms. Formal checks: the output σ (TEST-M3-07 S2) and the raw autocorrelation (TEST-M3-14 (g), INFO).
     - If formal testing shows material correlation between raw samples, the variance calculation (σ_raw, this ÷ N) is investigated. The DEC-032 published requirements are not weakened.
9. **Configuration constraint (dependency on DEC-026).**
   - The block period (10 × 1 ms = 10 ms) must equal the output period, and must be an integer multiple of the controller period (1 / `controller_manager.update_rate`) and of the physics step.
   - At the DEC-026 100 Hz rate, each block holds exactly one command step. Allowed controller rates are 100, 200, 500 and 1000 Hz. A rate such as 50 Hz would make blocks alternate between 0 and 2 steps, giving per-sample outputs of ≈ 0 and ≈ 2× the true value.
   - The plugin checks its own block, raw-rate and step consistency at load and refuses invalid values with an error. A static test checks the controller rate.
10. **Required verification before any PASS:** the retest plan in `docs/testing/test_plan.md` §7.3 (re-tests of TEST-M3-01 to -09, new TEST-M3-13 and -14).
    - The original TEST-M3-08 FAIL and all TS-027 and prototype evidence are kept. No test is marked PASS on prototype evidence.

**Relation to DEC-032:**
- DEC-038 **amends only** two points of DEC-032: "Update rate 100 Hz" becomes "internal sampling 1000 Hz, published output 100 Hz", and the noise values are defined at the `/imu` output.
- The values, placement, conventions, topic and frame are unchanged.
- DEC-032 gets a status note "amended by DEC-038"; its text is not rewritten.

**Alternatives considered (TS-027, `TS-027_C4_validation.log`):**
- C1, IMU at 1 kHz published directly: the mean is correct, but the per-sample signal is a 5–7 m/s² spike train.
- C2, controller at 1 kHz: changes DEC-026; braking reads −17 %; still impulsive.
- C3, continuous actuation model: changes the M2 control architecture; not prototyped.
- Other filters on the same data:
  - 20-sample sliding mean: unbiased, but outputs are 50 % correlated, with about 5 ms more delay.
  - 20 Hz first-order IIR: the residual 100 Hz ripple aliases into a −47 % to +65 % phase-dependent bias.
- Raw noise left at the DEC-032 values: the output is 0.31 σ, so S2 fails.
- Production technology: a ROS 2 C++ node or a standalone gz-transport C++ process (§8.2).

**Rationale and trade-offs:**
- The block mean equals the true mean acceleration of each 10 ms interval, at every command phase. It has nulls at 100 Hz and its harmonics, and its outputs are uncorrelated.
- The published interface, rate, frame and noise stay those of DEC-032. The M2 control architecture is untouched.
- Costs: 10× IMU sensor updates; one new compiled component; an interval-mean semantic and 5–9 ms effective delay that M4 must respect; and the DEC-026 coupling in item 9.

**Consequences:**
- `amr.sensors.xacro` changes when use_sensors is true: IMU rate, topic, raw noise, and a plugin element. Default-off output stays byte-identical to M1.
- New compiled plugin; TEST-M3-02's checker is updated for the new expected configuration before its re-test.
- REQ-M3-15 (proposed) and the retest plan apply.
- TEST-M3-08 can be re-tested once this is implemented.

**Follow-up / open questions:**
- *Done 2026-11-03:*
  - a dedicated implementation step in M3 (it blocks the M3 sensor verification);
  - DEC-032 status note added;
  - package `amr_gazebo_plugins` implemented (`sensors.md` §8.6);
  - a first, pre-fix execution of the retest plan (`test_plan.md` §7.3), **superseded** by TS-028 and TS-029. The formal re-run on the fixed build applies the DEC-039 rule (results in `TEST_RESULTS.md`).
- The M3 sensor verification stays open until all required verification passes.
- The rate-covariance propagation in item 8 was confirmed (2026-11-03).
- M4 must use the interval-mean semantics (item 6). No fusion is validated by this decision.

## DEC-039 — Upstream Gazebo Shutdown Deadlock (TS-029): Invalid-Run Rule for Sensor Launches
**Date:** 2026-11-04   **Status:** **Accepted** (decided 2026-11-04). First recorded exception under my "judgment over rules" principle: a rule is set aside only openly, with evidence and a decision record, never silently.

**Context:**
- Every M3 launch procedure requires 0 `[ERROR]` lines in the launch log and 0 leftover processes after SIGINT (test_plan §7.1).
- TS-029: `gz sim` intermittently fails to exit after SIGINT, so `ros2 launch` escalates to SIGTERM and sometimes SIGKILL and logs `[ERROR]` lines. This happens **after** every measurement is complete. It failed TEST-M3-04 R1 and TEST-M3-14 in the superseded pre-fix batch, although all their measurement checks passed.
- Diagnosis (`docs/troubleshooting.md` TS-029; stack trace `TS-029_V2_run15_gdb.txt`): an **upstream deadlock in Gazebo**. gz-common's signal handler stops the server *on the interrupted main thread*, here interrupted inside gz-transport `Publish()`. `Sensors::Stop()` then joins the render thread, which is destroying the `gpu_lidar` sensor and is blocked on a gz-transport mutex.
- It reproduced without the DEC-038 plugin, and also before DEC-038 in the same mechanism class (upstream ros_gz #1011). It is not caused by project code and cannot be fixed in it without patching Gazebo.

**Decision:**
1. **Invalid-run rule.** In a sensor launch (`sensors:=true`), an attempt is **INVALID** (recorded, not counted, repeated) when **both** hold:
   - its measurement checks passed;
   - its launch log shows **exactly the TS-029 signature and nothing else**, as judged by `docs/evidence/M3/TEST-M3_launch_shutdown_classify.py` (exit 3):
     - the user SIGINT was logged;
     - the only `[ERROR]` lines are those of the single `gz sim` process: the SIGINT→SIGTERM escalation (required), optionally SIGTERM→SIGKILL, and optionally its death with exit code −9 or −15;
     - every other started process finished cleanly;
     - 0 leftover processes (checked by the procedure).
2. **Unchanged:**
   - every measurement criterion (DEC-036, DEC-038);
   - the 0-`[ERROR]`/0-leftover rule for anything else: any other `[ERROR]` line, any other unclean process, or a leftover process still **fails** the attempt;
   - the default (sensors-off) launch of TEST-M3-04 Part 2 keeps the strict rule, because the mechanism needs a rendering sensor.
3. **Bounded:** invalid attempts count against the existing attempt limits: 3 attempts for TEST-M3-04 Part 1 and Task C; runs + 3 for Task D and TEST-M3-14. Too few valid runs is a FAIL.
4. **Recorded:** every procedure prints each occurrence and a total (`# TS-029 attempts declared invalid under DEC-039: N`). `TEST_RESULTS.md` reports the count per test. A measurement failure in a TS-029 attempt is still a FAIL.
5. Implemented in `TEST-M3-04_procedure.sh` (Part 1), `TEST-M3-C_procedure.sh`, `TEST-M3-D_procedure.sh` and `TEST-M3-14_procedure.sh`. Each change is stated in the script header, and was made before any run under this rule. In TEST-M3-14 the plugin shutdown-line check (b) of an invalid attempt is not counted, because a deadlocked server may never run the plugin destructor. The valid repeat checks it.

**Alternatives considered:**
- **Keep the rule unchanged:** an upstream defect would block the plugin step and the M3 sensor verification indefinitely, and repeating until a pass without a rule would be cherry-picking.
- **Shutdown workaround in the procedures** (remove the robot model through a gz service before SIGINT so the LiDAR is destroyed during normal operation): it changes the tested shutdown path, needs its own validation, and does not help normal use.
- **Patch Gazebo or host the server differently** (ros_gz PR #1012 approach): out of project scope; not in the installed release (gz-sim 8.15.0, ros_gz_sim 1.0.24).

**Rationale and trade-offs:**
- The defect occurs after the measurements and is fully characterized. The signature check is strict, so other shutdown problems still fail.
- Limitation: the log signature cannot distinguish TS-029 from a different future cause that produces identical gz-only escalation lines. Mitigations: the attempt limit, the per-test count, and the expected rate from the TS-029 rig. A count clearly above that rate is investigated, not accepted.

**Consequences:**
- The DEC-038 formal re-run (test_plan §7.3) can proceed.
- TS-029 stays **open (upstream)** and is monitored. When the installed Gazebo contains an upstream fix, this rule is re-evaluated and retired.
- Task E's TEST-M3-11 uses the same rule for its sensor launches.

**Follow-up / open questions:**
- Re-check upstream (ros_gz #1011, gz-sim) at each environment update (`docs/environment.md`); since 2026-11-04 also gz-sim#4173.

**Amendment, 2026-11-04 (after M3 closeout):**
- **Finding:** ros_gz PR #1012 cannot retire this rule. It changes only the `GzServer` ROS node, and `sim.launch.py` runs the `gz sim` CLI (TS-029 correction). Retirement now needs a gz-sim/gz-common fix, or a project-side stop path that has been shown to work.
- **Decision 1: keep this rule unchanged** as the handling of TS-029. It costs one repeated attempt in about 1 of 15–20 sensor launches, and the DEC-040 runner will make the repeat automatic.
- **Decision 2: the `/server_control` stop (TS-029, untested candidate) is deferred, not added to DEC-040.** Proving it needs a few hundred rig runs because the hang is rare. That is not justified while the cost of the hang is one repeat. **Trigger to take it up:** invalid TS-029 attempts exceed 10 % of sensor launches over a milestone, or longer runs (M5 onward) raise the rate. Any adoption changes the test procedures and needs a recorded decision.
- **Decision 3: report upstream to gz-sim.** No existing issue was found (duplicate search on 2026-11-04 in gz-sim, gz-common and gz-sensors). The report text is [docs/evidence/M3/TS-029_upstream_issue.md](docs/evidence/M3/TS-029_upstream_issue.md).
  - **Done 2026-11-04:** I posted the final text as [gazebosim/gz-sim#4173](https://github.com/gazebosim/gz-sim/issues/4173) (text: `docs/evidence/M3/TS-029_upstream_issue.md`). A Gazebo-only reproduction attempt (0 of 300) was run first and is stated in the report. The follow-up stays deferred; the retirement criteria are above.

## DEC-040 — Test Automation Between M3 and M4
**Date:** 2026-11-04   **Status:** **Accepted** for timing and intent (decided 2026-11-04). The detailed scope is **Proposed** and is reviewed when the work starts.
**Context:** every formal procedure is started and tracked by hand. My project self-review of 2026-11-04 found two costs: the manual effort grows with every milestone, and cheap checks can be skipped or mis-read (e.g. the TEST-M3-04 R1 exit-code defect, found only by reading the log).
**Decision:**
1. Test automation is a bounded step **after M3 closeout and before M4 starts**. It is not part of M3, so M3 scope is unchanged.
2. Intended scope:
   - (a) a local suite runner that executes a milestone's procedures serially, with the leftover-process check, unique run tags, and an exit-code vs `# overall:` cross-check, and writes a summary table;
   - (b) GitHub Actions CI for the GPU-free checks: build, unit tests, M1 byte identity, consistency checkers. It runs on pushes that change code, configuration or tests (item 3).
3. **CI minutes budget (limited free monthly allowance).**
   - CI starts only when code, configuration or test files change: path filters on `amr_ws/**` and `docs/evidence/**/*.py|*.sh`. Pushes that touch only Markdown (e.g. `DECISIONS.md`, documentation) do not start CI.
   - The record-consistency checkers, which do read the Markdown records, run on manual trigger (`workflow_dispatch`) and at milestone closeout. They do not run on every documentation push.
   - Superseded runs are cancelled (`concurrency`), and dependencies are cached.
4. Gazebo sensor tests stay local. Headless rendering of `gpu_lidar` needs the GPU, which hosted runners lack.
5. Automation never records a PASS by itself. A human review of each log stays required.
**Alternatives considered:** keep manual execution (cost grows with M4–M10); automate during M3 (widens the current milestone, against the milestone discipline); CI only (does not cover the Gazebo tests, which carry most of the effort).
**Rationale and trade-offs:** CI catches "works only on this machine" problems and accidental breakage of `main` on every push, at no manual cost. The runner makes the full local suite repeatable. Cost: one setup step and the CI configuration to maintain.
**Consequences:** ROADMAP gains the step between M3 and M4. The M3 consistency checker (TEST-M3-12) is written so that CI can run it.
**Follow-up / open questions:** detailed scope and acceptance criteria when the step starts. The CI runtime image (ROS 2 Jazzy on Ubuntu 24.04) is to be verified then.
**Detailed scope accepted 2026-11-04 (start of the step):** plan `docs/milestones/M3-M4_test_automation.md`, REQ-TA-01 to -05, TEST-TA-01 to -05. Choices:
- re-run every formal test whose harness uses the changed teardown helper (M2 motion, M3 Task D, TEST-M3-11, TEST-M3-14);
- CI in the official `ros:jazzy-ros-base` container with rosdep;
- the runner at `tools/run_suite.py`.
**Scope additions (2026-11-04, after M3 closeout; now part of the accepted scope):**
- (c) TS-030: capture the full spin-thread traceback, then the harness teardown fix (stop flag, join the spin thread, then shut down) in the shared harness pattern, with re-runs of the affected tests.
- (d) Stop-measurement timing instrumentation (from TEST-M3-11, where the stop distance was 3–6 mm longer than M2 R1, within criteria and not attributed). The M2 stop evaluation takes the ground-truth sample nearest an *estimated* zero-command time; at about 59 Hz that sample can be 8.5 ms off, i.e. ±4 mm at 0.5 m/s. Add INFO outputs: the latency from the zero command to the first decrease of `/diff_drive_controller/cmd_vel_out`, and the stop distance with the ground truth interpolated at that instant. The DEC-027 pass criteria are unchanged; changing them would need a separate decision.
**Amendment, 2026-11-04 (closeout; requirement: never pay GitHub for Actions):**
- The hard limit is the account's budget, not the workflow: GitHub Settings → Billing and licensing → Budgets and alerts, an Actions budget of $0 with "stop usage when the budget limit is reached", plus alerts. When the free monthly minutes are used up, Actions then stops until the next month instead of billing. Set on 2026-11-04.
- Workflow caps: job `timeout-minutes` lowered from 30 to 10, so a hung run uses at most 10 minutes (a normal run takes about 3 minutes, Measured at TEST-TA-05). Path filters, manual-only record checkers and `concurrency` cancel-in-progress stay in place.
- Dependency cache (item 3): **not added; confirmed on 2026-11-04** (item 3's "dependencies are cached" is withdrawn). Revisit only if monthly use passes about half the free minutes. Measured: the dependency install is about 115 s of about 180 s per run. Estimated use: a few dozen code pushes a month at 3 minutes each, under 10 % of 2,000 minutes.

## DEC-041 — One Owner for Test Status (Links Instead of Restated Results)
**Date:** 2026-11-04   **Status:** **Accepted** (decided 2026-11-04, at the DEC-040 closeout)
**Context:** a test result was restated in many places: `TEST_RESULTS.md`, `test_plan.md`, `requirements.md`, the milestone record, `ROADMAP.md`, my planning notes and the evidence index. Recording one result meant editing all of them, and such copies had drifted before (a stale "rig script not in the repository" line; stale re-test labels). Each fact should have one owner; test status did not follow that.
**Decision (applies from M4; existing M0–M3 and DEC-040 records stay as they are):**
1. `TEST_RESULTS.md` is the only place that holds a test's result details: numbers, run counts, diagnoses and evidence links.
2. `test_plan.md` (status column) and `requirements.md` (traceability) give only the state word from `test_plan.md` §1, the date and a link to the `TEST_RESULTS.md` entry. No numbers.
3. `ROADMAP.md` and the milestone record say what was done and link to `TEST_RESULTS.md`; they do not list per-test numbers.
4. Unchanged: the evidence index describes what each file demonstrates (that is its own fact), and failure history is preserved.
**Alternatives considered:** the same rule plus a script that generates the summary tables from `TEST_RESULTS.md` (less hand editing, but another tool to build, test and keep working); keep restating and rely on the record checkers to catch drift (keeps the editing cost and the drift risk).
**Rationale and trade-offs:** fewer copies means fewer places that can drift and less editing per result. The cost: a reader of a plan follows a link to see the numbers.
**Consequences:** the M4 record checker (successor of TEST-M2-11 / TEST-M3-12) checks state words and links, not restated numbers.
**Follow-up:** apply it from the first M4 record. If a summary generator becomes worthwhile later, it is a new decision.

## DEC-042 — M4 Odometry Covariance (OPEN-19)
**Date:** 2026-11-13   **Status:** **Accepted** (decided 2026-11-13, the M4 plan §4 recommendation)
**Context:** the installed `diff_drive_controller` 4.42.1 defaults `pose_covariance_diagonal` and `twist_covariance_diagonal` to zeros, and `controllers.yaml` sets neither. `/diff_drive_controller/odom` therefore claims a perfect estimate. M6 fuses odometry with the IMU and needs a usable uncertainty. The simulated odometry error is about 0.01 % (TEST-M2-05/-06 R1), much smaller than on a real robot.
**Decision:** option (c): constant covariance diagonals derived from an **Assumed** realistic odometry error model, about 1 % of the distance travelled and 2 % of the rotation. M4 Task B calculates the diagonal values from this model, records the derivation in the M4 plan §3, and fixes the numbers before they are written to `controllers.yaml`. The measured simulated error is recorded beside them.
**Alternatives considered:** (a) leave the zero defaults and decide in M6; (b) diagonals from the measured simulated error (a filter would over-trust odometry).
**Rationale and trade-offs:** the values describe a plausible real robot rather than the ideal simulation, so the M6 fusion weights stay meaningful when the simulation becomes more realistic or the robot becomes physical. Cost: the values are assumptions, not measurements.
**Consequences:** one product configuration change in M4 (`controllers.yaml`); TEST-M4-01 and -02 check it.
**Values (2026-11-13):** CALC-M4-04 (M4 plan §3.3a), accepted as proposed: pose [0.01, 0.01, 1e3, 1e3, 1e3, 0.0158], twist [2.5e-5, 2.5e-5, 1e3, 1e3, 1e3, 4.0e-4]; 10 m and one full turn as the pose reference excursion; 1e3 = not measured.
**Follow-up:** revisit in M6 (fusion tuning) and M13 (measured on hardware).

## DEC-043 — M4 Error Realism (OPEN-20)
**Date:** 2026-11-13   **Status:** **Accepted** (decided 2026-11-13)
**Context:** the simulation has real rigid-body dynamics but almost no odometry error sources: ideal encoders (DEC-033), exact calibration, uniform friction. M4 accuracy tests on it would pass with a large margin and prove little on their own.
**Decision:** option (b): the M4 accuracy tests run on the ideal simulation, and a sensitivity test (TEST-M4-09) reruns them with injected calibration errors through the controller's `wheel_separation_multiplier` and `*_wheel_radius_multiplier` parameters, in **test-only** override files under `docs/evidence/M4/`. The injected errors must make their target tests FAIL by the amount CALC-M4-02 predicts. The product configuration is not changed.
**Alternatives considered:** (a) ideal simulation only; (c) an encoder-emulation node (quantization, noise, slip), the DEC-033 alternative.
**Rationale and trade-offs:** proves that the tests detect real errors, with no new node or parameters. It does not make the simulation itself more realistic.
**Consequences:** I stated on 2026-11-13 that the simulation should move closer to realistic. Candidate realism additions (encoder emulation, a model-versus-controller calibration mismatch, floor-friction variation, IMU bias, LiDAR effects) were discussed and are **not** part of M4; they are recorded as a follow-up.
**Follow-up:** decide the realism additions and their milestones  (candidates M6 for IMU bias, M8 for LiDAR effects, a dedicated step for encoder and calibration realism).

## DEC-044 — M4 Test Trajectories and Error Bounds (OPEN-21)
**Date:** 2026-11-13   **Status:** **Accepted** (decided 2026-11-13)
**Context:** M2 verified the odometry signs only (REQ-M2-11). M4 needs quantitative criteria that are loose against run-to-run variation and tight enough to catch calibration errors (CALC-M4-02).
**Decision:** the M4 plan §8 trajectories and bounds, odometry minus ground truth at rest points, 3 runs per test, every run must pass: straight 2 m, distance error ≤ 0.5 % and heading ≤ 0.5°; in-place 360°, yaw ≤ 1.0° per turn and translation ≤ 20 mm; 1 m square CW and CCW and a 1 m-radius circle, end-point position ≤ 20 mm and yaw ≤ 1.0°; twist mean within ± 2 %; recomputation within 1 mm and 0.01°; sensitivity: each injected error fails its target test with the CALC-M4-02 prediction within ± 25 %.
**Alternatives considered:** tighter bounds near the measured 0.01 % (fragile, and meaningless for a real robot); real-robot bounds of a few percent (would not catch the injected errors).
**Rationale and trade-offs:** about 30–50× margin over the measured simulated error; the injected errors exceed the bounds 2–7×. A physical robot would need wider bounds (M13).
**Consequences:** procedures in `test_plan.md` §9; requirements REQ-M4-01 to -11.
**Follow-up:** none in M4.

## DEC-045 — M4 Test Launch Configuration (OPEN-22)
**Date:** 2026-11-13   **Status:** **Accepted** (decided 2026-11-13)
**Context:** the M4 tests can run on the default M2 launch (empty world, sensors off) or with sensors on.
**Decision:** option (a): the default M2 launch, sensors off.
**Alternatives considered:** (b) sensors on.
**Rationale and trade-offs:** faster; avoids the `gpu_lidar` shutdown hang (TS-029, DEC-039). TEST-M3-11 already showed that sensors do not change the motion.
**Consequences:** none on the model or configuration.
**Follow-up:** M6 runs odometry with the IMU on.

## DEC-046 — M5 Mapping World: Purpose-Built Test Arena
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** M5 needs a world to map. The world decides how the map's accuracy can be proven. The M3 world `sensor_test.sdf` is open (no enclosing walls) and has four targets; the factory world belongs to M9 (ros_architecture.md: "after M7").
**Decision:** option (a): a purpose-built enclosed test arena, `amr_bringup/worlds/mapping_arena.sdf`, about 10 × 8 m with asymmetric features at known coordinates and one feature below the scan plane. The map is checked against the world file. Layout: M5 plan §3.1 (CALC-M5-01, Proposed until the plan is finalized).
**Alternatives considered:** (b) an early, simple factory layout: reusable in M9, but pulls M9 scope forward; (c) map `sensor_test.sdf`: not enclosed, too few features, weak test.
**Rationale and trade-offs:** known ground truth makes the map measurable, as M3 and M4 measured against ground truth; the factory world stays an M9 deliverable. Cost: one more world file that M9 does not reuse directly.
**Consequences:** new world file only; the robot, sensors and controllers are unchanged.
**Follow-up:** layout, route and bounds are finalized with the M5 plan (OPEN-23 to -27).

## DEC-047 — M5 Map and Pose Accuracy Bounds (OPEN-23)
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** the M5 tests need numeric limits for map and pose accuracy (M5 plan §3.3, CALC-M5-03).
**Decision:** wall accuracy P95 ≤ 0.10 m; ghost cells ≤ 0.5 % beyond 0.25 m; completeness ≥ 90 % within 0.10 m; interior 10.0 × 8.0 m ± 0.10 m and walls within 1.0°; pose (`map → base_footprint` vs ground truth at rest points) ≤ 0.05 m and ≤ 1.0°; the low box L1 absent.
**Alternatives considered:** tighter or looser bounds not tied to the map resolution.
**Rationale and trade-offs:** tied to the 0.05 m cell (0.035 m quantization) and the sensor geometry (1° at 6 m = 0.105 m). Expected to pass with margin in simulation; TEST-M5-07 shows they can fail.
**Consequences:** criteria of TEST-M5-03, -04, -06 Accepted.
**Follow-up:** a real robot (M13) would need wider bounds.

## DEC-048 — M5 SLAM Toolbox Mode and Parameters (OPEN-24)
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** SLAM Toolbox 2.8.5 offers online async and online sync mapping; its default range limits do not match the sensor.
**Decision:** option (a): online async; the installed `mapper_params_online_async.yaml` defaults, except `max_laser_range` 12.0 m and `min_laser_range` 0.12 m (the DEC-031 sensor limits).
**Alternatives considered:** (b) online sync (processes every qualifying scan; more repeatable, can lag); (c) tuned thresholds.
**Rationale and trade-offs:** M6/M7 run live, so the live mode is tested. At one node per 0.5 m the load is low; TEST-M5-02 logs dropped scans, and (b) is the fallback if they matter.
**Consequences:** new `amr_bringup/config/slam_toolbox.yaml` (Task A).
**Follow-up:** revisit only if TEST-M5-02 shows dropped scans that affect the map.
**Note (2026-11-15, TS-038):** SLAM Toolbox 2.8.5 has no `min_laser_range` parameter; it takes the minimum range from the scan's `range_min` (0.12 m, DEC-031). The `min_laser_range: 0.12` line is therefore inert and is kept only with a comment saying so; the effective minimum range is unchanged.

## DEC-049 — M5 Test Route Driving (OPEN-25)
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** the mapping tests need the robot driven along the same route in every run, including runs with injected odometry errors.
**Decision:** option (a): a harness waypoint follower steered by Gazebo ground truth, using proportional heading and distance control with the route speed and turn-rate limits (no I or D term).
**Alternatives considered:** (b) steered by odometry (an injected error would move the path, with collision risk); (c) teleop (not repeatable; used only for demonstration).
**Rationale and trade-offs:** the system under test is SLAM, not the driver; an identical path makes runs comparable. P control suffices: the simulation has no steady disturbance for an I term, and a D term would amplify pose noise. Ground truth steers the robot only; SLAM never sees it.
**Consequences:** test tooling only (`docs/evidence/M5/TEST-M5_map_run.py`).
**Follow-up:** autonomous driving on the map is M7 (Nav2).

## DEC-050 — M5 Launch Structure (OPEN-26)
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** SLAM must run with the simulation without changing the M1–M4 launch behaviour.
**Decision:** option (a): a new `amr_bringup/launch/slam.launch.py` that starts only SLAM Toolbox (sim time, params file argument), run beside `sim.launch.py sensors:=true world:=mapping_arena.sdf`. `sim.launch.py` is unchanged.
**Alternatives considered:** (b) a `slam:=true` argument on `sim.launch.py`; (c) one all-in-one mapping launch.
**Rationale and trade-offs:** the default launch stays byte-for-byte unchanged (TEST-M5-01), and M6 can replace SLAM with localization without touching the simulation launch. Cost: two launch commands for a mapping session.
**Consequences:** new launch file only.
**Follow-up:** a convenience launch can be added later if useful.

## DEC-051 — M5 Map Artefacts (OPEN-27)
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** M6 can localize with AMCL on an image map or with SLAM Toolbox localization mode on a serialized pose graph.
**Decision:** option (b): save and commit both the `.pgm`/`.yaml` map (Nav2 `map_saver_cli`) and the SLAM Toolbox serialized pose graph (`.posegraph` + `.data`), if the pose graph stays under about 5 MB; otherwise (a) and the reason recorded.
**Alternatives considered:** (a) `.pgm`/`.yaml` only.
**Rationale and trade-offs:** keeps both M6 options open at a small repository cost.
**Consequences:** `amr_bringup/maps/` (Task C).
**Follow-up:** M6 chooses the localization method.

## DEC-052 — M5 Loop Closure Not Separately Verified
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** the M5 plan described loop closure and TEST-M5-09 required "the loop closes". A review note questioned whether a 10 × 8 m arena with a 12 m LiDAR exercises loop closure at all. A scratch spike (M5 plan §12) drove two laps with a 2 % track error injected, with SLAM `max_laser_range` 12 m and 3 m: in both runs `map → odom` corrected the injected heading error at each turn (scan matching), with no correction on return to the start; at 3 m the pose error grew to 0.064 m and part of the arena was not mapped.
**Decision:** keep the arena (DEC-046) and the DEC-048 configuration; add no short-range test case. TEST-M5-09 checks that the robot returns to the start with no visible misalignment; loop-closure edges are noted if seen, not required. The plan states the limitation; loop-closure verification is deferred to a larger or corridor environment.
**Alternatives considered:** (a) a TEST-M5-06 case with `max_laser_range` 3.0 m (spike: still scan matching, worse map, pose bound exceeded); (b) a larger arena or corridors now (M9-like scope, outside DEC-046).
**Rationale and trade-offs:** a test should not claim a mechanism it cannot observe. Cost: M5 does not show loop closure working.
**Consequences:** wording of TEST-M5-09 (plan §8, test_plan §10) and a plan limitation; no configuration change.
**Follow-up:** loop-closure verification in a larger or corridor environment (deferred).

## DEC-053 — TEST-M5-01 Criterion Restated: Dependency Declaration Allowed
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** the accepted TEST-M5-01 criterion said M5 adds "only new files". Task A also added one line to an existing file, `<exec_depend>slam_toolbox</exec_depend>` in `amr_bringup/package.xml`, and changed one comment line in `amr_bringup/CMakeLists.txt`. The M5 plan §12 first recorded a reading ("no behavioural change to existing files") without a recorded decision, against the rule that a test criterion is never relaxed silently (precedent DEC-039). A review note raised it before the result was recorded.
**Decision:** the criterion is restated as exactly what the procedure checks: build clean; the M1 default expansion and the M2 and M3/M5 launch-model expansions byte-identical to the M4 closeout `517608f`; `sim.launch.py`, `controllers.yaml`, `amr.sensors.xacro`, `amr_properties.xacro` unchanged; changes to existing files limited to that one dependency line and comment lines. The run already made counts under this criterion.
**Alternatives considered:** (a) literal reading: record FAIL, then revert or amend and re-run; (b) remove the dependency line and the comment: `slam_toolbox` would become an undeclared runtime dependency (a fresh install or `rosdep` would miss it).
**Rationale and trade-offs:** the purpose of the criterion is that M5 does not change verified M1–M4 behaviour; the protected files and expansions are byte-identical, and the dependency line is required for a correct package. The restated rule is narrower and checkable, not looser in what it protects.
**Consequences:** TEST-M5-01 wording in the M5 plan §8 and `test_plan.md` §10; the plan §12 note corrected.
**Follow-up:** none; later milestones state allowed edits to existing files explicitly in their criteria.

## DEC-054 — M5 Pose Graph Committed Compressed (amends DEC-051)
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** DEC-051 keeps the SLAM Toolbox serialized pose graph (`.posegraph` + `.data`) with the reference map if it stays under about 5 MB, otherwise the map only. Measured in the Task B dry runs (M5 plan §12): 6.9 MB right after SLAM starts and 7.4 MB + 0.47 MB after the route. The fixed-size part dominates and compresses about 20:1 (gzip -9: 0.33 + 0.23 MB).
**Decision:** commit the reference pose graph gzip-compressed (`mapping_arena.posegraph.gz`, `mapping_arena.data.gz`) next to `amr_bringup/maps/mapping_arena.{pgm,yaml}`. The serialized files are produced by the procedure and compressed with `gzip -9 -n` (no name or time stamp, so the output is reproducible).
**Alternatives considered:** (a) map only, the DEC-051 fallback: SLAM Toolbox localization in M6 would need a new mapping run; (c) commit the raw 7.9 MB: permanent binary weight in the history.
**Rationale and trade-offs:** about 0.56 MB keeps both M6 options (AMCL on the image map, SLAM Toolbox localization on the pose graph) at the cost of one decompression step before SLAM Toolbox loads the files.
**Consequences:** TEST-M5-05 checks that the compressed files decompress to the serialized pose graph of the reference run (byte-identical). The maps folder is committed in the source tree without an install rule (an install line would change `CMakeLists.txt`, outside the TEST-M5-01 criterion, DEC-053); M6 adds the install rule and the decompression when it loads the map.
**Follow-up:** M6 localization setup.

## DEC-055 — M5 Reference Map Origin Corrected by Half a Cell (TS-041)
**Date:** 2026-11-15   **Status:** **Accepted** (decided 2026-11-15)
**Context:** TS-041: SLAM Toolbox 2.8.5 writes Karto's grid offset, which is the centre of cell 0 (`WorldToGrid` rounds), into `OccupancyGrid.info.origin`, which ROS defines as the corner of cell 0. Every ROS consumer draws the map 0.025 m too far in +x and +y. Shown in the source (`karto_sdk/Karto.h`, `slam_toolbox/visualization_utils.hpp`) and in the data: all four walls of all three TEST-M5-03 maps are offset in +x/+y; a least-squares shift gives −0.020 to −0.030 m. The reference map (`dae225d`) was committed with the shift.
**Decision:** the reference map's origin is moved by −0.025 m in x and y, yaw unchanged: `origin: [-2.046, -4.055, 0]` → `[-2.071, -4.080, 0]` in `amr_bringup/maps/mapping_arena.yaml`. The image and the pose graph are unchanged. TEST-M5-05 criterion: the `.yaml` equals the attempt 1 file except the image name and this origin correction (checked exactly). TEST-M5-05 and TEST-M5-07 re-run on the corrected map.
**Alternatives considered:** keep the map as saved and correct it in M6 when loading (the shift would be easy to forget and would bias localization by about 0.035 m diagonally); correct in the map checker for every SLAM map (changes a measurement already used for the recorded TEST-M5-03 results).
**Rationale and trade-offs:** M6 localizes on this file, so it should be correct for every ROS consumer. The correction is derived from the source, not fitted to the data, and the data agree with it. The reference map is no longer byte-identical to the `map_saver_cli` output in its origin line; the procedure states and checks the exact difference.
**Consequences:** with the correction, the checker's best-fit offset on the reference map is (0.000, 0.000) and wall P95 0.045 m (was 0.070 m). TEST-M5-03 and TEST-M5-04 results stand as measured: the checker still reads SLAM maps as saved, so TEST-M5-06 maps carry the shift as TEST-M5-03 did (consistent with the recorded runs). Any later map made with SLAM Toolbox needs the same correction until upstream changes.
**Follow-up:** check whether newer SLAM Toolbox releases change `toNavMap`; M6 uses the corrected file.

## DEC-056 — M6 Localization Method: AMCL (OPEN-28)
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18, approving the M6 plan §4 recommendation)
**Context:** DEC-051 kept two inputs for M6: the `.pgm`/`.yaml` image map (AMCL) and the serialized pose graph (SLAM Toolbox localization mode).
**Decision:** option (a): AMCL (`nav2_amcl`) on the M5 reference image map, served by `nav2_map_server`.
**Alternatives considered:** (b) SLAM Toolbox localization mode on the pose graph; (c) both, compared.
**Rationale and trade-offs:** M7 (Nav2) is built around AMCL; it uses only the image map, so it checks the M5 map from a second method; its particle cloud represents an uncertain or wrong start (CALC-M6-03). (b) stays possible later because the pose graph is committed (DEC-054). (c) doubles the test work for a comparison M7 does not need.
**Consequences:** new `config/amcl.yaml` and `launch/localization.launch.py` (Task A); `maps/` gains an install rule (DEC-054).
**Follow-up:** none.

## DEC-057 — M6 Odometry and IMU Fusion: Selectable EKF (OPEN-29)
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18)
**Context:** DEC-042 gave the odometry a covariance for fusion, and DEC-045 deferred "odometry with the IMU on" to M6.
**Decision:** option (a): a `robot_localization` `ekf_node` fuses the `/diff_drive_controller/odom` velocities and the `/imu` yaw rate and publishes `odom → base_footprint`. It is started by an `ekf:=true` option of `localization.launch.py`, together with `config/controllers_ekf.yaml`, whose only difference from `controllers.yaml` is `enable_odom_tf: false` (enforced by the M6 consistency checker). Default off. IMU bias is not added.
**Alternatives considered:** (b) EKF output topic only, no TF; (c) defer fusion to the realism step (DEC-043 follow-up).
**Rationale and trade-offs:** delivers the prepared fusion with a measurable benefit under the injected calibration error (CALC-M6-04); M1–M5 behaviour stays unchanged. Cost: a second controllers file kept in step automatically.
**Consequences:** new `config/ekf.yaml`, `config/controllers_ekf.yaml` (Task D); TEST-M6-07.
**Follow-up:** M7 decides whether fusion becomes the default; IMU bias stays with the DEC-043 realism follow-up.

## DEC-058 — M6 Initial Pose and Global Localization (OPEN-30)
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18)
**Context:** AMCL can start from a known pose, from an operator's rough pose (`/initialpose`), or with particles spread over the whole map.
**Decision:** option (a): the accuracy tests start from the known spawn pose (`set_initial_pose`, (0, 0, 0)); TEST-M6-04 tests recovery from a 0.5 m / 15° wrong start with the RViz covariance; global localization is a recorded demonstration, not an acceptance criterion.
**Alternatives considered:** (b) global localization as an acceptance test; (c) known start only.
**Rationale and trade-offs:** at most 2000 particles cover about 7 % of the arena's pose bins (CALC-M6-03), so a global-localization test would depend on luck or need AMCL retuning for a case a docked factory robot avoids.
**Consequences:** TEST-M6-04; the demonstration in TEST-M6-10.
**Follow-up:** revisit if M10 needs start-up without a known dock.

## DEC-059 — M6 Localization Accuracy and Convergence Bounds (OPEN-31)
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18)
**Context:** the M6 tests need numeric limits (M6 plan §3.1, §3.3, §3.4).
**Decision:** `map → base_footprint` vs ground truth: at rest ≤ 0.05 m and ≤ 1.0°; while moving (10 Hz, stamp-matched) P95 ≤ 0.10 m and ≤ 2.0°, maximum ≤ 0.25 m; wrong-start recovery to the rest bounds within 3 m of travel (amended to 4.0 m by DEC-063); fusion (separation × 1.02): fused end yaw ≤ 0.5° and fused end position ≤ 25 % of raw, raw within ± 25 % of CALC-M5-04. The bounds are fixed before any formal run; if the default AMCL parameters miss them in the Task A gate, any parameter change is a recorded decision.
**Alternatives considered:** bounds not tied to the M7 goal tolerance.
**Rationale and trade-offs:** one fifth of the installed Nav2 goal tolerance (0.25 m, 0.25 rad), and consistent with the M5 pose bound on the map localization depends on (CALC-M6-01).
**Consequences:** criteria of TEST-M6-03 to -07 Accepted.
**Follow-up:** a real robot (M13) would need wider bounds.

## DEC-060 — M6 Test World, Route and Launch Structure (OPEN-32)
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18)
**Context:** the M6 tests need a world with a map, a repeatable route, and a launch for localization.
**Decision:** option (a): the M5 arena (DEC-046) and route (CALC-M5-02), driven by the DEC-049 ground-truth follower in both directions; a test-only copy of the arena with three unmapped boxes in `docs/evidence/M6/`; a new `localization.launch.py` (map server, AMCL, lifecycle manager; optional EKF) beside the unchanged `sim.launch.py`.
**Alternatives considered:** (b) a new world and route; (c) include the installed `nav2_bringup` `localization_launch.py`.
**Rationale and trade-offs:** verified geometry and clearances, the reference map belongs to this world, comparable runs; an own three-node launch is clearer than the installed one, which rewrites parameters and adds options M6 does not use.
**Consequences:** Tasks A and B; the reverse route and the box positions are checked for clearance in Task B.
**Follow-up:** none.

## DEC-061 — M6 AMCL Motion and Sensor Model Parameters
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18, after the Task A gate diagnosis)
**Context:** DEC-059 requires any AMCL parameter change to be a recorded decision. In the Task A gate, the installed Nav2 1.3.14 defaults (`alpha1`–`alpha4` 0.2, `sigma_hit` 0.2 m) gave random rest-point errors of 44–140 mm and up to 3.0° on the M5 route (two runs), against the DEC-059 bound of 0.05 m and 1.0°, while odometry was exact. The Nav2 Jazzy source shows that the alphas are variance ratios (σ_rot = √(α₁·rot² + α₂·trans²), σ_trans = √(α₃·trans² + α₄·rot²)), so 0.2 means a σ of about 45 % of every motion step; and a `sigma_hit` of 0.2 m is 20× the LiDAR noise (0.01 m, DEC-031). Scratch diagnosis D1–D9 (M6 plan §12): each change alone left random errors (D2, D3); both together removed them (D4).
**Decision:** `alpha1` 0.0016, `alpha2` 0.0004, `alpha3` 0.0004, `alpha4` 0.0004, `sigma_hit` 0.05 m in `amr_bringup/config/amcl.yaml`; all other AMCL values stay the installed defaults. The alphas are the DEC-042 odometry error model (σ 2 % of rotation, 1 % of distance) at **twice its σ** (α = (2σ)²): α₁ = (0.04)², α₃ = (0.02)²; the cross terms α₂, α₄ (rotation noise per metre, distance noise per radian) are not in DEC-042 and are **Assumed** equal to α₃. `sigma_hit` is one map cell, about √(0.01² + 0.035²) (sensor noise and the half-diagonal quantization of a 0.05 m cell), rounded up.
**Alternatives considered:** (a) the DEC-042 model at 1σ (α₁ 4×10⁻⁴, α₂–α₄ 1×10⁻⁴): within bounds in both scratch cases, but with the TEST-M4-09 injected errors one rest point was at 49.9 mm against 50 mm (D7), because the injected 1 % error equals the modelled σ; (b) the installed defaults with DEC-059 widened to about 0.15 m and 3°: too loose for the M7 goal tolerance.
**Rationale and trade-offs:** derived from the approved odometry error model, not fitted to the runs; doubling σ puts the injected test errors at 0.5σ. Scratch evidence with the DEC-062 map copy: ideal odometry max 10.6 mm / 0.12° (D8), injected errors max 23.1 mm / 0.19° (D9), against 11.2 mm and 49.9 mm at 1σ. Cost: values tuned to a near-ideal simulation (with the DEC-042 assumptions); a physical robot (M13) would need measured values. Single scratch runs per case; the formal tests (3 runs each) are the verification.
**Consequences:** `amcl.yaml` deviates from the installed file in these five lines (marked M6, DEC-061); TEST-M6-02 checks the values; TEST-M6-03 to -07 verify them.
**Follow-up:** revisit with the DEC-043 realism additions and in M13.

## DEC-062 — M6 AMCL Gets an AMCL-Convention Copy of the Map (TS-045)
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18)
**Context:** TS-045: Nav2 AMCL (1.3.14, `jazzy` source) reads `OccupancyGrid.info.origin` as the centre of cell 0, while ROS defines it as the corner. On the DEC-055-corrected reference map AMCL therefore sees every wall 0.025 m lower in x and y, which gave a constant bias of about 35–40 mm (scratch D2, D4). With a copy whose origin is +0.025 m the bias disappeared (D6: max 11.2 mm).
**Decision:** option (a): `/map` keeps serving the ROS-correct `maps/mapping_arena.yaml` (DEC-055), for RViz and, from M7, Nav2. A second `map_server` (`map_server_amcl`) serves `maps/mapping_arena_amcl.yaml` (the same image; origin +0.025 m in x and y; otherwise byte-identical apart from comments) on `/map_amcl`, and AMCL reads `map_topic: map_amcl`. The M6 consistency checker enforces the exact difference. The upstream Nav2 issue is in the follow-up below.
**Alternatives considered:** (b) serve the AMCL convention on `/map` for every consumer: RViz and the M7 costmaps would be 2.5 cm off, undoing DEC-055; (c) accept the bias as a known limitation: it uses about 70–80 % of the 0.05 m bound and hides a known error.
**Rationale and trade-offs:** every consumer sees the walls where they are; the correction is derived from the source code, not fitted. Cost: a second map server and a second map file that must stay in step (checked automatically).
**Consequences:** `localization.launch.py` starts four nodes; `amcl.yaml` gains `map_topic`; TEST-M6-02 checks both maps and AMCL's subscription; any later map used with AMCL needs the same copy (with the TS-041 origin correction for new SLAM maps).
**Follow-up:** retire this when Nav2 AMCL uses the ROS corner convention. Reported upstream 2026-11-20: [ros-navigation/navigation2#6833](https://github.com/ros-navigation/navigation2/issues/6833).

## DEC-063 — M6 Wrong-Start Recovery Bound Restated to 4.0 m of Travel (amends DEC-059)
**Date:** 2026-11-18   **Status:** **Accepted** (decided 2026-11-18, after the Task B diagnosis)
**Context:** DEC-059 set recovery from the 0.5 m / 15° wrong start (TEST-M6-04) to "the rest bounds within 3 m of travel". The 3 m came from CALC-M6-03's estimate (about 12 AMCL updates at 0.25 m), not from a measurement. In Task B (scratch runs, GUI shown, M6 plan §12), with the approved DEC-061 settings, recovery took 2.73, 2.89, 2.90 and 3.19 m (4 runs, 1 over). The heading was corrected within about 2 m; the lateral error decayed slowly on the first leg (driving east along y = 0, with the side walls 4 m away). Two candidate fixes did not help reliably: random-particle injection (`recovery_alpha_slow` 0.001, `recovery_alpha_fast` 0.1: 2.93 and 5.09 m) and `min_particles` 2000 (2.34 and 3.46 m). After recovery, every other bound held with wide margins in all 9 runs (worst 35 mm at rest, 49 mm moving maximum).
**Decision:** the TEST-M6-04 recovery bound is **4.0 m** of ground-truth travel: the measured maximum (3.19 m) plus 25 %, rounded up. Unchanged: the wrong start itself (0.5 m, 15°, RViz covariance), the rest and moving bounds after convergence, the AMCL settings (DEC-061), and every other DEC-059 bound. The checker requires the wrong start to be visible in the estimate before it looks for convergence (M6 plan §12).
**Alternatives considered:** (a) larger AMCL motion noise (4× or 8× the DEC-061 alphas) to spread the particles faster: untested, and it would trade against the tracking accuracy (the installed defaults gave up to 140 mm); (b) keep 3.0 m and record a likely FAIL in the formal runs; (c) the two parameter changes above, which did not help reliably.
**Rationale and trade-offs:** the bound now reflects measured behaviour with margin, instead of an estimate. Cost: a wrong start may take up to 4 m to correct, about one sixth of the M5 route. In M7 the robot normally starts from a known pose (DEC-058), and the moving bounds still apply after convergence.
**Consequences:** `TEST-M6_pose_check.py` uses 4.0 m; REQ-M6-06, test_plan §11 and M6 plan §3.3/§8 updated. The note in CALC-M6-03 records that its estimate was optimistic.
**Follow-up:** if a later change (M7 tuning, DEC-043 realism additions) changes AMCL's motion model, re-measure recovery.

## DEC-064 — Build-Identity Tests Check Only Their Own Milestone's Increment
**Date:** 2026-11-20   **Status:** **Accepted** (decided 2026-11-20, TEST-M6-09 regression)
**Context:** each milestone's build and regression identity test (TEST-M5-01, TEST-M6-01) has a step 5: existing files changed in `amr_ws/src` since the previous milestone's closeout may only be `package.xml` (an exact list of added `exec_depend` lines) and `CMakeLists.txt` (listed lines). That step compared the baseline with the working tree. In the M6 regression it failed TEST-M5-01 on M6's approved dependencies (TS-049): the rule measured the later milestone, not the M5 behaviour it guards. Steps 1–4 (build, M1 byte identity, launch-model identity, unchanged simulation, controller, sensor and SLAM files) passed and remain meaningful against the working tree.
**Decision:** step 5 of a milestone's identity test compares its baseline with **that milestone's closeout commit** (`END`). TEST-M5-01: `517608f` (M4 closeout) → `9b85171` (M5 closeout). TEST-M6-01: `9b85171` → the working tree while M6 is open; `END` is set to the M6 closeout commit when M6 closes. Steps 1–4 are unchanged. Each later milestone's own identity test covers its increment, so the chain covers every change since M4.
**Alternatives considered:** (a) add each later milestone's lines to the earlier tests' expected lists: every milestone would edit closed tests again; (b) drop TEST-M5-01 from the `m5` suite: loses steps 1–4 from regression.
**Rationale and trade-offs:** each test keeps measuring what its milestone committed to, and no closed test needs editing at every milestone. Cost: step 5 of a closed milestone no longer looks at the working tree; that coverage now depends on the next milestone's identity test existing and running in its suite.
**Consequences:** `TEST-M5-01_procedure.sh` (END = `9b85171`) and `TEST-M6-01_procedure.sh` (END variable; `robot_localization` added to its list, TS-049) changed; the TEST-M5-01 FAIL of TEST-M6-09 is kept and an R1 recorded.
**Follow-up:** at M6 closure, set TEST-M6-01's `END` default to the closeout commit; M7's identity test starts from that commit. Done 2026-11-21: `END` = `9777615`, verified (`docs/evidence/M6/TEST-M6-01-M6C_review.log`).

## DEC-065 — M6 Wrong-Start Recovery Bound Restated to 6.0 m of Travel (amends DEC-063)
**Date:** 2026-11-21   **Status:** **Accepted** (decided 2026-11-21, after a 10-run characterization)
**Context:** DEC-063 set the TEST-M6-04 recovery bound at 4.0 m: the maximum of 4 Task B dry runs (3.19 m) plus 25 %. In the `m6` suite run (TEST-M6-11, tag M611), TEST-M6-04 failed: one of 3 runs took 4.84 m. The user chose to measure before deciding. With the product settings (DEC-061), 10 further headless runs were made (`TEST-M6-04-char10_review.log`). Over all 21 wrong-start runs on record, recovery had a median of 2.93 m and a maximum of 4.84 m; 4 of 21 exceeded 4.0 m. The start error AMCL showed (78–468 mm) did not predict the recovery distance. Every run converged on the first leg of the route (6.49 m), and after recovery every bound held with wide margins. The wrong start is sent with RViz's covariance (σ 0.5 m, 15°), so each run starts from a randomly drawn particle cloud; 4 samples underestimated the spread.
**Decision:** the TEST-M6-04 recovery bound is **6.0 m** of ground-truth travel: the measured maximum of 21 runs (4.84 m) plus 25 % (6.05 m), rounded down to stay inside the first leg (6.49 m), so it also reads "recovered before the first turn". Unchanged: the wrong start (0.5 m, 15°, RViz covariance), the rest and moving bounds after convergence, and the AMCL settings (DEC-061).
**Alternatives considered:** (a) state the criterion as "before the end of the first leg" (same effect, tied to the route); (b) 5.0 m (about 3 % margin over the measured maximum); (c) keep 4.0 m and tune AMCL: in Task B, random-particle injection and 2000 particles did not help reliably and trade against tracking accuracy.
**Rationale and trade-offs:** the bound now rests on 21 measured runs, not 4, with the same 25 % rule as DEC-063. Cost: a wrong start may take up to 6 m to correct, about a fifth of the M5 route. M7 starts from a known pose (DEC-058); global localization is not relied on (TEST-M6-10 demonstration).
**Consequences:** `TEST-M6_pose_check.py` uses 6.0 m; REQ-M6-06, test_plan §11 and the M6 plan §8 updated; the TEST-M6-11 checker and mutation check follow. The TEST-M6-04 FAIL in the `m6` suite run is kept, and a TEST-M6-04 R1 is run under DEC-065. The 10 characterization runs are diagnosis data, not a formal result.
**Follow-up:** if AMCL's motion or sensor model changes (M7 tuning, DEC-043 realism additions), re-measure recovery with at least 10 runs. TEST-M6-04 R1 (2026-11-21) recovered after 5.68 m in one run: within the bound, but above the 4.84 m the bound was derived from (`TEST_RESULTS.md` § M6 Task E); reviewed and accepted as a known risk at M6 closeout.
