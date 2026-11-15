# M5 — SLAM (Mapping): Milestone Plan and Record

**Status:** **Complete** (2026-11-15; closed; in progress since 2026-11-15). Every exit criterion in §11 is met: TEST-M5-01 to -10 PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M5); OPEN-23 to -27 decided (DEC-047 to DEC-051); reference map committed (DEC-054, DEC-055); TEST-M5-10 and CI green. Carried forward: loop-closure verification (DEC-052) and the map-origin correction for new maps (TS-041). History: plan **finalized on 2026-11-15** with all five §4 recommendations (OPEN-23 to -27 = DEC-047 to DEC-051); mapping world DEC-046. The arena layout (CALC-M5-01) and the bounds (CALC-M5-03) are **Selected** with the plan; the route waypoints are fixed in Task B (CALC-M5-02). History: drafted as Proposed on 2026-11-15 (`8073372`). Values are labelled per `docs/README.md`.

**Record rule (DEC-041):** test results live only in `TEST_RESULTS.md`. This record and `test_plan.md` link to them and do not restate the numbers.

## 1. Purpose
M4 showed that odometry is accurate in the short term but, like all dead reckoning, its error is never corrected. M5 adds the first component that **corrects** it and the first **map** of the environment:
- **Mapping.** SLAM Toolbox builds a 2D occupancy-grid map from the LiDAR (`/scan`) while the robot drives.
- **Correction.** It publishes `map → odom`, so that `map → base_footprint` stays accurate even when `odom → base_footprint` drifts (REP-105; DEC-016 assigns `map → odom` to M5/M6).
- **A saved map.** The map is saved and reloadable. M6 localizes on it, and M7 plans on it.
- **Measured quality.** The map is checked against the world file it was built in, not judged by eye.

*Concept: SLAM (Simultaneous Localization and Mapping).* The robot does not know the map, and it cannot localize without one. SLAM solves both together. SLAM Toolbox is **graph-based**:
- each processed scan becomes a **node** (a pose and its scan);
- **scan matching** aligns a new scan with recent ones and gives an **edge** (a measured relative pose) that corrects the odometry guess;
- when the robot returns to a place it has seen, a **loop closure** adds an edge between distant nodes, and an optimizer (Ceres) adjusts every pose so that all edges agree. This removes the drift accumulated around the loop.

The map is then drawn from the optimized poses: each cell holds the probability that it is occupied (`/map`, `nav_msgs/OccupancyGrid`; saved as `.pgm` + `.yaml`).

*Concept: `map → odom`.* The odometry frame `odom` is smooth but drifts. The `map` frame is globally correct but can jump when a correction arrives. SLAM publishes the offset between them, so consumers that need smoothness (the controller, short-term motion) use `odom`, and consumers that need global correctness (planning, M7) use `map`.

## 2. Scope
Derived from ROADMAP § M5 (SLAM Toolbox, map building, mapping test, save map), ros_architecture.md (M5/M6 row), frames_and_tf.md (DEC-016: `map → odom` from M5/M6), DEC-046 and DEC-041.

**In scope:**
| Item | Source |
|---|---|
| Mapping test world: an enclosed arena with known geometry (DEC-046) | ROADMAP M5 ("mapping test"); DEC-046 |
| SLAM Toolbox online mapping: configuration, launch, `/map`, TF `map → odom`, sim time | ROADMAP M5 |
| Quantitative map and pose accuracy against the world file and Gazebo ground truth | ROADMAP M5 ("mapping test") |
| Saving the map (and reloading it identically); the reference map for M6 | ROADMAP M5 ("save map") |
| Robustness: mapping with the TEST-M4-09 injected odometry errors | §1 (correction) |
| Checker sensitivity: distorted maps must fail | M4 practice (TEST-M4-09) |
| RViz live mapping view; `m5` runner suite; GPU-free checks in CI; M1–M4 regression | DEC-040, DEC-041 |

**Out of scope:**
- Localization on a saved map (AMCL or SLAM Toolbox localization mode): M6.
- IMU/odometry fusion (EKF): M6.
- Nav2, costmaps, autonomous exploration: M7, M8.
- The factory/warehouse world: M9 (ros_architecture.md: "after M7"). The arena is a test fixture, not the factory.
- Detecting obstacles below the scan plane (M8). M5 only records that such an obstacle is absent from the map.
- Changing the robot model, the sensors, the controller limits or the odometry covariance.

## 3. Analysis (Calculated unless stated otherwise)
Inputs: LiDAR 360 samples (1° spacing), 10 Hz, 0.12–12 m, σ 0.01 m, scan plane 0.230 m above ground (`amr.sensors.xacro`, DEC-030/031); speed limits +0.5 / −0.25 m/s, ±1.0 rad/s (DEC-025); SLAM Toolbox 2.8.5 (installed defaults read from `/opt/ros/jazzy/share/slam_toolbox/config/mapper_params_online_async.yaml`, 2026-11-15): resolution 0.05 m, `minimum_travel_distance` 0.5 m, `minimum_travel_heading` 0.5 rad, `max_laser_range` 20.0 m, `loop_search_maximum_distance` 3.0 m, `loop_match_minimum_chain_size` 10, `base_frame` `base_footprint`, `scan_topic` `/scan`.

### 3.1 CALC-M5-01: arena layout and sensor coverage (layout **Proposed**)
World `mapping_arena.sdf`, world frame = REP-103, robot spawned at the world origin, yaw 0 (the `sim.launch.py` default).
| Item | Geometry (centre, size L × W × H, m) | Purpose |
|---|---|---|
| Perimeter walls | interior x −2.0 … +8.0, y −4.0 … +4.0 (10.0 × 8.0 m); walls 0.2 m thick, 1.0 m high | closed boundary; known dimensions |
| P1 pillar | (2.0, 2.0), 0.3 × 0.3 × 1.0 | small feature; breaks symmetry |
| P2 pillar | (5.0, −2.0), 0.3 × 0.3 × 1.0 | small feature |
| B1 box | (6.5, 2.5), 1.0 × 0.6 × 0.5 | medium feature, lower than the walls |
| W1 partition | x 3.4 … 3.6, y −4.0 … −1.5 (0.2 × 2.5 × 1.0), joined to the south wall | an alcove; two faces; breaks the rectangle's symmetry |
| L1 low box | (0.5, −2.5), 0.4 × 0.4 × 0.15 | **below** the 0.230 m scan plane: must **not** appear in the map |

Checks:
- *Heights:* every feature except L1 reaches above the scan plane (0.5–1.0 m vs 0.230 m). L1 (0.15 m) is 0.08 m below it.
- *Symmetry:* a plain rectangle looks the same after a 180° turn, which can mislead scan matching. P1, P2, B1 and W1 are placed asymmetrically.
- *Range:* the arena diagonal is 12.8 m, more than the 12 m range, but from any route point at least 1 m inside the walls the farthest wall point is ≤ 11.4 m away (worst case: (−1, −3) to the corner (8, 4), √(9² + 7²) = 11.40 m). Every wall is in range from most of the route.
- *Beam spacing:* 1° gives d·0.01745 m between beams on a perpendicular wall: 0.087 m at 5 m, 0.175 m at 10 m. A single scan therefore hits only every 2nd–4th 0.05 m cell of a far wall; scans from many poses fill the wall. This is one reason the completeness criterion is 90 %, not 100 %.
- *Noise:* σ 0.01 m is 1/5 of a cell; it blurs wall cells by at most one cell.

### 3.2 CALC-M5-02: route (waypoints **Selected**, finalized 2026-11-15 in Task B; owner `docs/evidence/M5/TEST-M5_route.py`)
- One closed loop of about 25–30 m that returns to the start, visits the alcove behind W1, passes every feature at 1.0–3.0 m, and keeps ≥ 0.8 m between the robot footprint (0.510 × 0.435 m, swept radius 0.385 m, CALC-M1-13) and any obstacle.
- Stop-and-turn: straight legs at 0.25 m/s (half the DEC-025 limit, to keep scans dense), turns in place at 0.5 rad/s, a 1 s settle at each waypoint (a rest point for the pose check, §3.4).
- Scan-node spacing with the default thresholds: one node per 0.5 m or 0.5 rad (28.6°): about 50–60 nodes on the loop, enough for the 10-node loop-closure chain.
- Duration: 30 m / 0.25 m/s = 120 s straight + about 10 turns × π/2 / 0.5 rad/s ≈ 31 s + settles: about 3 min of simulated time per run.
- **Selected route (Task B, 2026-11-15):** waypoints (0, 0) → (6.5, 0) → (6.5, −2.6) → (6.5, 0.9) → (4.1, 0.9) → (4.1, 2.7) → (4.1, 0.6) → (−0.6, 0.6) → (−0.6, 2.6) → (−0.6, 0) → (0, 0); the values live in `TEST-M5_route.py`, which also checks them against the obstacles read from the world file (`python3 -I docs/evidence/M5/TEST-M5_route.py`). *Calculated:* 28.8 m, 9 turns (1080° turned, net +360°; 180° turns made to the left), about 163 s of simulated time, about 95 scan nodes; the alcove east of W1 is entered (W2); tightest footprint gap 0.865 m (P1; required 0.8 m); features passed at 1.25–2.30 m (L1 at 2.30 m). P1, B1 and P2 are too close to the walls for the 1.185 m centre clearance to drive round them, so the route reaches those areas with out-and-back spurs (W2, W5, W8) inside the one closed loop.

### 3.3 CALC-M5-03: map-accuracy measures and bound rationale (bounds: OPEN-23)
The true geometry is read from `mapping_arena.sdf` by the checker (one source of truth). The map frame starts at the robot's first pose (the spawn pose = world origin), so the map and world coordinates coincide without fitting; Task A verifies this. A best-fit alignment is reported as INFO only.
- *Quantization:* a cell centre is at most half a cell diagonal (0.035 m) from the true surface it represents.
- *Pose error to wall error:* a 1° heading error moves a wall seen at 6 m by 0.105 m.
- Hence the proposed bounds: **wall accuracy** P95 ≤ 0.10 m (2 cells, about 3× quantization); **pose** ≤ 0.05 m (1 cell) and ≤ 1.0°, consistent with 0.10 m of wall error at mid range.
- *Ghost walls* (occupied cells far from any surface): ≤ 0.5 % beyond 0.25 m (5 cells); allows isolated noise cells, rejects a doubled wall.
- *Completeness:* ≥ 90 % of 0.05 m-spaced samples on the surfaces visible from the route have an occupied cell within 0.10 m (beam spacing and occlusion, §3.1).
- *Dimensions:* the interior measured from line fits to the four wall bands: 10.0 × 8.0 m within ± 0.10 m; opposite walls parallel and adjacent walls perpendicular within 1.0°. This is the human-readable form of the same accuracy.

### 3.4 CALC-M5-04: pose and drift measurement
- *Ground truth:* the `amr` pose from Gazebo `/world/mapping_arena/pose/info` (the M2/M4 reader, parameterized by world name).
- *SLAM pose:* TF `map → base_footprint` at the same rest point (after the settle), as in M4 §3.4.
- *Odometry pose:* TF `odom → base_footprint` at the same rest point. Its difference from ground truth is the drift that SLAM has to remove (TEST-M5-06).
- *Robustness prediction (CALC-M4-02):* with the separation × 1.02 override, the odometry yaw error is −1.96 % of the total rotation. For a loop with about 450–720° of turning that is 9–14° by the end, i.e. metres of position error after the following legs: far beyond the 0.05 m / 1° pose bound. The exact value is calculated for the final route in Task B, before the TEST-M5-06 runs.
- *Calculated for the Selected route (Task B, 2026-11-15; `TEST-M5_route.py`):* the yaw error follows the **net signed** rotation, not the total turned angle, because left and right turns cancel; the route's net rotation is +360°. Predicted odometry error at the end (truth back at (0, 0)): separation × 1.02: 0.400 m and −7.06°; separation × 1.02 with both radii × 1.01: 0.198 m and −3.53°. The earlier "metres" estimate does not hold for this loop. Both exceed 3× the pose bound (0.15 m, 3°), the combined case only narrowly; to be reviewed before Task D (TEST-M5-06).

## 4. Design items (**decided 2026-11-15**: OPEN-23 = DEC-047, OPEN-24 = DEC-048 (a), OPEN-25 = DEC-049 (a), OPEN-26 = DEC-050 (a), OPEN-27 = DEC-051 (b); each as recommended)
| ID | Item | Options | Recommendation (Proposed) |
|---|---|---|---|
| — | Mapping world | **Decided 2026-11-15 (DEC-046):** (a) purpose-built enclosed arena; not (b) an early factory layout (M9 scope) or (c) the M3 sensor world (open, few features) | — |
| OPEN-23 | Map and pose accuracy bounds | the §3.3 proposal (wall P95 ≤ 0.10 m, ghosts ≤ 0.5 %, completeness ≥ 90 %, dimensions ± 0.10 m and 1.0°, pose ≤ 0.05 m and 1.0°), or other bounds | the §3.3 proposal: tied to the 0.05 m cell and the sensor geometry. Like M4, they are expected to pass with margin in simulation; TEST-M5-07 shows they can fail |
| OPEN-24 | SLAM Toolbox mode and parameters | (a) **online async** (processes the newest scan, drops scans it cannot keep up with; the usual live mode), installed defaults except `max_laser_range` 12.0 and `min_laser_range` 0.12 (the sensor limits); (b) **online sync** (queues and processes every qualifying scan; more repeatable, can lag), same parameters; (c) tuned thresholds (e.g. node spacing 0.2 m) | **(a)**. M6/M7 run live, so test the live mode. At one node per 0.5 m the processing load is low, so drops are unlikely; TEST-M5-02 logs them. Only the two range values change, both from the sensor specification |
| OPEN-25 | How the test drives the route | (a) a harness waypoint follower steered by **Gazebo ground truth**: the path is identical in every run and with injected odometry errors; (b) steered by **odometry**: realistic, but an injected error moves the path (collision risk near walls); (c) driving by teleop: not repeatable | **(a)**. The system under test is SLAM, not the driver; the same path makes runs comparable. (c) is used only for the demonstration |
| OPEN-26 | Launch structure | (a) a new `slam.launch.py` that starts only SLAM Toolbox with `config/slam_toolbox.yaml`, run beside `sim.launch.py sensors:=true world:=mapping_arena.sdf`; `sim.launch.py` unchanged; (b) a `slam:=true` argument on `sim.launch.py`; (c) one all-in-one mapping launch | **(a)**. M1–M4 behaviour cannot change (default launch untouched); M6 swaps SLAM for localization without touching the simulation launch |
| OPEN-27 | Map artefacts kept | (a) `.pgm` + `.yaml` only (Nav2 `map_saver_cli` format); (b) also the SLAM Toolbox serialized pose graph (`.posegraph` + `.data`), which SLAM Toolbox localization mode needs | **(b)**, if the pose graph stays small (checked in Task C; limit about 5 MB, otherwise (a) and record why). It keeps both M6 options open: AMCL on the image map, or SLAM Toolbox localization |

## 5. Entry criteria and dependencies
- M4 complete (2026-11-13): ✅. Odometry is verified and has a covariance (DEC-042).
- M3 sensors verified (LiDAR `/scan`, TEST-M3-05/-06): ✅.
- SLAM Toolbox 2.8.5 and `nav2_map_server` 1.3.13 installed (`docs/environment.md`): ✅. Installed is not integrated (ros_architecture.md); Task A checks integration first.
- The plan is finalized and OPEN-23 to -27 are decided: ✅ 2026-11-15 (DEC-047 to DEC-051).

## 6. Architecture
```
amr_bringup/
  worlds/mapping_arena.sdf          the arena (CALC-M5-01); its <world name> is mapping_arena
  config/slam_toolbox.yaml          installed online-async defaults + the OPEN-24 changes, each commented
  launch/slam.launch.py             SLAM Toolbox (async node), use_sim_time, params file argument
  rviz/mapping.rviz                 fixed frame map: /map, /scan, robot model, TF, odometry trail
  maps/mapping_arena.{pgm,yaml}     reference map for M6 (+ .posegraph/.data per OPEN-27)
docs/evidence/M5/
  TEST-M5_map_run.py                harness: route follower (OPEN-25), rest-point SLAM/odometry/truth poses, map save
  TEST-M5_map_check.py              offline checker: world SDF -> true surfaces; saved map -> CALC-M5-03 measures (CI)
  TEST-M5-07_distort.py             distorted copies of a recorded map for the checker-sensitivity test (CI)
  TEST-M5-10_consistency_check.py   record and configuration checker (DEC-041)
tools/run_suite.py                  + 'm5' suite; TEST-M5-07 to 'ci', TEST-M5-10 to 'records'
```
Data path: Gazebo `gpu_lidar` → bridge `/scan` → SLAM Toolbox ← TF `odom → base_footprint` (`diff_drive_controller`, M4) and `base_footprint → laser_frame` (`robot_state_publisher`); SLAM Toolbox → `/map`, TF `map → odom`. Unchanged: the robot model, the sensors, the controllers, `sim.launch.py`.

## 7. Task breakdown (finalized 2026-11-15)
| Task | Objective and deliverables | Tests | Depends on |
|---|---|---|---|
| **A: World, SLAM launch and integration gate** | `mapping_arena.sdf`, `slam_toolbox.yaml`, `slam.launch.py`, `mapping.rviz`. Gate (scratch, before any formal run): SLAM starts on sim time; `/map` appears; one `map → odom` publisher; the map frame equals the world frame at start; RTF with GUI + LiDAR + SLAM; dropped scans | TEST-M5-01, -02 | Plan finalized; OPEN-24, -26 |
| **B: Harness and checker** | Route waypoints and clearance check (CALC-M5-02), route follower (DEC-049: proportional heading and distance control on Gazebo ground truth, with speed and turn-rate limits; no I or D term, because the simulation has no steady disturbance to integrate away and D would amplify pose noise), pose recorder, map save; offline map checker reading the SDF; distortion tool; dry runs; CALC-M5-04 robustness prediction for the final route | (TEST-M5-07 moved to Task C, 2026-11-15) | A; OPEN-23, -25 |
| **C: Mapping accuracy and saved map** | Formal mapping runs (3), map and pose evaluation, save/reload, reference map committed; checker sensitivity on the reference map | TEST-M5-03, -04, -05, -07 | B; OPEN-27 |
| **D: Robustness and closeout** | Injected-odometry-error mapping, regression, RViz observation, consistency checker, `m5` suite and CI, records | TEST-M5-06, -08, -09, -10 | C |

## 8. Tests (criteria Accepted: DEC-047, 2026-11-15)
Procedures: `test_plan.md` §10; evidence: `docs/evidence/M5/`. Launch: `sim.launch.py sensors:=true world:=mapping_arena.sdf` + `slam.launch.py`. Gazebo tests run 3 times and every run must pass; runs with RTF < 0.5 are invalid; interactive runs show the Gazebo GUI and RViz (`SHOW=1`). A TS-029 shutdown hang is handled under DEC-039.
| Test | Requirement | Method | Proposed criterion |
|---|---|---|---|
| TEST-M5-01 | REQ-M5-09 | Build; M1 default expansion byte-identical; launch-model expansions, `sim.launch.py`, `controllers.yaml`, `amr.sensors.xacro`, `amr_properties.xacro` unchanged since M4 (`517608f`); changes to existing files | Build clean; M1 default expansion and the M2 and M3/M5 launch-model expansions byte-identical to M4; `sim.launch.py`, `controllers.yaml`, `amr.sensors.xacro`, `amr_properties.xacro` unchanged; existing files otherwise changed only by the `slam_toolbox` dependency line in `amr_bringup/package.xml` and comment lines (DEC-053) |
| TEST-M5-02 | REQ-M5-02, -03 | Interface: SLAM node active on sim time; `/scan` subscribed; `/map` type, frame `map`, resolution 0.05 m; exactly one TF publisher of `map → odom`; complete tree `map → odom → base_footprint → … → laser_frame`; processed/dropped scan count logged | All hold |
| TEST-M5-03 | REQ-M5-01, -04 | Map accuracy: drive the route, save the map, run the checker | OPEN-23 map bounds; L1 absent (zero occupied cells in its footprint) |
| TEST-M5-04 | REQ-M5-05 | Pose: `map → base_footprint` vs ground truth at every rest point and at the end (same runs as TEST-M5-03) | ≤ 0.05 m and ≤ 1.0° at every rest point |
| TEST-M5-05 | REQ-M5-06 | Save and reload: `map_saver_cli` writes `.pgm`/`.yaml`; `map_server` reloads it; the served grid equals the file; the pose graph is serialized (OPEN-27) | Identical grid (cell by cell, resolution, origin); files committed |
| TEST-M5-06 | REQ-M5-07 | Robustness: TEST-M5-03/-04 with the TEST-M4-09 overrides (separation × 1.02; both radii × 1.01) through `controllers_file:=` | The map and pose criteria still hold, while the odometry drift at the end exceeds 3× the pose bound and agrees with the CALC-M5-04 prediction within ± 25 % |
| TEST-M5-07 | REQ-M5-08 | Checker sensitivity (offline, CI): the recorded map passes; copies rotated 2°, shifted 0.15 m, scaled × 1.02, with one wall erased, and with a ghost wall each FAIL | 1 PASS, 5 FAIL, each on the expected measure |
| TEST-M5-08 | REQ-M5-09 | Regression through the runner: static and regression suites, M4 suite | All PASS |
| TEST-M5-09 | REQ-M5-11 | RViz `mapping.rviz` during a mapping run (observed by me): the map grows, walls are straight and single, the robot returns to the start with no visible misalignment, no unexplained TF jumps (loop-closure edges noted if seen, not required; DEC-052) | Observed by me |
| TEST-M5-10 | REQ-M5-10 | Consistency checker (DEC-041), `m5` suite, TEST-M5-07 and -10 in CI | Zero mismatches; CI PASS |

## 9. Requirements (owner: `docs/requirements.md` § M5, from 2026-11-15; this list is the original draft)
| ID | Requirement |
|---|---|
| REQ-M5-01 | A mapping world with known geometry (DEC-046), including a feature below the scan plane |
| REQ-M5-02 | SLAM Toolbox maps online from `/scan` and the odometry TF, on sim time, and is the only publisher of `map → odom` |
| REQ-M5-03 | The map is published on `/map` (`OccupancyGrid`, frame `map`, 0.05 m) |
| REQ-M5-04 | Map accuracy within the OPEN-23 bounds |
| REQ-M5-05 | Pose accuracy during mapping within the OPEN-23 bounds |
| REQ-M5-06 | The map is saved (OPEN-27), reloads identically, and is committed as the M6 reference map |
| REQ-M5-07 | Mapping stays within bounds with the TEST-M4-09 odometry errors injected |
| REQ-M5-08 | The map checker detects distorted maps |
| REQ-M5-09 | M1–M4 behaviour unchanged |
| REQ-M5-10 | Records consistent under DEC-041; `m5` suite; GPU-free checks in CI |
| REQ-M5-11 | Live mapping visible in RViz |

## 10. Risks
- *An ideal simulation makes SLAM look perfect.* Mitigation: TEST-M5-06 (real drift injected) and TEST-M5-07 (bad maps fail).
- *Symmetric or featureless geometry misleads scan matching* (wrong loop closure). Mitigation: asymmetric features (§3.1); the dimension and ghost-wall checks catch a wrong closure.
- *Low RTF with GUI + `gpu_lidar` + SLAM.* Mitigation: measured in the Task A gate; sim-time evaluation; RTF < 0.5 invalid; headless fallback for the formal runs if needed (recorded).
- *Async mode drops scans.* Mitigation: TEST-M5-02 logs them; OPEN-24 (b) is the fallback.
- *TS-029 shutdown hang*, likelier with sensors on and longer runs. Mitigation: DEC-039; if invalid attempts exceed 10 % of launches, the DEC-039 Decision 2 trigger applies.
- *The map frame differs from the world frame* (spawn offset). Mitigation: checked in the Task A gate; the checker reports a best fit as INFO.
- *Large pose-graph files.* Mitigation: OPEN-27 size limit.
- *Limitation: loop closure is not separately verified in M5* (DEC-052). In this arena a wall is always in range, so scan matching removes drift at each turn and the tests cannot tell a loop closure from scan matching. Deferred to a larger or corridor environment.

## 11. Exit criteria
M5 is complete only when:
- TEST-M5-01 to -10 are PASS, with results in `TEST_RESULTS.md` and evidence in `docs/evidence/M5/`; failures kept, with TS entries and re-tests.
- OPEN-23 to -27 are decided in `DECISIONS.md`.
- The reference map is committed, and the configuration, documents and checker agree (TEST-M5-10); CI is green.
- The records are updated and the M5 Tasks are Done.

## 12. Implementation record
- 2026-11-15: mapping world decided (DEC-046, option A). Plan drafted as Proposed, pending the OPEN-23 to -27 decisions.
- 2026-11-15: question considered: could a PID controller correct the odometry errors? Answer recorded here: feedback control trusts its own measurement, so it cannot remove an error in that measurement (drift); drift needs an outside reference (SLAM in M5, localization and fusion in M6) and systematic errors need calibration. Feedback control is used where it fits: the Task B route follower (DEC-049).
- 2026-11-15: plan finalized with all five recommendations (DEC-047 to DEC-051); Tasks A–D defined.
- 2026-11-15, Task A: `worlds/mapping_arena.sdf` (`gz sdf -k`: valid), `config/slam_toolbox.yaml` (the installed online-async file with trailing spaces removed; `diff -b` against it shows only the two DEC-048 range lines), `launch/slam.launch.py` (includes the installed `online_async_launch.py`, which drives the lifecycle node through configure and activate), `rviz/mapping.rviz` (map, scan, pose-graph markers, odometry trail, TF). `package.xml` gains `exec_depend slam_toolbox`; this is the only edit to an existing file besides a CMake comment, so the original TEST-M5-01 wording "only new files" was not met literally. This reading was first written here without a recorded decision; it was raised before the test was recorded, and the restated criterion was accepted as DEC-053.
- 2026-11-15, Task A integration gate (scratch, Gazebo GUI + RViz shown; not a formal test): SLAM Toolbox activated and registered the LiDAR; `use_sim_time` true; `/map` `OccupancyGrid` from `slam_toolbox`, 0.05 m, 201 × 161 cells from the first scan (the whole arena is in range from the spawn point); `map → odom` identity at start, so the map frame starts on the world frame; RTF 1.00 with GUI, `gpu_lidar` and SLAM; no dropped-scan messages in the SLAM log; `/tf` publishers `robot_state_publisher`, `diff_drive_controller`, `slam_toolbox`. A 20.5 m open-loop demo rectangle (`tools/demo_drive.py`) ended within about 5 mm of ground truth in `map → base_footprint`, with `map → odom` about 5 mm; the low box L1 was absent from the map, and the areas behind P2 and inside the alcove stayed partly unknown because that rectangle did not enter the alcove (the Task B route does). Finding for TEST-M5-02: `tf2_monitor` cannot name the `map → odom` broadcaster in ROS 2 ("no authority available"), so the test must identify publishers itself (per-message publisher GID on `/tf`).
- 2026-11-15, loop-closure spike (scratch, shown live; not a formal test, nothing kept): two laps of a 5.3 × 3 m rectangle (33 m, 8 turns) with `wheel_separation_multiplier` 1.02, SLAM `max_laser_range` 12 m and 3 m. Odometry ended 0.60 m / 14.1° off in both runs. SLAM error vs ground truth: 12 m median 0.004 m, worst 0.015 m, end 0.004 m / 0.07°; 3 m median 0.028 m, end 0.064 m / 0.08°, and the south strip of the arena was never mapped. In both runs `map → odom` corrected about 1.8° at each turn (the injected error per turn), adding up to 14.2°; no single correction on return to the start. Conclusion: scan matching, not loop closure, removes the drift here, and a 3 m case would not exercise loop closure either. Decided as DEC-052.
- 2026-11-15, TEST-M5-01: procedure `docs/evidence/M5/TEST-M5-01_procedure.sh` written and run; criterion restated by DEC-053 before the result was recorded. Result in `TEST_RESULTS.md`.
- 2026-11-15, TEST-M5-02 procedure (`TEST-M5-02_procedure.sh`, `TEST-M5-02_interface_check.py`): two scratch dry runs (headless, not formal) found TS-038 (`min_laser_range` is not a SLAM Toolbox parameter; DEC-048 note) and a check that read parameters before the first scan. Both fixed in the procedure before the formal run. rclpy (Jazzy) gives no publisher GID per message, so the single `map → odom` publisher is shown with the per-writer publication sequence number and a before/after comparison of the `/tf` publishers (checker header).
- 2026-11-15, Task A complete: TEST-M5-01 and TEST-M5-02 recorded in `TEST_RESULTS.md` (TEST-M5-02: first run FAIL on a shutdown exit code, TS-039; procedure hardened; R1). Task B next.
- 2026-11-15, Task B started: route module `TEST-M5_route.py` (waypoints, clearance and feature-distance checks against the world file, CALC-M5-04 prediction); route finalized (Selected).
- 2026-11-15, Task B tooling: `TEST-M5_map_run.py` (route follower, DEC-049: gains K_TURN 2, K_HEAD 2, K_DIST 1 (Selected, tuned in dry runs); rest-point poses to CSV; cross-track abort 0.30 m; exit codes 0, 1 and 2 for pass, fail and invalid), `TEST-M5_map_check.py` (CALC-M5-03 measures; no ROS), `TEST-M5_procedure.sh` (mapping run, map and pose-graph save, teardown, checker), `TEST-M5-07_distort.py` (five distorted copies). Two scratch dry runs (GUI shown, not recorded, not formal results):
  - dry run 1: attempt 1 RTF 0.37 (invalid; GUI start-up), attempt 2 RTF 0.95; harness PASS in both; attempt 1 map passed the checker; `map_saver_cli` exited 1 in attempt 2 and did not reproduce (3 of 3 saves by hand; the procedure now keeps the saver's full output on failure); `serialize_map` failed in both because the procedure joined `$PWD` to an absolute path (fixed: `realpath`).
  - dry run 2: every step PASS (RTF 0.97; map 9.987 × 7.986 m, P95 0.069 m, completeness 99.8 %; shutdowns CLEAN).
  - Pose-graph size (OPEN-27, DEC-051): 6.9 MB right after SLAM starts and 7.4 MB `.posegraph` + 0.47 MB `.data` after the route, above the about 5 MB limit; gzip -9 gives 0.33 + 0.23 MB. Decision for Task C.
  - Distortion tool: without padding, a × 1.02 scale pushed the east and north walls off the cropped image and failed for the wrong reason; copies are now padded with 1 m of unknown cells (occupied-cell count printed per copy). On the dry-run map all five copies fail their measure; nearest-neighbour resampling makes the 2° rotation measure 1.1–1.8°, and the × 1.02 scale is caught mainly by the width (length 14 mm over its tolerance).
  - Checker limitation: the 5 cm grid can bias a fitted wall line by up to one cell (an ideal synthetic map measured 9.946 × 7.947 m).
- 2026-11-15, wall-accuracy spread between the dry-run maps (P95 0.041 vs 0.069 m), analysed per surface (scratch analysis; no bound changed): every wall-cell distance takes only a few discrete values, set by where the true surface falls inside a 0.05 m cell. That position depends on the map origin, which SLAM places from the first scan and which differed by about 2 cm between runs (x −2.034 vs −2.056 m). Walls are mapped 1–2 cells thick (endpoint noise near a cell boundary), and P95 moves by one cell (0.05 m) when the second layer exceeds 5 % of the cells: dry run 1 had layers at 0–0.01 and 0.037–0.041 m; dry run 2 at 0.019–0.023 and 0.069–0.073 m (the second layer on the south and west walls). So CALC-M5-03's 0.035 m quantization holds for one layer only; with two layers the quantization alone reaches about 0.025 + 0.05 = 0.075 m, leaving about 0.025 m of the 0.10 m bound for real mapping error. The spread is not random noise: a third layer or a real error of about 2.5 cm is needed to fail. Watched in the Task C formal runs; the per-surface breakdown is the diagnostic if one fails. *Correction (2026-11-15):* part of this spread is a uniform half-cell shift of SLAM Toolbox maps (TS-041), not only grid phase; with the shift corrected, P95 of the TEST-M5-03 maps is 0.040–0.045 m.
- 2026-11-15, TEST-M5-07 moved from Task B to Task C: its input is the Task C reference map `amr_bringup/maps/mapping_arena.yaml` (after TEST-M5-05), also used in CI, so every result comes from a formal run and no dry-run map is committed. Task B complete: tooling written, dry run 2 passed every step.
- 2026-11-15, Task C started. DEC-054: the reference pose graph is committed gzip-compressed (amends DEC-051). Reference map rule fixed before the formal runs: the map of TEST-M5-03 attempt 1 (the recorded attempt) becomes `amr_bringup/maps/mapping_arena`, whatever its scores, provided the run passes. The mapping procedure writes pose graphs to `PG_DIR` (not the evidence folder).
- 2026-11-15, TEST-M5-03 and TEST-M5-04 run (3 valid attempts, GUI shown, attempt 1 recorded); results in `TEST_RESULTS.md`. Next: TEST-M5-05 (reference map from attempt 1, reload, compressed pose graph), then TEST-M5-07.
- 2026-11-15, reference map committed (`amr_bringup/maps/mapping_arena.*`, pose graph gzip-compressed, DEC-054; no install rule, M6 adds it). TEST-M5-05 run; TS-040 (`ros2 run` and SIGINT) found in its dry run and fixed. Result in `TEST_RESULTS.md`. Next: TEST-M5-07 on the reference map.
- 2026-11-15, TS-041 (half-cell map shift) found from a review note; DEC-055: reference map origin corrected. TEST-M5-07 run (uncorrected map, kept), then TEST-M5-05 R1 and TEST-M5-07 R1 on the corrected map; results in `TEST_RESULTS.md`. **Task C complete** (TEST-M5-03, -04, -05, -07 PASS). Next: Task D.
- 2026-11-15, Task D started. CALC-M5-04 review before TEST-M5-06 (as planned in §3.4): the combined TEST-M4-09 overrides predict 0.198 m and −3.53° at the end, 1.32× and 1.18× the 3× pose bound. Kept unchanged: the same overrides matched their predictions within about 0.1 % in TEST-M4-09 R1 (−7.19° measured vs −7.20° predicted), because simulated wheels do not slip, so the margins are far larger than the prediction uncertainty. Tooling: `TEST-M5-06_procedure.sh` (builds the test-only controllers file as TEST-M4-09 did, runs the mapping procedure with it, then the drift check; product file checked unchanged) and `TEST-M5-06_drift_check.py` (fails on the TEST-M5-03 log, which has no drift, as a check of the check).
- 2026-11-15, TEST-M5-06 run (3 valid attempts, GUI shown, attempt 1 recorded); result in `TEST_RESULTS.md`. With the injected error the SLAM pose error is larger than without it (up to 35 mm vs 13.5 mm) and still within the bound.
- 2026-11-15, TEST-M5-09 run on `7f3d65b` and observed by me (one laptop screen, windows overlapping; no layout step); result in `TEST_RESULTS.md`. I noted that the W1 partition is mapped from both sides (two faces, unknown interior), which is the expected picture of a solid wall (§3.1), not a doubled wall. With TEST-M5-09 every M5 test (TEST-M5-01 to -10) has a PASS record; §11 exit criteria met.
- 2026-11-15, **M5 closed**; Task D complete. Next: M6 — Localization (plan first).
