#!/usr/bin/env python3
"""Cut the stale start of WebM screen recordings and re-encode them in place (tools/sim_record.sh, 2026-11-13).

Why: an ximagesrc capture of an XWayland OpenGL window delivers stale window content for about the first 2-3 s
(observed: a Gazebo camera view set before recording appears only 2.1-2.6 s into the video; TS-036).
Usage: python3 tools/webm_trim.py <seconds|auto> <first.webm> [<more.webm> ...]
  auto: the cut is found in the first file (the Gazebo recording, where the jump from the stale picture to the
        live view is large): the first frame within 4 s whose luminance differs from frame 0 by a mean of more
        than 1.0 (0-255 scale). If there is no such jump, the stale frames already show the live view (camera set
        well before recording, robot at rest) and nothing is cut. The same cut is applied to every file: the
        windows were recorded together, and the RViz picture changes too little to detect the jump on its own.
Re-encodes with the recorder's settings (VP9, 800 kbit/s); timestamps are shifted to start at 0. Prints the cut.
"""
import os
import sys

import gi
import numpy as np
gi.require_version('Gst', '1.0')
from gi.repository import Gst  # noqa: E402

LIMIT = 4 * Gst.SECOND


def frames(path):
    dec = Gst.parse_launch(f'filesrc location="{path}" ! decodebin ! videoconvert ! video/x-raw,format=I420 '
                           '! appsink name=sink sync=false emit-signals=false max-buffers=50')
    sink = dec.get_by_name('sink')
    dec.set_state(Gst.State.PLAYING)
    try:
        while True:
            sample = sink.emit('pull-sample')
            if sample is None:
                return
            yield sample
    finally:
        dec.set_state(Gst.State.NULL)


def find_cut(path):
    first = None
    for sample in frames(path):
        buf = sample.get_buffer()
        s = sample.get_caps().get_structure(0)
        w, h = s.get_value('width'), s.get_value('height')
        ok, m = buf.map(Gst.MapFlags.READ)
        y = np.frombuffer(m.data, dtype=np.uint8, count=w * h).reshape(h, w)[::4, ::4].astype(np.int16)
        buf.unmap(m)
        if first is None:
            first = y
        elif buf.pts >= LIMIT:
            return 0
        elif np.abs(y - first).mean() > 1.0:
            return buf.pts
    return 0


def cut_file(path, cut):
    tmp = path + '.trim.webm'
    enc = Gst.parse_launch('appsrc name=src format=time ! vp9enc deadline=1 cpu-used=8 row-mt=true '
                           f'target-bitrate=800000 ! webmmux ! filesink location="{tmp}"')
    appsrc, started, kept = enc.get_by_name('src'), False, 0
    for sample in frames(path):
        buf = sample.get_buffer()
        if buf.pts < cut:
            continue
        if not started:
            appsrc.set_property('caps', sample.get_caps())
            enc.set_state(Gst.State.PLAYING)
            started = True
        out = buf.copy_deep()
        out.pts, out.dts = buf.pts - cut, Gst.CLOCK_TIME_NONE
        appsrc.emit('push-buffer', out)
        kept += 1
    if not started:
        print(f'# webm_trim: {path} is shorter than the cut; left unchanged')
        return False
    appsrc.emit('end-of-stream')
    msg = enc.get_bus().timed_pop_filtered(120 * Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR)
    enc.set_state(Gst.State.NULL)
    if msg is None or msg.type == Gst.MessageType.ERROR:
        print(f'# webm_trim: re-encoding {path} failed; left unchanged')
        os.remove(tmp)
        return False
    os.replace(tmp, path)
    print(f'# webm_trim: {path}: first {cut / Gst.SECOND:.1f} s cut, {kept} frames kept')
    return True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    Gst.init(None)
    files = sys.argv[2:]
    cut = find_cut(files[0]) if sys.argv[1] == 'auto' else int(float(sys.argv[1]) * Gst.SECOND)
    if cut == 0:
        print(f'# webm_trim: no stale-frame jump in the first {LIMIT / Gst.SECOND:.0f} s of {files[0]}; nothing cut')
        return 0
    return 0 if all([cut_file(f, cut) for f in files]) else 1


if __name__ == '__main__':
    sys.exit(main())
