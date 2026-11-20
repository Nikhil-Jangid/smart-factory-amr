#!/usr/bin/env bash
# Screen recording of the Gazebo GUI and RViz windows (2026-11-13: videos of the robot moving).
# Usage: bash tools/sim_record.sh start <prefix>   -> records <prefix>_gazebo.webm and <prefix>_rviz.webm in the background
#        bash tools/sim_record.sh stop <prefix>    -> ends both recordings cleanly (EOS), trims, converts to MP4
# Each window is recorded on its own with GStreamer ximagesrc (X11 windows: start Gazebo and RViz with
# QT_QPA_PLATFORM=xcb under Wayland; a whole-screen capture is black under Wayland), VP9 in WebM, 15 fps.
# ximagesrc captures the visible pixels only: the windows must not cover each other (tools/demo_capture.sh layout).
# A missing window is skipped with a message. The PIDs are kept in <prefix>.recpids between start and stop.
# The first 2-3 s of a capture are stale frames (TS-036): stop cuts them (tools/webm_trim.py auto, cut found in the
# Gazebo video and applied to both). Callers wait 3 s after start before any motion, so no motion is cut.
# Output size: height 676, width from the window's aspect ratio (fixed 800/688 x 676 until 2026-11-15).
# stop then converts each WebM to H.264 MP4 (ffmpeg libx264, CRF 18, preset slow; the most compatible format and,
# measured 2026-11-13, 2-4x smaller than the real-time VP9 at SSIM >= 0.998) and deletes the WebM.
# Without ffmpeg the WebM files are kept.
set -u
CMD=${1:?start|stop}; P=${2:?prefix}
case $CMD in
  start)
    TREE=$(xwininfo -root -tree)
    GW=$(echo "$TREE" | grep -E '\("gz-sim-gui" "Gazebo GUI"\)' | head -1 | awk '{print $1}')
    RW=$(echo "$TREE" | grep -E ' - RViz": \("rviz2" "rviz2"\)' | head -1 | awk '{print $1}')
    : > "$P.recpids"
    for spec in "gazebo $GW" "rviz $RW"; do
      set -- $spec
      if [ -z "${2:-}" ]; then echo "# sim_record: no $1 window, not recorded"; continue; fi
      # Output height 676 (as the fixed sizes used until 2026-11-15) and the width from the window's own aspect
      # ratio, rounded to an even number (I420), so a resized or half-screen window is not stretched.
      read -r WW WH < <(xwininfo -id "$2" | awk '/^ *Width:/{w=$2} /^ *Height:/{h=$2} END{print w, h}')
      set -- "$1" "$2" $(( (676 * WW / WH + 1) / 2 * 2 )) 676
      nohup gst-launch-1.0 -e ximagesrc xid="$2" use-damage=false show-pointer=false ! video/x-raw,framerate=15/1 \
        ! videoconvert ! videoscale ! video/x-raw,format=I420,width="$3",height="$4",pixel-aspect-ratio=1/1 \
        ! vp9enc deadline=1 cpu-used=8 row-mt=true target-bitrate=800000 ! webmmux \
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
  *) echo "usage: $0 start|stop <prefix>"; exit 2 ;;
esac
