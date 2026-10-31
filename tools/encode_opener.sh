#!/usr/bin/env bash
# Deck-ready opener: same picture and sound, smaller file for sharing.
cd "$(dirname "$0")/.."
ffmpeg -v error -y -i video/ADBS_freefall_1920x1080.mp4 -c:v libx264 -preset slow -crf 26 -threads 2 \
  -x264-params rc-lookahead=10 -pix_fmt yuv420p -profile:v high -level 4.1 \
  -c:a aac -b:a 160k -movflags +faststart video/ADBS_opener_deck.mp4
ffmpeg -v error -y -ss 3 -i video/ADBS_opener_deck.mp4 -frames:v 1 video/ADBS_opener_poster.png
echo ENC_DONE
