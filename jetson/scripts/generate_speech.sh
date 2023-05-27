#!/bin/bash
python3 tools/generate_speech.py \
    --input-text="Tôi đang suy nghĩ, hãy đợi câu trả lời trong giây lát." \
    --output-path="assets/voices/think.mp3" \
    --speech-config="configs/speechprocess.yml"