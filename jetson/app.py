import os
import gc
import re
import time
import yaml
import uuid
import queue
import signal
import psutil
import serial
import pprint
import argparse
import requests
import threading
from pathlib import Path
from loguru import logger
from datetime import datetime

import cv2
import openai
import sseclient
import numpy as np
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from threading import Thread, currentThread

from models.yunet import TrtYuNet

from utils.draw import draw_caption, draw_circle, draw_rectangle
from utils.serial import send_angle
from utils.angle import calculate_angle
from utils.sound import play_sound_async, play_sound_sync
from utils.answer import get_chatgpt_answer, apply_prompt
from utils.distance import in_active_range


### === Variables === ###
# Bool Vars
# cam_stop = False
# error = False
# appear = False

# Event
cam_stop_event = threading.Event()
error_event = threading.Event()
appear_event = threading.Event()

# Global vars
current_face = None

# Lock
current_face_lock = threading.Lock()

# Queue
word_queue = queue.Queue()
answer_queue = queue.Queue()


### === Helper functions === #

# CLI params
def get_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--face-track-config", type=str, default='configs/facetrack.yml', help="Path to face tracking config file")
    parser.add_argument("--speech-process-config", type=str, default='configs/speechprocess.yml', help='Path to speech processing config file')
    parser.add_argument('--log-config', type=str, default='configs/log.yml', help='Path to log config file')
    
    return parser


# Camera thread: Update camera position function
def track_face(cap, w, h, w_scale, h_scale, model, ser, cam_configs):
    
    # Global vars
    global error_event
    global appear_event
    global cam_stop_event
    global current_face
    global current_face_lock
    
    log_state = cam_configs['log']['state']
    elapsed_list = []
    since = time.perf_counter()
    detect_face_since = time.time()
    try:
        while not cam_stop_event.is_set():
            # Read and horizontal flip image (camera vision is opposite to human vision)
            ret, frame = cap.read()
            if not ret:
                logger.error("{}: VideoCapture read failed!".format(currentThread().getName()))
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
                # Sort by box area  
                sorted(bboxes, key=lambda box: (box[2] - box[0]) * (box[3] - box[1]), reverse=True)
                
                # Get biggest face
                face = bboxes[0]
                
                # TODO: Keep or not
                # Drop if face is two small
                if (face[2] - face[0]) * (face[3] - face[1]) < cam_configs['infer']['face_size_thresh']:
                    continue
                
                # Qualified face -> record face and adjust camera
                detect_face_since = time.time()
                
                # Save face to global var
                with current_face_lock:
                    current_face = frame[face[1] : face[3], face[0] : face[2]].copy()
                
                # Calculate rotation angle
                x_delta, y_delta = calculate_angle(
                    (face[0] + face[2]) // 2, (face[1] + face[3]) // 2,
                    w, h,
                    cam_configs['cam']['scope']['x'], cam_configs['cam']['scope']['y'],
                    cam_configs['cam']['grid']
                )
                
                # Send angle to adjust camera
                send_angle(ser, x_delta, y_delta, reset=False, log=log_state)
                    
            else:
                # After a while not detect faces
                if time.time() - detect_face_since >= cam_configs['cam']['reset_every']:
                    if log_state:
                        logger.info('{}: Reset camera position after {}s not detecting faces!'.format(
                            currentThread().getName(),
                            cam_configs['cam']['reset_every']
                        ))
                    
                    # Reset camera
                    send_angle(ser, 0, 0, reset=True, log=log_state)   # Reset camera position
                    
                    # Reset system state
                    with current_face_lock:
                        current_face = None
                        
                    # error = False
                    # appear = False
                    error_event.clear()
                    appear_event.clear()


            # Calc fps.
            inference_time = (time.perf_counter() - start) * 1000
            elapsed_list.append(inference_time)
            
            if (time.perf_counter() - since) > cam_configs['log']['every']:
                # elapsed_list.pop(0)
                avg_elapsed_ms = np.mean(elapsed_list)
                avg_text = "{}: Average {:.2f}ms {:.1f}FPS".format(
                    currentThread().getName(), 
                    avg_elapsed_ms, 
                    1000 / avg_elapsed_ms
                )
                
                # log
                logger.info(avg_text)
                
                # reset
                since = time.perf_counter()
                elapsed_list = []
        
        logger.info('{}: Stop event catched. Current thread stopped!'.format(currentThread().getName()))
    
    finally:
        cap.release()


# Speak thread: Speak generated speech
def speak_answer(speech_configs):
    global answer_queue
    
    start = time.time()
    while True:
        # Get an speech from queue
        sentence, answerpath = answer_queue.get()
        if sentence == '[DONE]':
            logger.info('{}: Done speaking after {:.2f}s!'.format(currentThread().getName(), time.time() - start))
            break
        
        logger.info('{}: Speak: {}'.format(currentThread().getName(), sentence))
        
        # Speak
        play_sound_sync(
            answerpath,
            speech_configs['tts']['speed'],
            speech_configs['tts']['tone']
        )
        
        # Remove that speech
        os.remove(answerpath)

# Process speech thread: Generate speech with respect to recieved answer
def generate_speech(speech_configs):
    
    # global vars
    global word_queue
    global answer_queue
    global error_event
    
    # Params
    final_word = speech_configs['answer']['finish_word']
    break_word = speech_configs['answer']['break_word']
    split_char = speech_configs['tts']['split_char']
    num_sent = speech_configs['tts']['num_sent']
    lang = speech_configs['tts']['lang']
    slow = speech_configs['tts']['slow']
    speed = speech_configs['tts']['speed']
    tone = speech_configs['tts']['tone']
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
            target=speak_answer,
            args=(speech_configs,)
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
                    logger.error('{}: Speak: Get empty sentence'.format(currentThread().getName()))
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
                
                #  Convert audio file to wav
                audio = AudioSegment.from_mp3(answerpath)
                wavpath = answerpath.replace('mp3', 'wav')
                audio.export(wavpath, format='wav')
                os.remove(answerpath)
                 
                total_time += time.time() - start
                
                # # Speak
                # play_sound_sync(answerpath)
                # Add to speech queue
                answer_queue.put((sentence, wavpath))
                
                # Postprocess
                # os.remove(answerpath) # Delete temp file
                sent_list = [] # Reset
                    
            # Stop this thread if done flag is raise
            if done:
                break
        
        logger.info('{}: Text to speech done after {:.2f}s'.format(currentThread().getName(), total_time))
        
        # Wait speak thread to stop
        answer_queue.put(('[DONE]', ''))
        speak_thread.join()
        
    except:
        logger.exception("{}: Fail to generate speech".format(currentThread().getName()))
        play_sound_sync(sound_path, speed, tone)
        # error = True
        error_event.set()

# Log thread: Log system stats
def log_stats(log_configs, sleep_time=0.2):
    
    # Prepare for logs
    log_dir = log_configs['stats']['dir']
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = datetime.now().strftime("%Y%m%d-%H%M%S") + '.txt'
    log_path = os.path.join(log_dir, log_file)
    log_every = log_configs['stats']['every']
    mem_threshold = log_configs['stats']['mem_threshold']
    exit_code = log_configs['stats']['exit_code']
    
    start = time.time()
    while True:
        if time.time() - start > log_every:
            
            # Read system stats
            cpu_percent = psutil.cpu_percent(None)
            ram_percent = psutil.virtual_memory()[2]
            ram_total = psutil.virtual_memory()[0] / (2 ** 30) # Convert to GB
            ram_used = ram_total * ram_percent / 100
            
            # Write to file
            with open(log_path, 'a') as f:
                content = 'CPU: {:.1f}% - RAM: {:.1f}% ~ {:.2f}/{:.2f}GB'.format(
                    cpu_percent,
                    ram_percent,
                    ram_used, ram_total
                )
                
                f.write(
                    '[{}] {}\n'.format(
                        datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
                        content
                    )
                )
                
                logger.info('{}: {}'.format(currentThread().getName(), content))
                
                if ram_percent >= mem_threshold:
                    logger.info('{}: Ram used exceed memory threshold of {}%'.format(currentThread().getName(), mem_threshold))
                    logger.info('{}: System shut down!'.format(currentThread().getName()))
                    os.kill(os.getpid(), signal.SIGKILL) 
            
            # Minor sleep
            time.sleep(sleep_time)
            
            # Reset
            start = time.time()
            
            # # Collect gabbage
            # n_collected = gc.collect()
            # logger.info('{}: Gabbage collector has cleaned {} unused variables'.format(
            #     currentThread().getName(),
            #     n_collected
            # ))
            
        else:
            time.sleep(sleep_time)

### === Program loop === ###
def main():
    
    # Running main thread
    currentThread().setName('Main Thread')
    
    ### === CONFIG SECTION === ###
    # Global vars
    # Event
    global error_event
    global appear_event
    global cam_stop_event
    
    global current_face
    global current_face_lock
    
    global word_queue
    
    # Parse CLI args    
    parser = get_parser()
    args = parser.parse_args()
    
    # Load face tracking configs
    with open(args.face_track_config, 'r') as f:
        cam_configs = yaml.load(f, yaml.FullLoader)
    logger.info('{}: Face tracking configs: \n'.format(currentThread().getName()) + pprint.pformat(cam_configs))
    
    with open(args.speech_process_config, 'r') as f:
        speech_configs = yaml.load(f, yaml.FullLoader)
    logger.info('{}: Speech processing configs: \n'.format(currentThread().getName()) + pprint.pformat(speech_configs))
    
    with open(args.log_config, 'r') as f:
        log_configs = yaml.load(f, yaml.FullLoader)
    logger.info('{}: Log configs: \n'.format(currentThread().getName()) + pprint.pformat(log_configs))
    
    # Config openai
    openai.api_key = open(speech_configs['answer']['key'], 'r').read().strip()
    
    # Create dir
    Path(speech_configs['save']['dir']).mkdir(parents=True, exist_ok=True)
    
    ### === CAMERA SECTION === ###
    # 1. Init on main thread
    # Open camera
    logger.info('{}: Open camera'.format(currentThread().getName()))
    cap = cv2.VideoCapture(cam_configs['cam']['device'])
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    logger.info("{}: Camera info: h = {} \t w = {} \t fps = {} ".format(currentThread().getName(), h, w, fps))
    
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
    logger.info('{}: Load model: {}'.format(currentThread().getName(), model_name))

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
    logger.info('{}: Start face track thread'.format(currentThread().getName()))
    
    log_stats_thread = Thread(
        name='Log Stats Thread',
        target=log_stats,
        args=(
            log_configs,
            speech_configs['device']['sleep_time']
        )
    )
    log_stats_thread.start()
    logger.info('{}: Start log stats thread'.format(currentThread().getName()))
    
    ### === SPEECH SECTION === ###
    # Params
    speed = speech_configs['tts']['speed']
    tone = speech_configs['tts']['tone']
    
    try:
        # Create speech recognizer
        logger.info('{}: Setup listener'.format(currentThread().getName()))
        listener = sr.Recognizer()
        listener.energy_threshold = speech_configs['listen']['energy_threshold']
        listener.pause_threshold = speech_configs['listen']['pause_threshold']
        listener.dynamic_energy_threshold = speech_configs['listen']['auto_adjust']
        logger.info('{}: Turn {} auto adjustment for energy threshold'.format(currentThread().getName(), 'on' if speech_configs['listen']['auto_adjust'] else 'off'))
        logger.info('{}: Initial energy threshold value: {}'.format(currentThread().getName(), listener.energy_threshold))
        
        # Open microphone
        with sr.Microphone(device_index=speech_configs['device']['mic_index']) as mic:
            
            logger.info('{}: System is running'.format(currentThread().getName()))
            
            # Loop
            while True:
                
                # If face is none (distance = 9999) or face out of range
                with current_face_lock:
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
                logger.info('{}: Detect user in active range. Distance {}m.'.format(currentThread().getName(), distance))
                
                
                # LISTEN
                # Adjust energy threshold for background noise
                if speech_configs['listen']['auto_adjust']:
                    listener.adjust_for_ambient_noise(mic, duration=0.5)
                    logger.info('{}: Adjust energy threshold to {}'.format(currentThread().getName(), int(listener.energy_threshold)))
                
                # Greet if start or not error in previous time
                if not error_event.is_set():
                    logger.info('{}: Greet'.format(currentThread().getName()))
                    
                    if not appear_event.is_set():
                        play_sound_sync(speech_configs['sample']['greet'], speed, tone)
                        # appear = True
                        appear_event.set()
                    else:
                        play_sound_sync(speech_configs['sample']['continue'], speed, tone)
                
                
                # Wait for speech
                logger.info('{}: Listening'.format(currentThread().getName()))
                
                try:
                    voice = listener.listen(
                        mic,
                        timeout=speech_configs['listen']['timeout']
                    )
                
                # Timeout
                except sr.WaitTimeoutError:
                    logger.exception('{}: Listen timeout!'.format(currentThread().getName()))
                    play_sound_sync(speech_configs['sample']['listen_none'], speed, tone)
                    error_event.set()
                    continue
                    
                since = time.time()
                logger.info("{}: I'm hearing something...".format(currentThread().getName()))
                    
                
                # SPEECH TO TEXT
                # C1: Use Google API
                try:
                    start = time.time()
                    transcript = listener.recognize_google(voice, language=speech_configs['stt']['lang'])
                    logger.info('{}: Speech to text done after {:.2f}s'.format(currentThread().getName(), time.time() - start))
                    logger.success('{}: Transcript: {}'.format(currentThread().getName(), transcript))
                    
                    if speech_configs['statement']['exit'].lower() in transcript.lower():
                        logger.info('{}: Hear exit state: {}'.format(currentThread().getName(), speech_configs['statement']['exit']))
                        break
                    
                except sr.UnknownValueError:
                    logger.exception("{}: Can't hear what you're saying!".format(currentThread().getName()))
                    play_sound_sync(speech_configs['sample']['repeat'], speed, tone)
                    # error = True
                    error_event.set()
                    continue
                except:
                    logger.exception("{}: Some errors occured while doing STT".format(currentThread().getName()))
                    play_sound_sync(speech_configs['sample']['retry'], speed, tone)
                    # error = True
                    error_event.set()
                    continue
                
                
                # ANSWER
                start = time.time()
                
                # Streaming
                try:
                    # Send request to server
                    # question = apply_prompt(transcript, speech_configs['answer']['prompt']['default'])
                    
                    # Announce
                    play_sound_async(speech_configs['sample']['think'], speed, tone)
                    
                    # Get answer
                    # TODO: Attach current face in request
                    question = transcript
                    response = requests.post(
                        'http://{}:{}/{}'.format(
                            speech_configs['server']['address'],
                            speech_configs['server']['port'],
                            speech_configs['server']['api']
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
                            logger.info('{}: Establish connection done after {:.2f}s'.format(currentThread().getName(), time.time() - start))
                            has_recieved = True
                        word = event.data
                        word_queue.put(word)                           
                        if word == speech_configs['answer']['finish_word']:
                            logger.info('{}: Generate answer done after {:.2f}s'.format(currentThread().getName(), time.time() - start))                         
                    
                    # Wait for tts to stop
                    tts_thread.join()
                except KeyboardInterrupt:
                    logger.error('{}: Getting answer is interrupted by user!'.format(currentThread().getName()))
                except:
                    logger.exception("{}: Can't get answer. Try again.".format(currentThread().getName()))
                    play_sound_sync(speech_configs['sample']['retry'], speed, tone)
                    # error = True
                    error_event.set()
                    continue
                
                                
                # Logging
                logger.info('{}: All done after {:.2f}s!'.format(currentThread().getName(), time.time() - since))
                
                # Reset vars
                # error = False
                error_event.clear()
                
                # Loop sleep
                logger.info('{}: Minor sleep of {:.2f}s'.format(currentThread().getName(), speech_configs['device']['sleep_time']))
                time.sleep(speech_configs['device']['sleep_time'])
            
    except:
        logger.exception('{}: Interrupted!'.format(currentThread().getName()))
        
    finally:
        # Destroy CUDA context
        model.destroy()
        
        # Stop camera
        cam_stop_event.set()
        face_track_thread.join()
        
        # System shut down
        play_sound_sync(speech_configs['sample']['goodbye'], speed, tone)
        logger.info('{}: System shut down!'.format(currentThread().getName()))
        
        # Kill process for sure
        os.kill(os.getpid(), signal.SIGKILL) 

if __name__ == "__main__":
    main()
