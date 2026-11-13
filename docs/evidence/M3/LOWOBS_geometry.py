"""CALC-M3-04 (low-obstacle investigation): 2D self-occlusion of a horizontal scan plane by the
AMR body, plus floor-intersection range under pitch, for candidate LiDAR positions.
Geometry from amr_properties.xacro (Selected values), frame base_footprint (x forward, z up).
Usage: python3 -I lowobs_geometry.py"""
import math
# --- amr_properties.xacro (Selected) ---
r, ww, track = 0.075, 0.035, 0.400               # wheel_radius, wheel_width, wheel_track
L, W, H, axle, clr = 0.450, 0.350, 0.120, 0.100, 0.050  # chassis_length/width/height, axle_offset_x, ground_clearance
rc, xc = 0.025, -0.360                            # caster_radius, caster_x
bx, by, bz, bmx = 0.080, 0.080, 0.030, 0.070      # lidar_bracket_x/y/z, lidar_mount_x
cx0, cx1 = -axle - L / 2, -axle + L / 2           # chassis x range (-0.325, +0.125)
cz0, cz1 = clr, clr + H                           # chassis z range (0.050, 0.170)

def shapes(h):
    """Cross-sections of the body in the plane z = h: list of ('rect', x0, x1, y0, y1) / ('circ', x, y, R)."""
    s = []
    if cz0 <= h <= cz1: s.append(('rect', cx0, cx1, -W / 2, W / 2, 'chassis'))
    if abs(h - r) < r:
        a = math.sqrt(r * r - (h - r) ** 2)
        for sy in (1, -1):
            y0, y1 = sy * track / 2 - ww / 2, sy * track / 2 + ww / 2
            s.append(('rect', -a, a, min(y0, y1), max(y0, y1), 'wheel'))
    if h < 2 * rc:
        s.append(('circ', xc, 0.0, math.sqrt(rc * rc - (h - rc) ** 2), 'caster'))
    if cz1 <= h <= cz1 + bz: s.append(('rect', bmx - bx / 2, bmx + bx / 2, -by / 2, by / 2, 'bracket'))
    return s

def hit(ox, oy, dx, dy, sh):
    """Distance along the ray to the shape, or None."""
    if sh[0] == 'rect':
        _, x0, x1, y0, y1, _n = sh; tmin, tmax = -1e9, 1e9
        for o, d, lo, hi in ((ox, dx, x0, x1), (oy, dy, y0, y1)):
            if abs(d) < 1e-12:
                if not (lo <= o <= hi): return None
            else:
                t1, t2 = (lo - o) / d, (hi - o) / d; tmin, tmax = max(tmin, min(t1, t2)), min(tmax, max(t1, t2))
        return tmin if tmax >= max(tmin, 0) and tmin >= 0 else None
    _, x, y, R, _n = sh; fx, fy = ox - x, oy - y
    b = fx * dx + fy * dy; c = fx * fx + fy * fy - R * R; disc = b * b - c
    if disc < 0: return None
    t = -b - math.sqrt(disc)
    return t if t >= 0 else None

def coverage(xs, ys, h):
    blocked = {}
    for k in range(360):
        a = math.radians(-180 + k); dx, dy = math.cos(a), math.sin(a)
        for sh in shapes(h):
            t = hit(xs, ys, dx, dy, sh)
            if t is not None:
                blocked[k - 180] = (sh[-1], t); break
    return blocked

def sectors(blocked):
    """Contiguous blocked bearing ranges (deg), wrap-aware."""
    degs = sorted(blocked); out = []
    for d in degs:
        if out and d == out[-1][1] + 1: out[-1][1] = d
        else: out.append([d, d])
    if len(out) > 1 and out[0][0] == -180 and out[-1][1] == 179:
        out[0][0] = out[-1][0] - 360; out.pop()
    return out

cands = [
    ('O1  baseline: bracket top + 0.030 (DEC-030)', bmx, 0.0, cz1 + bz + 0.030),
    ('O2a lowered onto chassis top, no bracket (optical +0.020, Assumed)', bmx, 0.0, cz1 + 0.020),
    ('O2b front-protruding, plane 0.120 (housing centre 0.035 ahead of chassis face, Assumed)', cx1 + 0.035, 0.0, 0.120),
    ('O2c front-protruding, plane 0.060 (same housing)', cx1 + 0.035, 0.0, 0.060),
    ('O2d under chassis, plane 0.035 (centre, in the 0.050 m ground clearance)', -0.100, 0.0, 0.035),
]
print('# CALC-M3-04 geometry check; chassis x %.3f..%.3f, z %.3f..%.3f; wheel top %.3f; caster top %.3f; bracket top %.3f'
      % (cx0, cx1, cz0, cz1, 2 * r, 2 * rc, cz1 + bz))
for name, xs, ys, h in cands:
    b = coverage(xs, ys, h); free = 360 - len(b)
    floor_1deg = h / math.tan(math.radians(1.0)); floor_2deg = h / math.tan(math.radians(2.0))
    print(f'\n{name}\n  sensor (x, y, z) = ({xs:.3f}, {ys:.3f}, {h:.3f}) m in base_footprint')
    print(f'  unobstructed beams: {free}/360 ({free:.0f} deg)')
    for s0, s1 in sectors(b):
        parts = sorted({b[((d + 180) % 360) - 180][0] for d in range(s0, s1 + 1)})
        span = f'{s0 + 360:+d} .. +180 and -180 .. {s1:+d}' if s0 < -180 else f'{s0:+d} .. {s1:+d}'
        print(f'  blocked bearings {span} deg ({s1 - s0 + 1:3d} beams) by {", ".join(parts)}')
    print(f'  floor intersection of a level beam under pitch: 1 deg -> {floor_1deg:.2f} m, 2 deg -> {floor_2deg:.2f} m (range_max 12 m, DEC-031)')
    print(f'  obstacles detected only if their top is above {h:.3f} m (2D plane)')
