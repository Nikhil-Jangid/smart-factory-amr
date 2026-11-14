#!/usr/bin/env python3
"""Generate the dimensioned top/side SVG drawing of the AMR geometry.

Every number in the drawing is read from the model, never typed in:
  - amr_ws/src/amr_description/urdf/amr_properties.xacro (the owner of the M1 geometry values)
  - amr_ws/src/amr_description/urdf/amr.sensors.xacro (only laser_frame_z, for the LiDAR scan plane)

Usage:
  python3 -I tools/geometry_drawing.py           # (re)write docs/design/amr_geometry_drawing.svg
  python3 -I tools/geometry_drawing.py --check   # exit 1 if the committed SVG is stale, or if the
                                                 # mechanical_geometry.md section 2 table disagrees with the Xacro

No ROS installation is needed: <xacro:property> values are read with ElementTree and the ${...}
expressions are evaluated with a restricted arithmetic evaluator (numbers, names, + - * /).
"""
import ast
import operator
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URDF = ROOT / 'amr_ws/src/amr_description/urdf'
PROPS = URDF / 'amr_properties.xacro'
SENSORS = URDF / 'amr.sensors.xacro'
DOC = ROOT / 'docs/design/mechanical_geometry.md'
OUT = ROOT / 'docs/design/amr_geometry_drawing.svg'
XACRO_NS = '{http://www.ros.org/wiki/xacro}'

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def _eval(expr, names):
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name):
            return names[n.id]
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -ev(n.operand)
        raise ValueError(f'unsupported expression: {expr!r}')
    return ev(ast.parse(expr, mode='eval'))


def read_properties(path, only=None):
    """Return {name: float} for the <xacro:property> elements of a file, in file order."""
    values = {}
    for el in ET.parse(path).getroot().iter(f'{XACRO_NS}property'):
        name, raw = el.get('name'), el.get('value')
        if only is not None and name not in only:
            continue
        m = re.fullmatch(r'\$\{(.*)\}', raw.strip())
        values[name] = _eval(m.group(1), values) if m else float(raw)
    return values


def mm(v):
    """Format metres as millimetres: 0.450 -> '450', 0.0075 -> '7.5'."""
    s = f'{v * 1000:.1f}'
    return s[:-2] if s.endswith('.0') else s


# --------------------------------------------------------------------------- drawing
S = 1.4             # px per mm
OX = 689.0          # px of x = 0 (base_link) in both views
OY_TOP = 430.0      # px of y = 0 in the top view
OY_SIDE = 1170.0    # px of z = 0 (ground) in the side view
W, H = 1060, 1620

INK, DIM, CL = '#1a1a1a', '#1f5fa8', '#7a7a7a'


def X(x):
    return OX + S * x * 1000


def YT(y):
    return OY_TOP - S * y * 1000


def ZS(z):
    return OY_SIDE - S * z * 1000


class Svg:
    def __init__(self):
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def line(self, x1, y1, x2, y2, stroke=INK, w=1.0, dash=None, extra=''):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
                 f'stroke-width="{w}"{d}{extra}/>')

    def rect(self, x1, y1, x2, y2, fill, w=1.5):
        x, y = min(x1, x2), min(y1, y2)
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{abs(x2 - x1):.1f}" height="{abs(y2 - y1):.1f}" '
                 f'fill="{fill}" stroke="{INK}" stroke-width="{w}"/>')

    def circle(self, cx, cy, r, fill, w=1.5):
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{w}"/>')

    def text(self, x, y, s, size=13, anchor='middle', fill=INK, rot=None, weight=None):
        t = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot is not None else ''
        b = f' font-weight="{weight}"' if weight else ''
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{b}{t}>'
                 f'{s}</text>')

    def hdim(self, x1, x2, y, from1, from2, label, outside=False):
        """Horizontal dimension between px x1 < x2 on row y; extension lines from feature rows from1/from2."""
        for x, f in ((x1, from1), (x2, from2)):
            if f is not None:
                self.line(x, f + (4 if y > f else -4), x, y + (5 if y > f else -5), DIM, 0.7)
        self.line(x1, y, x2, y, DIM, 1.0, extra=' marker-start="url(#arr)" marker-end="url(#arr)"')
        if outside:
            self.text(x2 + 6, y + 4, label, anchor='start', fill=DIM)
        else:
            self.add(f'<rect x="{(x1 + x2) / 2 - 4 * len(label) - 4:.1f}" y="{y - 9:.1f}" '
                     f'width="{8 * len(label) + 8:.1f}" height="16" fill="#ffffff"/>')
            self.text((x1 + x2) / 2, y + 4.5, label, fill=DIM)

    def vdim(self, y1, y2, x, from1, from2, label, outside=False):
        """Vertical dimension between px y1 and y2 at column x; extension lines from feature columns."""
        for yy, f in ((y1, from1), (y2, from2)):
            if f is not None:
                self.line(f + (4 if x > f else -4), yy, x + (5 if x > f else -5), yy, DIM, 0.7)
        self.line(x, y1, x, y2, DIM, 1.0, extra=' marker-start="url(#arr)" marker-end="url(#arr)"')
        lo, hi = min(y1, y2), max(y1, y2)
        if outside:
            self.text(x + 6, lo - 6, label, anchor='start', fill=DIM)
        else:
            self.add(f'<rect x="{x - 9:.1f}" y="{(lo + hi) / 2 - 4 * len(label) - 4:.1f}" width="16" '
                     f'height="{8 * len(label) + 8:.1f}" fill="#ffffff"/>')
            self.text(x + 4.5, (lo + hi) / 2, label, fill=DIM, rot=-90)

    def axes(self, x, y, first, second, c1, c2, l1, l2):
        """Frame triad: first axis to the right, second axis up (both 40 px)."""
        for (dx, dy), c, lab in (((40, 0), c1, l1), ((0, -40), c2, l2)):
            self.line(x, y, x + dx, y + dy, c, 2.0, extra=f' marker-end="url(#ax{c[1:]})"')
            self.text(x + dx + (8 if dx else 0), y + dy - (6 if dy else -4), lab, size=12, fill=c,
                      anchor='start' if dx else 'middle', weight='bold')


def build(p, laser_frame_z):
    g = {k: p[k] for k in p}
    L, Wd, Hc = g['chassis_length'], g['chassis_width'], g['chassis_height']
    rw, ww, track = g['wheel_radius'], g['wheel_width'], g['wheel_track']
    rc, cx = g['caster_radius'], g['caster_x']
    bx, by, bz, bmx = g['lidar_bracket_x'], g['lidar_bracket_y'], g['lidar_bracket_z'], g['lidar_mount_x']
    clr = g['ground_clearance']
    # Derived placements, taken from the Xacro expressions (mechanical_geometry.md section 3)
    ch_x, ch_z, wy, cz, lmz, blz = (g['chassis_x'], g['chassis_z'], g['wheel_y'], g['caster_z'],
                                    g['lidar_mount_z'], g['base_link_z'])
    front, rear = ch_x + L / 2, ch_x - L / 2
    caster_rear = cx - rc
    # Heights above ground (side view uses ground z = 0, i.e. base_footprint)
    h_ch_bot, h_ch_top = blz + ch_z - Hc / 2, blz + ch_z + Hc / 2
    h_axle, h_caster = blz, blz + cz
    h_br_top = blz + lmz
    h_scan = h_br_top + laser_frame_z
    gap = track / 2 - ww / 2 - Wd / 2
    overall_w = track + ww

    s = Svg()
    s.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
          f'font-family="DejaVu Sans, Arial, Helvetica, sans-serif">')
    s.add('<title>Smart AMR: dimensioned top and side views (M1 geometry)</title>')
    s.add('<defs>'
          f'<marker id="arr" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" '
          f'orient="auto-start-reverse"><path d="M0,1.5 L10,5 L0,8.5 z" fill="{DIM}"/></marker>'
          + ''.join(f'<marker id="ax{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
                    f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#{c}"/></marker>'
                    for c in ('c62828', '2e7d32', '1565c0'))
          + '</defs>')
    s.add(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
    s.text(W / 2, 34, 'Smart AMR — dimensioned top and side views (M1 geometry)', size=20, weight='bold')
    s.text(W / 2, 56, 'All dimensions in mm · third-angle projection · base_link = drive-axle midpoint '
           f'({mm(blz)} above ground, DEC-016) · REP-103 frames', size=12.5, fill='#444444')

    # ---------------- top view (looking down -Z; +X right, +Y up)
    s.text(60, 110, 'TOP VIEW', size=14, anchor='start', weight='bold')
    s.text(60, 127, '(from +Z)', size=12, anchor='start', fill='#555555')
    s.line(X(caster_rear) - 30, YT(0), X(front) + 30, YT(0), CL, 0.8, '10 3 2 3')       # centre line y = 0
    s.line(X(0), YT(overall_w / 2) - 25, X(0), ZS(0) + 10, CL, 0.8, '10 3 2 3')       # axle line through both views
    s.rect(X(rear), YT(Wd / 2), X(front), YT(-Wd / 2), '#e6e6e6')
    s.rect(X(bmx - bx / 2), YT(by / 2), X(bmx + bx / 2), YT(-by / 2), '#cfe0f3')
    for sign in (1, -1):
        s.rect(X(-rw), YT(sign * (wy - ww / 2)), X(rw), YT(sign * (wy + ww / 2)), '#4a4a4a')
    s.line(X(0), YT(wy), X(0), YT(-wy), INK, 1.0, '4 3')                              # axle (hidden)
    s.circle(X(cx), YT(0), S * rc * 1000, '#9e9e9e')
    s.axes(X(0), YT(0), 'x', 'y', '#c62828', '#2e7d32', 'X', 'Y')
    s.text(X(0) - 8, YT(0) + 18, 'base_link', size=11.5, anchor='end')
    s.text(X(bmx), YT(by / 2) - 8, f'LiDAR bracket {mm(bx)} × {mm(by)}', size=11, fill='#1f4e79')
    s.text(X(cx), YT(rc) - 10, 'caster', size=11)
    # Y dimensions, right of the top view
    xr = X(front)
    s.vdim(YT(Wd / 2), YT(-Wd / 2), xr + 40, xr, xr, mm(Wd))
    s.vdim(YT(wy), YT(-wy), xr + 85, X(rw), X(rw), f'{mm(track)} track')
    s.vdim(YT(overall_w / 2), YT(-overall_w / 2), xr + 130, X(0), X(0), mm(overall_w))
    # wheel width and wheel-to-chassis gap (upper wheel), left of the wheel
    xl = X(-rw) - 30
    s.vdim(YT(wy + ww / 2), YT(wy - ww / 2), xl, X(-rw), X(-rw), mm(ww), outside=True)
    s.add(f'<line x1="{X(-0.02):.1f}" y1="{YT(Wd / 2 + gap / 2):.1f}" x2="{X(-0.17):.1f}" '
          f'y2="{YT(Wd / 2 + gap / 2) + 30:.1f}" stroke="{DIM}" stroke-width="0.8"/>')
    s.text(X(-0.17) - 4, YT(Wd / 2 + gap / 2) + 44, f'gap {mm(gap)} each side (nominal)', size=12,
           anchor='end', fill=DIM)

    # ---------------- side view (from -Y, the robot's right side; +X right, +Z up)
    s.text(60, ZS(h_scan) - 40, 'SIDE VIEW', size=14, anchor='start', weight='bold')
    s.text(60, ZS(h_scan) - 23, '(from −Y, right side)', size=12, anchor='start', fill='#555555')
    s.line(X(caster_rear) - 60, ZS(0), X(front) + 60, ZS(0), INK, 1.2)                # ground
    for i in range(16):
        x0 = X(caster_rear) - 55 + i * 40
        s.line(x0, ZS(0) + 1, x0 - 8, ZS(0) + 9, '#999999', 0.7)
    s.rect(X(rear), ZS(h_ch_top), X(front), ZS(h_ch_bot), '#e6e6e6')
    s.rect(X(bmx - bx / 2), ZS(h_br_top), X(bmx + bx / 2), ZS(h_ch_top), '#cfe0f3')
    s.circle(X(0), ZS(h_axle), S * rw * 1000, '#4a4a4a')
    s.circle(X(0), ZS(h_axle), 4, '#ffffff', 1.0)
    s.circle(X(cx), ZS(h_caster), S * rc * 1000, '#9e9e9e')
    s.line(X(caster_rear) - 40, ZS(h_scan), X(front) + 40, ZS(h_scan), '#1f5fa8', 0.9, '6 4')
    s.text(X(caster_rear) - 40, ZS(h_scan) - 6, f'LiDAR scan plane {mm(h_scan)} (laser_frame, M3)', size=11.5,
           anchor='start', fill='#1f5fa8')
    s.axes(90, ZS(0.10), 'x', 'z', '#c62828', '#1565c0', 'X', 'Z')
    s.text(90, ZS(0.10) + 18, 'frame axes', size=10.5, anchor='start', fill='#555555')
    s.text(X(0) + S * rw * 1000 + 6, ZS(h_axle) + 4, f'Ø{mm(2 * rw)} wheel', size=12, anchor='start', fill=DIM)
    s.text(X(cx) - S * rc * 1000 - 6, ZS(h_caster) + 4, f'Ø{mm(2 * rc)} caster', size=12, anchor='end', fill=DIM)
    s.text(X(0) + 30, ZS(0) + 18, 'base_footprint', size=11, anchor='start', fill='#555555')
    # bracket length above the side view
    s.hdim(X(bmx - bx / 2), X(bmx + bx / 2), ZS(h_br_top) - 22, ZS(h_br_top), ZS(h_br_top), mm(bx), outside=True)
    # heights, right of the side view
    xr = X(front)
    s.vdim(ZS(0), ZS(clr), xr + 30, None, xr, mm(clr), outside=True)
    s.vdim(ZS(h_ch_bot), ZS(h_ch_top), xr + 75, xr, xr, mm(Hc))
    s.vdim(ZS(0), ZS(h_ch_top), xr + 115, None, xr, mm(h_ch_top))
    s.vdim(ZS(0), ZS(h_br_top), xr + 155, None, X(bmx + bx / 2), mm(h_br_top))
    # axle height, left of the wheel
    s.vdim(ZS(0), ZS(h_axle), X(-rw) - 22, None, X(0) - 6, mm(h_axle))
    # X dimensions below the ground (rows of increasing span)
    g0 = ZS(0)
    s.hdim(X(ch_x), X(0), g0 + 35, ZS(h_ch_bot), ZS(0), mm(-ch_x))
    s.hdim(X(0), X(bmx), g0 + 35, None, ZS(h_br_top), mm(bmx))
    s.line(X(ch_x), ZS(h_ch_top) - 8, X(ch_x), ZS(h_ch_bot) + 8, CL, 0.8, '10 3 2 3')   # chassis centre line
    s.text(X(ch_x), ZS(h_ch_top) - 12, 'chassis centre', size=10.5, fill='#555555')
    s.hdim(X(cx), X(0), g0 + 65, ZS(h_caster), None, mm(-cx))
    s.hdim(X(rear), X(front), g0 + 95, ZS(h_ch_bot), ZS(h_ch_bot), mm(L))
    s.hdim(X(caster_rear), X(front), g0 + 125, ZS(0), ZS(h_ch_bot), f'{mm(front - caster_rear)} overall')

    # ---------------- parameter table and notes
    ty = OY_SIDE + 185
    s.text(60, ty, 'Values used (metres), read from amr_properties.xacro', size=13, anchor='start', weight='bold')
    rows = [(k, p[k]) for k in ('chassis_length', 'chassis_width', 'chassis_height', 'axle_offset_x',
                                'ground_clearance', 'wheel_radius', 'wheel_width', 'wheel_track',
                                'caster_radius', 'caster_x', 'lidar_bracket_x', 'lidar_bracket_y',
                                'lidar_bracket_z', 'lidar_mount_x')]
    rows += [('laser_frame_z (amr.sensors.xacro)', laser_frame_z)]
    derived = [(k, p[k]) for k in ('base_link_z', 'chassis_x', 'chassis_z', 'wheel_y', 'caster_z',
                                   'lidar_mount_z')]
    for col, items in enumerate((rows[:8], rows[8:], derived)):
        x0 = 60 + col * 310
        if col == 2:
            s.text(x0, ty + 22, 'Derived (Calculated, §3):', size=11.5, anchor='start', fill='#555555')
        for i, (k, v) in enumerate(items):
            yy = ty + 22 + (i + (1 if col == 2 else 0)) * 17
            s.text(x0, yy, k, size=11.5, anchor='start', fill='#333333')
            s.text(x0 + 285, yy, f'{v:+.4f}' if v < 0 else f'{v:.4f}', size=11.5, anchor='end')
    ny = ty + 185
    for i, line in enumerate((
            'Generated by tools/geometry_drawing.py from the Xacro model; do not edit by hand '
            '(regenerate, and check with --check).',
            'Simulation design geometry (primitive shapes, DEC-017), not a manufacturing drawing: no fasteners, '
            'tyre compliance or caster mounting arm',
            '(not modelled, CALC-M1-13). Rationale and status labels: docs/design/mechanical_geometry.md §2–§4.')):
        s.text(60, ny + i * 17, line, size=11.5, anchor='start', fill='#444444')
    s.add('</svg>')
    return '\n'.join(s.parts) + '\n'


# --------------------------------------------------------------------------- consistency check
def doc_table_values(path):
    """Values of the section 2 parameter table: {property: float or tuple}."""
    text = path.read_text(encoding='utf-8')
    sec = text.split('## 2. Parameter table', 1)[1].split('\n## ', 1)[0]
    out = {}
    for line in sec.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3 or not cells[1].startswith('`'):
            continue
        prop, val = cells[1].strip('`'), cells[2].replace('−', '-')
        nums = [float(n) for n in re.findall(r'-?\d+\.\d+', val)]
        out[prop] = nums[0] if len(nums) == 1 else tuple(nums)
    return out


def check(p, svg):
    failures = []
    if not OUT.exists() or OUT.read_text(encoding='utf-8') != svg:
        failures.append(f'{OUT.relative_to(ROOT)} is missing or stale: run python3 -I tools/geometry_drawing.py')
    table = doc_table_values(DOC)
    for prop, val in table.items():
        if prop == 'lidar_bracket_*':
            got = (p['lidar_bracket_x'], p['lidar_bracket_y'], p['lidar_bracket_z'])
            ok = len(val) == 3 and all(abs(a - b) < 1e-9 for a, b in zip(val, got))
        else:
            got = p.get(prop)
            ok = got is not None and abs(val - got) < 1e-9
        print(f'{"PASS" if ok else "FAIL"}  section 2 {prop}: doc {val} xacro {got}')
        if not ok:
            failures.append(f'mechanical_geometry.md section 2 {prop} = {val}, xacro = {got}')
    if len(table) < 12:
        failures.append(f'only {len(table)} section 2 rows parsed (expected 12)')
    for f in failures:
        print('FAIL ', f)
    print(f'# overall: {"FAIL" if failures else "PASS"} ({len(table)} table rows, drawing '
          f'{"stale" if any("stale" in f for f in failures) else "up to date"})')
    return 1 if failures else 0


def main(argv):
    p = read_properties(PROPS)
    laser_frame_z = read_properties(SENSORS, only={'laser_frame_z'})['laser_frame_z']
    svg = build(p, laser_frame_z)
    if '--check' in argv:
        return check(p, svg)
    OUT.write_text(svg, encoding='utf-8')
    print(f'wrote {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
