#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
mkdir -p build
python3 score.py
python3 master.py
python3 render.py 1920 1080 build/video_1920x1080.mp4
ffmpeg -v error -y -i build/video_1920x1080.mp4 -i build/score_master.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart ADBS_freefall_1920x1080.mp4
bash ../tools/encode_opener.sh
python3 measure.py
echo PIPELINE_DONE
