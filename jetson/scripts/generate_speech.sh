#!/bin/bash
python3 tools/generate_speech.py \
    --input-text="Đã xảy ra lỗi. Mời thử lại." \
    --output-path="assets/voices/retry.mp3" \
    --speech-config="configs/speechprocess.yml"