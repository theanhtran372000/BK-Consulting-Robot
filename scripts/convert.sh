#!/bin/bash
python3 /utils/convert.py \
    --model assets/models/face_detection_yunet_120x160.onnx \
    --output assets/models/face_detection_yunet_120x160.trt \