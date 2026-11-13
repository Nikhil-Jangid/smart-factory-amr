# Motion Control Design: Contact, Limits, Controller Interface, Motion-Test Criteria (M2)

**Status:** analysis prepared on 2026-10-22 for OPEN-09 to OPEN-12 ([M2 plan](../milestones/M2_basic_movement.md) §4). **The proposals were selected by me on 2026-10-22, unchanged:** OPEN-09 → DEC-024, OPEN-10 → DEC-025, OPEN-11 → DEC-026, OPEN-12 → DEC-027. Once implemented, the configuration files own the numeric values (`amr_description/urdf/amr.ros2_control.xacro`, `amr_bringup/config/controllers.yaml`), and this document keeps the rationale. "Proposed" below records the state when the analysis was written.
**Related:** DEC-013, DEC-016, DEC-019, DEC-023 · CALC-M1-06, -11, -12 ([mass_inertia.md](mass_inertia.md)) · REQ-M2-09 to -14 ([../requirements.md](../requirements.md))

Labels follow [../README.md](../README.md#parameter-status-labels). Inputs from M1 are Calculated (CALC-M1-11/12 are provisional because of OPEN-03; *final for current inputs since 2026-11-03, DEC-030/DEC-037*).

## 1. Inputs

| Symbol | Value | Source |
|---|---|---|
| m | 9.4 kg | CALC-M1-06 |
| g | 9.81 m/s² | mass_inertia.md §8 |
| x_cg (CG behind the axle) | 0.0913 m | CALC-M1-11 (provisional) |
| h (CG height above ground) | 0.106 m | CALC-M1-11 (provisional) |
| L (axle to caster contact) | 0.360 m | `caster_x` (Selected) |
| d_c = L − x_cg (CG ahead of the caster contact) | 0.2687 m | Calculated |
| b (wheel track) | 0.400 m | `wheel_track` (Selected) |
| r (wheel radius) | 0.075 m | `wheel_radius` (Selected) |
| r_s (swept radius about `base_link`) | 0.385 m | CALC-M1-13 |
| Physics step | 0.001 s (1 kHz), RTF target 1.0 | stock `empty.sdf` world (`gz-sim8`), inspected 2026-10-22 |

## 2. Simulator facts (installed software, inspected or measured 2026-10-22)
- **Engine:** Gazebo Sim 8 with the DART engine through `gz-physics7` (TS-005 shows DART messages in M1).
- **Parameters the DART plugin consumes** (from the strings in `libgz-physics7-dartsim-plugin.so.7.8.0`):
  - It reads `friction` (`mu`/`mu2`), `fdir1`, `slip1`/`slip2` and `restitution_coefficient`.
  - It reports "DART doesn't support torsional friction setting" and "… rolling friction setting".
  - No ODE contact parameters (`kp`, `kd`, `max_vel`, `min_depth`, `soft_cfm`/`soft_erp`) appear in the plugin. Setting them is therefore expected to have **no effect** with this engine. That is an inference from the binary, not a measurement.
- **SDF defaults** (SDFormat 1.11 spec, `gz sdf -d 1.11`):
  - `<surface><friction><ode>`: `mu` = 1, `mu2` = 1, `fdir1` = 0 0 0, `slip1` = `slip2` = 0.
  - Torsional `coefficient` = 1; ignored by DART.
- **Ground:** the stock `empty.sdf` ground plane sets no `<surface>`, so it has μ = 1. The current M1 model sets no surface either, so the wheels **and the caster** have μ = 1.
- **Friction combination (Measured, [OPEN-09 probe](../evidence/M2/OPEN-09_friction_probe.log)):**
  - Probe setup: tilted gravity with tan θ = 0.4, ground μ = 0.6, and boxes with μ = 0, 0.01, 0.3, 0.5, 1.0 and the default.
  - The measured sliding accelerations match **μ_eff = min(μ₁, μ₂)** within 0.05 %. For example, μ = 0.3 measured 0.9112 m/s² against 0.9108 predicted by the min rule and 2.0038 by the product rule. Boxes with μ ≥ 0.5 did not slide.
  - With the stock ground (μ = 1), **the μ set on the robot's collision is the effective μ** whenever it is ≤ 1.
  - Limitation: the probe measures sliding of flat box faces. Rolling-wheel contact is checked in TEST-M2-05/06.
- **Actuation:**
  - `gz_ros2_control` commands wheel joint velocity.
  - The wheel joints are `continuous` with no `<limit>` (M1), so the commanded velocity is not effort-limited.
  - Wheel slip is therefore limited only by friction: a commanded acceleration above the traction limit produces slip, not a slower ramp.

## 3. OPEN-09 — Contact and friction (proposal)

**CALC-M2-01: caster drag with the current default μ = 1** (Calculated)
- Caster normal load N_c = m·g·x_cg/L = 92.21 × 0.0913 / 0.360 = **23.39 N** (25.4 %, matches CALC-M1-11).
- The caster is a **fixed** sphere (DEC-013): it can only slide, never roll.
  - Sliding drag F = μ_c·N_c = **23.4 N at μ_c = 1**, the same as 2.49 m/s² of deceleration on the whole robot.
  - In-place yaw drag torque μ_c·N_c·L = **8.42 N·m**, against a maximum wheel-traction couple of 2 × 34.4 N × 0.200 m = **13.8 N·m** at μ = 1.
- *Interpretation:* with the defaults, the caster acts as a strong brake, and rotation needs more than 60 % of the available wheel traction. This is why DEC-013 deferred a low-friction caster contact to M2.

**CALC-M2-02: friction needed by the proposed limits (§4)** (Calculated; caster drag neglected)
| Case | Required μ (drive wheels) |
|---|---|
| Accelerate forward at 0.5 m/s² (load moves to the caster) | a·L / (g·d_c − a·h) = **0.070** |
| Brake from forward at 1.0 m/s² (load moves to the wheels) | a·L / (g·d_c + a·h) = **0.131** |
| Brake from reverse at 1.0 m/s² (load moves to the caster) | a·L / (g·d_c − a·h) = **0.142** |

| Parameter | Proposed | Label | Rationale | Alternatives |
|---|---|---|---|---|
| Wheel `mu`, `mu2` | **1.0** (written explicitly) | Assumed | Equals the engine default and the stock ground, so it is the effective μ (measured min rule). It is at least 7× the largest required μ (CALC-M2-02), so wheel slip should be negligible in M2. Being explicit makes the value traceable and testable. A real rubber/polyurethane tyre on a dry floor is commonly quoted around 0.5–1.0 (**assumption, not measured**) | 0.7 (closer to a mid-range floor; still ≥ 4.9× margin) |
| Caster `mu`, `mu2` | **0.01** | Assumed | It represents the rolling resistance of the real swivel caster that the rigid sphere stands in for (DEC-013); a typical caster rolling-resistance coefficient is of order 0.01 (**assumption**). Drag 0.23 N (0.025 m/s² equivalent); yaw drag 0.08 N·m. It is isotropic, which suits a swivel caster | 0.0 (ideal; no drag at all); 0.05 (drag 1.17 N, 0.12 m/s²) |
| `fdir1`, `slip1`, `slip2` | Not set (defaults 0) | Proposed | Isotropic friction; no slip compliance. DART supports slip compliance, but there is no evidence that it is needed | Slip compliance only if TEST-M2-05/06 show contact jitter |
| `kp`, `kd`, `max_vel`, `min_depth`, torsional and rolling friction | Not set | Proposed | Not consumed by DART (§2), so setting them would only look like a decision | — |
| Location | Gazebo `<collision>` surface of the wheel and caster links, emitted only when `use_ros2_control:=true` (DEC-023), so the M1 expansion stays byte-identical | Proposed (follows DEC-023) | — | — |

*Note on lumping:* the caster collision is merged into `base_footprint` by fixed-joint lumping (TEST-M1-03). How a URDF `<gazebo reference="caster_link">` surface carries over to the lumped collision must be checked in the generated SDF (TEST-M2-02, element-level check). If it does not carry over, the surface is set on the lumped collision name instead. This is an implementation detail, not a new decision.

*Update 2026-10-22 (DEC-028, TS-014):* in the M2 simulation model the wheel collision is a sphere of `wheel_radius`, because the DART cylinder contact gave an effective track of ≈ 0.3665 m in rotation. The DEC-024 surface values apply unchanged to the sphere.

**Sensitivity and failure risks:**
- *Wheel slip:* not expected at the proposed limits (margin ≥ 7×). It becomes likely if the limits are raised toward the traction values in CALC-M2-03, or if the wheel μ is reduced below about 0.3.
- *Caster μ too high* (for example the default 1): rotation slows or the robot pivots about the caster, and the measured in-place translation fails the OPEN-12 bound.
- *Caster μ = 0:* no lateral support from the caster. The wheels still provide all lateral force, so this is acceptable. It is kept as the alternative.
- *Unstable contact:* cylinder-on-plane contact in DART can chatter, and TS-005 recorded DART collision warnings for other shapes. This is detected by roll/pitch and jitter checks in TEST-M2-05/06/10. A collision-geometry change (for example sphere wheels) would be a geometry decision and needs a recorded decision.
- *Verification:* TEST-M2-02 checks that the values appear in the generated SDF. TEST-M2-05/06/08 check behaviour, including a slip ratio recorded from `/joint_states` against ground truth. TEST-M2-10 checks the rest behaviour.

## 4. OPEN-10 — Velocity and acceleration limits (proposal)

The tipping values of CALC-M1-12 (8.4 and 12.1 m/s²) are **quasi-static reference values, not operating limits**. Traction limits are lower, and both are divided by a safety factor.

**CALC-M2-03: traction-limited accelerations** (Calculated; quasi-static, rigid bodies, caster friction neglected, drive wheels supply all longitudinal force)
- Forward acceleration (inertia shifts load to the caster): a = μ·g·d_c / (L + μ·h).
- Braking from forward (load shifts to the wheels): a = μ·g·d_c / (L − μ·h).
- Lateral sliding (drive wheels only): a ≈ μ·g·N_d/W, with N_d/W = 0.746.
- Tipping (CALC-M1-12 geometry):
  - forward about the axle (braking forward / accelerating in reverse) g·x_cg/h = **8.45 m/s²**;
  - rearward about the caster (accelerating forward / braking in reverse) g·d_c/h = **24.9 m/s²**;
  - lateral **12.1 m/s²**.

| μ | Forward accel | Brake from forward | Lateral slide |
|---|---|---|---|
| 0.3 | 2.02 | 2.41 | 2.20 |
| 0.5 | 3.19 | 4.29 | 3.66 |
| 0.7 | 4.25 | 6.46 | 5.13 |
| 1.0 | 5.66 | 10.38 | 7.32 |

(m/s²)

**Margin policy (Proposed):**
- Every acceleration limit is at most **one third** of the lower of (traction at a *design* μ of 0.5, tipping).
- The design μ of 0.5 is deliberately below the simulated wheel μ (OPEN-09). That way the limits remain sensible on a lower-friction floor, for example later on hardware (M13).

**Operating assumption (missing in the repository; needs your confirmation):** there is no speed requirement anywhere in the project. The proposal assumes indoor, low-speed operation, with people possibly nearby in later milestones, for early simulation, manual control, and the first Nav2 tuning (M7). Higher speeds can be revisited with evidence.

| Controller parameter (`diff_drive_controller`) | Proposed | Unit | Check against | Margin |
|---|---|---|---|---|
| `linear.x.max_velocity` | **0.5** | m/s | Matches the `teleop_twist_keyboard` default speed (0.5); stopping distance v²/(2·a_dec) = 0.125 m in 0.5 s | — |
| `linear.x.min_velocity` (reverse) | **−0.25** | m/s | DEC-014: the LiDAR is front-mounted, so reverse motion will have weaker sensing (M3); reverse stopping distance 0.031 m | — |
| `linear.x.max_acceleration` | **0.5** | m/s² | Forward traction at μ 0.5: 3.19 | 6.4× |
| `linear.x.max_deceleration` | **1.0** | m/s² | min(brake traction 4.29, forward tip 8.45) | 4.3× |
| `linear.x.max_acceleration_reverse`, `max_deceleration_reverse` | not set: the installed controller then uses −max_acceleration / −max_deceleration | — | Reverse braking loads the caster: traction 3.19 | 3.2× (at 1.0) |
| `angular.z.max_velocity` (±) | **1.0** | rad/s | Matches the teleop default turn (1.0). In place: wheel speed 0.20 m/s, rear-corner speed 0.385 m/s. At v 0.5 m/s: outer wheel 0.70 m/s (9.33 rad/s), lateral acceleration v·ω = 0.5 m/s² against a lateral slide of 3.66 and a lateral tip of 12.1 | 7.3× (slide) |
| `angular.z.max_acceleration`, `max_deceleration` | **2.0** | rad/s² | Wheel tangential share α·b/2 = 0.4 m/s². Worst wheel 0.5 + 0.4 = 0.9 m/s² (accelerating), 1.0 + 0.4 = 1.4 m/s² (braking); rear-corner tangential acceleration 0.77 m/s² | ≥ 3.0× |
| Jerk limits (`max_jerk`, `min_jerk`) | not set (NaN = disabled) | — | No requirement; fewer parameters to verify | — |

- **Configuration location:** `amr_bringup/config/controllers.yaml` (DEC-023) owns the values once implemented. This section keeps the rationale.
- **Installed-controller facts:** all limits default to NaN, meaning *no limit*. The `has_*_limits` flags are deprecated (log text: "set the respective limits to NAN"). The limits must therefore be set explicitly, or the robot has none.
- **Verification:** TEST-M2-08 (`cmd_vel_out` never exceeds the limits; measured accelerations within tolerance; roll/pitch bound). TEST-M2-07 (stop distance against v²/(2·a_dec)).

## 5. OPEN-11 — Controller rate and command interface (proposal)

| Item | Proposed | Rationale and evidence |
|---|---|---|
| `controller_manager` `update_rate` | **100 Hz** | An integer divisor of the 1 kHz physics step: 10 steps per control cycle, so no aliasing. A 10 ms period is short compared with the fastest commanded transient (0.5 s from full speed to rest; 0.25 s angular ramp), and the velocity quantization per cycle is a·Δt = 0.005 m/s. 1 kHz would only add load; 50 Hz is acceptable but halves the limiter resolution |
| `publish_rate` (odometry/TF) | **50 Hz** (installed default) | Enough for M2 checks; M4 may revisit |
| `cmd_vel_timeout` | **0.5 s** (installed default) | Dead-man behaviour (see the teleop note below) |
| Command topic and type | **`/cmd_vel`**, `geometry_msgs/msg/TwistStamped` | The installed controller accepts only `TwistStamped` on `~/cmd_vel`. It is remapped to `/cmd_vel` with the spawner's `--controller-ros-args` (option present in the installed `spawner --help`) so teleop and Nav2 (M7) share one topic. *Superseded by DEC-029 (2026-10-22): there is no spawner remap; `cmd_vel_guard` forwards `/cmd_vel` to `/diff_drive_controller/cmd_vel`. The public topic and type are unchanged.* Nav2 Jazzy has stamped-output support (`enable_stamped_cmd_vel` in `nav2_util`) |
| Controller names | `joint_state_broadcaster`, `diff_drive_controller` | Package defaults; topics `/joint_states`, `/diff_drive_controller/odom` |
| Frames | `odom_frame_id: odom`, `base_frame_id: base_footprint` (installed default is `base_link`), `enable_odom_tf: true` | DEC-016; frames_and_tf.md §5 |
| Teleop | `teleop_twist_keyboard` with `stamped:=true`, `frame_id:=base_footprint`, **`use_sim_time:=true`**, remapped to `/cmd_vel` | Installed parameters `stamped`, `frame_id`, `speed` (0.5), `turn` (1.0) |
| Sim time | `use_sim_time: true` on every M2 node that publishes or consumes stamped data | See the stamp hazard below |

**Stamp hazard (found in the installed controller; observed in formal TEST-M2-07 as TS-015; guarded by DEC-029 `cmd_vel_guard`):** the controller logs "Ignoring the received message (timestamp …) because it is older than the current time by … which exceeds the allowed timeout", so it compares the command's **header stamp** with its own (simulation) clock.
- A publisher on wall-clock time stamps its commands far in the *future* relative to simulation time.
- Depending on the implementation, such a command may never be judged stale, so the timeout would not stop the robot.
- *Original assessment (2026-10-22, before the formal tests):* this is an **unverified hypothesis**. TEST-M2-07(c) characterizes it. Until then, mandatory `use_sim_time` is the mitigation.
- **Current status (2026-11-03): observed and addressed.**
  - *Observed:* formal TEST-M2-07 `wallclock` characterization (`26a6048`) confirmed the hazard. Wall-clock-stamped commands were never timed out, and the robot kept moving 0.598 m in the 3 s after the last command ([TS-015](../troubleshooting.md)).
  - *Addressed:* DEC-029 adds `amr_bringup/cmd_vel_guard` between `/cmd_vel` and `/diff_drive_controller/cmd_vel`. It forwards a command only if \|now − stamp\| ≤ `cmd_vel_timeout`. The DEC-026 values and the controller configuration are unchanged.
  - *Verified:* TEST-M2-07 re-test 1 **PASS**: stop, timeout, stale, wall-clock (0.000 mm of motion) and domain-switch cases, 3/3 each ([../../TEST_RESULTS.md](../../TEST_RESULTS.md)).
  - `use_sim_time` on every command publisher remains required (DEC-026). The guard's residual limits (direct publishers to the controller input; an unreported guard death; simulation only; not a certified safety function) are listed in DEC-029.

**Teleop and timeout interaction:**
- The installed `teleop_twist_keyboard` reads one key per blocking read and publishes once per key event.
- Holding a key therefore relies on the terminal's key auto-repeat. Its initial delay is set by the desktop and was not measured; it may exceed 0.5 s.
- A single key press moves the robot for about `cmd_vel_timeout`. Holding a key may cause a brief stop/start before auto-repeat begins.
- This is the safe behaviour. TEST-M2-09 records it (observed by me), and `cmd_vel_timeout` is revisited only with that evidence.

**Verification:** TEST-M2-03 (startup), TEST-M2-04 (topics, frames, sim time), TEST-M2-07 (delivery, stop, timeout, stale and wall-clock stamps).

## 6. OPEN-12 — Motion-test criteria (proposal)

**Measurement method:**
- **Ground truth:** the model pose in the world from `/world/<world>/pose/info`, stamped in simulation time; the TEST-M1-07 method extended to a stream.
- **Controller outputs:** `/joint_states` and `/diff_drive_controller/odom` (odometry), and `/diff_drive_controller/cmd_vel_out` (limited command).
- Odometry is compared with ground truth **only for sign and gross faults**. Odometry accuracy is M4.
- All times are simulation times, and every run logs the RTF. A run with mean RTF < 0.5 is invalid and repeated (not counted as a failure).
- Each motion test has **3 runs** from a fresh spawn at the origin. All runs must pass; the report gives the mean and maximum.
- Body-frame quantities use the heading at command start.

**Expected values from the limits (CALC-M2-04, Calculated):**
- With acceleration a and deceleration d, a command v held for T and then zero gives a distance of v·T − v²/(2a) + v²/(2d).
  - v = 0.2 m/s, T = 5.0 s: **0.980 m**.
  - v = −0.2 m/s (the reverse limits default to the same magnitudes): **−0.980 m**.
- Rotation: ω = 0.5 rad/s for T = π/ω = 6.283 s with α = 2.0 rad/s² on both ramps gives **π rad (180°)**.
- Stopping from 0.5 m/s at 1.0 m/s²: **0.125 m in 0.50 s**.

| Test | Criterion (Proposed) | Tolerance rationale |
|---|---|---|
| TEST-M2-05 direction | +v: ground-truth displacement along the start heading > 0; both wheel velocities > 0 during cruise. −v: both < 0, displacement < 0 | Sign checks; no tolerance |
| TEST-M2-05 distance | Measured distance within **±5 %** of CALC-M2-04 (0.931–1.029 m) | Allows limiter discretization and contact compliance; slip is expected to be negligible (CALC-M2-02). Still tight enough to catch a wrong `wheel_radius` (a 10 % error gives a 10 % distance error) |
| TEST-M2-05 straightness | Lateral deviation **≤ 20 mm** per metre; heading change **≤ 1.0°** | A 1° heading error over 1 m is 17 mm laterally. Catches a wrong `wheel_separation` or asymmetric contact |
| TEST-M2-06 rotation | +ω: yaw increases; right wheel velocity > 0 > left. Angle within **±5 %** of 180° (±9°). `base_footprint` translation **≤ 20 mm** | The translation bound catches caster drag pivoting (§3) |
| TEST-M2-07(a) stop | From 0.5 m/s, after the zero command: at rest (ground-truth speed **< 5 mm/s**) within **0.70 s** (0.50 + 0.20 s); stop distance **≤ 0.150 m** (0.125 + 20 %) | Margin for the limiter and controller period |
| TEST-M2-07(b) timeout | From 0.2 m/s, publishing stopped: the limited command (`cmd_vel_out`) starts decreasing within `cmd_vel_timeout` + 2 control periods (**0.52 s**) of the last message, and the robot is at rest within **0.90 s** | 0.5 timeout + 0.2 s ramp at 1.0 m/s² + 0.2 margin. Whether the post-timeout stop is ramped by the limiter is recorded |
| TEST-M2-07(c) stamps | A command stamped older than `cmd_vel_timeout` gives **no motion** (< 5 mm) and the "Ignoring the received message" warning. A wall-clock-stamped command is **characterized** (motion and stop behaviour recorded). If it does not time out, record a TS entry and a hazard note | Safety-relevant hypothesis; recorded, not assumed |
| TEST-M2-03 startup | Both controllers `active` within **10 s** of sim time after spawn; 0 error lines; a command published **before** activation causes **< 5 mm** motion | No unintended motion at startup |
| TEST-M2-03 fault (characterization) | Deactivate `diff_drive_controller` while moving at 0.2 m/s and record the wheel behaviour (stops, holds or coasts; the plugin has a `hold_joints` parameter). It passes as a characterization when recorded; coasting is reported as a hazard for a decision | The behaviour of the installed plugin is not documented in the repository |
| TEST-M2-04 TF/odometry consistency | `odom → base_footprint` from TF equals the odometry pose at the same stamp within 1 mm / 0.1°; exactly one parent per frame; odometry frame ids `odom`/`base_footprint` | Identity check, not accuracy |
| TEST-M2-05/06 odometry sign | The sign of the odometry Δx (Δψ) equals the ground-truth sign. Gross-fault bound: odometry/ground-truth magnitude ratio within **0.5–1.5** | Detects a sign, unit or parameter fault only. **Accuracy acceptance is M4** |
| TEST-M2-05/06/08 attitude | \|roll\|, \|pitch\| **< 1.0°** throughout motion | Twice the at-rest OPEN-07 bound; detects wheel lift or tipping onset |
| TEST-M2-08 limits | `cmd_vel_out` never exceeds the configured velocity limits for step commands of 2× the limit. Measured ground-truth acceleration ≤ limit × 1.10 | 10 % for finite-difference noise over a 0.1 s window |
| Slip (recorded) | Slip ratio 1 − (ground-truth distance)/(r·mean Δθ_wheels) recorded for each run; **≤ 5 %** in TEST-M2-05 | Consistent with CALC-M2-02 margins |
| Zero command at rest | TEST-M2-10 (OPEN-07 thresholds) | — |

## 7. OPEN-07 review (2026-10-22): thresholds unchanged and still provisional
> **Current status (2026-11-03): finalized unchanged.** The rest-stability thresholds \|Δz\| < 2 mm, \|roll\| and \|pitch\| < 0.5° and horizontal drift < 5 mm over 30 s are **Selected (final)**. Sources: DEC-019 update 2026-11-03 in `DECISIONS.md`. Basis: the evaluation rule below (first case) applied to the TEST-M2-10 re-test 1 measurements in `TEST_RESULTS.md`, plus a GUI observation of no jitter. No calculation changed; there is no CALC entry for these thresholds. The 2026-10-22 review below is kept as dated history.
- **Evidence available now:** TEST-M1-07 measured Δz 0 mm, pitch 0.000098° and drift 0 mm over 30.1 s, against \|Δz\| < 2 mm, \|roll/pitch\| < 0.5° and drift < 5 mm. The margins are large; the thresholds act as gross-fault detectors.
- **What M2 changes:**
  - The caster contact changes from μ = 1 to the OPEN-09 value. Low caster friction removes the resistance to sliding, but on level ground no horizontal force acts at rest.
  - With active controllers, the wheels are velocity-held at zero instead of free-rolling (M1).
  - The rest behaviour therefore needs re-measurement, not extrapolation.
- **Conclusion:** no new evidence justifies revising or finalizing the thresholds. They **stay provisional** until TEST-M2-10 has run on the M2 configuration. Nothing is changed automatically.
- **Proposed evaluation rule** for after TEST-M2-10, to be decided:
  - If all 3 runs pass with every measured value at most 50 % of its threshold, recommend finalizing unchanged.
  - If any value lies between 50 % and 100 % of its threshold, keep the thresholds provisional and investigate.
  - If any run fails, record a TS entry and do not revise the thresholds without a decision.
- **Outcome (2026-11-03):**
  - TEST-M2-10 PASS: re-test 1 met the quantitative criteria with every value ≈ 0 (≪ 50 % of each threshold), and I observed no visible jitter.
  - The first case of the rule applied. I decided to **finalize the thresholds unchanged** (DEC-019 update 2026-11-03).
