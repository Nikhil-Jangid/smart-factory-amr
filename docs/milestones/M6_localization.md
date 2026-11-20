# M6 — Localization: Milestone Plan and Record

**Status:** **Complete** (2026-11-21; closed; in progress since 2026-11-18). Every exit criterion in §11 is met: TEST-M6-01 to -11 PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6), with the failures kept beside their re-tests; OPEN-28 to -32 decided (DEC-056 to DEC-060), and DEC-061 to DEC-065 added during implementation; CI green. Known limitations: §13. History: plan **finalized on 2026-11-18** with all five §4 recommendations: OPEN-28 to -32 = DEC-056 to DEC-060). The bounds (DEC-059) are **Selected** by that approval. History: drafted as Proposed on 2026-11-18 (`f15b19f`). Values are labelled per `docs/README.md`.

**Record rule (DEC-041):** test results live only in `TEST_RESULTS.md`. This record and `test_plan.md` link to them and do not restate the numbers.

## 1. Purpose
M5 built and saved a map while estimating the pose at the same time (SLAM). A factory robot does not re-map at every start: it **localizes** on a known map. M6 adds this:
- **Localization on the saved map.** The M5 reference map (`amr_bringup/maps/mapping_arena.yaml`, origin corrected by DEC-055) is loaded and served on `/map`. A localization node estimates the robot's pose in it from `/scan` and odometry, and publishes `map → odom` (REP-105; `frames_and_tf.md`: "`map → odom` (on a saved map): localization, M6").
- **Pose estimation from an imperfect start.** The robot must find its pose when the initial guess is wrong, and keep it when odometry is wrong.
- **Odometry fusion.** The odometry covariance (DEC-042) and the IMU (DEC-032, DEC-038) were prepared for fusion; DEC-045 says "M6 runs odometry with the IMU on". M6 decides how the fusion is integrated (OPEN-29).
- **Measured quality.** Pose estimates are compared with Gazebo ground truth, at rest points and while moving.

*Concept: localization vs SLAM.* SLAM changes the map while it estimates the pose. Localization keeps the map fixed and estimates only the pose. A fixed map is what M7 (Nav2) plans on, and it lets the robot start anywhere on the map without rebuilding it.

*Concept: AMCL (Adaptive Monte Carlo Localization).* A **particle filter**: the pose belief is a cloud of a few hundred to a few thousand guesses (particles).
1. **Predict:** when the robot moves (odometry), every particle moves the same way plus random noise sized by the motion-model parameters `alpha1`–`alpha5`.
2. **Weight:** each particle is scored by how well the current scan, placed at that particle's pose, matches the map. The **likelihood field** model precomputes, for every map cell, the distance to the nearest occupied cell; a beam ending close to a wall scores high.
3. **Resample:** particles are redrawn in proportion to their weights; poor guesses disappear and good ones multiply. "Adaptive" (KLD sampling) shrinks the particle count when the cloud is concentrated.
The pose estimate is the cloud's mean (`/amcl_pose`, with covariance). AMCL then publishes `map → odom` so that `map → odom → base_footprint` equals that estimate. It updates only after the robot moves `update_min_d` (0.25 m) or turns `update_min_a` (0.2 rad); between updates `map → odom` stays fixed.

*Concept: EKF fusion.* An Extended Kalman Filter combines measurements of the same quantity in proportion to their confidence (inverse covariance). Wheel odometry measures yaw rate from wheel speeds and the wheel separation; the IMU gyroscope measures it directly. If the wheel separation is wrong, odometry yaw drifts; an unbiased gyro does not. The fused `odom → base_footprint` is then better than either alone. Fusion improves the *smooth* odometry frame; it does not replace localization, because nothing in it sees the map.

## 2. Scope
Derived from ROADMAP § M6 (localization setup, pose estimation, TF verification, localization testing), `frames_and_tf.md` (DEC-016: `map → odom` from localization on a saved map), DEC-042 and DEC-045 (fusion follow-ups), DEC-051 (M6 chooses the localization method), DEC-041.

**In scope:**
| Item | Source |
|---|---|
| Serving the M5 reference map (`nav2_map_server`) and installing the `maps/` folder (DEC-054: "M6 adds it") | ROADMAP M6 ("localization setup"); DEC-054 |
| Localization node (OPEN-28), configuration, launch, sim time, lifecycle start-up | ROADMAP M6 |
| TF verification: one `map → odom` publisher, complete tree, no SLAM node running | ROADMAP M6 ("TF verification") |
| Tracking accuracy against Gazebo ground truth, at rest points and while moving | ROADMAP M6 ("localization testing") |
| Recovery from a wrong initial pose; robustness to odometry error and to unmapped obstacles | ROADMAP M6 ("pose estimation") |
| Odometry + IMU fusion (OPEN-29) | DEC-042, DEC-045 |
| Checker sensitivity: wrong poses must fail | M4/M5 practice (TEST-M4-09, TEST-M5-07) |
| RViz localization view; `m6` runner suite; GPU-free checks in CI; M1–M5 regression | DEC-040, DEC-041 |

**Out of scope:**
- Nav2 planning, controllers, costmaps, goal following: M7. M6 only states the localization accuracy M7 needs (§3.3).
- Mapping changes: the M5 reference map is used as committed. No new map is saved in M6, so the origin correction for new maps (TS-041) stays deferred and the loop-closure follow-up (DEC-052) is unaffected.
- The factory world: M9.
- IMU bias and drift, encoder emulation and other realism additions (DEC-043 follow-up, TODO): the fusion test injects the M4 calibration error instead (§3.4). Adding IMU bias in M6 it is a scope change decided under OPEN-29.
- Changing the robot model, the sensors, the controller limits or the odometry covariance values.

## 3. Analysis (Calculated unless stated otherwise)
Inputs: LiDAR 360 samples (1°), 10 Hz, 0.12–12 m, σ 0.01 m (DEC-031); IMU 100 Hz, gyro σ 0.001 rad/s, zero bias (DEC-032, DEC-038); odometry twist covariance yaw rate 4.0e-4 (rad/s)² (DEC-042, CALC-M4-04); reference map 0.05 m, origin (−2.071, −4.080) (DEC-055); route and arena from M5 (CALC-M5-01, -02). Installed (`dpkg-query`, after my apt upgrade of 2026-11-18; the plan draft read 1.3.13 and 3.8.3 before it): `nav2_amcl`, `nav2_map_server`, `nav2_lifecycle_manager`, `nav2_bringup` 1.3.14; `robot_localization` 3.8.4; `slam_toolbox` 2.8.5. The AMCL defaults below were re-read from the 1.3.14 `nav2_params.yaml`. AMCL defaults read from `/opt/ros/jazzy/share/nav2_bringup/params/nav2_params.yaml`: 500–2000 particles, `alpha1`–`alpha5` 0.2, `laser_model_type` likelihood_field, `max_beams` 60, `sigma_hit` 0.2, `laser_max_range` 100.0, `update_min_d` 0.25 m, `update_min_a` 0.2 rad, `transform_tolerance` 1.0 s, `recovery_alpha_*` 0.0 (no random-particle injection), `base_frame_id` `base_footprint`.

### 3.1 CALC-M6-01: what M7 needs from localization (basis for the bounds, OPEN-31)
- The installed Nav2 goal checker accepts a goal within `xy_goal_tolerance` 0.25 m and `yaw_goal_tolerance` 0.25 rad (14.3°) (`nav2_params.yaml`, installed defaults).
- Localization error uses part of that tolerance directly. Allowing it one fifth: 0.05 m and 2.9°.
- The M5 SLAM pose bound is 0.05 m and 1.0° (DEC-047). Localization on the map that SLAM built cannot be expected to be much better than the map itself (map wall P95 0.10 m bound; measured values in `TEST_RESULTS.md` § M5 Task C).
- Hence the proposal: **at rest** ≤ 0.05 m and ≤ 1.0° (as M5); **while moving** P95 ≤ 0.10 m and ≤ 2.0°, maximum ≤ 0.25 m (never more than a whole goal tolerance). The moving bound is looser because AMCL updates only every 0.25 m / 0.2 rad (§3.2) and the ground-truth and TF samples are matched in time to ± 10 ms.

### 3.2 CALC-M6-02: error between filter updates
Between AMCL updates, `map → odom` is fixed and the pose follows odometry alone.
- *Ideal simulation:* odometry error about 0.01 % (TEST-M2-05/-06 R1): negligible within 0.25 m.
- *With the TEST-M4-09 overrides* (separation × 1.02, both radii × 1.01): yaw error −1.96 % of rotation (CALC-M4-02) → at most 1.96 % × 0.2 rad = 0.0039 rad (0.22°) before the next update; distance error 1 % × 0.25 m = 2.5 mm. Both are far inside the §3.1 bounds, so the injected error tests the filter's correction, not its update spacing.
- *`transform_tolerance` 1.0 s:* AMCL stamps `map → odom` up to 1 s in the future so that consumers can use it before the next update. The harness reads `map → base_footprint` at the ground-truth stamp; it must not read "latest" (Task B checks this).

### 3.3 CALC-M6-03: initial-pose recovery and global localization
- *Known start:* the robot spawns at the world origin, which is the map origin used by M5 (`map → odom` identity at the start of mapping, M5 plan §12). AMCL can start from that pose (`set_initial_pose` with (0, 0, 0)).
- *Wrong start (proposed TEST-M6-04):* the initial guess is offset by 0.5 m and 15° from the truth, sent on `/initialpose` with the covariance RViz's "2D Pose Estimate" sends (x, y variance 0.25 m², yaw variance 0.0685 rad², i.e. σ 0.5 m and 15°). The truth is then one standard deviation from the guess, inside the initial cloud. Proposed criterion: within the rest bounds after at most 3 m of travel (12 filter updates at 0.25 m) and staying within the moving bounds afterwards. *Task B finding (§12):* the estimate of 12 updates was optimistic; with the DEC-061 settings the measured recovery is 2.73–3.19 m, set mainly by the slow lateral correction on the first leg. DEC-063 restates the bound to 4.0 m.
- *Global localization* (particles spread over the whole map, `reinitialize_global_localization`): the arena's free area is about 78.7 m² (80 m² interior minus W1 0.5, B1 0.6, P1 and P2 0.18 m²; CALC-M5-01). With 0.25 m × 0.25 m × 15° bins that is about 1260 × 24 ≈ 30 000 pose bins, against at most 2000 particles: about 7 % coverage, so convergence would depend on luck and route. A factory AMR normally starts at a known dock (M10). Proposal: a demonstration, not an acceptance criterion (OPEN-30).

### 3.4 CALC-M6-04: fusion benefit with an injected odometry error (if OPEN-29 (a) or (b))
- *Raw odometry* on the M5 route with separation × 1.02 and both radii × 1.01 (CALC-M5-04, net rotation +360°): 0.198 m and −3.53° at the end; separation × 1.02 alone: 0.400 m and −7.06°.
- *Yaw-rate weights in the EKF:* odometry variance 4.0e-4 (rad/s)² (DEC-042); gyro σ 0.001 rad/s, variance 1.0e-6. The fused yaw rate weights the gyro by 4.0e-4 / (4.0e-4 + 1.0e-6) = 0.9975, so 0.25 % of the odometry yaw-rate error remains: about 0.02° of the 7.06°. **Assumption to check in Task A:** the `/imu` message carries this covariance; if it is zero or unset, `robot_localization` must be configured with it explicitly.
- *Gyro noise alone:* angle random walk 0.001 rad/s × √(163 s × 0.01 s) = 0.0013 rad (0.07°) over the route (about 163 s, CALC-M5-02).
- *Translation:* the separation multiplier affects only the angular rate; with yaw corrected, the remaining position error comes from the radius error (1 % of distance, along the path).
- Proposed criterion for TEST-M6-07: with separation × 1.02 alone, the fused end yaw error ≤ 0.5° (≤ 10 % of the 7.06° raw prediction) and the fused end position error ≤ 25 % of the raw one, while raw odometry matches CALC-M5-04 within ± 25 %.

## 4. Design items (**decided 2026-11-18**: OPEN-28 = DEC-056 (a), OPEN-29 = DEC-057 (a), OPEN-30 = DEC-058 (a), OPEN-31 = DEC-059, OPEN-32 = DEC-060 (a); each as recommended)
| ID | Item | Options | Recommendation (Proposed) |
|---|---|---|---|
| OPEN-28 | Localization method (DEC-051 kept both inputs) | (a) **AMCL** (`nav2_amcl`) on the `.pgm`/`.yaml` map with `nav2_map_server`; (b) **SLAM Toolbox localization mode** on the serialized pose graph (scan matching against the stored graph; it also keeps adding temporary nodes); (c) both, compared | **(a)**. It is the method M7 (Nav2) is built and documented around; it uses only the image map, so it is independent of the mapping algorithm and checks the map from a second method; its particle cloud can represent an uncertain or wrong start (§3.3). (b) stays possible later because the pose graph is committed (DEC-054). (c) doubles the test work for a comparison M7 does not need |
| OPEN-29 | Odometry + IMU fusion | (a) **EKF in the TF chain, selectable:** `robot_localization` `ekf_node` fuses `/diff_drive_controller/odom` (velocities) and `/imu` (yaw rate) and publishes `odom → base_footprint`; it is started by an `ekf:=true` launch option with a controllers file whose only difference is `enable_odom_tf: false` (the consistency checker enforces the one-line difference); default off, so M1–M5 behaviour is unchanged; (b) **EKF output topic only** (`/odometry/filtered`, no TF): measurable, but nothing uses it until M7; (c) **defer fusion** to the realism step (DEC-043 follow-up) | **(a)**. It delivers the fusion that DEC-042 and DEC-045 prepared, its benefit is measurable with the injected error (§3.4), and the default stays unchanged until M7 decides whether to make it the default. Cost: a second controllers file to keep in step (checked automatically). IMU bias is not added (out of scope) unless chosen here |
| OPEN-30 | Initial pose and global localization | (a) **known start** from `set_initial_pose` (0, 0, 0) for the accuracy tests, a **wrong-start recovery** test (§3.3), global localization as a **demonstration** (recorded, not a criterion); (b) as (a) with global localization as an acceptance test (likely needs more particles or random-particle injection, §3.3); (c) known start only | **(a)**. It tests the realistic cases (a known dock and an operator's rough initial pose) without tuning AMCL for a case the factory workflow avoids |
| OPEN-31 | Accuracy and convergence bounds | the §3.1 and §3.3 proposal: at rest ≤ 0.05 m and ≤ 1.0°; while moving P95 ≤ 0.10 m and ≤ 2.0°, maximum ≤ 0.25 m; recovery within 3 m of travel; fusion per §3.4; or other bounds | the proposal: derived from the M7 goal tolerance and consistent with M5. Like M5, the bounds are fixed before any formal run; Task A measures the default-parameter accuracy in a scratch gate, and if the defaults miss the bounds, any parameter change is a recorded decision, not silent tuning |
| OPEN-32 | Test world, route and launch structure | (a) the **M5 arena and route** (DEC-046, CALC-M5-02) driven by the M5 ground-truth follower (DEC-049), in both directions (the reverse route turns the other way and sees the features from the other side); a **test-only** copy of the arena with three unmapped boxes for the robustness test; a new `localization.launch.py` (map server, AMCL, lifecycle manager; optional EKF) beside the unchanged `sim.launch.py`, as DEC-050 did for SLAM; (b) a new world and route; (c) include the installed `nav2_bringup` `localization_launch.py` | **(a)**. The arena's geometry and clearances are already verified, the reference map belongs to it, and the follower makes runs comparable. An own launch file with three nodes is shorter and clearer than the installed one, which rewrites parameters and adds options M6 does not use |

## 5. Entry criteria and dependencies
- M5 complete (2026-11-15): ✅. The reference map is committed with the corrected origin (DEC-055) and the pose graph (DEC-054).
- M4 odometry with covariance (DEC-042) and M3 IMU (DEC-038): ✅.
- `nav2_amcl`, `nav2_map_server`, `nav2_lifecycle_manager` 1.3.14 and `robot_localization` 3.8.4 installed (§3): ✅. The M1–M5 behaviour on the upgraded packages is re-verified (`TEST_RESULTS.md` § Environment re-verification 2026-11-18). Installed is not integrated; Task A checks integration first.
- The user approves this plan and decides OPEN-28 to -32: ✅ 2026-11-18 (DEC-056 to DEC-060).

## 6. Architecture (for the §4 recommendations)
```
amr_bringup/
  CMakeLists.txt                  + install rule for maps/ (DEC-054)
  package.xml                     + exec_depend nav2_map_server, nav2_amcl, nav2_lifecycle_manager, robot_localization
  config/amcl.yaml                installed AMCL defaults + the M6 changes, each commented (laser_max_range 12.0, initial pose)
  config/ekf.yaml                 robot_localization EKF: odometry velocities + IMU yaw rate, two_d_mode (OPEN-29)
  config/controllers_ekf.yaml     controllers.yaml with enable_odom_tf: false only (OPEN-29)
  launch/localization.launch.py   map_server + map_server_amcl (DEC-062) + amcl + lifecycle_manager (autostart), use_sim_time, map argument; ekf:=false|true
  rviz/localization.rviz          fixed frame map: /map, /scan, particle cloud, /amcl_pose covariance, robot model, TF
  maps/mapping_arena_amcl.yaml    AMCL-convention copy of the reference map, origin +0.025 m (DEC-062, TS-045)
docs/evidence/M6/
  TEST-M6_loc_run.py              harness: drives the M5 route (forward/reverse) with the DEC-049 follower; records
                                  map→base_footprint, odom→base_footprint and ground truth at rest points and at 10 Hz
  TEST-M6_pose_check.py           offline checker: rest and moving errors against the OPEN-31 bounds (CI)
  TEST-M6_unmapped_arena.sdf      test-only world: the arena + three boxes not in the map
  TEST-M6-08_distort.py           offset/rotated copies of a recorded log for the checker-sensitivity test (CI)
  TEST-M6-11_consistency_check.py record and configuration checker (DEC-041)
tools/run_suite.py                + 'm6' suite; GPU-free checks to 'ci', TEST-M6-11 to 'records'
```
Data path: `map_server` → `/map` (RViz; Nav2 from M7); `map_server_amcl` → `/map_amcl` (DEC-062) → AMCL ← `/scan`, TF `odom → base_footprint` (from `diff_drive_controller`, or from the EKF with `ekf:=true`) → TF `map → odom`, `/amcl_pose`, `/particle_cloud`. SLAM Toolbox is not running. Unchanged: the robot model, the sensors, `sim.launch.py`, `controllers.yaml`, the reference map files.

## 7. Task breakdown (finalized 2026-11-18)
| Task | Objective and deliverables | Tests | Depends on |
|---|---|---|---|
| **A: Localization launch and integration gate** | `amcl.yaml`, `localization.launch.py`, `localization.rviz`, maps install rule, package dependencies. Gate (scratch, Gazebo GUI and RViz shown, before any formal run): lifecycle nodes active on sim time; `/map` equals the reference file; AMCL converges at the spawn pose; one `map → odom` publisher; RTF with GUI + LiDAR + AMCL; default-parameter accuracy on one route (informs, does not change, the OPEN-31 bounds); `/imu` covariance contents (§3.4 assumption) | TEST-M6-01, -02 | Plan approval; OPEN-28, -31, -32 |
| **B: Harness and checker** | Route follower reuse (forward and reverse, clearance check for the reverse route and the unmapped boxes), 10 Hz pose recorder with stamp matching (§3.2), initial-pose injection, offline pose checker, distortion tool, unmapped-box world; dry runs | TEST-M6-08 | A |
| **C: Accuracy and robustness** | Formal runs: known start (both directions), wrong start, injected odometry error, unmapped obstacles; global-localization demonstration (OPEN-30) | TEST-M6-03, -04, -05, -06 | B; OPEN-30 |
| **D: Odometry fusion** | `ekf.yaml`, `controllers_ekf.yaml`, `ekf:=true` launch option; interface check (one `odom → base_footprint` publisher); fusion benefit with the injected error; localization with fusion on | TEST-M6-07 | B; OPEN-29 |
| **E: Closeout** | Regression, RViz observation, consistency checker, `m6` suite and CI, records | TEST-M6-09, -10, -11 | C, D |

## 8. Tests (criteria Accepted: DEC-059, 2026-11-18)
Procedures: `test_plan.md` §11 (commands fixed in Tasks A–E before any formal run); evidence: `docs/evidence/M6/`. Launch: `sim.launch.py sensors:=true world:=mapping_arena.sdf` + `localization.launch.py`. Gazebo tests run 3 times and every run must pass; runs with RTF < 0.5 are invalid; interactive runs show the Gazebo GUI and RViz (`SHOW=1`). A TS-029 shutdown hang is handled under DEC-039.
| Test | Requirement | Method | Proposed criterion |
|---|---|---|---|
| TEST-M6-01 | REQ-M6-11 | Build; M1 default expansion and the M2 and M3/M5 launch-model expansions byte-identical; `sim.launch.py`, `controllers.yaml`, `amr.sensors.xacro`, `amr_properties.xacro`, `slam_toolbox.yaml`, `slam.launch.py` and the reference map files unchanged since M5 (`9b85171`); changes to existing files listed | Build clean; all identical; existing files changed only by the `package.xml` dependency lines, the `CMakeLists.txt` maps install rule and comment lines |
| TEST-M6-02 | REQ-M6-01, -02, -03 | Interface: `map_server`, `amcl` active on sim time; served `/map` equals the reference file cell by cell (resolution, origin); exactly one `map → odom` publisher and no SLAM node; complete tree `map → odom → base_footprint → … → laser_frame`; `/amcl_pose` with covariance; `laser_max_range` 12.0 | All hold |
| TEST-M6-03 | REQ-M6-04, -05 | Tracking from the known start: M5 route forward and reverse; `map → base_footprint` vs ground truth at rest points and at 10 Hz | Rest ≤ 0.05 m, ≤ 1.0°; moving P95 ≤ 0.10 m, ≤ 2.0°, max ≤ 0.25 m |
| TEST-M6-04 | REQ-M6-06 | Wrong start: initial pose offset 0.5 m and 15° on `/initialpose` (§3.3), then the route | Rest bounds reached within 6.0 m of travel (DEC-065; 4.0 m in DEC-063, 3 m in DEC-059); moving bounds afterwards |
| TEST-M6-05 | REQ-M6-07 | Robustness: TEST-M6-03 with the TEST-M4-09 overrides (separation × 1.02, both radii × 1.01) through `controllers_file:=` | TEST-M6-03 bounds hold, while odometry drift at the end exceeds 3× the rest bound and agrees with CALC-M5-04 within ± 25 % |
| TEST-M6-06 | REQ-M6-08 | Unmapped obstacles: TEST-M6-03 in `TEST-M6_unmapped_arena.sdf` | TEST-M6-03 bounds hold |
| TEST-M6-07 | REQ-M6-09 | Fusion (`ekf:=true`): one `odom → base_footprint` publisher (the EKF); separation × 1.02 alone, raw vs fused odometry at the end; TEST-M6-03 bounds with fusion on | Fused yaw ≤ 0.5°, fused position ≤ 25 % of raw, raw within ± 25 % of CALC-M5-04; localization bounds hold |
| TEST-M6-08 | REQ-M6-10 | Checker sensitivity (offline, CI): a recorded log passes; copies with the estimate offset 0.08 m, rotated 1.5°, with one 0.30 m jump, and delayed 0.5 s each FAIL | 1 PASS, 4 FAIL, each on the expected measure |
| TEST-M6-09 | REQ-M6-11 | Regression through the runner: static and regression suites, M4 and M5 suites | All PASS |
| TEST-M6-10 | REQ-M6-12 | RViz `localization.rviz` (observed by me): the particle cloud converges after the wrong start, the scan lies on the map walls during the route, no unexplained TF jumps; global-localization demonstration shown (OPEN-30) | Observed by user |
| TEST-M6-11 | REQ-M6-13 | Consistency checker (DEC-041, including the one-line `controllers_ekf.yaml` difference), `m6` suite, TEST-M6-08 and -11 in CI | Zero mismatches; CI PASS |

## 9. Requirements (owner: `docs/requirements.md` § M6, from 2026-11-18; this list is the original draft)
| ID | Requirement |
|---|---|
| REQ-M6-01 | The M5 reference map is installed and served on `/map` unchanged |
| REQ-M6-02 | The localization node (OPEN-28) runs on sim time from `/scan` and the odometry TF and is the only publisher of `map → odom`; SLAM is not running |
| REQ-M6-03 | The TF tree `map → odom → base_footprint → … → laser_frame` is complete; the pose estimate is published with covariance |
| REQ-M6-04 | Pose accuracy at rest within the OPEN-31 bounds from a known start |
| REQ-M6-05 | Pose accuracy while moving within the OPEN-31 bounds |
| REQ-M6-06 | Recovery from a wrong initial pose within the OPEN-31 travel bound |
| REQ-M6-07 | Localization stays within bounds with the TEST-M4-09 odometry errors injected |
| REQ-M6-08 | Localization stays within bounds with unmapped obstacles present |
| REQ-M6-09 | Odometry + IMU fusion per OPEN-29, with a measured benefit and no `odom → base_footprint` conflict |
| REQ-M6-10 | The pose checker detects wrong estimates |
| REQ-M6-11 | M1–M5 behaviour unchanged |
| REQ-M6-12 | Localization visible in RViz |
| REQ-M6-13 | Records consistent under DEC-041; `m6` suite; GPU-free checks in CI |

## 10. Risks
- *An ideal simulation makes localization look perfect.* Mitigation: TEST-M6-04 (wrong start), -05 (real drift injected), -06 (unmapped obstacles) and -08 (wrong estimates fail).
- *Default AMCL parameters are tuned for a real robot* (motion noise 0.2, large particle counts). In a near-ideal simulation they are conservative, which costs smoothness rather than correctness. Mitigation: the Task A gate measures them; any change is a recorded decision with evidence.
- *The map is good but not perfect* (M5 wall P95 bound 0.10 m). Localization error has a floor set by the map. Mitigation: bounds consistent with M5 (§3.1); the pose checker reports per-rest-point errors for diagnosis.
- *Future-dated `map → odom`* (`transform_tolerance`, §3.2) can make a naive harness read the wrong time. Mitigation: stamp-matched lookups; TEST-M6-08 includes a delayed copy.
- *Two `odom → base_footprint` publishers* with fusion on would make the tree flicker. Mitigation: OPEN-29 (a) disables the controller TF in the fusion controllers file; TEST-M6-07 checks one publisher.
- *Lifecycle start-up order* (map server, AMCL) and the first-scan wait. Mitigation: a lifecycle manager with autostart; the interface test waits for the active states.
- *Low RTF with GUI + `gpu_lidar` + AMCL.* Mitigation: measured in the Task A gate; RTF < 0.5 invalid.
- *TS-029 shutdown hang.* Mitigation: DEC-039.

## 11. Exit criteria
M6 is complete only when:
- TEST-M6-01 to -11 are PASS, with results in `TEST_RESULTS.md` and evidence in `docs/evidence/M6/`; failures kept, with TS entries and re-tests.
- OPEN-28 to -32 are decided in `DECISIONS.md`.
- The configuration, documents and checker agree (TEST-M6-11); CI is green.
- The records are updated, the M6 Tasks are complete, and the closure is reviewed.

## 12. Implementation record
- 2026-11-18: plan drafted as Proposed from the current repository (M5 closed at `9b85171`) and the installed packages. Awaiting review and the OPEN-28 to -32 decisions. No implementation.
- 2026-11-18: plan finalized with all five recommendations (DEC-056 to DEC-060). I upgraded ROS 2 and Gazebo packages with apt the same day: before Task A, the installed versions in §3 and `docs/environment.md` are re-read, the workspace is rebuilt and the existing suites are re-run (regression check of the upgrade).
- 2026-11-18, Task A: environment re-verified after the upgrade (TEST_RESULTS.md, TS-043, TS-044). Files: `config/amcl.yaml` (installed Nav2 1.3.14 `amcl:` section, changes marked M6), `launch/localization.launch.py`, `rviz/localization.rviz`, the maps install rule, and exec_depends `nav2_map_server`, `nav2_amcl`, `nav2_lifecycle_manager` and `nav2_rviz_plugins` (the last one, for the particle-cloud display, was not in §6).
- 2026-11-18, Task A integration gate (scratch, GUI and RViz shown). Integration held: nodes active on sim time; served `/map` equal to the file (0 of 32 724 cells differ); AMCL at (0, 0) from the start; RTF 1.00; IMU angular-velocity variance 1×10⁻⁶ (CALC-M6-04 holds); `ros2 lifecycle get` does not find Nav2 nodes, so the tests use the `get_state` services. **Accuracy failed with the installed parameters:** rest-point errors up to 123 mm and 2.1° on the M5 route, while odometry was exact.
- 2026-11-18, diagnosis (scratch D1–D9, one M5 route each, GUI shown; nothing committed until the decisions). Worst rest-point errors:

  | Run | AMCL settings | Map given to AMCL | Odometry | Within 0.05 m / 1.0° | Worst error |
  |---|---|---|---|---|---|
  | D1 | installed (alphas 0.2, `sigma_hit` 0.2) | reference | ideal | 3 / 11 | 139.8 mm, 3.0° |
  | D2 | DEC-042 alphas (1σ) | reference | ideal | 3 / 11 | 66.2 mm |
  | D3 | `sigma_hit` 0.05 | reference | ideal | 4 / 11 | 124.0 mm, 2.5° |
  | D4 | both | reference | ideal | 11 / 11 | 41.0 mm (constant (−22, −32) mm offset) |
  | D5 | both | reference | TEST-M4-09 errors | 5 / 11 | 74.0 mm |
  | D6 | both | origin +0.025 m | ideal | 11 / 11 | 11.2 mm |
  | D7 | both | origin +0.025 m | TEST-M4-09 errors | 11 / 11 | 49.9 mm |
  | D8 | 2σ alphas, `sigma_hit` 0.05 | origin +0.025 m | ideal | 11 / 11 | 10.6 mm, 0.12° |
  | D9 | 2σ alphas, `sigma_hit` 0.05 | origin +0.025 m | TEST-M4-09 errors (odometry 254 mm, 3.5° off) | 11 / 11 | 23.1 mm, 0.19° |

  Findings: the installed motion and sensor noise are both far too large for the simulation (random errors); the constant offset is TS-045 (AMCL reads the map origin as a cell centre). User decisions: **DEC-061** (2σ alphas, `sigma_hit` 0.05) and **DEC-062** (AMCL-convention map copy on `/map_amcl`). Single scratch runs, not test results.
- 2026-11-18, gate repeated on the final configuration: three lifecycle nodes active; `/map` read only by RViz, `/map_amcl` only by AMCL; route 11 / 11 rest points within the bound (max 7.7 mm, 0.10°). TEST-M6-01 and -02 procedures written (test_plan §11).
- 2026-11-18, TEST-M6-01 PASS and TEST-M6-02 PASS on `8a515c2` ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6 Task A). Task A complete.
- 2026-11-18, Task B: tooling in `docs/evidence/M6/`:
  - `TEST-M6_route.py`: the M5 route forward and reversed; clearance, visibility and separation checks for the unmapped boxes; CALC-M5-04 drift prediction per direction (forward 0.198 m / −3.53°, reverse 0.440 m / −8.82°: the reverse route turns +900° net, every 180° turn to the left);
  - `TEST-M6_unmapped_arena.sdf`: the M5 arena (10 models byte-identical) plus three 0.5 m cubes, U1 (1.5, −1.6), U2 (2.6, 2.6) beside P1, and U3 (4.6, −3.3) in the alcove; robot centre ≥ 1.25 m from each;
  - `TEST-M6_run.py`: the M5 follower plus a 10 Hz recorder with TF looked up at the ground-truth stamp, and `/initialpose` injection;
  - `TEST-M6_pose_check.py`: DEC-059 bounds, recovery and drift;
  - `TEST-M6-08_distort.py`;
  - `TEST-M6_procedure.sh`, with options `ROUTE`, `WRONG`, `WORLD`, `INJECT` and `AMCL` (the last for diagnosis only).
- 2026-11-18, Task B dry runs (scratch, GUI shown, one run each, product settings):

  | Run | Rest max | Moving P95 | Moving max | Note |
  |---|---|---|---|---|
  | forward | 10.4 mm | 9.8 mm | 10.4 mm | 1995 samples, 0 missing |
  | reverse | 11.9 mm | 11.5 mm | 12.9 mm | |
  | unmapped boxes | 7.6 mm | 9.3 mm | 10.2 mm | |
  | injected errors, reverse | 26.8 mm | 27.4 mm | 30.4 mm | odometry 438.6 mm / −8.82°, −0.4 % of prediction |
  | wrong start | 15.4 mm | 22.1 mm | 44.0 mm | recovery 3.19 m |

  Distortion tool on the forward run: original PASS; offset, rotation, jump and delay each FAIL on their measure.
- Task B defects found and fixed in the dry runs (not test results):
  1. Harness deadlock: `start_sampling()` took the recorder's lock and then called `truth()`, which takes it again (`threading.Lock` is not re-entrant). Found with a thread dump of the hung process.
  2. Checker recovery logic: AMCL applies `/initialpose` to `map → odom` only at its next filter update (about 1 s later), so the first samples were still correct and were taken as "converged at 0 m". The checker now requires the wrong start to be visible first.
  3. Teardown: interrupting the harness by hand ended the procedure before its teardown. Stuck harnesses are stopped with SIGTERM, then the processes by PID.
- 2026-11-18, wrong-start diagnosis (user choice "diagnose first"; scratch, GUI shown, `AMCL=` option, product files unchanged). Recovery travel:
  - DEC-061 settings: 2.73, 2.89, 2.90 m (plus 3.19 m in the dry run);
  - `recovery_alpha_slow` 0.001 / `recovery_alpha_fast` 0.1: 2.93, 5.09 m;
  - `min_particles` 2000: 2.34, 3.46 m.

  The heading was corrected within about 2 m; the lateral error decayed slowly on the first leg. After convergence all bounds held in all 9 runs (worst 35 mm at rest, 49 mm moving maximum). User decision: **DEC-063**, recovery bound 4.0 m (amends DEC-059's 3 m); AMCL settings unchanged.
- 2026-11-18, TEST-M6-08 PASS on `3ed8eb6` ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6 Task B). Task B complete. The unmapped-box positions (U1–U3) are to be confirmed before TEST-M6-06 (Task C).
- 2026-11-18, I confirmed the unmapped-box positions U1 (1.5, −1.6), U2 (2.6, 2.6) and U3 (4.6, −3.3) (`TEST-M6_unmapped_arena.sdf`, unchanged). Task C started.
- 2026-11-19, Task C complete: TEST-M6-03, -04, -05 and -06 PASS in every run and direction, on `f2d344a` ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6 Task C; worst cases there). Incident: an empty Gazebo recording hung the trim step after attempt 1 of TEST-M6-04 (TS-046; no effect on the data). Next: Task D, TEST-M6-07.
- 2026-11-20, Task D started. Files: `config/ekf.yaml` (`robot_localization` EKF at 50 Hz, two-D; fuses the odometry vx, vy, yaw rate and the IMU yaw rate only; installed defaults otherwise), `config/controllers_ekf.yaml` (`controllers.yaml` with `enable_odom_tf: false` and a header comment), `localization.launch.py` option `ekf:=true`, `package.xml` dependency `robot_localization`. Test tooling: `TEST-M6-07_fusion_check.py` (`pre`/`main`), raw-odometry columns at rest points in `TEST-M6_run.py`, checker option `--fusion`, procedure options `FUSION=1` and `INJECT=sep`.
- 2026-11-20, Task D gate (scratch, GUI shown, separation × 1.02 alone, forward route; not test results):
  - The §3.4 assumption holds: `/imu` carries the gyro variance, 9.99999997e-07 on the wire (1.0e-6 as float32).
  - Dry run 1: the fusion and route results were as in run 2, but two fusion-check items FAILED on checker defects: the variance compare used an absolute tolerance of 1e-15 (float32 value), and the stamp check compared a 5.0 s window with a 5 s limit (the first stamp predates the window by one period). A headless diagnosis showed the stamps were simulation time. Both fixed: relative tolerance 1e-6; stamps within the window ± 1 s.
  - Dry run 2: every check PASS. Raw odometry at the end 400.0 mm, −7.06° (CALC-M5-04 400 mm, +0.1 %); fused 3.8 mm, −0.16° (run 1: 2.4 mm, −0.12°); AMCL rest max 21.3 mm, moving P95 19.4 mm; one `odom → base_footprint` writer (the EKF, 50 Hz); clean shutdown.
  - Finding: the fused heading error is larger than the CALC-M6-04 estimate (0.02° from the odometry weight + 0.07° gyro random walk) but within the 0.5° bound. Not investigated further (the bound is met with margin ×3); candidate causes are the EKF's default process noise and the IMU's own noise model.
- 2026-11-20, TEST-M6-07 on `19200ee`: FAIL (attempt 1, the EKF dropped its `get_parameters` reply just after start-up; checker defect TS-047; every measure passed in every run). Fix: the query is repeated while there is no reply. R1 on `c2b6805`: PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6 Task D). Task D complete. Next: Task E.
- 2026-11-20, Task E started. Tooling: `TEST-M6-11_consistency_check.py` (configuration vs DEC-043 and DEC-055 to DEC-063, records under DEC-041, evidence index, automation) and its mutation check (every one of 18 injected faults detected); `m6` suite in `tools/run_suite.py`; TEST-M6-11 joins the `records` suite and TEST-M6-08 the `ci` suite (`ci.yml` labels updated); `TEST-M6-08_distort.py` prints a runner `# overall:` line. The new checker's first run found DEC-041 violations from Tasks A, C and D (run counts restated on result lines in a changelog and this record) and the missing TEST-M6-07 traceability entry; corrected. The first mutation set missed one fault because TEST-M6-07 has two execution records; that mutation now targets a single-record test.
- 2026-11-20, TEST-M6-09 (Task E): FAIL, then R1 PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6 Task E). The first GUI `regression` run was stopped when I switched regression re-tests to headless; its TEST-M2-04 FAIL diagnosed TS-048. Headless suites: TEST-M4-12 and TEST-M5-10 failed on batch evidence not yet indexed (TS-043 class), and TEST-M5-01 on M6's approved dependencies (TS-049). The user chose DEC-064: identity tests check only their own milestone's increment. TEST-M6-01's list gained Task D's `robot_localization`. TEST-M6-11 checks DEC-064, and its mutation check now covers it.
- 2026-11-20, TEST-M6-10 (Task E): PASS, observed by me ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6 Task E). The global-localization demonstration (DEC-058) locked onto one cluster rotated by a half turn and was not corrected. The TEST-M6-11 checker rejected the CLAUDE.md label "observed by me" in status cells (checker too strict, found before its formal run); corrected.
- 2026-11-21, `m6` suite run (Task E, tag M611): TEST-M6-04 FAIL, one run over DEC-063's recovery bound. A 10-run characterization with the product settings followed (`TEST-M6-04-char10_review.log`); with the earlier runs it showed a wider spread than DEC-063's 4 dry runs, and that the start error does not predict recovery. User decision DEC-065: the bound is restated (DECISIONS.md), AMCL unchanged. TEST-M6-04 R1 follows.
- 2026-11-21, TEST-M6-04 R1 (Task E): PASS under DEC-065. One run came close to the restated bound, which is recorded in TEST_RESULTS.md and for review at closeout.
- 2026-11-21, TEST-M6-11 (Task E): PASS, including CI with records ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M6 Task E). Every M6 acceptance test has a PASS on record; closeout review next.
- 2026-11-21: **M6 closed**, with the DEC-065 margin accepted as a known risk. TEST-M6-01's `END` is set to the closeout commit (DEC-064).

## 13. Known limitations and carried items (at closure, 2026-11-21)
- **Wrong-start recovery margin (DEC-065):** in one TEST-M6-04 R1 run, recovery came close to the restated bound. The user accepted this as a known risk at closure. Re-measure with at least 10 runs if AMCL's motion or sensor model changes in M7.
- **Global localization is not reliable in this arena:** the TEST-M6-10 demonstration locked onto a pose rotated by a half turn and never corrected (DEC-058: demonstration only). M7 must start from a known or user-given pose.
- **TS-045 workaround in use:** AMCL reads a half-cell-shifted map copy on `/map_amcl` (DEC-062); every other consumer, including Nav2 costmaps in M7, keeps `/map`. Upstream report [ros-navigation/navigation2#6833](https://github.com/ros-navigation/navigation2/issues/6833). Remove the copy only if an upstream fix lands and is verified, and coordinate with TS-041 (the opposite SLAM Toolbox error).
- **Fusion is selectable, not the default (DEC-057):** `ekf:=true` with `controllers_ekf.yaml`. The fused heading error was sometimes above the CALC-M6-04 estimate (TEST-M6-07 observation, not investigated).
- **Gallery media** for TEST-M6-02 to -07 and TEST-M6-10: added on 2026-11-21, after the closure ([`docs/gallery/M6/`](../gallery/M6/)).
