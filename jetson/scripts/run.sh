#!/bin/bash
# Restart audio devices
sudo bash scripts/restart_media.sh

# Run program
python3 app.py \
  --face-track-config=configs/facetrack.yml \
  --speech-process-config=configs/speechprocess.yml \
  --log-config=configs/log.yml