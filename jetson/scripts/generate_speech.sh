#!/bin/bash
python3 tools/generate_speech.py \
    --input-text="Tôi không nghe thấy gì hết" \
    --output-path="assets/voices/hear_nothing.wav" \
    --speech-config="configs/speechprocess.yml"