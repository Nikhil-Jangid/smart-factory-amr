#!/usr/bin/env python3
"""TEST-M5-07 checker sensitivity (REQ-M5-08; M5 Task B). No ROS needed (runs in CI).

Usage: python3 -I TEST-M5-07_distort.py <map.yaml> [<output dir>]
       Without an output dir the copies go to a temporary folder that is deleted afterwards (the runner and CI
       call it this way; they run commands without a shell).
Exit 0 = the original map PASSES the checker and every distorted copy FAILS the measure it targets; 1 otherwise;
2 = the map cannot be read.

A checker that passes good maps is only half a test: it must also fail bad ones. This tool writes five distorted
copies of a recorded map (same Nav2 map_saver format, same size, resolution and origin) and runs the checker
(TEST-M5_map_check.py) on the original and on each copy. Distortions (test plan §10, TEST-M5-07):
  rotate  2 deg about the map-frame origin (the robot's start)   -> expected FAIL: dimensions (wall rotation, 1 deg)
  shift   0.15 m in +x                                           -> expected FAIL: wall_accuracy (P95 0.10 m)
  scale   x 1.02 about the map-frame origin                      -> expected FAIL: dimensions (10.0 x 8.0 +/- 0.10 m)
  erase   every occupied cell of the north wall band (y >= 3.7 m) set to unknown -> expected FAIL: completeness (90 %)
  ghost   a 2.0 m wall, 2 cells thick, in free space (0.5 <= x <= 2.5, y = -1.5)  -> expected FAIL: ghosts (0.5 %)
Other measures may fail as well (a rotated map also has a larger wall P95); they are reported, not required.
Each copy is drawn on the source image padded with 1.0 m of unknown cells on every side (origin moved by the same
amount), so that no distorted wall falls outside the image: a recorded map is cropped close to the mapped area, and
without the margin a x 1.02 scale would cut the east and north walls off, failing for the wrong reason. The
geometric distortions resample by nearest neighbour (each output cell takes the source cell its centre maps back
to); cells that map outside the source image are unknown. The printed occupied-cell count of each copy shows that
no walls were lost (the erase and ghost copies change it on purpose).
"""
import importlib.util
import json
import math
import os
import sys
import tempfile

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('map_check', os.path.join(HERE, 'TEST-M5_map_check.py'))
mc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mc)

OCC, FREE, UNKNOWN = 0, 254, 205
GHOST = ((0.5, -1.5), (2.5, -1.5))   # ghost wall end points (x, y), m; at least 0.5 m from every true surface
PAD = 1.0                            # margin of unknown cells around each copy, m


def cell_centres(img, meta):
    h, w = img.shape
    res, ox, oy = meta['resolution'], meta['origin'][0], meta['origin'][1]
    cols, rows = np.meshgrid(np.arange(w), np.arange(h))
    return ox + (cols + 0.5) * res, oy + (h - rows - 0.5) * res


def pad(img, meta, margin=PAD):
    """The image with `margin` m of unknown cells added on every side, and its moved origin."""
    n = int(round(margin / meta['resolution']))
    out = np.pad(img, n, constant_values=UNKNOWN)
    m = dict(meta, origin=[meta['origin'][0] - n * meta['resolution'], meta['origin'][1] - n * meta['resolution'],
                           meta['origin'][2]])
    return out, m


def resample(img, meta, inverse):
    """Output cell centre (x, y) takes the source cell containing inverse(x, y); outside the source: unknown."""
    h, w = img.shape
    res, ox, oy = meta['resolution'], meta['origin'][0], meta['origin'][1]
    x, y = cell_centres(img, meta)
    xs, ys = inverse(x, y)
    col = np.floor((xs - ox) / res).astype(int)
    row = h - 1 - np.floor((ys - oy) / res).astype(int)
    inside = (col >= 0) & (col < w) & (row >= 0) & (row < h)
    out = np.full_like(img, UNKNOWN)
    out[inside] = img[row[inside], col[inside]]
    return out


def rotate(img, meta, deg=2.0):
    a = math.radians(deg)
    return resample(img, meta, lambda x, y: (math.cos(a) * x + math.sin(a) * y, -math.sin(a) * x + math.cos(a) * y))


def shift(img, meta, dx=0.15):
    return resample(img, meta, lambda x, y: (x - dx, y))


def scale(img, meta, k=1.02):
    return resample(img, meta, lambda x, y: (x / k, y / k))


def erase(img, meta, y_min=3.7):
    _x, y = cell_centres(img, meta)
    out = img.copy()
    out[(y >= y_min) & (img < UNKNOWN)] = UNKNOWN
    return out


def ghost(img, meta, seg=GHOST, cells=2):
    x, y = cell_centres(img, meta)
    (x0, y0), (x1, y1) = seg
    res = meta['resolution']
    out = img.copy()
    # cells whose centre lies within the segment's x range and within `cells` cells of its line (horizontal segment)
    band = (x >= x0) & (x <= x1) & (y >= y0 - cells * res / 2) & (y < y0 + cells * res / 2)
    out[band] = OCC
    return out


DISTORTIONS = [('rotate', rotate, 'dimensions'), ('shift', shift, 'wall_accuracy'), ('scale', scale, 'dimensions'),
               ('erase', erase, 'completeness'), ('ghost', ghost, 'ghosts')]


def write_map(img, meta, prefix):
    with open(prefix + '.pgm', 'wb') as f:
        f.write(b'P5\n%d %d\n255\n' % (img.shape[1], img.shape[0]))
        f.write(img.tobytes())
    m = dict(meta, image=os.path.basename(prefix) + '.pgm')
    with open(prefix + '.yaml', 'w') as f:
        yaml.safe_dump(m, f, default_flow_style=None, sort_keys=False)
    return prefix + '.yaml'


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        return 2
    if len(sys.argv) == 2:
        with tempfile.TemporaryDirectory() as tmp:
            return run(sys.argv[1], tmp)
    return run(sys.argv[1], sys.argv[2])


def run(src, outdir):
    try:
        meta, img, _occ = mc.load_map(src)
    except (OSError, ValueError, KeyError) as exc:
        print(f'# cannot read the map: {type(exc).__name__}: {exc}')
        return 2
    os.makedirs(outdir, exist_ok=True)
    boxes = [b for b in mc.route.world_boxes().values() if b[4] > mc.route.SCAN_Z]
    gd = mc.surface_distance(np.array([GHOST[0], GHOST[1], ((GHOST[0][0] + GHOST[1][0]) / 2, GHOST[0][1])]), boxes)
    if gd.min() < 0.5:
        print(f'# ghost wall placement {GHOST} is only {gd.min():.2f} m from a true surface (needs >= 0.5 m)')
        return 2
    ok = True
    summary = {'source': os.path.basename(src), 'cases': {}}
    print(f'# TEST-M5-07 checker sensitivity on {os.path.basename(src)}')
    print('\n## original')
    res, out = mc.check(src)
    print('\n'.join(out))
    print(f'{"PASS" if res["pass"] else "FAIL"}  original map passes every measure')
    ok &= res['pass']
    summary['cases']['original'] = {'expected': 'PASS', 'failed_measures': [k for k, v in res['measures'].items()
                                                                            if not v]}
    for name, fn, target in DISTORTIONS:
        prefix = os.path.join(outdir, f'{os.path.splitext(os.path.basename(src))[0]}_{name}')
        pimg, pmeta = pad(img, meta)
        path = write_map(fn(pimg, pmeta), pmeta, prefix)
        print(f'\n## {name} -> expected FAIL on {target}')
        res, out = mc.check(path)
        print('\n'.join(out))
        failed = [k for k, v in res['measures'].items() if not v]
        hit = target in failed
        print(f'{"PASS" if hit else "FAIL"}  {name}: the checker fails {target} '
              f'(measures failed: {", ".join(failed) or "none"})')
        ok &= hit
        summary['cases'][name] = {'expected': target, 'failed_measures': failed, 'detected': hit}
    summary['pass'] = bool(ok)
    with open(os.path.join(outdir, 'TEST-M5-07_summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)
    print(f'\n# result: {"PASS" if ok else "FAIL"}')
    print(f'# overall: {"ORIGINAL PASSED, EVERY DISTORTION DETECTED" if ok else "AT LEAST ONE CASE NOT AS EXPECTED (FAIL)"}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
