# M7 — Autonomous Navigation (Nav2): Milestone Plan and Record

**Status:** **Approved** (2026-11-21, with all nine §4 recommendations: OPEN-33 to -41 = DEC-066 to DEC-074). The bounds (DEC-073) and the goal set (DEC-074; values finalized in Task B) are **Selected** by that approval. **M7 complete (2026-11-23; closed):** Tasks A–D done, TEST-M7-01 to -10 PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M7); known limitations in §13. History: drafted as Proposed on 2026-11-21 (`787bb50`). Values are labelled per `docs/README.md`; every number in §3 is **Calculated** from the sources named there unless stated otherwise.

**Record rule (DEC-041):** test results live only in `TEST_RESULTS.md`. This record and `test_plan.md` link to them and do not restate the numbers.

## 1. Purpose
M6 gave the robot a pose on the saved map. M7 makes it **drive itself to a goal** on that map:
- **Goal navigation.** An operator (RViz) or a program sends a goal pose in the `map` frame; the robot plans a collision-free path on the M5 reference map and follows it to the goal.
- **Safe commands.** The navigation stack drives the robot only through the existing command path (`/cmd_vel`, `TwistStamped`, simulation-time stamps, `cmd_vel_guard`, DEC-026, DEC-029) and within the DEC-025 limits.
- **The real footprint.** Planning and collision checking use the robot's actual outline, including the wheels and the caster overhang (DEC-011, CALC-M1-05).
- **Measured quality.** Arrival accuracy, clearance from obstacles, command limits and localization during navigation are measured against Gazebo ground truth and the world file, not judged by eye.

*Concept: Nav2.* The ROS 2 navigation stack. Its parts, each a separate server (a ROS lifecycle node):
1. **Costmaps.** Grids over the map in which each cell holds a cost from 0 (free) to 254 (lethal). The **global costmap** covers the whole saved map (static layer from `/map`); the **local costmap** is a small rolling window around the robot, updated from `/scan`. An **inflation layer** spreads cost outward from obstacles, so that paths keep away from walls.
2. **Planner server** (global planner). Finds a path through the global costmap from the robot to the goal.
3. **Controller server** (local controller). Converts the path into velocity commands at a fixed rate (default 20 Hz), checking the footprint against the local costmap.
4. **Behavior tree navigator** (`bt_navigator`). Runs a behavior tree (an XML file) that sequences "plan, follow, re-plan, recover" and offers the `NavigateToPose` and `NavigateThroughPoses` actions.
5. **Velocity smoother.** Limits the commanded velocity and acceleration before the commands leave the stack.
6. **Lifecycle manager.** Brings the servers up in order (configure, activate), as in M6.

*Concept: footprint, inscribed and circumscribed radius.* The footprint is the robot's outline in `base_footprint`. The **inscribed radius** is the largest circle around the origin that fits inside it; the **circumscribed radius** is the smallest circle around the origin that contains it, which is also the circle the robot sweeps when it turns in place. A cell closer to an obstacle than the inscribed radius is certainly in collision; one closer than the circumscribed radius may be, depending on heading.

*Concept: action.* A ROS 2 interface for long tasks: the client sends a goal, receives feedback while it runs, and gets a final result (succeeded, aborted, canceled). The goal can be canceled.

## 2. Scope
Derived from ROADMAP § M7 (Nav2, costmaps, global planner, local controller, goal navigation, navigation testing), DEC-011 / CALC-M1-05 (footprint), DEC-029 (Nav2 must publish stamped simulation-time commands), DEC-057 follow-up ("M7 decides whether fusion becomes the default"), DEC-058 (known start pose), DEC-062 (Nav2 uses `/map`, AMCL `/map_amcl`), DEC-041.

**In scope:**
| Item | Source |
|---|---|
| Nav2 servers (planner, controller, behavior tree navigator, velocity smoother, behaviors), configuration, launch, lifecycle start-up on simulation time | ROADMAP M7 ("Nav2") |
| Global and local costmaps on the reference map (`/map`, not `/map_amcl`) with the robot footprint | ROADMAP M7 ("Costmaps"); DEC-062 |
| Global planner (OPEN-35) and local controller (OPEN-34) selection and parameters | ROADMAP M7 |
| Command path: Nav2 → `/cmd_vel` (`TwistStamped`) → `cmd_vel_guard` → `diff_drive_controller`, within DEC-025 | DEC-025, DEC-029 |
| Single goals (`NavigateToPose`) and a multi-pose route (`NavigateThroughPoses`); goal cancel; invalid goals | ROADMAP M7 ("Goal navigation") |
| Arrival accuracy, clearance, command limits and localization during navigation, against ground truth and the world file | ROADMAP M7 ("Navigation testing") |
| Checker sensitivity (wrong results must fail); RViz navigation view; `m7` suite; GPU-free checks in CI; M1–M6 regression | DEC-040, DEC-041; M4–M6 practice |
| The fusion-default decision (OPEN-39) | DEC-057 follow-up |

**Out of scope:**
- Avoiding obstacles that are not in the map, moving obstacles, the collision monitor, keep-out zones and the low-obstacle depth camera: M8 (DEC-037). M7 keeps the local costmap's LiDAR obstacle layer as configured by Nav2, but does not test avoidance.
- The factory world: M9. Docking, stations and pickup/delivery tasks: M10.
- Global localization and start-up without a known pose (DEC-058): M7 starts from the known spawn pose.
- Mapping changes (the M5 reference map is used as committed; its origin correction (TS-041) stays deferred) and AMCL changes (DEC-061 values unchanged; a change would require re-measuring recovery, DEC-065 follow-up).
- Changing the robot model, the sensors, the controller limits (DEC-025) or the command guard.

## 3. Analysis (Calculated unless stated otherwise)
Inputs: chassis 0.450 × 0.350 m, front edge x +0.125 m, rear edge −0.325 m in `base_link` (`amr_properties.xacro`, `chassis_x`); wheels radius 0.075 m, width 0.035 m, track 0.400 m (outer faces y ±0.2175 m); caster radius 0.025 m at x −0.360 m (rear point −0.385 m) (CALC-M1-05, CALC-M1-13); limits +0.5 / −0.25 m/s, ±1.0 rad/s, acceleration 0.5 m/s² (braking 1.0 m/s²), angular 2.0 rad/s² (DEC-025); command timeout 0.5 s (DEC-026, DEC-029); localization bounds (DEC-059); arena and features (CALC-M5-01). `base_footprint` lies directly below `base_link` (DEC-016), so the footprint coordinates are the same in both. Installed (`dpkg-query`, 2026-11-21): `navigation2` and every `nav2_*` package 1.3.14 (including `nav2_regulated_pure_pursuit_controller`, `nav2_mppi_controller`, `nav2_dwb_controller`, `nav2_navfn_planner`, `nav2_smac_planner`, `nav2_velocity_smoother`, `nav2_bt_navigator`, `nav2_behaviors`, `nav2_rviz_plugins`). The installed binaries of the controller server, the velocity smoother and the behaviors contain the `enable_stamped_cmd_vel` parameter (`strings`); installed is not integrated, so Task A verifies the stamped output and its stamps. Installed defaults read from `/opt/ros/jazzy/share/nav2_bringup/params/nav2_params.yaml`: controller MPPI at 20 Hz, `vx_max` 0.5, `vx_min` −0.35, `wz_max` 1.9; planner NavFn; goal checker `xy_goal_tolerance` 0.25 m, `yaw_goal_tolerance` 0.25 rad; costmaps `robot_radius` 0.22 m, resolution 0.05 m, inflation radius 0.70 m, `cost_scaling_factor` 3.0; local costmap 3 × 3 m rolling, voxel layer; velocity smoother `max_velocity` [0.5, 0, 2.0], `max_accel` [2.5, 0, 3.2], `odom_topic` `odom`.

### 3.1 CALC-M7-01: footprint (OPEN-36)
The convex hull of the chassis rectangle, the two wheels and the caster sphere, in `base_footprint`, counter-clockwise from the front left:
`[[0.125, 0.175], [0.075, 0.2175], [-0.075, 0.2175], [-0.325, 0.175], [-0.385, 0.025], [-0.385, -0.025], [-0.325, -0.175], [-0.075, -0.2175], [0.075, -0.2175], [0.125, -0.175]]` (m).
- **Circumscribed radius** 0.386 m (the caster's rear corner, (−0.385, ±0.025)); it matches the M1 swept radius 0.385 m (CALC-M1-13) to rounding. A plain bounding rectangle (x −0.385 … +0.125, y ±0.2175) would give 0.442 m, 15 % more.
- **Inscribed radius** 0.125 m: the front edge. `base_link` sits on the wheel axle, near the front of the chassis, so the robot reaches 0.125 m forward but 0.386 m backward. The default `robot_radius` 0.22 m is therefore wrong in both directions: too large forward, too small backward by 0.166 m.
- *Consequence for planning:* the global planner treats the robot as a point at `base_link` and keeps it out of cells within the inscribed radius of an obstacle. A path can therefore pass where the rear of the robot would touch an obstacle during a turn. The inflation cost (§3.2) keeps paths away from obstacles in practice, and the controller checks the full footprint; the clearance measurement (§3.4) verifies the outcome.

### 3.2 CALC-M7-02: inflation and the arena's passages
- The inflation radius must be at least the circumscribed radius (0.386 m) so that the cost reaches every cell where a turn could touch an obstacle. The installed default 0.70 m meets this.
- Cost with `cost_scaling_factor` 3.0 beyond the inscribed radius: 252 · e^(−3.0 · (d − 0.125)). At d = 0.50 m: 82; at 0.625 m: 56; at 0.70 m and beyond: 0.
- Narrowest gaps between features in the arena (CALC-M5-01): B1 to the east wall 1.0 m; W1 (east face x 3.6) to P2 (west face x 4.85) 1.25 m; P1 to the north wall 1.85 m. In a 1.0 m gap the centre line is 0.5 m from both sides (cost 82): passable, and the robot's 0.435 m width leaves 0.28 m on each side. None of the proposed goal paths needs that gap (§3.5).
- **L1 (the low box at (0.5, −2.5), 0.15 m high) is not in the map and the LiDAR cannot see it** (it lies below the 0.230 m scan plane; DEC-031). The chassis underside is at 0.05 m, so the robot would hit it. Nav2 cannot avoid an obstacle it cannot see; this is the M8 problem. M7 keeps the goals and routes clear of it (§3.5), and the clearance check includes it, so a path that comes too close fails the test instead of passing unnoticed.

### 3.3 CALC-M7-03: speed, stopping distance and timing
- Proposed navigation speed 0.30 m/s (60 % of the DEC-025 forward limit; OPEN-37): the robot covers the 0.25 m AMCL update distance in 0.83 s, and the slower speed reduces the following error on the tight turns of the arena.
- Stopping distance from 0.30 m/s at the 1.0 m/s² braking limit: v² / 2a = 0.045 m, plus one controller period (0.05 s at 20 Hz) of travel, 0.015 m: **0.060 m**. Proposed cancel criterion: the robot stops within 0.15 m of travel after the cancel is accepted (2.5× the estimate, to cover the smoother and controller latency), then stays still.
- Expected time to a goal: planned path length / 0.30 m/s + heading change / 1.0 rad/s + acceleration phases. Proposed bound: each goal reached within 2.0× the time computed from the path length at 0.30 m/s plus the heading change at 0.5 rad/s, so that only a stall, an oscillation or a recovery loop exceeds it.

### 3.4 CALC-M7-04: arrival accuracy, clearance and localization (OPEN-40)
- *Arrival:* Nav2 stops when its own estimate of the pose (AMCL) is within the goal checker tolerance. The ground-truth error is at most that tolerance plus the localization error at rest (≤ 0.05 m and ≤ 1.0°, DEC-059). Proposal: goal checker `xy_goal_tolerance` **0.10 m** and `yaw_goal_tolerance` **0.10 rad** (5.7°), tighter than the installed 0.25 m / 0.25 rad because M10 will dock at stations; acceptance: ground truth within **0.15 m** and **7.0°** of the goal (tolerance + localization bound).
- *Clearance:* the minimum distance between the robot footprint (CALC-M7-01, placed at the ground-truth pose at 10 Hz) and every obstacle in the world file, **including L1**, over the whole run. Proposal: ≥ **0.10 m** (two map cells: a margin for the map's 0.05 m resolution, so a near-miss counts as a failure, not as a success).
- *Commands:* every `/cmd_vel` message within DEC-025 (linear +0.5 / −0.25 m/s, angular ±1.0 rad/s), stamped in simulation time within the 0.5 s guard window; zero commands dropped by `cmd_vel_guard`; one publisher on `/cmd_vel`.
- *Localization during navigation:* the DEC-059 moving bounds (P95 ≤ 0.10 m and ≤ 2.0°, maximum ≤ 0.25 m) hold while Nav2 drives. M6 measured them on the scripted route; Nav2's speed profile differs, so they are measured again here.

### 3.5 CALC-M7-05: goal set (**Selected**; finalized in Task B, 2026-11-21, by the check in `docs/evidence/M7/TEST-M7_goals.py`, which owns the values; placement rule DEC-076)
Start at the spawn pose (0, 0, 0°) with the known initial pose (DEC-058). Goals (x, y, yaw):
| Goal | Pose | Why |
|---|---|---|
| G1 | (6.5, −2.6, −90°) | far end of the arena, south-east, 1.35 m east of P2; long first leg |
| G2 | (6.5, 1.3, 0°) | 0.9 m south of B1; tests the approach beside a box lower than the walls |
| G3 | (4.1, 2.7, 90°) | north side, between P1 and B1 |
| G4 | (2.5, −2.8, 180°) | in the alcove west of W1: the path must go around the free end of W1 (y −1.5); 1.8 m from L1 |
| G5 | (−0.6, 2.6, 90°) | north-west corner region |
| G6 | (0, 0, 0°) | back to the start |
Placement rule (DEC-076, amending the first proposal): each goal centre ≥ the inflation radius (0.70 m) from every obstacle (zero cost at the goal); the circle swept by the footprint turning in place at the goal ≥ 0.10 m from every obstacle, L1 included (DEC-073); the footprint ≥ 1.5 m from L1; every map cell under the footprint free in `/map`. The first proposal, footprint ≥ 0.8 m from every feature, failed for G2 (0.683 m to B1) and G4 (0.515 m to W1) and cannot hold in the alcove west of W1 (2.70 m wide, ≥ 2.735 m needed) ([log](../evidence/M7/CALC-M7-05_goal_check_first-rule_FAIL.log)). Final check: all PASS; smallest margins G2 and G4, centre 0.900 m, swept circle 0.514 m ([log](../evidence/M7/CALC-M7-05_goal_check.log)). The `NavigateThroughPoses` route uses G1 → G3 → G5 (DEC-078; first proposed as G1 → G3 → G5 → G6, which ends at the spawn pose and is "reached" before any motion, TS-054). The invalid goals are one inside P1 ((2.0, 2.0)) and one outside the map ((12.0, 0.0)).

## 4. Design items (**decided 2026-11-21**: OPEN-33 = DEC-066 (a), OPEN-34 = DEC-067 (a), OPEN-35 = DEC-068 (a), OPEN-36 = DEC-069 (a), OPEN-37 = DEC-070 (a), OPEN-38 = DEC-071 (a), OPEN-39 = DEC-072 (a), OPEN-40 = DEC-073, OPEN-41 = DEC-074 (a); each as recommended)
| ID | Item | Options | Recommendation (Proposed) |
|---|---|---|---|
| OPEN-33 | Navigation launch structure | (a) **an own `navigation.launch.py`** that starts only the servers M7 uses (planner, controller, behaviors, `bt_navigator`, velocity smoother, lifecycle manager), with an own `config/nav2.yaml` (the installed defaults plus the M7 changes, each commented), run beside the unchanged `sim.launch.py` and `localization.launch.py`; (b) the installed `nav2_bringup` `navigation_launch.py` with our parameter file; (c) the installed `bringup_launch.py` (it also starts its own localization) | **(a)**. Same reasoning as DEC-060: every node and remapping is visible in one short file, and the installed launch starts servers M7 does not use (collision monitor, docking, route server, smoother server, waypoint follower) and rewrites parameters. (c) would replace the verified M6 localization |
| OPEN-34 | Local controller | (a) **Regulated Pure Pursuit (RPP)**: follows the path with a look-ahead point, slows in curves and near obstacles, rotates in place to the path heading and the goal heading; collision checking with the footprint; (b) **MPPI** (installed default): samples thousands of trajectories per cycle and scores them with critics; (c) **DWB**: samples velocities and scores them with critics | **(a)**. A differential-drive robot on a known static map needs to follow the planned path, not search for alternatives. RPP has few parameters, behaves predictably and can be explained step by step; MPPI and DWB have many critics to tune and cost more CPU (risk to the real-time factor with the GUI). M8 may revisit the choice for dynamic obstacles |
| OPEN-35 | Global planner | (a) **NavFn** (installed default; Dijkstra or A* on the costmap); (b) **Smac 2D** (A* with path smoothing); (c) **Smac Hybrid-A*** or **State Lattice** (kinematically feasible paths) | **(a)**. The robot turns in place, so kinematically feasible paths (c) add nothing; NavFn is the standard and needs almost no parameters. Paths are checked by the clearance measurement (§3.4) |
| OPEN-36 | Footprint | (a) **the convex-hull polygon of CALC-M7-01** (10 points), in both costmaps; (b) the bounding rectangle (x −0.385 … +0.125, y ±0.2175); (c) a circle, `robot_radius` 0.386 m | **(a)**. It is the real outline, so collision checks are exact. (b) adds 0.056 m to the swept radius at no gain; (c) makes the robot 0.77 m wide for every check, which would block the 1.0 m gaps |
| OPEN-37 | Command path and speed | (a) **RPP at 0.30 m/s** (CALC-M7-03), angular ≤ 1.0 rad/s; **velocity smoother** limits set exactly to DEC-025 (+0.5 / −0.25 m/s, ±1.0 rad/s; 0.5 / −1.0 m/s², ±2.0 rad/s²); reversing disabled; `enable_stamped_cmd_vel: true` in every node that publishes; the smoother publishes on `/cmd_vel` → `cmd_vel_guard` → controller (unchanged); (b) as (a) without the velocity smoother (the controller's own limiter acts alone); (c) as (a) at 0.5 m/s | **(a)**. The smoother is what Nav2 expects in front of the robot; with DEC-025 values it never commands what the controller would have to clip, so the two limiters agree. 0.30 m/s keeps margin on the arena's turns; speed can rise in M9 when the factory world needs it |
| OPEN-38 | Behavior tree and recoveries | (a) **an own behavior tree**: the installed `navigate_to_pose_w_replanning_and_recovery.xml` (and its through-poses twin) **without the spin and back-up recoveries**; re-planning, costmap clearing and wait stay; (b) the installed trees unchanged (spin and back up 0.30 m when stuck); (c) no recoveries at all | **(a)**. On a known static map, the motion recoveries rarely help, and backing up blind can drive into L1, which the robot cannot see. The planner and controller failures they would hide are reported instead. M8 (dynamic obstacles) can bring them back with evidence |
| OPEN-39 | Fusion default (DEC-057 follow-up) | (a) **keep wheel odometry as the default** (`ekf:=false`); the EKF stays an option; (b) make the EKF the default in M7 | **(a)**. In this simulation the wheel odometry is near-ideal; the EKF's benefit was shown only with injected errors (TEST-M6-07). Switching the default would change the TF source under every M7 test with no measurable gain. Revisit with the DEC-043 realism additions or M13 |
| OPEN-40 | Bounds | the §3.3 and §3.4 proposal: goal checker 0.10 m / 0.10 rad; arrival ≤ 0.15 m and ≤ 7.0° (ground truth); clearance ≥ 0.10 m including L1; commands within DEC-025, zero guard drops, one publisher; DEC-059 moving bounds during navigation; time ≤ 2.0× nominal; cancel stop ≤ 0.15 m; or other bounds | the proposal: derived from the localization bounds, the map resolution and the braking limit, and fixed before any formal run. If a bound is missed in Task C, the change is a recorded decision with evidence (as DEC-063, DEC-065), not silent tuning |
| OPEN-41 | Test world and goals | (a) **the M5 arena and reference map** with the CALC-M7-05 goal set, single goals and one through-poses route, both invalid goals, and a cancel during the first leg; (b) a new world (or wait for the M9 factory world) | **(a)**. The map is verified (M5) and localization on it is verified (M6), so a navigation failure can be attributed to navigation. The factory world belongs to M9 |

## 5. Entry criteria and dependencies
- M6 complete (2026-11-21): ✅. AMCL on `/map_amcl`, `/map` for every other consumer (DEC-062); known start pose (DEC-058).
- M2 command path with the stamped-command guard (DEC-029) and DEC-025 limits: ✅.
- Nav2 1.3.14 installed (§3): ✅. Installed is not integrated; Task A checks the integration first.
- The user approves this plan and decides OPEN-33 to -41: ✅ 2026-11-21 (DEC-066 to DEC-074).

## 6. Architecture (for the §4 recommendations)
```
amr_bringup/
  package.xml                     + exec_depend nav2_controller, nav2_planner, nav2_bt_navigator, nav2_behaviors,
                                    nav2_velocity_smoother, nav2_regulated_pure_pursuit_controller, nav2_navfn_planner,
                                    nav2_rviz_plugins
  config/nav2.yaml                installed defaults for the servers M7 uses + the M7 changes, each commented
                                  (footprint, RPP, goal checker, velocity smoother, stamped output, odometry topic)
  behavior_trees/navigate_to_pose.xml, navigate_through_poses.xml   installed trees without spin and back-up (OPEN-38)
  launch/navigation.launch.py     planner_server, controller_server, behavior_server, bt_navigator, velocity_smoother,
                                  lifecycle_manager_navigation (autostart); use_sim_time; remaps the final output to /cmd_vel
  rviz/navigation.rviz            fixed frame map: /map, both costmaps, global plan, footprint, /scan, particle cloud,
                                  robot model, Nav2 goal tool and panel
  CMakeLists.txt                  + install rule for behavior_trees/
docs/evidence/M7/
  TEST-M7_nav_run.py              harness: sends goals (NavigateToPose / NavigateThroughPoses), cancels, records ground
                                  truth, AMCL pose, /cmd_vel and the guard output at 10 Hz and every command
  TEST-M7_nav_check.py            offline checker: arrival, clearance against the world file, commands, localization, timing (CI)
  TEST-M7_goals.py                goal set and its clearance check against the world file
  TEST-M7-07_distort.py           distorted copies of a recorded log for the checker-sensitivity test (CI)
  TEST-M7-10_consistency_check.py record and configuration checker (DEC-041)
tools/run_suite.py                + 'm7' suite; GPU-free checks to 'ci', TEST-M7-10 to 'records'
```
Data path: `/map` (M6 `map_server`) → global costmap static layer; `/scan` → local (and global) costmap obstacle layer; TF `map → odom` (AMCL) → `odom → base_footprint` (controller) → robot pose; goal → `bt_navigator` → planner (path) → controller (`cmd_vel_nav`) → velocity smoother → `/cmd_vel` (`TwistStamped`) → `cmd_vel_guard` → `diff_drive_controller`. Odometry for the smoother and the navigator: `/diff_drive_controller/odom`. Unchanged: the robot model, the sensors, `sim.launch.py`, `controllers.yaml`, `localization.launch.py`, `amcl.yaml`, the maps.

## 7. Task breakdown (finalized 2026-11-21)
| Task | Objective and deliverables | Tests | Depends on |
|---|---|---|---|
| **A: Navigation launch and integration gate** | `nav2.yaml`, behavior trees, `navigation.launch.py`, `navigation.rviz`, dependencies and install rule. Gate (scratch, Gazebo GUI and RViz shown, before any formal run): every server active on simulation time; costmaps on `/map` with the footprint; `/cmd_vel` is `TwistStamped` with simulation-time stamps and the guard forwards it; one publisher on `/cmd_vel`; RTF with GUI + LiDAR + AMCL + Nav2; one goal reached; default-parameter observations recorded (they inform, not change, the OPEN-40 bounds) | TEST-M7-01, -02 | Plan approval; OPEN-33 to -38 |
| **B: Harness and checker** | Goal set with its world-file clearance check, goal-sending and recording harness (ground truth, AMCL, commands, cancel), offline navigation checker, distortion tool; dry runs | TEST-M7-07 | A |
| **C: Navigation runs** | Formal runs: single goals, the through-poses route, invalid goals, cancel | TEST-M7-03, -04, -05, -06 | B; OPEN-40, -41 |
| **D: Closeout** | Regression, RViz observation (goals sent by me), consistency checker, `m7` suite and CI, records | TEST-M7-08, -09, -10 | C |

## 8. Tests (criteria Accepted: DEC-073, 2026-11-21)
Procedures: `test_plan.md` §12 (commands fixed in Tasks A–D before any formal run); evidence: `docs/evidence/M7/`. Launch: `sim.launch.py sensors:=true world:=mapping_arena.sdf` + `localization.launch.py` + `navigation.launch.py`. Gazebo tests run 3 times and every run must pass; runs with RTF < 0.5 are invalid; current-milestone runs show the Gazebo GUI and RViz (`SHOW=1`), regression re-tests run headless. A TS-029 shutdown hang is handled under DEC-039.
| Test | Requirement | Method | Proposed criterion |
|---|---|---|---|
| TEST-M7-01 | REQ-M7-11 | Build; M1 default expansion and the M2 and M3–M6 launch-model expansions byte-identical; `sim.launch.py` changed only by the DEC-075 `gui_config` lines (12 added, 0 removed; from 2026-11-21); `cmd_vel_guard.cpp`, `sensor_bridge.yaml`, `controllers.yaml`, `controllers_ekf.yaml`, the world, the sensor and properties Xacro, the SLAM files, `localization.launch.py`, `amcl.yaml`, `ekf.yaml` and the map files unchanged since M6 (`9777615`); changes to existing files listed (DEC-064); behavior trees = installed trees minus Spin and BackUp (DEC-071) | Build clean; all identical; existing files changed only by the `package.xml` dependency lines, the `CMakeLists.txt` install rule and comment lines |
| TEST-M7-02 | REQ-M7-01, -02, -03 | Interface: every navigation server active on simulation time; the global costmap's static layer on `/map` and no costmap on `/map_amcl` (the local costmap has no static layer: installed layers, rolling window from `/scan`); footprint parameter equals CALC-M7-01 and the published footprint equals it plus `footprint_padding` (installed 0.01 m, kept; Nav2 publishes the padded outline); `/cmd_vel` type `TwistStamped`, one publisher (the velocity smoother), stamps in simulation time; the guard forwards a navigation command | All hold |
| TEST-M7-03 | REQ-M7-04, -06, -07 | Single goals G1 to G6 in sequence (`NavigateToPose`), from the known start | Every goal SUCCEEDED; arrival ≤ 0.15 m and ≤ 7.0°; clearance ≥ 0.10 m including L1; commands within DEC-025, zero guard drops; DEC-059 moving bounds; each goal ≤ 2.0× nominal time |
| TEST-M7-04 | REQ-M7-05, -06, -07 | Route G1 → G3 → G5 as one `NavigateThroughPoses` goal (DEC-078) | SUCCEEDED; final arrival, clearance, command, localization and time bounds as TEST-M7-03 |
| TEST-M7-05 | REQ-M7-08 | Invalid goals: inside P1, outside the map | Each ends ABORTED or REJECTED within 60 s; the robot moves ≤ 0.05 m; no command outside DEC-025 |
| TEST-M7-06 | REQ-M7-09 | Cancel during the first leg to G1, at ≥ 1.0 m of travel | Result CANCELED; the robot stops within 0.15 m of travel after the cancel is accepted and stays still (≤ 0.01 m/s) for 5 s |
| TEST-M7-07 | REQ-M7-10 | Checker sensitivity (offline, CI): a recorded log passes; copies with the final pose offset 0.20 m, rotated 10°, the path shifted into an obstacle (clearance < 0.10 m), one command at 0.6 m/s, and the localization shifted 0.30 m each FAIL | 1 PASS, 5 FAIL, each on the expected measure |
| TEST-M7-08 | REQ-M7-11 | Regression through the runner, headless: `static`, `regression`, `m4`, `m5`, `m6` | All PASS |
| TEST-M7-09 | REQ-M7-12 | RViz `navigation.rviz` (observed by me): I send goals with the Nav2 goal tool; the plan, both costmaps and the footprint are shown; the robot reaches the goals without touching anything | Observed by user |
| TEST-M7-10 | REQ-M7-13 | Consistency checker (DEC-041, configuration vs decisions), `m7` suite, TEST-M7-07 and -10 in CI | Zero mismatches; CI PASS |

## 9. Requirements (owner: `docs/requirements.md` § M7, from 2026-11-21; this list is the original draft)
| ID | Requirement |
|---|---|
| REQ-M7-01 | The navigation servers (OPEN-33 to -35, -38) run on simulation time, started by a lifecycle manager; the costmaps use `/map` (DEC-062) |
| REQ-M7-02 | Both costmaps use the robot footprint per OPEN-36 |
| REQ-M7-03 | Navigation commands reach the robot only as `TwistStamped` on `/cmd_vel` through `cmd_vel_guard`, with simulation-time stamps, within DEC-025 |
| REQ-M7-04 | The robot reaches single goals within the OPEN-40 arrival bounds |
| REQ-M7-05 | The robot follows a multi-pose route to its final goal within the OPEN-40 bounds |
| REQ-M7-06 | The robot keeps the OPEN-40 clearance from every obstacle in the world, including obstacles it cannot see |
| REQ-M7-07 | Localization stays within the DEC-059 moving bounds while navigating |
| REQ-M7-08 | Invalid goals end in failure without unsafe motion |
| REQ-M7-09 | A canceled goal stops the robot within the OPEN-40 distance |
| REQ-M7-10 | The navigation checker detects wrong results |
| REQ-M7-11 | M1–M6 behaviour unchanged |
| REQ-M7-12 | Navigation visible and commandable in RViz |
| REQ-M7-13 | Records consistent under DEC-041; `m7` suite; GPU-free checks in CI |

## 10. Risks
- *The robot cannot see L1* (§3.2). Mitigation: goals and routes keep clear of it, and the clearance check includes it. Avoiding it is M8 (DEC-037). Demonstrated in TEST-M7-09 (my deliberate probe, 2026-11-23): a goal on L1 drives the robot into it, localization is then lost and Nav2 reports false successes (TS-058, known issue).
- *The small inscribed radius* (0.125 m, §3.1) lets the planner draw paths that are safe for `base_link` but not for the rear during a turn. Mitigation: inflation ≥ the circumscribed radius, footprint collision checking in the controller, and the clearance measurement over the whole footprint.
- *Real-time factor* with GUI + `gpu_lidar` + AMCL + six Nav2 servers. Mitigation: measured in the Task A gate; RPP and NavFn chosen partly for low CPU; RTF < 0.5 invalid.
- *Unstamped or wall-clock commands* would be dropped by the guard (DEC-029, TS-015) and the robot would not move. Mitigation: `enable_stamped_cmd_vel` and simulation time on every node; TEST-M7-02 checks the stamps; zero guard drops is a criterion.
- *Two limiters* (velocity smoother and `diff_drive_controller`) with different values would make the commanded and actual motion differ. Mitigation: the smoother uses exactly the DEC-025 values (OPEN-37); the consistency checker compares them.
- *Goal tolerance tighter than the default* (0.10 m vs 0.25 m) may make RPP oscillate near the goal. Mitigation: observed in the Task A gate; a change is a recorded decision.
- *Lifecycle start-up order* (localization before navigation; costmaps need `map → odom`). Mitigation: navigation starts after localization is active; the lifecycle manager waits; the interface test waits for the active states.
- *TS-029 shutdown hang; TS-044 controller-load failure.* Mitigation: DEC-039; TS-044 monitoring.

## 11. Exit criteria
M7 is complete only when:
- TEST-M7-01 to -10 are PASS, with results in `TEST_RESULTS.md` and evidence in `docs/evidence/M7/`; failures kept, with TS entries and re-tests.
- OPEN-33 to -41 are decided in `DECISIONS.md`; the DEC-011 footprint requirement is verified.
- The configuration, documents and checker agree (TEST-M7-10); CI is green.
- The records are updated and the M7 Tasks are done.

## 12. Implementation record
- 2026-11-21: plan drafted as Proposed from the current repository (M6 closed at `9777615`) and the installed packages. Awaiting review and the OPEN-33 to -41 decisions. No implementation.
- 2026-11-21: plan finalized with all nine recommendations (DEC-066 to DEC-074); the footprint requirement decided by DEC-069 (resolved when TEST-M7-02 verifies the footprint). Next: Task A.
- 2026-11-21, Task A: files `config/nav2.yaml` (the installed Nav2 1.3.14 sections, changes marked M7), `behavior_trees/navigate_to_pose.xml` and `navigate_through_poses.xml`, `launch/navigation.launch.py`, `rviz/navigation.rviz`, the seven exec_depends of §6 and the `behavior_trees` install rule. Implementation choices within the approved decisions: `robot_base_frame` stays `base_link` (installed; directly above `base_footprint`, DEC-016, so CALC-M7-01 applies unchanged); `controller_server` and `behavior_server` publish on `cmd_vel_nav`, so the velocity smoother is the only `/cmd_vel` publisher; local costmap layers as installed (voxel and inflation, no static layer); `footprint_padding` as installed (0.01 m).
- 2026-11-21, Task A integration gate (scratch, GUI and RViz shown; [TEST_RESULTS.md](../../TEST_RESULTS.md) § M7 Task A): servers active on simulation time, costmaps and footprint as designed, one `/cmd_vel` publisher, RTF about 1.0, G1 and G6 reached. Two installed defaults were wrong for this robot and were corrected before the formal runs: the controller's odometry topic (TS-051) and the smoother's copied stamps, which the guard rejected once (TS-050). The 0.10 m / 0.10 rad goal checker showed no oscillation.
- 2026-11-21, TEST-M7-01 PASS and TEST-M7-02 PASS on `e0474ba` ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M7 Task A); footprint requirement resolved (verified). Task A complete. Next: Task B.
- 2026-11-21, capture quality (my review of the TEST-M7-02 videos): recordings at native window size, Gazebo follow camera and a larger `navigation.rviz` view (`a299c66`); DEC-075: optional `sim.launch.py gui_config` with a panel-free Gazebo layout for recordings (`da18313`). TEST-M7-01 R1 PASS. Recordings of TEST-M7-03 and -04 use the capture layout, the follow camera behind and above the robot and end with a whole-arena view; the TEST-M7-02 clips are not used for the gallery.
- 2026-11-21, Task B started: goal set CALC-M7-05 finalized by `docs/evidence/M7/TEST-M7_goals.py`. The first placement rule (plan §3.5 footprint margin) failed for G2 and G4; DEC-076 keeps the goals with a rule based on the inflation cost and the turn clearance. All goal checks PASS.
- 2026-11-21, Task B harness and checker: dry runs found TS-052 (checker), TS-053 (goal inside P1 driven to; DEC-077, NavFn `tolerance` 0.0 and `allow_unknown` false) and TS-054 (route ending at the start; DEC-078, route G1 → G3 → G5). Recording camera: fixed M5 view (DEC-075 amendment). After the fixes all four modes PASS the checker in dry run 4. Next: TEST-M7-07 and TEST-M7-02 R1.
- 2026-11-21, Task C navigation runs ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M7 Task C): TEST-M7-03 (G1–G6), TEST-M7-04 (route) and TEST-M7-06 (cancel) PASS; TEST-M7-05 (invalid goals) measurements passed but one GUI shutdown exited 1 (TS-039 recurrence), FAIL; DEC-079 (user) extends the DEC-039 invalid-run rule to that GUI signature; R1 PASS. Task C Done; next Task D.
- 2026-11-23, Task D regression ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M7 Task D): TEST-M7-08 FAIL: one tag reused across suites (offline entries refused), the M7 `sim.launch.py` option failed the earlier identity tests (DEC-080, user), and two attempts lost a lifecycle `change_state` reply (TS-055). Re-run as R1. TEST-M7-10 checker, mutation check and `m7` suite written.
- 2026-11-23, TEST-M7-08 R1 PASS (refused and failed entries, one tag per run). CI on `6331b91` failed: TEST-M7-07 lacked the runner's overall line (TS-056); fixed, and TEST-M7-10 now checks it.
- 2026-11-23, TEST-M7-09 PASS, observed by me (RViz goals; recorded through `TEST-M7_procedure.sh` mode `observe` after an ad-hoc first session, TS-057). My deliberate L1 probe showed the §3.2 limitation: contact, localization loss and false successes (TS-058, M8).
- 2026-11-23, TEST-M7-10 PASS: `m7` suite (GUI shown; TEST-M7-05 attempt 3 INVALID under DEC-079, repeated), checker and mutation check. All TEST-M7-01 to -10 PASS.
- 2026-11-23, M7 closed; gallery media selected (TEST-M7-02 R1, -03, -04, -05 R1, -06, -09).

## 13. Known limitations and carried items (at closure, 2026-11-23)
- **Low obstacles are invisible (TS-058, open):** L1 lies below the LiDAR scan plane and is not in the map, so Nav2 accepts goals on it and drives into it. The TEST-M7-09 probe showed the consequences: contact, wheel-odometry slip, AMCL converging on a wrong pose, and later goals reported SUCCEEDED in that wrong estimate. Nothing detects the contact, the stall or the localization loss. M8 decides at least low-obstacle sensing (DEC-037), stall/contact detection and localization-loss detection. Until then, M7 goals keep clear of L1.
- **Nav2 success is judged on the estimate:** the goal checker uses the localization estimate. The formal tests judge arrival on Gazebo ground truth (DEC-073); a deployed robot has no ground truth, which makes the localization-loss item above a safety item.
- **Start pose:** navigation still starts from the known start pose (M6 §13: global localization not reliable in this arena).
- **Upstream start-up and shutdown issues:** dropped lifecycle `change_state` replies (TS-055, open, watched) and the GUI shutdown race (TS-039, handled by DEC-079). Both cost repeated attempts, not results.
- **Carried from M6:** the `/map_amcl` workaround (DEC-062, navigation2#6833), the DEC-065 margin, and fusion selectable only (DEC-057), unchanged in M7.
- **Process rules from M7:** one tag per suite (TEST-M7-08); every formal test recorded through the milestone's shared procedure (TS-057, `docs/gallery/README.md` § Recording rule); each new suite entry is run once through the runner before commit (TS-056).
- **Gallery media:** TEST-M7-02, -03, -04, -05, -06 and -09, selected at the closure ([`docs/gallery/M7/`](../gallery/M7/)).
