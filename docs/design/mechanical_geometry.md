# Mechanical Geometry and Component Placement (M1)

**Status:** Design baseline recorded 2026-10-19. The M1 design-review resolutions (DEC-019) were reviewed and finalized on 2026-10-19, and DEC-016 and DEC-017 were accepted the same day. Implemented on 2026-10-21 in `amr_ws/src/amr_description/urdf/`; the generated model matched this table in TEST-M1-03 re-test 1.
**Related:** DEC-011 to DEC-017 · REQ-M1-03, REQ-M1-04, REQ-M1-09, REQ-M1-10 · OPEN-01 to OPEN-03, OPEN-06 ([M1 plan](../milestones/M1_custom_amr.md))

**Since 2026-10-21 the numeric values are owned by `amr_ws/src/amr_description/urdf/amr_properties.xacro`** ([../README.md](../README.md#source-of-truth)). The table in §2 keeps the values with their rationale and status labels and names the matching property. A value is changed in the properties file and in this table together; TEST-M1-08 checks that they agree. *(Until then, this table was the authoritative source.)*

All values are simulation design values, not physical hardware specifications. Units are SI. Frames follow REP-103 (+X forward, +Y left, +Z up); see [frames_and_tf.md](frames_and_tf.md). Status labels are defined in [../README.md](../README.md#parameter-status-labels).

## 1. Reference frame for this document
- `base_footprint`: on the ground plane (z = 0), directly below the midpoint of the drive-wheel axle.
- `base_link`: the axle midpoint, **0.075 m above the ground**. This height is not chosen independently: it follows from DEC-016 (Accepted), which puts `base_link` on the axle, and the Selected `wheel_radius`. Unless stated otherwise, positions below are given in `base_link`.
- Height above ground = z(`base_link`) + 0.075 m.

## 2. Parameter table (authoritative)
"Property" is the Xacro property name in `amr_properties.xacro`. Derived placements (§3) are expressions of these properties in the same file (`chassis_x`, `chassis_z`, `wheel_y`, `caster_z`, `lidar_mount_z`, `base_link_z`).

| Parameter | Property | Value | Status | Source |
|---|---|---|---|---|
| Chassis length (X) | `chassis_length` | 0.450 m | Selected | chosen baseline |
| Chassis width (Y) | `chassis_width` | 0.350 m | Selected | chosen baseline |
| Chassis height (Z) | `chassis_height` | 0.120 m | Selected | chosen baseline |
| Drive arrangement | — | 2 independently driven wheels + 1 rear caster | Selected | chosen baseline |
| Drive wheel radius | `wheel_radius` | 0.075 m | Selected | chosen baseline |
| Drive wheel width | `wheel_width` | 0.035 m | Selected | chosen baseline |
| Wheel track (centre-to-centre) | `wheel_track` | 0.400 m | Selected | DEC-011 |
| Axle offset forward of chassis centre | `axle_offset_x` | 0.100 m | Selected | DEC-012 |
| `base_link` height above ground | — | 0.075 m (= `wheel_radius`) | Calculated (not an independent parameter) | DEC-016 (Accepted) + `wheel_radius` |
| Ground clearance (chassis bottom) | `ground_clearance` | 0.050 m | Selected | OPEN-06, DEC-019; feasibility in CALC-M1-02 |
| Caster type | — | rigid sphere, fixed joint | Selected | DEC-013 |
| Caster sphere radius | `caster_radius` | 0.025 m | Selected | OPEN-01, DEC-019 |
| Caster centre X | `caster_x` | −0.360 m | Selected | OPEN-01, DEC-019; revised from −0.280 m (§4, CALC-M1-13) |
| LiDAR mount | — | passive bracket, laterally centred, near the front of the top platform | Selected | DEC-014 |
| Bracket size (X × Y × Z) | `lidar_bracket_*` | 0.080 × 0.080 × 0.030 m | Selected (DEC-030, 2026-11-03; provisional placeholder until then) | OPEN-03, DEC-019, DEC-030 |
| Bracket centre X | `lidar_mount_x` | +0.070 m | Selected (DEC-030, 2026-11-03; provisional placeholder until then) | OPEN-03, DEC-019, DEC-030 |
| Payload | — | excluded from M1 | Selected | DEC-015 |
| Geometry type | — | primitive shapes only (box, cylinder, sphere), no meshes | Selected | DEC-017 |

## 3. Derived placement (Calculated from §2)

| Item | Expression | Value (`base_link`) | Height above ground |
|---|---|---|---|
| Chassis centre X | −`axle_offset_x` | −0.100 m | — |
| Chassis centre Z | `ground_clearance` + H/2 − r_w | 0.050 + 0.060 − 0.075 = **+0.035 m** | 0.110 m |
| Chassis X extents | −0.100 ∓ 0.225 | **−0.325 m … +0.125 m** | — |
| Chassis Z extents | 0.035 ∓ 0.060 | −0.025 m … +0.095 m | **0.050 m … 0.170 m** |
| Top platform surface | | +0.095 m | 0.170 m |
| Wheel joint origins | (0, ±`wheel_track`/2, 0) | (0, ±0.200, 0) | 0.075 m (axle) |
| Wheel Y extents | 0.200 ∓ 0.0175 | ±0.1825 m (inner face) … ±0.2175 m (outer face) | — |
| Wheel X / Z extents | ±r_w | X −0.075 … +0.075 m | Z 0.000 … 0.150 m |
| Caster centre | (`caster_x`, 0, r_c − r_w) | (−0.360, 0, **−0.050**) | 0.025 m |
| Caster X extents | −0.360 ∓ 0.025 | −0.385 m … −0.335 m | Z 0.000 … 0.050 m |
| Bracket centre (candidate) | platform + h_b/2 | (+0.070, 0, +0.110) | 0.185 m |
| Bracket X extents (candidate) | 0.070 ∓ 0.040 | +0.030 m … +0.110 m | Z 0.170 … 0.200 m |
| `lidar_mount_link` origin (candidate) | bracket top surface | (+0.070, 0, +0.125) | 0.200 m |

## 4. Geometry consistency checks
These are analytical checks of the design values. They do not prove that the simulated model is collision-free or stable; that is the job of TEST-M1-03, -06 and -07.

**CALC-M1-01: chassis longitudinal extents.** The chassis is centred at x = −0.100 m and is 0.450 m long, so it spans −0.100 ± 0.225 = **−0.325 m to +0.125 m**.

**CALC-M1-02: vertical stack and ground clearance.**
- Chassis centre = 0.075 + 0.035 = 0.110 m above ground.
- Chassis bottom = 0.110 − 0.060 = **0.050 m**. Chassis top (platform) = 0.110 + 0.060 = **0.170 m**.
- Wheel top = 2 × 0.075 = 0.150 m, which is 0.020 m below the platform. The wheels therefore do not break the flat payload surface.
- The axle height (0.075 m) is 0.025 m above the chassis bottom, i.e. within the height of the chassis side wall.
- *Feasible ground-clearance window (OPEN-06, Calculated 2026-10-19):* the wheel tops stay at or below the platform if 0.150 ≤ c + 0.120, i.e. c ≥ 0.030 m. The axle stays above the chassis bottom, so the wheel can mount on the side wall, if c < 0.075 m. The Selected c = 0.050 m leaves 20 mm and 25 mm of margin to these two limits.

**CALC-M1-03: lateral wheel-to-chassis clearance.**
- Wheel inner face = 0.400/2 − 0.035/2 = 0.1825 m. Chassis side = 0.350/2 = 0.175 m.
- **Nominal gap = 0.0075 m (7.5 mm) per side.**
- Overall width across the wheel outer faces = 0.400 + 0.035 = **0.435 m**.
- The gap is nominal only. It ignores tyre compliance, hub or axle hardware, and simulator contact margins. OPEN-02 is accepted (DEC-019); the gap is checked by dimensions in TEST-M1-03 and visually in TEST-M1-06.
- This is a **geometric** requirement, not a demonstrated physics risk in M1. In the installed SDFormat 1.11 specification, `self_collide` defaults to `false`, and "links connected by a joint will never collide". Each wheel is joint-connected to the chassis body. Contact between them is therefore not expected in simulation (see [frames_and_tf.md §4](frames_and_tf.md#4-gazebo-specific-behaviour); confirmed on the real model on 2026-10-21 by TEST-M1-03 re-test 1 and TEST-M1-06).
- *Correction recorded:* an earlier proposal used a 0.300 m track. That would put the wheels at ±0.1325 … ±0.1675 m, inside the 0.175 m chassis half-width, so the wheels would overlap the chassis box. The track was changed to 0.400 m (DEC-011).

**CALC-M1-04: ground contacts.** All three supports must reach z = −0.075 m in `base_link` (the ground):
- Drive wheels: 0 − 0.075 = −0.075 m.
- Caster (r_c = 0.025 m, centre z = −0.050 m; Selected): −0.050 − 0.025 = −0.075 m. The sphere is tangent to the ground.

With three point contacts the ideal model is statically determinate (no rocking).

**CALC-M1-13: caster-to-chassis separation** (revised 2026-10-19; OPEN-01 resolved: Selected, DEC-019).
- *Problem with the earlier candidate (x = −0.280 m):*
  - The sphere (x −0.305 … −0.255 m) lay under the chassis footprint.
  - Its top (0.050 m above ground) exactly touched the chassis underside (0.050 m), so there was zero clearance.
- *Selected position (x = −0.360 m, z = −0.050 m, r = 0.025 m):*
  - The sphere spans x −0.385 … −0.335 m, entirely behind the chassis rear face (−0.325 m).
  - The closest chassis feature is the bottom-rear edge at (x −0.325, height 0.050 m). Its distance from the sphere centre (x −0.360, height 0.025 m) is √(0.035² + 0.025²) = 0.0430 m.
  - Clearance = 0.0430 − 0.025 = **0.018 m (18.0 mm)**.
  - The horizontal gap to the rear face alone is 0.010 m, but the face ends at the chassis bottom (0.050 m), above the sphere's centre height.
- *Consequences:*
  - Rear overhang of 0.060 m beyond the chassis.
  - Overall length becomes 0.510 m (CALC-M1-05).
  - The caster's share of the weight changes (CALC-M1-11).
  - Swept radius about `base_link` (the in-place rotation centre), Calculated 2026-10-19: the chassis rear corners (−0.325, ±0.175) already give 0.369 m. The caster rear point (−0.385, 0) raises it to **0.385 m** (+16 mm, +4.3 %).
  - A real caster at this position would need a mounting arm or bracket behind the chassis. That arm is **not modelled** and has **not been validated physically**; its mass is assumed to be part of the 0.2 kg caster assembly.
- *Alternatives considered and not selected (DEC-019):*
  - (a) Keep the caster under the chassis with a smaller sphere, e.g. r = 0.020 m, which would leave 10 mm to the underside. It would require every dependent calculation to be redone.
  - (b) Increase ground clearance.
  - (c) Accept the original tangent contact as a modelled mounting interface. In simulation the fixed caster is **expected** to be lumped into the same SDF link as the chassis, so it would not produce a contact force against it (frames_and_tf.md §4; based on the spec and a generic probe; the lumping was later observed on the AMR in TEST-M1-03 re-test 1). But zero clearance is a real interference in any physical reading of the design.

**CALC-M1-05: overall envelope** (caster Selected; bracket height provisional until 2026-11-03, Selected since then by DEC-030, confirmed by DEC-037).
- Length = front of chassis (+0.125 m) to rear of caster (−0.385 m) = **0.510 m** (0.450 m chassis + 0.060 m caster overhang).
- Width = **0.435 m** (across the wheel outer faces).
- Height = **0.200 m** to the bracket top (0.170 m to the platform).

The future Nav2 footprint (M7) must cover the caster overhang as well as the wheels.

**CALC-M1-14: LiDAR bracket placement** (provisional placeholder, OPEN-03, DEC-019; *finalized unchanged 2026-11-03, DEC-030: scan plane 0.230 m, CALC-M3-01 in [sensors.md](sensors.md)*).
- The bracket spans x +0.030 … +0.110 m, which is 0.015 m behind the chassis front edge (+0.125 m), and y ±0.040 m, well inside the chassis width.
- Its base sits on the platform (0.170 m). That is an intended mounting interface, not a clearance.
- It lies above the wheel tops (0.150 m), so in the design geometry it does not overlap the wheels.
- The bracket dimensions have no basis beyond being a placeholder. The sensor size, scan-plane height, and field of view are M3 decisions. M3 can attach the sensor through a `lidar_mount_link → laser_frame` offset without moving the mount.
- Consequence to record for M3/M8: a scan plane at or above 0.200 m will not detect obstacles lower than the scan plane.

## 5. Sketches (not to scale)

Side view (+X to the right), heights above ground:
```
 0.200 ┤                       ┌──┐   ← lidar bracket (candidate, x = +0.07)
 0.170 ┤      ┌────────────────┴──┴─┐ ← top platform
       │      │ chassis 0.45 × 0.12 │
 0.075 ┤      │             (◯)     │ ← drive axle, x = 0 (base_link)
 0.050 ┤      └─────────────────────┘ ← chassis bottom
 0.025 ┤   ○                            ← caster centre (x = −0.36)
 0.000 ┼───●────────────────●────────── ground
          caster          wheel contact x = 0
     x: −0.385  −0.325                +0.125
```

Top view (+X up, +Y left):
```
        +0.125 ┌─────────────┐
               │  [bracket]  │
  wheel ███    │             │    ███ wheel      wheel centres y = ±0.200
  (y=+0.2)███ ─┼──── axle ───┼─  ███ (y=−0.2)    chassis sides y = ±0.175
               │             │
        −0.325 └─────────────┘
                     ○          caster x = −0.36 (behind chassis)
```

**Dimensioned drawing:** [`amr_geometry_drawing.svg`](amr_geometry_drawing.svg) (top and side views, mm; added 2026-11-15). It is generated from `amr_properties.xacro` (plus `laser_frame_z` from `amr.sensors.xacro` for the scan plane) by `tools/geometry_drawing.py`, so it holds no numbers of its own. `python3 -I tools/geometry_drawing.py --check` fails if the committed SVG is stale or if the §2 table disagrees with the Xacro; it is the first CI step (TEST-TA-06). *Scope (decided 2026-10-21):* the drawing was **not required for M1 closure**; REQ-M1-11 and TEST-M1-04 used the sketches above.

## 6. Limitations
- Primitive shapes approximate a real chassis. There are no wheel wells, bumpers, fasteners, cable routing, or caster mounting arm.
- Bracket geometry was a provisional placeholder (OPEN-03) until 2026-11-03; DEC-030 finalized it unchanged and DEC-037 confirmed it. It remains a simplified primitive block, not a modelled product bracket. The `base_link` height is derived from DEC-016 (Accepted) and is not an independent parameter. The caster mounting arm is not modelled.
- Tyre compliance and contact patch are not modelled. Gazebo contacts are rigid with solver-specific margins.
- Friction and surface parameters are deferred to M2 (motion).
