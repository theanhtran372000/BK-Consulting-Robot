#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    TensorRT YuNet demo.

    Copyright (c) 2021 Nobuo Tsukamoto
    This software is released under the MIT License.
    See the LICENSE file in the project root for more information.
"""

import os
import time
import yaml
import serial
import argparse

import cv2
import numpy as np

from models.yunet import TrtYuNet

from utils.draw import draw_caption, draw_circle, draw_rectangle
from utils.serial import send_angle
from utils.angle import calculate_angle

def get_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--config", type=str, default='configs/infer.yml', help="Path to config file", required=True)
    
    return parser

def main():
    
    # Parse CLI args    
    parser = get_parser()
    args = parser.parse_args()
    
    # Load configs
    with open(args.config, 'r') as f:
        configs = yaml.load(f, yaml.FullLoader)
    print('[INFO] Configs: ', configs)
    
    # Open camera
    print('[INFO] Open camera')
    cap = cv2.VideoCapture(configs['cam']['device'])
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("[INFO] Camera info: h = {} \t w = {} \t fps = {} ".format(h, w, fps))
    
    ser = serial.Serial(port=configs['serial']['port'], baudrate=configs['serial']['baudrate'])
    time.sleep(configs['serial']['warmup'])
    
    # Load Yunet model
    model_name = os.path.splitext(os.path.basename(configs['model']['path']))[0]
    input_shape = tuple(map(int, configs['infer']['input_shape'].split(",")))
    model = TrtYuNet(
        model_path=configs['model']['path'],
        input_size=input_shape,
        conf_threshold=configs['infer']['conf_threshold'],
        nms_threshold=configs['infer']['nms_threshold'],
        top_k=configs['infer']['top_k'],
        keep_top_k=configs['infer']['keep_top_k'],
    ) 
    w_scale = w / input_shape[0]
    h_scale = h / input_shape[1]
    print('[INFO] Load model: ', model_name)

    # Inferencing
    log_state = configs['log']['state']
    elapsed_list = []
    since = time.perf_counter()
    detect_face_since = time.time()
    while cap.isOpened():
        # Read and horizontal flip image (camera vision is opposite to human vision)
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] VideoCapture read failed!")
            break
        frame = cv2.flip(frame, 1)

        # Inference
        start = time.perf_counter()
        results = model.infer(frame)
        
        # Preprocess boxes
        bboxes = []
        for det in results:
            xmin = int(det[0] * w_scale)
            ymin = int(det[1] * h_scale)
            xmax = xmin + int(det[2] * w_scale)
            ymax = ymin + int(det[3] * h_scale)
            
            conf = det[-1]
            landmarks = det[4:14].astype(np.int32).reshape((5, 2))
            
            bboxes.append([xmin, ymin, xmax, ymax, conf, landmarks])
        
        # Adjust camera
        if len(bboxes) > 0: # Detect face
            detect_face_since = time.time()
            
            # Sort by box area  
            sorted(bboxes, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]), reverse=True)
            
            # Get biggest face
            face = bboxes[0]
            
            # print(f'[INFO] {face[:4]}')
            
            # Calculate rotation angle
            x_delta, y_delta = calculate_angle(
                (face[0] + face[2]) // 2, (face[1] + face[3]) // 2,
                w, h,
                configs['cam']['scope']['x'], configs['cam']['scope']['y'],
                configs['cam']['grid']
            )
            
            # Send angle to arduino
            send_angle(ser, x_delta, y_delta, reset=False, log=log_state)
                
        else:
            # After a while not detect faces
            if time.time() - detect_face_since >= configs['cam']['reset_every']:
                if log_state:
                    print('[INFO] Reset camera position after {}s not detecting faces!'.format(configs['cam']['reset_every']))
                send_angle(ser, 0, 0, reset=True, log=log_state)   # Reset camera position
        
        # Future dev:
        # - 
        
        # # Draw result.
        # im = frame
        # print('[INFO] Found {} faces'.format(len(results)))
        # for det in results:
        #     xmin = int(det[0] * w_scale)
        #     xmax = int(det[2] * w_scale)
        #     ymin = int(det[1] * h_scale)
        #     ymax = int(det[3] * h_scale)

        #     # Draw on image
        #     draw_rectangle(im, (xmin, ymin, xmax, ymax))

        #     conf = det[-1]
        #     draw_caption(im, (xmin, ymin - 10), "{:.4f}".format(conf))

        #     landmarks = det[4:14].astype(np.int32).reshape((5, 2))
        #     for landmark in landmarks:
        #         draw_circle(im, (int(landmark[0] * w_scale), int(landmark[1] * h_scale)))

        # Calc fps.
        inference_time = (time.perf_counter() - start) * 1000
        elapsed_list.append(inference_time)
        
        if (time.perf_counter() - since) > configs['log']['every']:
            # elapsed_list.pop(0)
            avg_elapsed_ms = np.mean(elapsed_list)
            avg_text = "Average {0:.2f}ms {1:.1f}FPS".format(avg_elapsed_ms, 1000 / avg_elapsed_ms)
            
            # log
            print('[INFO]', avg_text)
            
            # reset
            since = time.perf_counter()
            elapsed_list = []

        # # Display fps
        # fps_text = "Inference: {0:.2f}ms {1:.1f}FPS".format(inference_time, 1000 / inference_time)
        # display_text = model_name + " " + fps_text + avg_text
        # draw_caption(im, (10, 30), display_text)

    # When everything done, release the window
    cap.release()

if __name__ == "__main__":
    main()
