# M1 — Custom AMR Model: Milestone Plan and Record


**Status:** Design / documentation baseline prepared on 2026-10-19. The M1 design-review findings (R-01 to R-08) and OPEN-item resolutions (DEC-019) were applied, then reviewed and finalized on 2026-10-19. DEC-016 and DEC-017 were accepted the same day. **Implementation:** step 1 is complete and committed (`6227f66`); TEST-M1-01 passed. Steps 2–4 are complete and committed (`d9a295b`): TEST-M1-02 passed, and TEST-M1-03 passed on re-test 1. Step 5 is complete and committed (`1601440`): TEST-M1-04 and TEST-M1-05 passed. Steps 6–7 are complete and committed (`5bf390b`): TEST-M1-06 and TEST-M1-07 passed, and I finalized the results on 2026-10-21. Step 8: TEST-M1-08 passed on re-test 1, and I accepted the result on 2026-10-21 (commit `5612a42`). OPEN-07 stays provisional with follow-up milestone M2. **M1 is closed (2026-10-21)** (see step 8 below).

## 1. Purpose
Create and verify a static robot description of the project's own differential-drive AMR: geometry, inertial properties, and frames. Later milestones add motion, sensors, and autonomy on top of it.

## 2. Scope

**In scope:**
- A primitive-geometry chassis with a flat top platform.
- Two drive wheels on continuous joints, a rigid spherical rear caster, and a passive LiDAR mounting bracket and frame.
- Explicit inertial properties and the TF frame relationships.
- Xacro expansion, URDF structural validation, and geometry, mass, and inertia consistency checks.
- RViz visualization, and Gazebo Harmonic spawn and rest-stability checks.
- Documented test results and reasonably sized evidence.

**Out of scope (later milestones):**
- An active simulated LiDAR, IMU, or camera (M3, M11).
- Wheel control, `cmd_vel`, `ros2_control`, odometry, and the `/clock` bridge (M2, M4).
- SLAM, localization, Nav2, and obstacle avoidance (M5–M8).
- Task management, station recognition, and the dashboard (M10–M12).
- Payload dynamics (DEC-015) and physical hardware (M13).

## 3. Design baseline
- Geometry: [../design/mechanical_geometry.md](../design/mechanical_geometry.md)
- Mass and inertia: [../design/mass_inertia.md](../design/mass_inertia.md)
- Frames and TF: [../design/frames_and_tf.md](../design/frames_and_tf.md)
- Package architecture: [../architecture/ros_architecture.md](../architecture/ros_architecture.md)
- Requirements and traceability: [../requirements.md](../requirements.md)
- Tests: [../testing/test_plan.md](../testing/test_plan.md)
- Decisions: DEC-009 to DEC-017 and DEC-019 in [../../DECISIONS.md](../../DECISIONS.md)

## 4. Design items (resolved in the M1 design review, DEC-019)
Each item had to be resolved, or explicitly accepted as provisional, before the step that needs it. I finalized the M1 Engineering Decision Report recommendations and then reviewed and accepted the resulting documentation on 2026-10-19.

| ID | Item | Resolution | Needed by | Status |
|---|---|---|---|---|
| OPEN-01 | Caster radius, position, and contact geometry; whether to model a caster mounting arm | r = 0.025 m; centre (−0.360, 0, −0.050) in `base_link`, behind the chassis, 18.0 mm clearance, 0.060 m rear overhang, swept radius 0.385 m (CALC-M1-13). The mounting arm is not modelled and not physically validated | Step 4 | Resolved: Selected |
| OPEN-02 | Final wheel-to-chassis collision clearance (7.5 mm nominal per side) | Accepted as a Calculated geometric clearance (track 0.400 m, wheel width 0.035 m). Not expected to be a physics contact in M1 (frames_and_tf.md §4) | Steps 4, 6 (TEST-M1-03, TEST-M1-06) | Resolved: TEST-M1-03 PASS (re-test 1) and TEST-M1-06 PASS (no visible interpenetration, observed by me) |
| OPEN-03 | LiDAR bracket size, platform clearance, and sensor-frame placement | 0.080 × 0.080 × 0.030 m bracket at x = +0.070 m; mount frame on the bracket top (0.200 m above ground). Placeholder dimensions; scan plane and FOV deferred to M3 | Step 4 | Accepted as provisional (until M3) |
| OPEN-04 | Wheel joint axis and cylinder axis mapping | Unrotated wheel link, axis (0 1 0) on both wheels, geometry rpy (π/2, 0, 0), Iyy axial (frames_and_tf.md §3) | Step 4 | Resolved: Selected; sign verified by TEST-M1-04 (PASS 2026-10-21) |
| OPEN-05 | Final inertial origins and link-level inertia definitions (chassis inertia on `base_link` vs a separate `chassis_link`) | Chassis inertial on `base_link` at (−0.100, 0, +0.035); no `chassis_link` | Step 3 | Resolved: Selected |
| OPEN-06 | Ground clearance and `base_link` height | Ground clearance 0.050 m (feasible window 0.030–0.075 m, CALC-M1-02). The `base_link` height of 0.075 m is Calculated from DEC-016 and `wheel_radius`; it is not an independent parameter | Step 3 | Resolved: Selected (clearance) |
| OPEN-07 | Rest-stability acceptance thresholds | \|Δz\| < 2 mm, \|roll\|/\|pitch\| < 0.5°, drift < 5 mm over 30 s; procedure refined in TEST-M1-07 | Step 7 | Accepted as provisional; TEST-M1-07 PASS on 2026-10-21. I decided on 2026-10-21 to keep the thresholds provisional, with follow-up milestone **M2** (DEC-019) |

The OPEN-04, -05, and -06 selections assume DEC-016 (accepted on 2026-10-19). They must be revisited if DEC-016 is ever revised.

## 5. Entry criteria

| Criterion | Status |
|---|---|
| M0 complete and verified | ✅ Met (TEST-M0-01 to -05; TEST-M0-04 re-test 1) |
| Documentation baseline reviewed and finalized | ✅ Met: reviewed and finalized on 2026-10-19 |
| OPEN items resolved or accepted as provisional for their step | ✅ Met: DEC-019 (OPEN-03 provisional until M3, OPEN-07 until TEST-M1-07) |
| DEC-011 to DEC-014 accepted (no longer provisional) | ✅ Met: Accepted on a decision of review finding R-04 (2026-10-19) |
| Proposed DEC-016 and DEC-017 accepted | ✅ Met: accepted on 2026-10-19 as the proposed M1 baseline (`DECISIONS.md`) |

## 6. Implementation sequence (planned 2026-10-19; all steps complete 2026-10-21)
Each step follows Inspect → Plan → Implement → Build → Test → Verify → Document → Review diff, and is committed only after review.

| Step | Work | Verification |
|---|---|---|
| 1 | Create `amr_ws/src/amr_description` (`package.xml`, `CMakeLists.txt`) | TEST-M1-01 |
| 2 | `amr_properties.xacro`, `inertial_macros.xacro`, top-level `amr.urdf.xacro` with `base_footprint` + `base_link` (chassis) only | TEST-M1-02 (partial) |
| 3 | Resolve OPEN-05/06; finalize the chassis inertial | TEST-M1-03 (chassis) |
| 4 | Add wheels, caster, and LiDAR mount (needs OPEN-01, -03, -04) | TEST-M1-02, TEST-M1-03 |
| 5 | `display.launch.py` + `display.rviz` | TEST-M1-04, TEST-M1-05 |
| 6 | `gazebo.launch.py` (empty world, spawn) | TEST-M1-06 |
| 7 | Rest-stability check (needs OPEN-07) | TEST-M1-07 |
| 8 | Consistency review; record results and evidence; update tracking files | TEST-M1-08 |

## 7. Exit criteria
M1 is complete only when:
- TEST-M1-01 to TEST-M1-08 are all PASS, with evidence recorded in `TEST_RESULTS.md` and `docs/evidence/M1/`.
- Every OPEN item is resolved and recorded in `DECISIONS.md`, or stays provisional **only if** a named follow-up milestone for it is recorded in `DECISIONS.md`. A provisional item without a recorded follow-up milestone blocks M1 closure. *(Revised 2026-10-19, review follow-up G1: OPEN-03 is provisional until M3. Wording made explicit 2026-10-21 by my decision; OPEN-07 is provisional with follow-up milestone M2.)*
- The design documents, properties file, and generated model agree (TEST-M1-08).
- I have reviewed the final diff.

## 8. Implementation record
*(Record each step's outcome, deviations from plan, issues (TS-IDs), and lessons learned here.)*

**Step 1: workspace and package skeleton, 2026-10-19 (licence change and re-test 1 on 2026-10-21). Complete.**
- Created `amr_ws/src/amr_description` (DEC-008, DEC-017):
  - `package.xml`: format 3; `buildtool_depend` `ament_cmake`; `exec_depend` `xacro`, `robot_state_publisher`, `joint_state_publisher`, `joint_state_publisher_gui`, `rviz2`, `ros_gz_sim`, `launch`, `launch_ros`.
  - `CMakeLists.txt`: installs `urdf/`, `launch/` and `rviz/` to `share/amr_description`, excluding `.gitkeep`.
  - Empty `urdf/`, `launch/` and `rviz/` directories, kept with `.gitkeep`.
- Result: TEST-M1-01 PASS (exit 0, no warnings). Re-test 1 PASS after the licence change ([TEST_RESULTS.md](../../TEST_RESULTS.md)).
- Deviations: none from the plan. The licence is the Apache License 2.0 (DEC-020; my decision, 2026-10-21): `package.xml` says `Apache-2.0`, and the root `LICENSE` holds the official text.
- Issues: none (no TS entry).

**Steps 2–4: Xacro model and inertials, 2026-10-21. Complete (commit `d9a295b`).**
- Created in `amr_ws/src/amr_description/urdf/`:
  - `amr_properties.xacro`: every numeric parameter from mechanical_geometry.md §2 and the masses from mass_inertia.md §1, plus the §3 derived placements written as expressions of those parameters. It now owns the numeric values ([../README.md](../README.md#source-of-truth)).
  - `inertial_macros.xacro`: `box_inertia`, `cylinder_inertia` (Iyy axial) and `sphere_inertia`, implementing mass_inertia.md §3–6.
  - `amr.urdf.xacro`: the 6-link / 5-joint tree of frames_and_tf.md §2 (robot name `amr`). The visual and collision geometry are identical primitives.
  - Removed `urdf/.gitkeep`; the directory is no longer empty.
- The three steps were implemented together and tested together (the plan listed TEST-M1-02 as partial after step 2). Reason: they are one reviewable change, and TEST-M1-02 and -03 check the complete model.
- Results ([TEST_RESULTS.md](../../TEST_RESULTS.md)):
  - TEST-M1-02 PASS.
  - TEST-M1-03 **FAIL**, then re-test 1 PASS (52/52 checks). The failure was a false positive in the check script ([TS-007](../troubleshooting.md)); the model was not changed.
  - The SDF lumping expected from the generic probe (CALC-M1-15) was observed on the real model: 3 links, 8.4 kg at (−0.1021, 0, +0.1098).
- Deviations from the design: none. No `<material>` colours or Gazebo-specific tags were added; colours can be added with the RViz work if wanted.
- Not verified yet: wheel rotation sign (TEST-M1-04), TF values in a running system (TEST-M1-04/05), Gazebo spawn and rest (TEST-M1-06/07).
- Lesson: check generated XML at element level. xacro keeps comments, so text searches give false matches. The planned TEST-M1-08 `grep -ri mesh` had the same flaw; it was replaced with an element-level check before running (TS-007 follow-up).

**Step 5: RViz display and TF verification, 2026-10-21. Complete (commit `1601440`).**
- Created `launch/display.launch.py`: `robot_state_publisher` with the xacro-expanded model, `joint_state_publisher_gui`, and `rviz2` with `rviz/display.rviz`. No launch arguments.
- Created `rviz/display.rviz`: fixed frame `base_footprint`, Grid, RobotModel (from `/robot_description`, alpha 0.6 so the TF axes stay visible), and TF with frame names.
- Removed `launch/.gitkeep` and `rviz/.gitkeep`. The model files are unchanged from `d9a295b`.
- Results ([TEST_RESULTS.md](../../TEST_RESULTS.md)):
  - TEST-M1-04 PASS: TF translations equal the design to 1 mm. The model matches the sketches and both wheels roll forward for a positive slider (both **observed by me**), supported by the TF readback.
  - TEST-M1-05 PASS: the `view_frames` tree equals §2 of frames_and_tf.md.
- Deviation: `ROS_DOMAIN_ID=47` was used for test isolation (TS-006 lesson).
- Issues: TS-008. A Qt `QSocketNotifier` warning at start-up, and `joint_state_publisher_gui` exit code −2 when the launch is stopped with SIGINT. Both accepted as benign.
- Not verified yet: Gazebo spawn and rest (TEST-M1-06/07); the consistency review (TEST-M1-08).

**Steps 6–7: Gazebo spawn and rest stability, 2026-10-21. Complete (commit `5bf390b`); results finalized.**
- Created `launch/gazebo.launch.py`:
  - `robot_state_publisher` (xacro-expanded model) publishes `/robot_description`.
  - `gz sim -r empty.sdf` starts the stock world, running.
  - `ros_gz_sim create -world empty -topic robot_description -name amr` spawns the model at an explicit pose, given as launch arguments `x y z roll pitch yaw` (all default 0, so `base_footprint` sits on the ground).
  - No bridge, controllers, sensors or damping.
  - `CMakeLists.txt` and `package.xml` are unchanged: `launch/` was already installed and `ros_gz_sim` was already a dependency.
- Results ([TEST_RESULTS.md](../../TEST_RESULTS.md)):
  - TEST-M1-06 PASS: `amr` is listed, with no `[Err]`/`[Wrn]`. The ground contact and the absence of interpenetration were **observed by me**.
  - TEST-M1-07 PASS: over 30.107 s of sim time at RTF 0.9996, Δz = 0 mm, roll 0°, pitch 0.000098° and drift 0 mm. No jitter was **observed by me**.
- Deviations:
  - Gazebo is started with `gz sim` instead of `ros_gz_sim/gz_sim.launch.py`, because of the leftover-process problem TS-009.
  - The TEST-M1-07 sample A came about 8 s of sim time after the spawn (estimated), not about 1 s; it is bounded by the P0-vs-spawn comparison (see the test record).
  - The measurement uses `/world/empty/pose/info` (sim-time stamped, full precision) as the primary source and `gz model -p` as the cross-check.
- Issues: TS-009 (resolved before testing).
- OPEN-07: after TEST-M1-07 PASS, I decided on 2026-10-21 to keep the thresholds provisional. M2 was named as the follow-up milestone later the same day (recorded in DEC-019).
- Open at the time: TEST-M1-08, since run (see step 8).

**Step 8: documentation / code consistency review, 2026-10-21. TEST-M1-08 passed (re-test 1, accepted); M1 closed on 2026-10-21.**
- Added `docs/evidence/M1/TEST-M1-08_procedure.sh`, `TEST-M1-08_consistency_check.py` and `TEST-M1-08_records_check.py`. The expected values come from the design documents, never from the Xacro files.
- Results ([TEST_RESULTS.md](../../TEST_RESULTS.md)): TEST-M1-08 **FAIL**, a procedure defect ([TS-010](../troubleshooting.md): xacro header path), then **re-test 1 PASS**:
  - 0 mismatches across 18 properties, 6 links, 5 joints, the placements and CALC-M1-01 to -05, -13 and -14;
  - TEST-M1-03 re-run 52/52;
  - generated URDF/SDF byte-identical to the evidence;
  - 0 `<mesh>` elements;
  - records consistent.
- Documentation corrected (no values changed): dated confirmations were added where design documents still said "not yet observed" or "nothing verified in simulation yet" (frames_and_tf.md §4; mass_inertia.md status, §5 and §11; mechanical_geometry.md CALC-M1-03 and -13). In requirements.md, the planned-path marker wording and the REQ-M1-13 threshold label ("Proposed" → "accepted as provisional", per DEC-019) were corrected.
- **M1 exit criteria (§7) after step 8:**
  - TEST-M1-01 to -08 PASS with evidence: ✅ (TEST-M1-03 and -08 on re-test 1; the failures are kept).
  - Design documents, properties file and generated model agree: ✅ (TEST-M1-08 re-test 1).
  - Traceability updated: ✅ (in this change).
  - Every OPEN item resolved, or provisional with a recorded follow-up milestone: ✅ after the 2026-10-21 decision. OPEN-01, -02, -04, -05 and -06 are resolved; OPEN-03 is provisional until **M3**; OPEN-07 is provisional with follow-up **M2** (DEC-019). *(When the review was first run, OPEN-07 had no named follow-up and this criterion was ❌.)*
  - I have reviewed the final diff: ✅ (reviewed before the closing commit).
- **Findings, and my decisions of 2026-10-21:**
  1. OPEN-07 had no named follow-up milestone. *Decided:* keep it provisional, with **M2** as the follow-up milestone; the thresholds are unchanged. Recorded in DEC-019 and this plan.
  3. DEC-019 still said the OPEN-04 wheel sign "is analytical until TEST-M1-04" and OPEN-07 is provisional "until TEST-M1-07". *Decided:* corrected with dated updates; the history and all values are kept.
  4. mechanical_geometry.md §5 called a dimensioned SVG drawing "a planned M1 deliverable", but it is not in the §7 exit criteria. *Decided:* it is **not required for M1 closure**. It stays a planned deliverable, not yet scheduled, and §7 is not extended. No authoritative requirement contradicts this: REQ-M1-11 and TEST-M1-04 refer to "the drawing", which TEST-M1-04 satisfied with the §5 sketches.
  5. TEST-M1-08 re-test 1: *accepted as PASS by me*. The failed first run and TS-010 are kept.
