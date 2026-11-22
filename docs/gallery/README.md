# Gallery: screenshots and recordings

Pictures and videos of the simulated AMR, sorted by milestone and test ID, for demonstrations and as a visual record of
what was tested (2026-11-13). Layout: `docs/gallery/<milestone>/<TEST-ID>/`.

**This folder is not test evidence.** Test results and their evidence (logs, checker output) are in
[`TEST_RESULTS.md`](../../TEST_RESULTS.md) and [`docs/evidence/`](../evidence/README.md). Each file here is one of:

| Kind | Name pattern | What it is |
|---|---|---|
| **Test-run capture** | `<log name>_a1_gazebo.png`, `_a1_rviz.png`, `_a1_*.mp4` | Taken automatically during attempt 1 of a formal test run with `SHOW=1` (M4 procedures; `tools/sim_capture.py`, `tools/sim_record.sh`). Same run as the logged result. |
| **Original screenshot** | `<TEST-ID>_original_*.png` | Copy of a screenshot recorded during an observed GUI test; the original stays in `docs/evidence/`. |
| **Re-created demonstration** | `<scene>_demo_*.png`, `_demo_*.mp4` | Made afterwards with `tools/demo_capture.sh` on a later revision, to show what an earlier test covered. Earlier tests ran headless, so no original picture exists. **Not the original test run.** |

Common content: `*_gazebo.*` is the Gazebo GUI (the true, simulated motion); `*_rviz.*` is RViz (what the robot's
software sees: the model, TF and, from M4, the odometry trail in the `odom` frame). Videos are H.264 MP4, 15 fps,
recorded per window (plays in every common player, browser and on phones).

## Review rule (2026-11-13)

Nothing is committed here until I have reviewed it, so the repository holds only final pictures and no replaced or
rejected media (Git keeps every committed file in its history).
1. Captures are written to `docs/gallery/_pending/<milestone>/<TEST-ID>/`, which is git-ignored.
2. Every picture and sampled video frames are reviewed; anything with an error status, a covered window, a cut-off trail
   or a missing robot is deleted and re-captured.
3. Accepted files move to `docs/gallery/<milestone>/<TEST-ID>/` and are committed once
   (per milestone or per accepted batch); rejected files are deleted.
4. Size budget: H.264 MP4, CRF 18, native window size. Measured on the accepted media (2026-11-23): M4 about 0.3 MB per video; M5 and M6 navigation runs Gazebo about 0.2–2 MB and RViz about 0.4–10 MB (the costmap and scan layers change every frame); M5 29 MB and M6 80 MB in total. Idle footage before and after the motion is cut with `tools/sim_record.sh trim`. No Git LFS (paid storage).

## Contents (accepted)

| Milestone | Test | Files | Kind | Shows |
|---|---|---|---|---|
| M1 | [TEST-M1-04](M1/TEST-M1-04/) | `m1_rviz_model_demo_rviz.png` | Re-created demonstration | The AMR model in RViz with its TF frames (base_footprint, base_link, wheels, caster, LiDAR mount), status OK |
| M1 | [TEST-M1-06](M1/TEST-M1-06/) | `m1_gazebo_spawn_demo_gazebo.png` | Re-created demonstration | The M1 model spawned in Gazebo, at rest on the ground |
| M2 | [TEST-M2-05](M2/TEST-M2-05/) | `m2_linear_demo_{gazebo,rviz}.{png,mp4}` | Re-created demonstration | Forward 0.2 m/s for 5 s, stop 3 s, reverse 5 s (the TEST-M2-05 profile) |
| M2 | [TEST-M2-06](M2/TEST-M2-06/) | `m2_rotate_demo_{gazebo,rviz}.{png,mp4}` | Re-created demonstration | In-place rotation ±0.5 rad/s, one turn each way (the TEST-M2-06 profile) |
| M3 | [TEST-M3-10](M3/TEST-M3-10/) | `TEST-M3-10_original_{gazebo,rviz}.png` | Original screenshot | Sensor world in Gazebo and the LiDAR scan in RViz, from the observed TEST-M3-10 (2026-11-04) |
| M3 | [TEST-M3-10](M3/TEST-M3-10/) | `m3_lidar_demo_{gazebo,rviz}.{png,mp4}` | Re-created demonstration | The robot turning in the sensor world; the LiDAR scan outlines the target boxes in RViz |
| M4 | [TEST-M4-06](M4/TEST-M4-06/) | `m4_square_demo_{gazebo,rviz}.{png,mp4}` | Re-created demonstration | The 1 m square, stop and turn; the odometry trail closes in RViz |
| M4 | [TEST-M4-07](M4/TEST-M4-07/) | `m4_circle_demo_{gazebo,rviz}.{png,mp4}` | Re-created demonstration | The circle, v 0.2 m/s, ω 0.2 rad/s |
| M4 | [TEST-M4-09](M4/TEST-M4-09/) | `TEST-M4-09-R1_<case>_a1_{gazebo,rviz}.{png,mp4}` (case R_straight, B_rotate, L_square_ccw, L_square_cw) | Test-run capture (R1) | The injected-calibration-error runs: Gazebo shows the true motion, RViz the odometry with the wrong calibration. The videos start 1–4 s into the first motion (stale frames cut, TS-036) |
| M4 | [TEST-M4-11](M4/TEST-M4-11/) | `TEST-M4-11_square_{ccw,cw}_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | The two squares I watched for TEST-M4-11: Gazebo shows the true motion, RViz the odometry trail in `odom` closing the 1 m square, with the robot model and TF |
| M5 | [TEST-M5-02](M5/TEST-M5-02/) | `TEST-M5-02-R1_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture (R1) | The SLAM interface test: the mapping arena from above in Gazebo; in RViz the map that SLAM Toolbox builds while the robot drives 1 m and turns (scan in red, map frame fixed) |
| M5 | [TEST-M5-03](M5/TEST-M5-03/) | `TEST-M5-03_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | The mapping-accuracy run (TEST-M5-03/-04, attempt 1, whose map became the reference map): the robot drives the 28.8 m test route in Gazebo while RViz shows SLAM Toolbox building the map |
| M5 | [TEST-M5-06](M5/TEST-M5-06/) | `TEST-M5-06_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | Mapping with deliberately wrong odometry (TEST-M5-06, attempt 1): the robot drives the test route in Gazebo while, in RViz, SLAM Toolbox corrects the drifting odometry and builds a clean map |
| M5 | [TEST-M5-09](M5/TEST-M5-09/) | `TEST-M5-09_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | Live mapping watched by me (TEST-M5-09): the robot drives the test route in Gazebo while, in RViz, SLAM Toolbox grows the map and the pose graph and the robot returns to its start |
| M6 | [TEST-M6-02](M6/TEST-M6-02/) | `TEST-M6-02_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | The localization interface test: AMCL starts at the known pose on the reference map; RViz shows the map, the particle cloud and the scan on the walls |
| M6 | [TEST-M6-03](M6/TEST-M6-03/) | `TEST-M6-03-{forward,reverse}_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | Localization accuracy on the test route, both directions: the robot drives in Gazebo while, in RViz, the AMCL pose and the scan stay on the map |
| M6 | [TEST-M6-04](M6/TEST-M6-04/) | `TEST-M6-04_a1_{gazebo,rviz}.png`, `TEST-M6-04_a1_rviz.mp4` | Test-run capture | Wrong-start recovery: AMCL starts 0.5 m and 15° off, then the particle cloud converges on the first leg (no Gazebo video for this run) |
| M6 | [TEST-M6-05](M6/TEST-M6-05/) | `TEST-M6-05-{forward,reverse}_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | Localization with deliberately wrong wheel odometry (TEST-M4-09 errors): AMCL keeps the pose on the map while the odometry drifts |
| M6 | [TEST-M6-06](M6/TEST-M6-06/) | `TEST-M6-06-{forward,reverse}_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | Localization with unmapped boxes in the arena: the scan shows the boxes, the pose stays on the map |
| M6 | [TEST-M6-07](M6/TEST-M6-07/) | `TEST-M6-07{,-R1}_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | Wheel odometry + IMU fusion with the EKF: in RViz the raw odometry trail drifts while the fused estimate and AMCL stay on course (original run and R1) |
| M6 | [TEST-M6-10](M6/TEST-M6-10/) | `TEST-M6-10-{wrongstart,global}_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | The RViz test I observed: wrong-start convergence, and the global-localization demonstration, where the particles spread over the map and settle on a pose turned by a half turn |
| M7 | [TEST-M7-02](M7/TEST-M7-02/) | `TEST-M7-02-R1_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture (R1) | The Nav2 integration gate: one short goal; RViz shows the plan, both costmaps and the footprint |
| M7 | [TEST-M7-03](M7/TEST-M7-03/) | `TEST-M7-03_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | Single goals G1 to G6 in sequence: each planned path in RViz and the robot driving it in Gazebo |
| M7 | [TEST-M7-04](M7/TEST-M7-04/) | `TEST-M7-04_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | The through-poses route G1 → G3 → G5 as one path |
| M7 | [TEST-M7-05](M7/TEST-M7-05/) | `TEST-M7-05-R1_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture (R1) | Invalid goals (inside pillar P1, outside the map) refused: the robot does not move |
| M7 | [TEST-M7-06](M7/TEST-M7-06/) | `TEST-M7-06_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | A goal cancelled after 1 m: the robot stops |
| M7 | [TEST-M7-09](M7/TEST-M7-09/) | `TEST-M7-09_a1_{gazebo,rviz}.{png,mp4}` | Test-run capture | The RViz test I observed: goals sent with the Nav2 goal tool, then my deliberate probe on the low box L1: the robot drives into it (invisible to the LiDAR) and localization is lost (TS-058). Trimmed to the motion |

Finalized on 2026-11-13 (first batch: 22 PNG, 18 MP4, 5.7 MB; second batch, TEST-M4-11: 4 PNG, 4 MP4, 1.6 MB, captured on `adfc7ea`). The re-created demonstrations were made on the robot code of `4db5197` (`amr_ws/src` unchanged since), with the capture tools as committed in `1d426eb`; the TEST-M4-09 R1 captures come from the formal run on `4db5197`. Videos converted from WebM to MP4 afterwards (`2b5037f`).

M5: TEST-M5-02 R1 captures (2 PNG, 2 MP4, 0.9 MB) accepted on 2026-11-15, from the formal run on `8130ee8`; the Gazebo and RViz windows were arranged side by side before the recording started (`LAYOUT_FLAG` option of the M5 procedure), and the camera view was chosen from trial screenshots.
M5: TEST-M5-03 attempt 1 captures (2 PNG, 2 MP4, 8.6 MB) accepted on 2026-11-15, from the formal run on `59ee7f0`; windows side by side, camera view as TEST-M5-02 R1.
M5: TEST-M5-06 attempt 1 captures (2 PNG, 2 MP4) accepted on 2026-11-15, from the formal run on `6cb8f23`; windows side by side, camera view as TEST-M5-02 R1. TEST-M5-09 attempt 1 captures (2 PNG, 2 MP4) accepted on 2026-11-15, from the formal run on `7f3d65b`; one laptop screen, so the RViz window is partly covered on its left by the Gazebo window.

M6: test-run captures (attempt 1 of each formal GUI run; 20 PNG, 27 MP4, about 83 MB), selected on 2026-11-21 after the M6 closure. Revisions: TEST-M6-02 `8a515c2`; TEST-M6-03 to -06 `f2d344a`; TEST-M6-07 `19200ee`, R1 `c2b6805`; TEST-M6-10 `00f1b75`. The videos are full route length (about 3.5 min each), larger than the earlier milestones' clips.

M7: test-run captures (attempt 1 of each formal GUI run; 12 PNG, 12 MP4, about 32 MB) selected on 2026-11-23, at the M7 closure. Revisions: TEST-M7-02 R1 `2b62a94`; TEST-M7-03, -04 `b8fc601`; TEST-M7-05 R1, -06 `5e3b728`; TEST-M7-09 `66d197f` (procedure mode `observe`, committed in `85cd1e1`), trimmed with `tools/sim_record.sh trim` (5 to 256 s). Capture layout and fixed M5 camera view (DEC-075). The TEST-M7-10 (M710) re-run captures are not committed.

## Recording rule (2026-11-23)

1. **Every formal test of the current milestone that uses the simulation is shown and recorded**, as in M4, M5 and M6:
   run with `SHOW=1`; attempt 1 gets a video of the Gazebo and RViz windows and screenshots of both, into
   `docs/gallery/_pending/<milestone>/<TEST-ID>/`. Tests I observe myself (e.g. TEST-M7-09) are recorded too.
2. **Regression suites and re-runs of earlier formal tests are headless and not recorded by default.** Record one only
   when the record needs the video or pictures as proof or documentation; say why in `TEST_RESULTS.md`.
3. **One recording method everywhere.** Every recording comes from the milestone's shared procedure with `SHOW=1`
   (`TEST-M4_procedure.sh`, `TEST-M5_procedure.sh`, `TEST-M6_procedure.sh`, `TEST-M7_procedure.sh`), which uses
   `tools/sim_record.sh` (started before motion, stopped after it) and `tools/sim_capture.py` (camera `view`/`follow`,
   `shot`). Window layout, Gazebo GUI layout and camera views (DEC-075), frame rate and encoding are the same for every
   test; only the scene differs. A new formal test is added as a mode of that procedure, never as a separate script
   (TS-057). The procedure may be extended, but its recording and teardown code is reused unchanged.
4. Before a formal run, confirm the procedure records (with `SHOW=1`) and has job control (`set -m`, TS-011).

## How to regenerate

From the repository root, after `source /opt/ros/jazzy/setup.bash && source amr_ws/install/setup.bash`, with no other
simulation running:

```bash
bash tools/demo_capture.sh <scene>   # m1_rviz_model m1_gazebo_spawn m2_linear m2_rotate m3_lidar m4_square m4_circle
SHOW=1 bash docs/evidence/M4/TEST-M4_procedure.sh <mode> <runs> <log>   # formal M4 run with GUI, capture of attempt 1
# both write to docs/gallery/_pending/ (git-ignored) until accepted
```

Requirements: X11 windows (the scripts set `QT_QPA_PLATFORM=xcb`; a whole-screen capture is black under Wayland),
`xwininfo`, `xwd`, GStreamer with `ximagesrc`, `vp9enc`, `webmmux` (capture), and ffmpeg with libx264 (MP4) (all present on the development machine,
`docs/environment.md`). Windows must not overlap, because only visible pixels are captured: RViz is started after the
Gazebo window and is 860 px wide so the window manager places it beside Gazebo.

## History

- 2026-11-13: the first TEST-M4-09 screenshots (RViz partly covered by Gazebo) were removed. A first demo batch, corrupted by processes left from the previous scene, was deleted before any commit
  (TS-036). The recordings' first 2–3 s are stale frames and are cut automatically (`tools/webm_trim.py`).
