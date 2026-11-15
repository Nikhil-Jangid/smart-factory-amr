#!/usr/bin/env python3
"""TEST-M5-05 reload check (REQ-M5-06; M5 Task C): the grid that Nav2 map_server serves equals the file.

Usage: python3 TEST-M5-05_reload_check.py <map.yaml>   (map_server must already be active and serving that file)
Exit 0 = every check PASS, 1 = a check FAIL.

The expected grid is built from the files themselves (yaml + PGM P5), with the Nav2 map_server rules for mode
`trinary` and negate 0 (nav2_map_server map_io.cpp): for a pixel value p, occ = (255 - p) / 255; occ > occupied_thresh
-> 100 (occupied); occ < free_thresh -> 0 (free); otherwise -1 (unknown). The image's top row is the map's last row
(row 0 of the grid is the bottom of the image). One /map message is read (transient-local QoS, so the latched map
arrives even though it was published before this node started) and compared field by field: frame, width, height,
resolution, origin (x, y, yaw), and every cell.
"""
import math
import os
import sys

import numpy as np
import rclpy
import yaml
from nav_msgs.msg import OccupancyGrid
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy


def read_pgm(path):
    with open(path, 'rb') as f:
        data = f.read()
    tokens, pos = [], 0
    while len(tokens) < 4:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b'#':
            pos = data.index(b'\n', pos) + 1
            continue
        end = pos
        while not data[end:end + 1].isspace():
            end += 1
        tokens.append(data[pos:end])
        pos = end
    if tokens[0] != b'P5' or int(tokens[3]) > 255:
        raise ValueError(f'{path}: not an 8-bit binary PGM')
    w, h = int(tokens[1]), int(tokens[2])
    return np.frombuffer(data[pos + 1:pos + 1 + w * h], dtype=np.uint8).reshape(h, w)


def expected_grid(yaml_path):
    meta = yaml.safe_load(open(yaml_path))
    img = read_pgm(os.path.join(os.path.dirname(os.path.abspath(yaml_path)), meta['image']))
    if meta.get('mode', 'trinary') != 'trinary' or meta.get('negate', 0):
        raise ValueError('only mode trinary with negate 0 is handled')
    occ = (255.0 - img.astype(float)) / 255.0
    grid = np.full(img.shape, -1, dtype=np.int8)
    grid[occ > meta['occupied_thresh']] = 100
    grid[occ < meta['free_thresh']] = 0
    return meta, np.flipud(grid)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    meta, exp = expected_grid(sys.argv[1])
    rclpy.init()
    node = rclpy.create_node('test_m5_05_reload_check')
    got = []
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
    node.create_subscription(OccupancyGrid, '/map', got.append, qos)
    end = node.get_clock().now().nanoseconds + 15e9
    while not got and node.get_clock().now().nanoseconds < end:
        rclpy.spin_once(node, timeout_sec=0.2)
    pubs = [i.node_name for i in node.get_publishers_info_by_topic('/map')]
    node.destroy_node()
    rclpy.shutdown()
    ok = True

    def check(cond, text):
        nonlocal ok
        print(f'{"PASS" if cond else "FAIL"}  {text}')
        ok &= bool(cond)

    check(bool(got), f'/map received within 15 s (publishers: {sorted(pubs)})')
    if got:
        m = got[0]
        o = m.info.origin
        yaw = math.atan2(2 * (o.orientation.w * o.orientation.z), 1 - 2 * o.orientation.z ** 2)
        check(pubs == ['map_server'], 'only map_server publishes /map')
        check(m.header.frame_id == 'map', f'frame_id "{m.header.frame_id}" (map)')
        check((m.info.width, m.info.height) == (exp.shape[1], exp.shape[0]),
              f'size {m.info.width} x {m.info.height} cells (file {exp.shape[1]} x {exp.shape[0]})')
        check(abs(m.info.resolution - meta['resolution']) < 1e-6,
              f'resolution {m.info.resolution:.6f} m (file {meta["resolution"]})')
        check(abs(o.position.x - meta['origin'][0]) < 1e-6 and abs(o.position.y - meta['origin'][1]) < 1e-6
              and abs(yaw - meta['origin'][2]) < 1e-6,
              f'origin ({o.position.x:.6f}, {o.position.y:.6f}, yaw {yaw:.6f}) (file {meta["origin"]})')
        if (m.info.width, m.info.height) == (exp.shape[1], exp.shape[0]):
            served = np.array(m.data, dtype=np.int8).reshape(m.info.height, m.info.width)
            diff = int((served != exp).sum())
            counts = {v: int((exp == v).sum()) for v in (0, 100, -1)}
            check(diff == 0, f'cells: {diff} of {exp.size} differ (file: {counts[100]} occupied, {counts[0]} free, '
                  f'{counts[-1]} unknown)')
    print(f'# result: {"PASS" if ok else "FAIL"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
