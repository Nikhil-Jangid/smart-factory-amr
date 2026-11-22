#!/usr/bin/env python3
"""Screenshots of a running GUI simulation for test evidence and demonstrations (2026-11-13).

Usage (same ROS_DOMAIN_ID / GZ_PARTITION as the running simulation; Gazebo started with the GUI):
    python3 tools/sim_capture.py view <x> <y> <z> <tx> <ty> <tz>   point the Gazebo camera from (x,y,z) at (tx,ty,tz)
    python3 tools/sim_capture.py follow <model> <ox> <oy> <oz> [gain]  camera follows <model> at offset (ox, oy, oz) m;
                                                                   gain 0..1 (default 0.2) = camera catch-up per update
    python3 tools/sim_capture.py shot <out_prefix>                 -> <out_prefix>_gazebo.png, <out_prefix>_rviz.png

Gazebo: the 3D view through the GUI's Screenshot plugin (service /gui/screenshot, loaded by the default gz-sim 8 GUI
config); the camera through /gui/move_to/pose, or
(follow, added 2026-11-21 for navigation videos: a fixed whole-arena view leaves the robot a few pixels wide) through
the /gui/track topic (gz.msgs.CameraTrack, FOLLOW_LOOK_AT: the camera keeps the offset and looks at the model). RViz: the window is captured with `xwd`, which needs RViz on X11
(start it with QT_QPA_PLATFORM=xcb under Wayland), and is converted to PNG here (XWD ZPixmap, 24/32 bit).
A missing window or a failed service is reported and skipped; the exit code is 0 unless no image was written.
"""
import glob
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np
from PIL import Image


def gz_service(name, reqtype, reptype, req, timeout=5000):
    r = subprocess.run(['gz', 'service', '-s', name, '--reqtype', reqtype, '--reptype', reptype,
                        '--timeout', str(timeout), '--req', req], capture_output=True, text=True)
    return r.returncode == 0 and 'true' in r.stdout


def view(x, y, z, tx, ty, tz):
    dx, dy, dz = tx - x, ty - y, tz - z
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(-dz, math.hypot(dx, dy))  # positive pitch looks down (Gazebo camera +x forward)
    cy, sy, cp, sp = math.cos(yaw / 2), math.sin(yaw / 2), math.cos(pitch / 2), math.sin(pitch / 2)
    q = (cy * cp, -sy * sp, cy * sp, sy * cp)  # w, x, y, z for roll 0
    req = (f'pose: {{position: {{x: {x}, y: {y}, z: {z}}}, '
           f'orientation: {{w: {q[0]}, x: {q[1]}, y: {q[2]}, z: {q[3]}}}}}')
    gz_service('/gui/follow', 'gz.msgs.StringMsg', 'gz.msgs.Boolean', 'data: ""')  # stop a follow (if any) first
    ok = gz_service('/gui/move_to/pose', 'gz.msgs.GUICamera', 'gz.msgs.Boolean', req)
    print(f'# sim_capture: gazebo camera {"set" if ok else "NOT set"} ({x}, {y}, {z}) -> ({tx}, {ty}, {tz})')
    return ok


def follow(model, ox, oy, oz, gain=0.2):
    """Camera follows <model> at offset (ox, oy, oz) m and keeps looking at it (CameraTrack FOLLOW_LOOK_AT on the GUI's
    /gui/track topic, gz-gui 8). The older /gui/follow service only sets the target: the GUI's default gain then
    leaves the camera metres behind a moving robot, and /gui/follow/p_gain does not exist in this version."""
    ent = f'{{name: "{model}"}}'
    msg = (f'track_mode: FOLLOW_LOOK_AT, follow_target: {ent}, track_target: {ent}, '
           f'follow_offset: {{x: {ox}, y: {oy}, z: {oz}}}, follow_pgain: {gain}, track_pgain: {gain}')
    ok = False
    for _ in range(3):  # a single publish can be missed before the GUI's subscription is matched
        r = subprocess.run(['gz', 'topic', '-t', '/gui/track', '-m', 'gz.msgs.CameraTrack', '-p', msg],
                           capture_output=True, text=True)
        ok = ok or r.returncode == 0
        time.sleep(0.3)
    print(f'# sim_capture: gazebo camera {"follows" if ok else "NOT following"} {model} at offset '
          f'({ox}, {oy}, {oz}), gain {gain}')
    return ok


def xwd_to_png(data, out):
    h = np.frombuffer(data[:100], dtype='>u4')
    hsize, fmt, depth, w, ht = int(h[0]), int(h[2]), int(h[3]), int(h[4]), int(h[5])
    byte_order, bpp, bpl, ncolors = int(h[7]), int(h[11]), int(h[12]), int(h[19])
    if fmt != 2 or bpp not in (24, 32):
        raise ValueError(f'unsupported XWD (format {fmt}, {bpp} bpp)')
    off = hsize + 12 * ncolors
    px = np.frombuffer(data[off:off + bpl * ht], dtype=np.uint8).reshape(ht, bpl)[:, :w * bpp // 8]
    px = px.reshape(ht, w, bpp // 8)
    rgb = px[:, :, [2, 1, 0]] if byte_order == 0 else px[:, :, [bpp // 8 - 3, bpp // 8 - 2, bpp // 8 - 1]]
    Image.fromarray(np.ascontiguousarray(rgb), 'RGB').save(out, optimize=True)


def rviz_window():
    tree = subprocess.run(['xwininfo', '-root', '-tree'], capture_output=True, text=True).stdout
    for line in tree.splitlines():
        m = re.match(r'\s*(0x[0-9a-f]+) "(.*) - RViz": \("rviz2" "rviz2"\)', line)
        if m:
            return m.group(1)
    return None


def shot(prefix):
    os.makedirs(os.path.dirname(os.path.abspath(prefix)), exist_ok=True)
    wrote = 0
    tmp = tempfile.mkdtemp()
    try:
        if gz_service('/gui/screenshot', 'gz.msgs.StringMsg', 'gz.msgs.Boolean', f'data: "{tmp}"'):
            for _ in range(50):
                files = glob.glob(os.path.join(tmp, '*.png'))
                if files:
                    time.sleep(0.3)
                    shutil.move(files[0], f'{prefix}_gazebo.png')
                    print(f'# sim_capture: wrote {prefix}_gazebo.png')
                    wrote += 1
                    break
                time.sleep(0.1)
        else:
            print('# sim_capture: gazebo screenshot service failed (GUI not running?)')
        wid = rviz_window()
        if wid:
            r = subprocess.run(['xwd', '-id', wid, '-silent'], capture_output=True)
            if r.returncode == 0:
                xwd_to_png(r.stdout, f'{prefix}_rviz.png')
                print(f'# sim_capture: wrote {prefix}_rviz.png')
                wrote += 1
        else:
            print('# sim_capture: no RViz window on X11 (start RViz with QT_QPA_PLATFORM=xcb)')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return wrote


def main():
    if len(sys.argv) == 8 and sys.argv[1] == 'view':
        return 0 if view(*map(float, sys.argv[2:])) else 1
    if len(sys.argv) in (6, 7) and sys.argv[1] == 'follow':
        return 0 if follow(sys.argv[2], *map(float, sys.argv[3:])) else 1
    if len(sys.argv) == 3 and sys.argv[1] == 'shot':
        return 0 if shot(sys.argv[2]) else 1
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
