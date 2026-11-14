# Engineering Documentation Index

This directory holds the detailed engineering records. The root files (`ROADMAP.md`, `DECISIONS.md`, `TEST_RESULTS.md`) stay concise; the documents here hold the detail and are linked from them.

## Source of truth

| Information | Authoritative location |
|---|---|
| Milestones and current status | [`../ROADMAP.md`](../ROADMAP.md) |
| Engineering decisions | [`../DECISIONS.md`](../DECISIONS.md) |
| Results of tests actually performed | [`../TEST_RESULTS.md`](../TEST_RESULTS.md) |
| Requirements, acceptance criteria, traceability | [`requirements.md`](requirements.md) |
| Environment and dependency versions | [`environment.md`](environment.md) |
| Mechanical geometry and placement | [`design/mechanical_geometry.md`](design/mechanical_geometry.md); dimensioned drawing [`design/amr_geometry_drawing.svg`](design/amr_geometry_drawing.svg) (generated from the Xacro by `tools/geometry_drawing.py`) |
| Mass budget and inertia calculations | [`design/mass_inertia.md`](design/mass_inertia.md) |
| Contact/friction, motion limits, controller interface, motion-test criteria (M2) | [`design/motion_control.md`](design/motion_control.md) |
| Sensor models, placement, integration and test criteria (M3; decisions DEC-030 to DEC-037) | [`design/sensors.md`](design/sensors.md); numeric sensor values: named properties in `amr_description/urdf/amr.sensors.xacro` (since M3 Task A) |
| Coordinate frames, links, joints, TF | [`design/frames_and_tf.md`](design/frames_and_tf.md) |
| ROS architecture and milestone boundaries | [`architecture/ros_architecture.md`](architecture/ros_architecture.md) |
| Test strategy, procedures, planned tests | [`testing/test_plan.md`](testing/test_plan.md) |
| Milestone plans and implementation records | [`milestones/`](milestones/): [`M1_custom_amr.md`](milestones/M1_custom_amr.md) (closed), [`M2_basic_movement.md`](milestones/M2_basic_movement.md) (closed), [`M3_sensors.md`](milestones/M3_sensors.md) (closed), [`M3-M4_test_automation.md`](milestones/M3-M4_test_automation.md) (DEC-040, in progress) |
| Troubleshooting and known issues | [`troubleshooting.md`](troubleshooting.md) |
| Evidence files and evidence policy | [`evidence/README.md`](evidence/README.md) |
| Screenshots and recordings, by milestone and test (demonstration material) | [`gallery/README.md`](gallery/README.md) |

Rules:
- Each fact has one owner. Other documents link to it instead of copying it.
- Until implementation existed, M1 design parameters were owned by the parameter table in [`design/mechanical_geometry.md` §2](design/mechanical_geometry.md#2-parameter-table-authoritative). Ownership passed to the properties file on 2026-10-21 (next rule).
- Test-state definitions (`PLANNED`, `NOT RUN`, `PASS`, `FAIL`, `BLOCKED`) are owned by [`testing/test_plan.md` §1](testing/test_plan.md#1-test-states).
- Once implementation exists, numeric robot parameters are owned by the Xacro properties file `amr_ws/src/amr_description/urdf/amr_properties.xacro` (created 2026-10-21). Design documents keep the tables with rationale and status labels and must name the matching property. A consistency test (TEST-M1-08) checks that they agree.
- Planned tests live in `testing/test_plan.md`; only executed tests are recorded in `TEST_RESULTS.md`.
- Test status, from M4 on (DEC-041): result details (numbers, run counts, diagnoses, evidence links) are only in `TEST_RESULTS.md`. Other files give the state word, the date and a link.

## Parameter status labels

| Label | Meaning |
|---|---|
| **Selected** | Chosen by me as the design value |
| **Proposed** | Candidate value under review; may change |
| **Assumed** | Simulation assumption, not measured (e.g. component masses) |
| **Calculated** | Derived analytically from other values; valid only while its inputs are unchanged |
| **Measured** | Obtained from a test or simulation output (cite the test ID) |
| **Verified** | Confirmed by a passed test (cite the test ID) |

## Identifier conventions

| Prefix | Example | Defined in |
|---|---|---|
| `REQ-Mx-nn` | REQ-M1-06 | `requirements.md` |
| `DEC-nnn` | DEC-011 | `../DECISIONS.md` |
| `CALC-Mx-nn` | CALC-M1-03 | `design/mass_inertia.md`, `design/mechanical_geometry.md` (M1); `design/motion_control.md` (M2) |
| `OPEN-nn` | OPEN-01 | Unresolved design items, in the milestone plan that raises them: OPEN-01 to -07 in `milestones/M1_custom_amr.md`, OPEN-08 onward in `milestones/M2_basic_movement.md` |
| `REQ-TA-nn`, `TEST-TA-nn` | REQ-TA-03 | Test-automation step between M3 and M4 (DEC-040): `requirements.md`, `testing/test_plan.md` §8 |
| `TEST-Mx-nn` | TEST-M1-04 | `testing/test_plan.md` (procedure), `../TEST_RESULTS.md` (result) |
| `TS-nnn` | TS-001 | `troubleshooting.md` |

## Units and conventions
SI units throughout (m, kg, s, rad, kg·m²). Coordinate frames follow ROS REP-103 (+X forward, +Y left, +Z up) and REP-105 frame naming. See [`design/frames_and_tf.md`](design/frames_and_tf.md).
