# Mass Budget and Inertia Calculations (M1)

**Status:** Calculations recorded 2026-10-19. Inputs are **simulation assumptions**, not measured hardware values. The generated model reproduces these calculations (TEST-M1-03 re-test 1, 2026-10-21) and rests stably in Gazebo (TEST-M1-07, 2026-10-21). The inputs themselves remain assumptions.
**Related:** DEC-011 to DEC-016, DEC-019 · REQ-M1-06, REQ-M1-07 · OPEN-01, OPEN-03, OPEN-05 · geometry in [mechanical_geometry.md](mechanical_geometry.md)

Each calculation's status:
- **Final for current inputs:** recomputed independently on 2026-10-19 and will only change if an input changes.
- **Provisional:** depends on an unresolved (OPEN) input, so the numeric result is a candidate value.

The numbers were recomputed independently with a short Python check (not committed; trivial arithmetic). The implementation (`inertial_macros.xacro`) computes inertias in Xacro from the same parameters (see §7), so code and documentation cannot drift; TEST-M1-03 re-test 1 and TEST-M1-08 re-test 1 verified the generated values against this document.

## 1. Mass budget — CALC-M1-06 (final for current inputs)

| Component | Mass (kg) | Status | Centre of mass in `base_link` (m) | Height above ground (m) |
|---|---|---|---|---|
| Chassis + top platform | 8.0 | Assumed | (−0.100, 0, +0.035) | 0.110 |
| Left drive wheel | 0.5 | Assumed | (0, +0.200, 0) | 0.075 |
| Right drive wheel | 0.5 | Assumed | (0, −0.200, 0) | 0.075 |
| Caster assembly | 0.2 | Assumed | (−0.360, 0, −0.050) | 0.025 |
| LiDAR bracket | 0.2 | Assumed | (+0.070, 0, +0.110) *provisional (OPEN-03) until 2026-11-03; final, DEC-030/DEC-037* | 0.185 |
| **Total M1 model** | **9.4** | Calculated | see CALC-M1-11 | |
| Virtual payload | (2.0) | Deferred (DEC-015) | not in M1 | |

Xacro properties for the masses: `chassis_mass`, `wheel_mass`, `caster_mass`, `lidar_bracket_mass` (`amr_properties.xacro`).

Positions are taken from [mechanical_geometry.md §3](mechanical_geometry.md#3-derived-placement-calculated-from-2) (authoritative).

8.0 + 0.5 + 0.5 + 0.2 + 0.2 = **9.4 kg**. The 8.0 kg is the chassis body only, not the assembled robot. Each massive component has its own link. The 0.2 kg bracket belongs to `lidar_mount_link`, whose inertial origin is (0, 0, −0.015) in that link (the link origin is on the bracket top; [frames_and_tf.md §2](frames_and_tf.md#2-m1-frame-tree-static-robot-description)). The only massless link is the root `base_footprint`. This gives the 6-link tree of REQ-M1-02, with no separate bracket link. *(Corrected 2026-10-19, review finding R-01: this sentence previously listed `lidar_mount_link` as massless, which contradicted the link inventory.)*

## 2. Validity checks applied to every inertia tensor
A rigid body's inertia tensor about its centre of mass (in kg·m²) is physically valid only if:
1. All principal moments are > 0.
2. They satisfy the **triangle inequality**: Ixx + Iyy ≥ Izz, Ixx + Izz ≥ Iyy, Iyy + Izz ≥ Ixx.

Gazebo/DART may warn about, reject, or behave unstably with tensors that violate these. The tensors below are diagonal because each shape's principal axes are aligned with its link frame (off-diagonal terms Ixy = Ixz = Iyz = 0).

## 3. Chassis — CALC-M1-07 (final for current inputs)

**Model:** uniform-density solid rectangular cuboid (Assumed).

**Variables:**
- m = 8.0 kg (mass)
- L = 0.450 m (length along X)
- W = 0.350 m (width along Y)
- H = 0.120 m (height along Z)

The axes pass through the cuboid centroid, parallel to its edges.

**Equations (solid cuboid about its centroid):**
- Ixx = m(W² + H²)/12
- Iyy = m(L² + H²)/12
- Izz = m(L² + W²)/12

**Substitution:**
- W² = 0.1225, H² = 0.0144, L² = 0.2025 (m²)
- Ixx = 8.0 × (0.1225 + 0.0144)/12 = 8.0 × 0.1369/12 = **0.091267 kg·m²** (≈ 0.0913)
- Iyy = 8.0 × (0.2025 + 0.0144)/12 = 8.0 × 0.2169/12 = **0.144600 kg·m²** (≈ 0.1446)
- Izz = 8.0 × (0.2025 + 0.1225)/12 = 8.0 × 0.3250/12 = **0.216667 kg·m²** (≈ 0.2167)

**Checks:**
- All moments > 0 ✓
- Triangle inequality ✓: 0.2359 ≥ 0.2167; 0.3079 ≥ 0.1446; 0.3613 ≥ 0.0913
- Izz > Iyy > Ixx, as expected for L > W > H.

**Precision:** the inputs have 2–3 significant figures, so report 4 significant figures. Keep full precision in the Xacro computation.

**Reasonableness:**
- The implied density is 8.0 / (0.45 × 0.35 × 0.12) = **423 kg/m³**. That is far below solid aluminium (~2700 kg/m³), which is consistent with a mostly hollow body whose mass is "smeared" uniformly.

**Limits:**
- A real thin-walled shell of the same mass has *larger* moments, because its mass sits near the outer walls. A uniform solid therefore underestimates rotational inertia.
- Internal components (battery, motors, electronics) are not represented. They would move the CG and change the tensor.
- The tensor is valid **only about the chassis centroid**: the URDF `<inertial>` origin must be the chassis geometric centre (−0.100, 0, +0.035) in `base_link`. OPEN-05 is resolved (DEC-019): the chassis inertial stays on `base_link` with this offset origin, and there is no separate `chassis_link`.
- Acceptable for simulation. Revisit if hardware is ever built (M13).

## 4. Drive wheel (each) — CALC-M1-08 (final for current inputs)

**Model:** uniform solid cylinder (Assumed).

**Variables:**
- m = 0.5 kg
- r = 0.075 m (radius)
- w = 0.035 m (width, along the spin axis)

**Axis identification:** the wheel link frame is **unrotated** relative to `base_link` (implemented in `amr.urdf.xacro`; identity rotation verified by TEST-M1-04), with the joint axis along link **+Y** (DEC-016; OPEN-04 Selected in DEC-019). The spin axis is therefore link Y; X and Z are transverse.

**Equations (solid cylinder about its centroid):**
- I_axial = m·r²/2
- I_transverse = m(3r² + w²)/12

**Substitution:**
- r² = 0.005625 m², w² = 0.001225 m²
- Iyy (axial) = 0.5 × 0.005625/2 = **1.4063 × 10⁻³ kg·m²** (exact: 0.00140625)
- Ixx = Izz (transverse) = 0.5 × (3 × 0.005625 + 0.001225)/12 = 0.5 × 0.018100/12 = **7.5417 × 10⁻⁴ kg·m²**

**Checks:**
- All moments > 0 ✓
- Triangle inequality: Ixx + Izz = 1.5083 × 10⁻³ ≥ Iyy = 1.4063 × 10⁻³ ✓. It is close to equality, as expected: a thin disc (w → 0) reaches exact equality.

**Reasonableness:** the implied density is 0.5 / (π × 0.075² × 0.035) = **808 kg/m³**. That is plausible for a tyre on a partly hollow hub.

**Axis-mapping caution:**
- A URDF `<cylinder>` has its axis along the *geometry* Z axis. The visual and collision elements must therefore be rotated (e.g. rpy = (π/2, 0, 0)) so the cylinder lies along link Y.
- If the inertial frame were rotated the same way instead, the axial moment would have to be entered as Izz.
- Mixing the two conventions is a common modelling error. The chosen mapping must be confirmed against the generated model and RViz (OPEN-04, TEST-M1-03, TEST-M1-04). *(Confirmed 2026-10-21: TEST-M1-03 re-test 1 found Iyy axial; in TEST-M1-04 I observed the RViz wheel direction.)*

## 5. Caster — CALC-M1-09 (final for current inputs; OPEN-01 Selected in DEC-019)

**Model:** uniform solid sphere on a fixed joint, with the whole 0.2 kg assembly lumped into the sphere (DEC-013, Assumed).

**Variables:** m = 0.2 kg, r_c = 0.025 m (Selected).

**Equation (solid sphere about its centre):** I = (2/5)·m·r_c², the same about every axis.

**Substitution:** I = 0.4 × 0.2 × 0.000625 = **5.0 × 10⁻⁵ kg·m²**. It changes only if the caster radius or mass changes.

**Checks:**
- Positive ✓
- Triangle inequality ✓ (a sphere is isotropic)
- Implied density 0.2 / (4/3 π × 0.025³) = **3056 kg/m³**. That is plausible for a metal/plastic ball-and-housing assembly.

**Limits:**
- Swivel dynamics, a caster wheel, and housing are not represented.
- Very small inertias can make some physics solvers stiff. In M1 Gazebo this is **expected** not to apply directly: based on the generic probe (§11), the fixed-joint caster should be lumped into the root SDF link, so its inertia would not act as a separate body. *Confirmed 2026-10-21:* TEST-M1-03 re-test 1 showed the caster lumped into `base_footprint`. TEST-M1-07 measured no motion (Δz 0 mm, drift 0 mm) and I observed no jitter. The concern returns if fixed joints are preserved or the caster gets its own joint.

## 6. LiDAR bracket — CALC-M1-10 (**provisional**: OPEN-03 is a provisional placeholder until M3; *final since 2026-11-03: OPEN-03 finalized unchanged, DEC-030; the 0.2 kg represents bracket plus LiDAR, DEC-034*)

**Model:** uniform solid cuboid (Assumed).

**Variables:**
- m = 0.2 kg
- Candidate size 0.080 (X) × 0.080 (Y) × 0.030 (Z) m

**Equations:** the same as CALC-M1-07.

**Substitution:**
- Ixx = 0.2 × (0.0064 + 0.0009)/12 = **1.2167 × 10⁻⁴ kg·m²**
- Iyy = 0.2 × (0.0064 + 0.0009)/12 = **1.2167 × 10⁻⁴ kg·m²**
- Izz = 0.2 × (0.0064 + 0.0064)/12 = **2.1333 × 10⁻⁴ kg·m²**

**Checks:** positive ✓; triangle inequality ✓ (2.4333 × 10⁻⁴ ≥ 2.1333 × 10⁻⁴).

## 7. Implementation of these formulas
The `inertial_macros.xacro` macros `box_inertia(m, x, y, z)`, `cylinder_inertia(m, r, h)` (axial along link Y, per OPEN-04 in DEC-019), and `sphere_inertia(m, r)` evaluate the equations above from the properties in `amr_properties.xacro`; each takes the centre of mass as an optional `xyz` argument. TEST-M1-03 compares the per-link values in the **generated URDF** with this document to 4 significant figures. The Gazebo SDF does not keep these per-link values for fixed-joint links (see §11). *(Created 2026-10-21; TEST-M1-03 re-test 1 PASS.)*

## 8. Centre of gravity and static load — CALC-M1-11 (**provisional**: the caster is Selected, but the bracket position is provisional, OPEN-03; *final for current inputs since 2026-11-03: OPEN-03 finalized unchanged, DEC-030, confirmed by DEC-037; values unchanged*)

Positions are taken from §1; heights are above ground.

**Equations:**
- x_cg = Σmᵢxᵢ / Σmᵢ
- z_cg = Σmᵢzᵢ / Σmᵢ
- y_cg = 0 by left/right symmetry

**Substitution** (caster x = −0.360 m, Selected):
- x_cg = (8.0 × −0.100 + 1.0 × 0 + 0.2 × −0.360 + 0.2 × 0.070) / 9.4 = −0.858 / 9.4 = **−0.0913 m** (0.091 m behind the axle)
- z_cg = (8.0 × 0.110 + 1.0 × 0.075 + 0.2 × 0.025 + 0.2 × 0.185) / 9.4 = 0.997 / 9.4 = **0.106 m above ground**

**Static load split** (moments about the axle line; caster lever arm 0.360 m):
- Caster share = 0.0913 / 0.360 = **25.4 %** ≈ 23.4 N of the 92.2 N weight (g = 9.81 m/s²)
- Each drive wheel ≈ 34.4 N (37.3 %)

*Revision note:* with the earlier caster candidate (x = −0.280 m) the values were x_cg = −0.0896 m and a 32.0 % caster share. They were superseded when the caster moved behind the chassis (CALC-M1-13).

**Reasonableness:**
- The CG is inside the support triangle formed by the wheel contacts (0, ±0.200) and the caster contact (−0.360, 0).
- Moving the caster rearward puts more of the weight on the drive wheels, which helps traction.
- If the axle were at the chassis centre with a single rear caster, the CG would sit on the front tipping line. That is why the axle is offset forward (DEC-012).

## 9. Quasi-static tipping thresholds — CALC-M1-12 (**provisional**: depends on CALC-M1-11; *final for current inputs since 2026-11-03, with CALC-M1-11; values unchanged*)

**Equation:** a_crit = g·d / h, where:
- d = horizontal distance from the CG to the tipping edge
- h = z_cg = 0.106 m

**Forward tipping (about the axle line, e.g. hard braking while driving forward):**
- d = 0.0913 m → a_crit ≈ **8.4 m/s²**

**Lateral tipping (about the wheel–caster edge):**
- The edge runs from (0, 0.200) to (−0.360, 0).
- Perpendicular distance from the CG (−0.0913, 0) to that edge: d = 0.1305 m → a_crit ≈ **12.1 m/s²**
- With the earlier x = −0.280 m candidate these were 8.3 and 10.2 m/s².

**Interpretation:**
- Both thresholds are far above expected AMR accelerations (order 1 m/s²; actual limits will be set in M2).
- Rigid bodies and no suspension are assumed. Wheel slip and dynamic effects are ignored.
- In practice, traction limits are reached before these values.

## 10. Payload (deferred)
The candidate 2.0 kg virtual payload is excluded from M1 (DEC-015). Its effect on the CG, load split, and tipping must be recalculated in the milestone that introduces it.

## 11. Expected Gazebo SDF lumped link — CALC-M1-15 (**provisional**: uses the provisional bracket position; *final for current inputs since 2026-11-03: bracket finalized unchanged, DEC-030/DEC-037; values unchanged*)
Added 2026-10-19 (review finding R-02) for TEST-M1-03.

**Why it is needed:** when `gz sdf -p` converts the URDF, sdformat merges every link attached by a fixed joint into its parent. A generic probe run on the installed tools (sdformat 14.9.0; [frames_and_tf.md §4](frames_and_tf.md#4-gazebo-specific-behaviour)) showed that the chain is merged all the way into the **root link**, and the merged link keeps the root's name. The expected AMR SDF therefore has **3 links**: `base_footprint` (lumped: chassis + caster + bracket) and the two wheels. The probe also showed that the merged inertial is combined with the parallel-axis theorem about the combined centre of mass.

**Equations:** m_L = Σmᵢ; r_L = Σmᵢrᵢ / m_L. Inputs are the §1 positions in `base_link`. `base_link` is 0.075 m above `base_footprint` (DEC-016).

**Substitution:**
- m_L = 8.0 + 0.2 + 0.2 = **8.4 kg**; model total = 8.4 + 2 × 0.5 = **9.4 kg** (matches CALC-M1-06)
- x_L = (8.0 × −0.100 + 0.2 × −0.360 + 0.2 × 0.070) / 8.4 = −0.858 / 8.4 = **−0.1021 m**
- z_L in `base_link` = (8.0 × 0.035 + 0.2 × −0.050 + 0.2 × 0.110) / 8.4 = 0.292 / 8.4 = **+0.0348 m**
- z_L in `base_footprint` = 0.0348 + 0.075 = **+0.1098 m**. This is the frame the SDF `<inertial><pose>` is expressed in, because the lumped link is `base_footprint`.

**Reasonableness:** the 0.4 kg of attachments moves the CoM 2.1 mm rearward and 0.2 mm down from the chassis centroid (−0.100, +0.035), as expected for a small mass split fore and aft. *Discrepancy note:* the review report described the lumped link as `base_link` with the CoM in `base_link` coordinates. The numbers reproduce, but the link name and frame are corrected here from the probe result.

**Limits:** the lumped inertia tensor is not tabulated here. TEST-M1-03 recomputes it at test time from CALC-M1-07, -09, and -10 using the parallel-axis theorem. This is behaviour expected from a generic probe; it is confirmed on the real model only in TEST-M1-03. *(Confirmed 2026-10-21 by TEST-M1-03 re-test 1: 8.4 kg at (−0.1021, 0, +0.1098); the tensor matches the parallel-axis combination to 4 s.f.)*
