# M4 — Odometry: Milestone Plan and Record


**Status:** **Complete** (2026-11-13; closed; in progress since 2026-11-13). Every exit criterion in §11 is met: TEST-M4-01 to -12 PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4); OPEN-19 to -22 decided (DEC-042 to DEC-045); TEST-M4-12 and CI green. Plan finalized 2026-11-13 with the §4 recommendations. Values are labelled Selected / Proposed / Assumed / Calculated / Measured / Verified.

**Record rule (DEC-041):** from M4 on, test results live only in `TEST_RESULTS.md`. This record and `test_plan.md` link to them and do not restate the numbers.

## 1. Purpose
Since M2 the robot has published wheel odometry: `diff_drive_controller` integrates the wheel positions into the pose `odom → base_footprint`. M2 checked only that its **signs** are right (REQ-M2-11; "magnitude accuracy is M4"). M4 makes odometry a **measured, characterized and correctly described** input for the later milestones:
- **Accuracy.** It measures how far the odometry pose drifts from Gazebo ground truth on straight, rotating and closed paths.
- **Description.** It gives the published estimate an uncertainty (covariance) that a fusion filter can use. M6 fuses odometry with the IMU, and M5/M6 correct `map → odom` on the assumption that `odom → base_footprint` is smooth and drifts slowly.
- **Test strength.** It shows that the accuracy tests would catch a real calibration error, so that a PASS in an almost ideal simulation still means something.

*Concept: dead reckoning.* Odometry estimates the pose by adding up small wheel motions. Each step's error is small, but the errors **accumulate** and are never corrected. There are two kinds:
- *systematic* errors repeat the same way on every run: a wrong wheel radius, or a wrong track width;
- *random* errors differ from run to run: slip, and encoder quantization.

This is why odometry is tested on long and closed paths and not only on short legs. It is also why it is later fused with other sensors.

## 2. Scope
Derived from ROADMAP § M4, REQ-M2-11, frames_and_tf.md (DEC-016: `odom → base_footprint` "M4 (validated)"), ros_architecture.md (M4 row), DEC-033 (ideal encoder; emulation "can be revisited in M4") and DEC-041.

**In scope:**
| Item | Source |
|---|---|
| Differential-drive kinematics and odometry integration: documented, and checked independently against the controller | ROADMAP M4 |
| Odometry interface: topic, frames, rate, sim-time stamps, single `odom → base_footprint` publisher | ROADMAP M4 ("TF tree"); DEC-016 |
| Quantitative accuracy against ground truth: straight, in-place rotation, closed paths, velocity (twist) | ROADMAP M4; REQ-M2-11 |
| Odometry covariance (the installed default is all zeros, §3.2) | needed by M6 |
| Sensitivity: the tests detect injected calibration errors | §1 (test strength) |
| `m4` runner suite; the GPU-free parts in CI; M1–M3 regression | DEC-040, DEC-041 |

**Out of scope:**
- Fusing odometry with the IMU (EKF), and `map → odom` (M5, M6).
- Calibrating a real robot, and real-floor slip (M13).
- Changing the accepted geometry, the controller limits (DEC-025) or the contact parameters (DEC-024, DEC-028).
- An encoder-emulation node, unless I choose it under OPEN-20.

## 3. Analysis (Calculated unless stated otherwise)
Inputs, owned by `amr_properties.xacro` and `controllers.yaml`: wheel radius r = 0.075 m, track b = 0.400 m (Selected; `wheel_separation` = `wheel_track`, checked by TEST-M2-11). Control and odometry update rate: 100 Hz. Odometry publish rate: 50 Hz (DEC-026). Installed `diff_drive_controller` version: 4.42.1, with `position_feedback: true` and `open_loop: false`, so odometry is integrated from the **wheel positions**.

### 3.1 CALC-M4-01: kinematics
For one update with wheel position changes Δθ_L and Δθ_R (rad):
- Δs_L = r·Δθ_L and Δs_R = r·Δθ_R (wheel travel, m).
- Δs = (Δs_R + Δs_L)/2 (forward travel of `base_footprint`), and Δψ = (Δs_R − Δs_L)/b (heading change, rad).
- Pose update, per control cycle (100 Hz), **verified from the controller source** (ros2_controllers tag `4.42.1`, commit `aacd842`, `diff_drive_controller/src/odometry.cpp`, read 2026-11-13):
  - if |Δψ| ≥ 1e-6 rad (per step): **exact arc integration**, with R = Δs/Δψ: ψ' = ψ + Δψ, x += R·(sin ψ' − sin ψ), y −= R·(cos ψ' − cos ψ);
  - otherwise second-order Runge–Kutta: x += Δs·cos(ψ + Δψ/2), y += Δs·sin(ψ + Δψ/2), ψ += Δψ.
  - The draft of this plan assumed RK2 throughout; the source shows that RK2 is only the near-straight fallback.
- Inputs, from `diff_drive_controller.cpp` (same tag): with `position_feedback: true` the controller calls `update()` with the wheel joint **positions**; Δs_L and Δs_R are differences of position × radius between cycles. A cycle with dt < 0.1 ms is skipped.
- Multipliers: r_L = `left_wheel_radius_multiplier`·r, r_R = `right_wheel_radius_multiplier`·r, b = `wheel_separation_multiplier`·b. They are applied **both** to the wheel commands (inverse kinematics, every cycle) and to the odometry (`setWheelParams`, in `on_configure` only, so they take effect at controller load, not at runtime). This is what TEST-M4-09 relies on: with a wrong multiplier, the robot executes the commanded profile with the true geometry, while the odometry integrates with the wrong one.
- Published twist: the rolling mean of the per-cycle velocities over `velocity_rolling_window_size` = 10 cycles (installed default, not set in `controllers.yaml`), i.e. 0.1 s at 100 Hz. It lags a velocity change by about 0.05 s, so TEST-M4-08 compares cruise phases only.
- Publication: odometry and TF at 50 Hz (`publish_rate`); the pose is integrated at 100 Hz.

Reasonableness check, using the M2 profiles: 0.2 m/s forward gives wheel speeds of 0.2/0.075 = 2.67 rad/s. 0.5 rad/s in place gives wheel rim speeds of ±0.5·0.200 = ±0.100 m/s, which is ±1.33 rad/s.

### 3.2 Installed odometry covariance (checked 2026-11-13)
In the installed `diff_drive_controller_parameters.hpp` (4.42.1), `pose_covariance_diagonal` and `twist_covariance_diagonal` both default to `{0, 0, 0, 0, 0, 0}`. `controllers.yaml` sets neither, so `/diff_drive_controller/odom` currently claims a **perfect** estimate. A fusion filter cannot weigh a zero-uncertainty input sensibly, so this must be decided before M6 (OPEN-19).

### 3.3 CALC-M4-02: sensitivity to systematic errors
These show what each calibration error does to the odometry. They also give the bounds that the sensitivity test (TEST-M4-09) must exceed.
| Error | Effect on odometry vs truth | Example |
|---|---|---|
| Both radii wrong by fraction ε_r | Distance error = ε_r·d; heading not affected | ε_r = 1 %, d = 2 m: 20 mm |
| Radii unequal by fraction δ (r_R = r(1+δ/2), r_L = r(1−δ/2)) | Odometry reports a straight line while the robot curves: heading error d·δ/b, end lateral offset ≈ d²·δ/(2b) | δ = 0.1 %, d = 1 m: 0.0025 rad = 0.14°, 1.25 mm |
| Track wrong: true b_t = b(1+ε_b) | ψ_true = ψ_odom·b/b_t, so the yaw error ≈ ε_b·ψ | ε_b = 1 %, 360°: 3.6° |

*Measured in M2 (TEST-M2-05/-06 R1):* the odometry/ground-truth ratio was 0.9999–1.0001 for both straight and rotation legs, and wheel slip was −0.005 %. The simulated systematic errors are therefore of order 0.01 %, far below any useful bound. The simulation is close to ideal, so a PASS alone proves little. TEST-M4-09 adds the missing evidence: deliberately wrong calibrations must FAIL.

### 3.3a CALC-M4-04: covariance values from the DEC-042 model (**Selected**: accepted as proposed on 2026-11-13; written to `controllers.yaml` in Task B)
Model (DEC-042, **Assumed**): odometry error σ = 1 % of the distance travelled and 2 % of the rotation. `diff_drive_controller` publishes **constant** diagonals in the order (x, y, z, roll, pitch, yaw) for the pose and (v_x, v_y, v_z, ω_x, ω_y, ω_z) for the twist.
- **Twist** (the per-instant estimate, which does not grow with distance), at the DEC-025 maximum speeds:
  - v_x: σ = 0.01 × 0.5 m/s = 0.005 m/s → variance **2.5e-5** (m/s)².
  - ω_z: σ = 0.02 × 1.0 rad/s = 0.02 rad/s → variance **4.0e-4** (rad/s)².
  - v_y: a differential drive cannot move sideways; lateral slip was not observed (TEST-M3-09: |y| < 1 mm). Proposed: the same variance as v_x, **2.5e-5**.
  - v_z, ω_x, ω_y: not measured by a planar odometry; **1.0e3** ("unknown"), so a filter that reads them gives them no weight.
- **Pose** (the accumulated estimate, whose real error grows with distance; a constant can only describe it for a reference excursion). Proposed reference: 10 m of travel and one full turn (about the M9 factory-world scale, an assumption):
  - x, y: σ = 0.01 × 10 m = 0.1 m → variance **0.01** m².
  - yaw: σ = 0.02 × 2π rad = 0.126 rad (7.2°) → variance **0.0158** rad².
  - z, roll, pitch: **1.0e3** ("unknown", planar robot).
- Reasonableness: the measured simulated errors (TEST-M2-05/-06, dry runs 2026-11-13) are 100–1000× smaller than these σ, so the values are deliberately conservative for the ideal simulation (DEC-042 rationale). Which fields M6 fuses, and whether it uses the pose or only the twist, is an M6 decision.

### 3.3b CALC-M4-05: TEST-M4-09 predictions (Calculated 2026-11-13, before the TEST-M4-09 runs)
With a multiplier, the controller both commands the wheels and integrates the odometry with the wrong value (§3.1), while Gazebo moves the true geometry (r = 0.075 m, b = 0.400 m). Odometry therefore reports the commanded motion, and the truth differs from it. Errors are odometry minus ground truth, as in §3.4.
- **R: both radii × 1.01 (target TEST-M4-04, straight).** Each wheel turns v/(1.01 r), so the true travel is the odometry travel ÷ 1.01. Distance error = **+1.00 %** of the true distance (bound 0.5 %).
- **B: separation × 1.02 (target TEST-M4-05, rotation).** The wheel-arc difference is ω·1.02b·t; truth ψ = arc difference / b, odometry ψ = arc difference / 1.02b. Yaw error = (1/1.02 − 1) × ψ_true = **−1.961 % of the true turn**, about ∓7.06° for a ±360° turn (bound 1°).
- **L: left radius × 1.005 (target TEST-M4-06, square), k = 1.005.**
  - Straight legs: the left wheel turns v/(k r), so the left wheel travels 1/k as far as the right; the robot curves left by (1 − 1/k)/b per metre of true centre travel times 2k/(k+1), i.e. +0.012469 rad/m, while odometry reports 0. Error per metre = **−0.012469 rad/m (−0.714°/m)**.
  - In-place turns: the true turn is the odometry turn × (k+1)/(2k). Error = **+0.0024938 × the true turn angle**.
  - Square (4 legs of about 0.98 m, the measured TEST-M2-05 leg, L = 3.92 m): turns ≈ ψ_total − 0.0489 rad. Predicted yaw error: **CCW −1.91°, CW −3.71°** (bound 1°). CW and CCW differ because the turn term changes sign with the turn direction and the leg term does not, which is the UMBmark separation.
- **Acceptance (DEC-044):** each target criterion FAILs, and the measured error is within ± 25 % of its prediction. The prediction uses the run's own ground-truth turn (B) and the measured leg length (L).

### 3.4 CALC-M4-03: measurement limits
- *Ground truth:* the `amr` pose from Gazebo `/world/empty/pose/info`, about 59 Hz (M2 harness). At 0.2 m/s it moves 3.4 mm between samples. **Proposal:** compare odometry with ground truth only at **rest points**, after the robot has stopped and settled (the M2 rest rule). This makes the comparison independent of the timing of the two streams. Interpolated values in motion are INFO only.
- *Frame alignment:* `odom` starts at the spawn pose. The ground-truth path is expressed relative to the spawn pose (the M2 method), so both paths start at (0, 0, 0).
- *Encoder resolution:* ideal (DEC-033). For reference, a 4096-count/rev encoder would resolve 0.115 mm of travel and 0.016° of heading per count (CALC-M3-03). Both are negligible at the proposed bounds.

## 4. Design items (**decided 2026-11-13**: OPEN-19 = DEC-042 (c), OPEN-20 = DEC-043 (b), OPEN-21 = DEC-044, OPEN-22 = DEC-045 (a))
| ID | Item | Options | Recommendation (Proposed) |
|---|---|---|---|
| OPEN-19 | Odometry covariance | (a) leave the zero defaults and decide in M6; (b) constant diagonals derived from the M4 **measurements** (tiny in an ideal simulation, so a filter would over-trust odometry); (c) constant diagonals from an **Assumed realistic** error model, e.g. 1 % of distance and 2 % of rotation, labelled as an assumption and revisited in M6 and M13 | **(c)**. It gives M6 sensible weights. The measured simulated error is recorded beside it to show that the values are conservative. Values are fixed after I choose the model |
| OPEN-20 | Error realism in M4 | (a) ideal simulation only; (b) ideal simulation, plus sensitivity tests with injected calibration errors through the controller's `*_multiplier` parameters in a **test-only** config; (c) an encoder-emulation node with quantization, noise and slip (the DEC-033 alternative) | **(b)**. No new node, no change to the product configuration. It proves that the tests detect real errors. (c) remains an option for M13 |
| OPEN-21 | Test trajectories and error bounds | the proposal in §8 (straight, rotation, square CW/CCW, circle, twist), or other trajectories or bounds | the §8 proposal: bounds about 10–100× the measured simulated error and 2–10× below the injected errors of TEST-M4-09 |
| OPEN-22 | Test launch configuration | (a) the default M2 launch (empty world, sensors off); (b) sensors on | **(a)**. Faster, and avoids the `gpu_lidar` shutdown hang (TS-029, DEC-039). TEST-M3-11 already showed that sensors do not change the motion |

## 5. Entry criteria and dependencies
- M3 complete (2026-11-04): ✅.
- The DEC-040 test-automation step is complete (2026-11-04): ✅. M4 uses `tools/run_suite.py` and CI.
- The plan is finalized and OPEN-19 to -22 are decided.

## 6. Architecture
Only one product change is planned: the covariance parameters in `controllers.yaml` (OPEN-19). Everything else is test tooling.
```
amr_bringup/config/controllers.yaml        + pose/twist_covariance_diagonal (OPEN-19)
docs/evidence/M4/
  TEST-M4_odom_measure.py                  Gazebo harness: profiles, rest-point comparison
                                           (reuses the M2 ground-truth reader and the shared teardown helper)
  TEST-M4-03_recompute.py                  offline: recomputes odometry from recorded
                                           /joint_states (CALC-M4-01) and compares with /odom
  TEST-M4-03_record.csv                    small recorded run, the CI input
  TEST-M4-09_procedure.sh, _check.py      test-only overrides generated at run time (OPEN-20 (b); see §12)
  TEST-M4-12_consistency_check.py          record and configuration checker (DEC-041 rules; not published)
tools/run_suite.py                         + 'm4' suite; TEST-M4-03 and -12 added to 'ci'
```
Data path, unchanged from M2: Gazebo wheel joints → `gz_ros2_control` → `diff_drive_controller` → `/diff_drive_controller/odom` and TF `odom → base_footprint`.

## 7. Task breakdown (finalized 2026-11-13)
| Task | Objective and deliverables | Tests | Depends on |
|---|---|---|---|
| **A: Kinematics and harness** | Read the integration rule from the 4.42.1 source and record it in §3.1. Write the odometry harness (profiles, rest-point comparison) and the offline recomputation checker with its recorded input | TEST-M4-03 (TEST-M4-02 harness mode written and dry-run; its formal run is in Task B, because it checks the DEC-042 covariance) | Plan finalized |
| **B: Covariance configuration** | Set the OPEN-19 covariances in `controllers.yaml`, rebuild, and run the M2/M3 regression | TEST-M4-01, -02, -10 (partly) | A; OPEN-19 |
| **C: Accuracy** | Straight, rotation, square CW/CCW, circle, twist, each 3 runs | TEST-M4-04 to -08 | A; OPEN-21, -22 |
| **D: Sensitivity and closeout** | Injected-error runs, regression, consistency checker, `m4` suite and CI, records | TEST-M4-09, -10, -11, -12 | B, C; OPEN-20 |

## 8. Tests (criteria Accepted: DEC-044, 2026-11-13)
Procedures and status: `test_plan.md` §9; evidence goes to `docs/evidence/M4/`. Each Gazebo test runs **3 times**, and every run must pass. All errors are odometry minus ground truth at a rest point (§3.4).
| Test | Requirement | Profile / method | Proposed criterion |
|---|---|---|---|
| TEST-M4-01 | REQ-M4-09 | Build; M1 default expansion byte-identical; M2 controller configuration unchanged except the covariances | Build clean; identity holds |
| TEST-M4-02 | REQ-M4-02, -07 | `/diff_drive_controller/odom`: frames, rate, stamps, covariance; TF publishers of `odom → base_footprint` | `odom`/`base_footprint`; 50 Hz ± 2 %; sim-time stamps; covariance equals OPEN-19; exactly one TF publisher; TF equals odometry within 1 mm / 0.1° |
| TEST-M4-03 | REQ-M4-01 | Offline: recompute odometry from the recorded `/joint_states` with CALC-M4-01 and compare with the recorded `/odom` (runs in CI) | Position within 1 mm and yaw within 0.01° over the whole record |
| TEST-M4-04 | REQ-M4-03 | Straight: +0.2 m/s for 10 s (2 m), stop; then −0.2 m/s back | Distance error ≤ 0.5 % (10 mm); heading error ≤ 0.5° |
| TEST-M4-05 | REQ-M4-04 | Rotation: +0.5 rad/s for 4π s (360°), stop; then −0.5 rad/s back | Yaw error ≤ 1.0° per turn; translation ≤ 20 mm |
| TEST-M4-06 | REQ-M4-05 | Square 1 m × 1 m, stop-and-turn (90° turns at 0.5 rad/s), CW and CCW (the UMBmark pattern, which separates the radius and track errors) | End-point position error ≤ 20 mm; yaw error ≤ 1.0°; CW and CCW recorded separately |
| TEST-M4-07 | REQ-M4-05 | Circle: v = 0.2 m/s, ω = 0.2 rad/s (R = 1 m), one turn (10π s, 6.28 m) | End-point position error ≤ 20 mm; yaw error ≤ 1.0° |
| TEST-M4-08 | REQ-M4-06 | Twist: published odometry velocity vs ground-truth body velocity in cruise (straight and rotation legs) | Mean within ± 2 %; sign correct |
| TEST-M4-09 | REQ-M4-08 | Sensitivity: rerun TEST-M4-04/-05/-06 with test-only overrides: both radii × 1.01; track × 1.02; left radius × 1.005 | Each override makes its target test FAIL, with the error predicted by CALC-M4-02 within ± 25 % (expected: 20 mm on 2 m; 7.2° per 360°; square drift per CALC-M4-02). The product configuration is untouched |
| TEST-M4-10 | REQ-M4-09 | Regression through the runner: the M2 suite, and the M3 static checks | All PASS |
| TEST-M4-11 | REQ-M4-02 | RViz: the odometry trail and the TF tree during the square (observed by me) | Trail closes visibly; no TF jumps |
| TEST-M4-12 | REQ-M4-10, -11 | Consistency checker (DEC-041: state words and links, no restated numbers); `m4` suite present; TEST-M4-03 and -12 in CI | Zero mismatches; CI PASS |

Basis of the bounds (OPEN-21): the measured simulated errors are about 0.01 % (§3.3), so 0.5 % and 1° leave a margin of 10–100× against run-to-run variation. The injected errors of TEST-M4-09 produce errors 2–7× above the bounds, so the bounds are tight enough to catch them. A real robot would need wider bounds; that belongs to M13.

## 9. Requirements (owner: `docs/requirements.md` § M4, from 2026-11-13; this list is the original draft)
| ID | Requirement |
|---|---|
| REQ-M4-01 | The odometry integration matches the documented kinematics (CALC-M4-01) with the configured r and b |
| REQ-M4-02 | Odometry is published on `/diff_drive_controller/odom` (`odom` → `base_footprint`, 50 Hz, sim time), with one TF publisher of `odom → base_footprint` |
| REQ-M4-03 | Linear odometry accuracy within the OPEN-21 bound |
| REQ-M4-04 | Rotational odometry accuracy within the OPEN-21 bound |
| REQ-M4-05 | Closed-path (square and circle) accuracy within the OPEN-21 bounds |
| REQ-M4-06 | Odometry velocity agrees with ground truth |
| REQ-M4-07 | The odometry covariance is configured per OPEN-19 and is not zero |
| REQ-M4-08 | The accuracy tests detect injected calibration errors of the CALC-M4-02 size |
| REQ-M4-09 | M1 to M3 behaviour unchanged |
| REQ-M4-10 | Records, configuration and evidence are consistent under DEC-041 |
| REQ-M4-11 | M4 runs through `tools/run_suite.py`; its GPU-free checks run in CI |

## 10. Risks
- *An almost ideal simulation gives near-zero errors, so the tests could pass vacuously.* Mitigation: TEST-M4-09 (injected errors must fail), and limits stated for M13.
- *Caster scrub during turns* (TS-014 contact history) could move the robot without wheel rotation. Mitigation: the square and circle measure it; the translation during rotation is checked (TEST-M4-05).
- *Timing between ground truth and odometry.* Mitigation: rest-point comparison (§3.4).
- *The covariance choice biases M6.* Mitigation: OPEN-19 labels the values as Assumed, with a named revisit in M6.
- *A sensitivity override leaks into the product configuration.* Mitigation: test-only files under `docs/evidence/M4/`; TEST-M4-01 checks that the product configuration differs from M2 only in the covariances.
- *The upstream shutdown hang (TS-029)* with sensors on. Mitigation: OPEN-22 (a); DEC-039 applies if it occurs.
- *Long profiles at a low real-time factor.* Mitigation: sim-time evaluation; RTF logged; runs below RTF 0.5 invalid (M2 rule).

## 11. Exit criteria
M4 is complete only when:
- TEST-M4-01 to -12 are PASS, with results in `TEST_RESULTS.md` and evidence in `docs/evidence/M4/`. Failures are kept, with TS entries and re-tests.
- OPEN-19 to -22 are decided in `DECISIONS.md`.
- The configuration, the documents and the checker agree (TEST-M4-12), and CI is green.
- The roadmap and records are updated and the M4 Tasks are done.

## 12. Implementation record
- 2026-11-13: plan finalized with the §4 recommendations (DEC-042 to DEC-045). Moving the simulation closer to realistic is recorded as a follow-up in DEC-043, not M4 scope.
- 2026-11-13, Task A: integration rule read from the 4.42.1 source and recorded in §3.1 (exact arc integration with an RK2 fallback; multipliers; twist rolling mean). Harness, procedure and recomputation checker committed (`0ca7ee4`); TS-035 found and handled in a dry run. TEST-M4-03 PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4 Task A). Task A complete.
- 2026-11-13, Task B: covariance values derived (CALC-M4-04) and accepted as proposed; written to `controllers.yaml` (`76a67a2`). TEST-M4-01 and TEST-M4-02 PASS; CI green ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4 Task B). Task B complete. The motion regression is TEST-M4-10 (Task D).
- 2026-11-13, Task C: TEST-M4-04 to -08 PASS ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4 Task C). Task C complete. Afterwards I watched the square and the circle in a Gazebo GUI + RViz demo (scratch RViz config, not evidence).
- 2026-11-13, Task D, preparation: `sim.launch.py` argument `controllers_file` (default unchanged); `rviz/odometry.rviz` (TEST-M4-11); procedure options `SHOW=1` (GUI + RViz, screenshots; my requests: show every simulation test, keep screenshots as evidence) and `CONTROLLERS=`; `tools/sim_capture.py`; CALC-M4-05 predictions; TEST-M4-09 procedure and checker. Deviation from DEC-043 wording: the override files are generated from the product file at run time and logged as a diff, instead of committed copies, so they cannot drift from it. A 1-run dry run (scratch) matched every prediction within 1 % and found one procedure defect before the formal run: `pgrep -E` is not a valid option on this system, so the leftover check was ineffective in that dry run; fixed (pgrep patterns are already extended regular expressions).
- 2026-11-13, Task D: TEST-M4-09 PASS on `ecbf64c`, run with the GUI and RViz shown, with screenshots ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4 Task D). Afterwards `odometry.rviz` was adjusted (whole square in view, no Views panel) because the Gazebo window covered part of the RViz shots. Remaining: TEST-M4-10, -11, -12.
- 2026-11-13, Task D: the first run's RViz screenshots were partly covered by the Gazebo window (TS-036); removed at my request. TEST-M4-09 R1 PASS on `4db5197` with the fixed layout and screen recording; agrees with the first run. Gallery rule : pictures are committed only after I review them (`docs/gallery/README.md`).
- 2026-11-13, Task D: TEST-M4-10 PASS on `16a5255` (runner suites static and regression; M2 entries with the Gazebo GUI, M3 sensor entries headless) ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4 Task D). TS-037 (`colcon version-check` network hang) fixed on the way.
- 2026-11-13, Task D: TEST-M4-12 implementation: `docs/evidence/M4/TEST-M4-12_consistency_check.py` (DEC-041 rules; its first run found restated results in M4 lines of my planning notes and this record, and a TEST-M4-10 status without its link; all reworded, the numbers stay in `TEST_RESULTS.md`), mutation check of the checker, runner suite `m4`, TEST-M4-03 added to `ci` and TEST-M4-12 to `records`. `TEST-M4_procedure.sh` derives the gallery test ID with any run tag.
- 2026-11-13, Task D: TEST-M4-11 PASS on `adfc7ea`, observed by me (odometry trail and TF in RViz during the CCW and CW squares) ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4 Task D).
- 2026-11-13, Task D: TEST-M4-12 PASS (local `records` run on `f8fa525`; CI code push and manual dispatch with records, both green) ([TEST_RESULTS.md](../../TEST_RESULTS.md) § M4 Task D). Every M4 test has now passed.
- 2026-11-13, closeout: M4 closed. Open follow-ups outside M4: the DEC-043 realism additions, TS-035 root cause.
