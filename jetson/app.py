import os
import re
import time
import yaml
import uuid
import json
import queue
import serial
import pprint
import argparse
import requests
from pathlib import Path
from loguru import logger

import cv2
import pydub
import openai
import sseclient
import numpy as np
from gtts import gTTS
import speech_recognition as sr
from threading import Thread, currentThread

from models.yunet import TrtYuNet

from utils.draw import draw_caption, draw_circle, draw_rectangle
from utils.serial import send_angle
from utils.angle import calculate_angle
from utils.sound import play_sound_async, play_sound_sync
from utils.answer import get_chatgpt_answer, apply_prompt
from utils.distance import in_active_range

def get_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--face-track-config", type=str, default='configs/facetrack.yml', help="Path to face tracking config file")
    parser.add_argument("--speech-process-config", type=str, default='configs/speechprocess.yml', help='Path to speech processing config file')
    
    return parser

# Update camera position function
cam_stop = False
current_face = None
def track_face(cap, w, h, w_scale, h_scale, model, ser, cam_configs):
    
    # Global vars
    global error
    global cam_stop
    global current_face
    
    log_state = cam_configs['log']['state']
    elapsed_list = []
    since = time.perf_counter()
    detect_face_since = time.time()
    try:
        while not cam_stop:
            # Read and horizontal flip image (camera vision is opposite to human vision)
            ret, frame = cap.read()
            if not ret:
                logger.error("VideoCapture read failed!")
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
                
                # Save result to global var
                current_face = frame[face[1] : face[3], face[0] : face[2]].copy()
                # logger.info('Face size: ' +  str(current_face.shape))
                
                # Calculate rotation angle
                x_delta, y_delta = calculate_angle(
                    (face[0] + face[2]) // 2, (face[1] + face[3]) // 2,
                    w, h,
                    cam_configs['cam']['scope']['x'], cam_configs['cam']['scope']['y'],
                    cam_configs['cam']['grid']
                )
                
                # Send angle to arduino
                send_angle(ser, x_delta, y_delta, reset=False, log=log_state)
                    
            else:
                # After a while not detect faces
                if time.time() - detect_face_since >= cam_configs['cam']['reset_every']:
                    if log_state:
                        logger.info('Reset camera position after {}s not detecting faces!'.format(cam_configs['cam']['reset_every']))
                    
                    # Reset camera
                    send_angle(ser, 0, 0, reset=True, log=log_state)   # Reset camera position
                    
                    # Reset system state
                    current_face = None
                    error = False
            
            # Future dev:
            # TODO: Threshold for face size

            # Calc fps.
            inference_time = (time.perf_counter() - start) * 1000
            elapsed_list.append(inference_time)
            
            if (time.perf_counter() - since) > cam_configs['log']['every']:
                # elapsed_list.pop(0)
                avg_elapsed_ms = np.mean(elapsed_list)
                avg_text = "Face tracking: Average {0:.2f}ms {1:.1f}FPS".format(avg_elapsed_ms, 1000 / avg_elapsed_ms)
                
                # log
                logger.info(avg_text)
                
                # reset
                since = time.perf_counter()
                elapsed_list = []
        
        logger.info('{}: Stopped!'.format(currentThread().getName()))
    
    finally:
        cap.release()


answer_queue = queue.Queue()
# Run in background
def speak_answer():
    global answer_queue
    
    start = time.time()
    while True:
        # Get an speech from queue
        sentence, answerpath = answer_queue.get()
        if sentence == '[DONE]':
            logger.info('Done speaking after {:.2f}s!'.format(time.time() - start))
            break
        
        logger.info('Speak: ' + sentence)
        
        # Speak
        play_sound_sync(answerpath)
        
        # Remove that speech
        os.remove(answerpath)

word_queue = queue.Queue()
def generate_speech(speech_configs):
    
    # global vars
    global word_queue
    global answer_queue
    global error
    
    # Params
    final_word = speech_configs['answer']['finish_word']
    break_word = speech_configs['answer']['break_word']
    split_char = speech_configs['tts']['split_char']
    num_sent = speech_configs['tts']['num_sent']
    lang = speech_configs['tts']['lang']
    slow = speech_configs['tts']['slow']
    save_dir = speech_configs['save']['dir']
    sound_path = speech_configs['sample']['retry']
    
    # List unpacked words
    sent_list = []
    stream = "" 
    total_time = 0
    done = False
    
    # Empty answer queue first
    while not answer_queue.empty():
        answer_queue.get()
    
    # Read until final word reached
    try:
        # Create speak thread
        speak_thread = Thread(
            name='Speaking thread',
            target=speak_answer
        )
        speak_thread.start()
        
        # Start reading sentence
        while True:
            # Get a word from queue and add to word stream
            word = word_queue.get()
            
            # Remove line break characters
            word = word.replace(break_word, ' ')
            word = re.sub(' +', ' ', word)
            # print('[{}] - {}'.format(word, len(word)))
            stream += word
            
            # Split sentence every time see a split character or finish word
            if split_char in stream:
                idx = stream.find(split_char)
                sent_list.append(stream[: idx + len(split_char)])
                stream = stream[idx + len(split_char):]
            
            if final_word in stream:
                idx = stream.find(final_word)
                sent_list.append(stream[: idx])
                stream = ""
                done = True
            
            # If get enough sentence or final word
            if len(sent_list) >= num_sent or done:
                sentence = "".join(sent_list)
                if len(sentence) == 0:
                    logger.error('Speak: Get empty sentence')
                    continue
                # logger.info('Speak: ' + sentence)
                
                # Speech to text this sentence
                start = time.time()
                speech = gTTS(
                    text=sentence, 
                    lang=lang, 
                    slow=slow
                )
                
                answerfile = '{}.mp3'.format(str(uuid.uuid4()))
                answerpath = os.path.join(save_dir, answerfile)
                speech.save(answerpath)
                total_time += time.time() - start
                
                # # Speak
                # play_sound_sync(answerpath)
                # Add to speech queue
                answer_queue.put((sentence, answerpath))
                
                # Postprocess
                # os.remove(answerpath) # Delete temp file
                sent_list = [] # Reset
                    
            # Stop this thread if done flag is raise
            if done:
                break
        
        logger.info('Text to speech done after {:.2f}s'.format(total_time))
        
        # Wait speak thread to stop
        answer_queue.put(('[DONE]', ''))
        speak_thread.join()
        
    except:
        logger.exception("Fail to generate speech")
        play_sound_sync(sound_path)
        error = True
        
# Vars
error = False
def main():
    
    ### === CONFIG SECTION === ###
    # Global vars
    global error
    global word_queue
    global cam_stop
    global current_face
    
    # Parse CLI args    
    parser = get_parser()
    args = parser.parse_args()
    
    # Load face tracking configs
    with open(args.face_track_config, 'r') as f:
        cam_configs = yaml.load(f, yaml.FullLoader)
    logger.info('Face tracking configs: \n' + pprint.pformat(cam_configs))
    
    with open(args.speech_process_config, 'r') as f:
        speech_configs = yaml.load(f, yaml.FullLoader)
    logger.info('Speech processing configs: \n' + pprint.pformat(speech_configs))
    
    # Config openai
    openai.api_key = open(speech_configs['answer']['key'], 'r').read().strip()
    
    # Create dir
    Path(speech_configs['save']['dir']).mkdir(parents=True, exist_ok=True)
    
    ### === CAMERA SECTION === ###
    # 1. Init on main thread
    # Open camera
    logger.info('Open camera')
    cap = cv2.VideoCapture(cam_configs['cam']['device'])
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    logger.info("Camera info: h = {} \t w = {} \t fps = {} ".format(h, w, fps))
    
    ser = serial.Serial(port=cam_configs['serial']['port'], baudrate=cam_configs['serial']['baudrate'])
    time.sleep(cam_configs['serial']['warmup'])
    
    # Load Yunet model
    model_name = os.path.splitext(os.path.basename(cam_configs['model']['path']))[0]
    input_shape = tuple(map(int, cam_configs['infer']['input_shape'].split(",")))
    model = TrtYuNet(
        model_path=cam_configs['model']['path'],
        input_size=input_shape,
        conf_threshold=cam_configs['infer']['conf_threshold'],
        nms_threshold=cam_configs['infer']['nms_threshold'],
        top_k=cam_configs['infer']['top_k'],
        keep_top_k=cam_configs['infer']['keep_top_k'],
    ) 
    w_scale = w / input_shape[0]
    h_scale = h / input_shape[1]
    logger.info('Load model: ' + model_name)

    # 2. Run on background thread
    face_track_thread = Thread(
        name='Face Tracking Thread',
        target=track_face,
        args=(
            cap, 
            w, h, 
            w_scale, h_scale, 
            model, 
            ser, 
            cam_configs
        )
    )
    face_track_thread.start()
    
    
    ### === SPEECH SECTION === ###
    # Running main thread
    currentThread().setName('Main Thread')
    
    try:
        # Create speech recognizer
        listener = sr.Recognizer()
        
        # Open microphone
        with sr.Microphone(device_index=speech_configs['device']['mic_index']) as mic:
            
            # Loop
            while True:
                
                # Deactive if can't detect face 
                if current_face is None:
                    time.sleep(speech_configs['device']['sleep_time'])
                    continue
                
                # Or face out of range
                distance, in_range = in_active_range(
                    current_face,
                    cam_configs['cam']['active_range'],
                    cam_configs['cam']['facesize_1m'],
                    cam_configs['cam']['range_precise']
                )
                
                if not in_range:
                    time.sleep(speech_configs['device']['sleep_time'])
                    continue
                
                # Else: active to user
                logger.info('Detect user in active range. Distance {}m.'.format(distance))
                
                
                # LISTEN
                # Process background noise
                listener.adjust_for_ambient_noise(mic)
                
                # Greet if start or not error in previous time
                if not error:
                    logger.info('Greet')
                    play_sound_sync(speech_configs['sample']['greet'])
                
                # Wait for speech
                logger.info('Listening')
                voice = listener.listen(mic)
                since = time.time()
                logger.info("I'm hearing something...")
                    
                
                # SPEECH TO TEXT
                # C1: Use Google API
                try:
                    start = time.time()
                    transcript = listener.recognize_google(voice, language=speech_configs['stt']['lang'])
                    logger.info('Speech to text done after {:.2f}s'.format(time.time() - start))
                    logger.success('Transcript: ' + transcript)
                    
                    if speech_configs['statement']['exit'].lower() in transcript.lower():
                        logger.info('Here exit state: {}'.format(speech_configs['statement']['exit']))
                        break
                except sr.UnknownValueError:
                    logger.exception("Can't hear what you're saying!")
                    play_sound_sync(speech_configs['sample']['repeat'])
                    error = True
                    continue
                except:
                    logger.exception("Some errors occured while doing STT")
                    play_sound_sync(speech_configs['sample']['retry'])
                    error = True
                    continue
                
                
                # ANSWER
                start = time.time()
                
                # Not streaming
                # try:
                #     # Send request to server
                #     question = apply_prompt(transcript, speech_configs['answer']['prompt']['default'])
                #     response = requests.post(
                #         'http://{}:{}/answer'.format(
                #             speech_configs['server']['address'],
                #             speech_configs['server']['port']
                #         ),
                #         data={
                #             'question': question
                #         }
                #     )
                #     logger.info('Generate answer done after {:.2f}s'.format(time.time() - start))
                #     response = json.loads(response.text)
                #     if response['state'] != 'success':
                #         logger.error(response['message'])
                #         continue
                #     else:
                #         answer = response['result']['answer']
                #         logger.success('Question: "{}"'.format(question))
                #         logger.success('Answer: "{}"'.format(answer))
                # except:
                #     logger.error("Can't get answer. Try again.")
                #     play_sound_sync(speech_configs['sample']['retry'])
                #     error = True
                #     continue
                
                # Streaming
                try:
                    # Send request to server
                    # question = apply_prompt(transcript, speech_configs['answer']['prompt']['default'])
                    
                    # Announce
                    play_sound_async(speech_configs['sample']['think'])
                    
                    # Get answer
                    question = transcript
                    response = requests.post(
                        'http://{}:{}/stream_answer_stable'.format(
                            speech_configs['server']['address'],
                            speech_configs['server']['port']
                        ),
                        json={
                            'question': question
                        },
                        stream=True
                    )
                    
                    # Empty queue
                    while not word_queue.empty():
                        word_queue.get()
                        
                    # Start TTS thread
                    tts_thread = Thread(
                        name='TTS Thread',
                        target=generate_speech,
                        args=(
                            speech_configs,
                        )
                    )
                    tts_thread.start()
                    
                    # Recieving object
                    has_recieved = False
                    client = sseclient.SSEClient(response)
                    for event in client.events():
                        if not has_recieved:
                            logger.info('Establish connection done after {:.2f}s'.format(time.time() - start))
                            has_recieved = True
                        word = event.data
                        word_queue.put(word)                           
                        if word == speech_configs['answer']['finish_word']:
                            logger.info('Generate answer done after {:.2f}s'.format(time.time() - start))                         
                    
                    # Wait for tts to stop
                    tts_thread.join()
                except KeyboardInterrupt:
                    logger.error('Getting answer is interrupted by user!')
                except:
                    logger.exception("Can't get answer. Try again.")
                    play_sound_sync(speech_configs['sample']['retry'])
                    error = True
                    continue
                
                # TEXT TO SPEECH
                # start = time.time()
                # try:
                #     speech = gTTS(
                #         text=answer, 
                #         lang=speech_configs['tts']['lang'], 
                #         slow=speech_configs['tts']['slow']
                #     )
                    
                #     answerfile = '{}.mp3'.format(str(uuid.uuid4()))
                #     answerpath = os.path.join(speech_configs['save']['dir'], answerfile)
                #     speech.save(answerpath)
                #     logger.info('Text to speech done after {:.2f}s'.format(time.time() - start))
                    
                # except:
                #     logger.error("Fail to generate speech")
                #     play_sound_sync(speech_configs['sample']['retry'])
                #     error = True
                #     continue
                
                # # Playsound
                # logger.info('All jobs done after {:.2f}s'.format(time.time() - since))
                # play_sound_sync(answerpath)
                
                # # Delete temp file
                # os.remove(answerpath)
                
                # Logging
                logger.info('All done after {:.2f}s!'.format(time.time() - since))
                
                # Reset vars
                error = False
            
    except:
        logger.exception('{}: Interrupted!'.format(currentThread().getName()))
        
    finally:
        # Destroy CUDA context
        model.destroy()
        
        # Stop camera
        cam_stop = True
        face_track_thread.join()
        
        # System shut down
        play_sound_sync(speech_configs['sample']['goodbye'])
        logger.info('System shut down!')

if __name__ == "__main__":
    main()
