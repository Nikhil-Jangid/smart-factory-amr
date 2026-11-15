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
4. Size budget: videos short (H.264 MP4, CRF 18; about 0.1–0.4 MB each so far), a few per milestone; no Git LFS (paid storage).

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

Finalized on 2026-11-13 (first batch: 22 PNG, 18 MP4, 5.7 MB; second batch, TEST-M4-11: 4 PNG, 4 MP4, 1.6 MB, captured on `adfc7ea`). The re-created demonstrations were made on the robot code of `4db5197` (`amr_ws/src` unchanged since), with the capture tools as committed in `1d426eb`; the TEST-M4-09 R1 captures come from the formal run on `4db5197`. Videos converted from WebM to MP4 afterwards (`2b5037f`).

M5: TEST-M5-02 R1 captures (2 PNG, 2 MP4, 0.9 MB) accepted on 2026-11-15, from the formal run on `8130ee8`; the Gazebo and RViz windows were arranged side by side before the recording started (`LAYOUT_FLAG` option of the M5 procedure), and the camera view was chosen from trial screenshots.
M5: TEST-M5-03 attempt 1 captures (2 PNG, 2 MP4, 8.6 MB) accepted on 2026-11-15, from the formal run on `59ee7f0`; windows side by side, camera view as TEST-M5-02 R1.
M5: TEST-M5-06 attempt 1 captures (2 PNG, 2 MP4) accepted on 2026-11-15, from the formal run on `6cb8f23`; windows side by side, camera view as TEST-M5-02 R1. TEST-M5-09 attempt 1 captures (2 PNG, 2 MP4) accepted on 2026-11-15, from the formal run on `7f3d65b`; one laptop screen, so the RViz window is partly covered on its left by the Gazebo window.

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
