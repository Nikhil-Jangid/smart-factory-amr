#!/usr/bin/env bash
# Screen recording of the Gazebo GUI and RViz windows (2026-11-13: videos of the robot moving).
# Usage: bash tools/sim_record.sh start <prefix>   -> records <prefix>_gazebo.webm and <prefix>_rviz.webm in the background
#        bash tools/sim_record.sh stop <prefix>    -> ends both recordings cleanly (EOS), trims, converts to MP4
#        bash tools/sim_record.sh trim <prefix> <start s> <end s>   -> keeps only [start, end] of both MP4s, re-encoded
#          with the same settings as stop (2026-11-23, user: cut idle footage before and after the motion; both
#          windows are recorded together, so one cut applies to both). Done before gallery review, never on evidence.
# Each window is recorded on its own with GStreamer ximagesrc (X11 windows: start Gazebo and RViz with
# QT_QPA_PLATFORM=xcb under Wayland; a whole-screen capture is black under Wayland), VP9 in WebM, 15 fps (intermediate at
# 3 Mbit/s since 2026-11-21 with native-size capture; 0.8 Mbit/s before).
# ximagesrc captures the visible pixels only: the windows must not cover each other (tools/demo_capture.sh layout).
# A missing window is skipped with a message. The PIDs are kept in <prefix>.recpids between start and stop.
# The first 2-3 s of a capture are stale frames (TS-036): stop cuts them (tools/webm_trim.py auto, cut found in the
# Gazebo video and applied to both). Callers wait 3 s after start before any motion, so no motion is cut.
# Output size: the window's own size, rounded down to even numbers (I420) (since 2026-11-21; until then height 676 with
# the width from the aspect ratio, which shrank an 845 px RViz window to 80 % and blurred its text and thin lines;
# fixed 800/688 x 676 until 2026-11-15).
# stop then converts each WebM to H.264 MP4 (ffmpeg libx264, CRF 18, preset slow; the most compatible format and,
# measured 2026-11-13, 2-4x smaller than the real-time VP9 at SSIM >= 0.998) and deletes the WebM.
# Without ffmpeg the WebM files are kept.
set -u
CMD=${1:?start|stop|trim}; P=${2:?prefix}
case $CMD in
  start)
    TREE=$(xwininfo -root -tree)
    GW=$(echo "$TREE" | grep -E '\("gz-sim-gui" "Gazebo GUI"\)' | head -1 | awk '{print $1}')
    RW=$(echo "$TREE" | grep -E ' - RViz": \("rviz2" "rviz2"\)' | head -1 | awk '{print $1}')
    : > "$P.recpids"
    for spec in "gazebo $GW" "rviz $RW"; do
      set -- $spec
      if [ -z "${2:-}" ]; then echo "# sim_record: no $1 window, not recorded"; continue; fi
      # Native size: the window's width and height, rounded down to even numbers (I420); no scaling.
      read -r WW WH < <(xwininfo -id "$2" | awk '/^ *Width:/{w=$2} /^ *Height:/{h=$2} END{print w, h}')
      set -- "$1" "$2" $(( WW / 2 * 2 )) $(( WH / 2 * 2 ))
      nohup gst-launch-1.0 -e ximagesrc xid="$2" use-damage=false show-pointer=false ! video/x-raw,framerate=15/1 \
        ! videoconvert ! videoscale ! video/x-raw,format=I420,width="$3",height="$4",pixel-aspect-ratio=1/1 \
        ! vp9enc deadline=1 cpu-used=8 row-mt=true target-bitrate=3000000 ! webmmux \
        ! filesink location="${P}_$1.webm" > /dev/null 2>&1 &
      echo $! >> "$P.recpids"
      echo "# sim_record: recording $1 window to ${P}_$1.webm"
    done ;;
  stop)
    [ -f "$P.recpids" ] || { echo "# sim_record: nothing to stop"; exit 0; }
    for pid in $(cat "$P.recpids"); do kill -INT "$pid" 2>/dev/null; done
    for pid in $(cat "$P.recpids"); do for _ in $(seq 20); do kill -0 "$pid" 2>/dev/null || break; timeout 0.5 tail -f /dev/null; done; done
    rm -f "$P.recpids"
    # An empty recording (the capture pipeline ended at once, e.g. the window went away) makes webm_trim.py wait
    # forever for a first frame (TS-046): report it and delete it instead.
    for w in "${P}_gazebo.webm" "${P}_rviz.webm"; do
      [ -f "$w" ] && [ ! -s "$w" ] && { echo "# sim_record: $w is empty (capture failed), deleted"; rm -f "$w"; }
    done
    V=$(ls "${P}_gazebo.webm" "${P}_rviz.webm" 2>/dev/null)
    [ -n "$V" ] && python3 tools/webm_trim.py auto $V | sed "s|$PWD/||g"
    for w in $V; do
      if command -v ffmpeg > /dev/null && ffmpeg -hide_banner -loglevel error -y -i "$w" -c:v libx264 -preset slow \
           -crf 18 -pix_fmt yuv420p -movflags +faststart -an "${w%.webm}.mp4"; then rm -f "$w"; fi
    done
    ls "${P}"_*.mp4 "${P}"_*.webm 2>/dev/null | sed 's/^/# sim_record: wrote /' ;;
  trim)
    T0=${3:?start s}; T1=${4:?end s}
    for m in "${P}"_gazebo.mp4 "${P}"_rviz.mp4; do
      [ -s "$m" ] || { echo "# sim_record: $m missing; skipped"; continue; }
      ffmpeg -hide_banner -loglevel error -y -ss "$T0" -to "$T1" -i "$m" -c:v libx264 -preset slow \
        -crf 18 -pix_fmt yuv420p -movflags +faststart -an "${m%.mp4}.trim.mp4" && mv "${m%.mp4}.trim.mp4" "$m" \
        && echo "# sim_record: trimmed $m to ${T0}-${T1} s ($(du -h "$m" | cut -f1))"
    done ;;
  *) echo "usage: $0 start|stop <prefix> | trim <prefix> <start s> <end s>"; exit 2 ;;
esac
