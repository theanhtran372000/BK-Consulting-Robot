import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

import json
import time
import queue
import pprint
import requests
import sseclient
from PIL import Image
from loguru import logger
from threading import Thread
from requests.adapters import HTTPAdapter
from flask import Blueprint, Response, request

from utils.format import format_response, format_sse
from utils.openai import prepare_streaming_request, create_answer_generator
from utils.base64 import image_to_base64, base64_to_image

module = Blueprint('answer_stream', __name__)

# Module config

# Configs
API_KEY = ''
configs = None
database = None


# Stream configure function
def configure(_API_KEY, _configs, _database):
    global API_KEY
    global configs
    global database
    
    API_KEY = _API_KEY
    configs = _configs
    database = _database


### === API === ###

# Unstable stream: 1 trial
@module.route('/unstable', methods=['POST'])
def stream_answer_unstable():
    
    # Get params
    content = request.get_json()
    if 'question' in content:
        query = content['question']
        logger.info('[ANSWER] Recieve question: "{}"'.format(query))
    else:
        logger.error('Question not found!')
        return format_response(
            success=False,
            message='Question not found!',
            data=None
        ), 400
    
    try:
        # Streaming result from ChatGPT
        logger.info('[ANSWER] Streaming answer:')
        url, header, body = prepare_streaming_request(
            query, 
            API_KEY, 
            model_name=configs['answer']['model_name'],
            role=configs['answer']['role'],
            temperature=configs['answer']['temperature'],
            max_tokens=configs['answer']['max_tokens'],
        )
        
        response = requests.post(
            url,
            headers=header,
            json=body,
            stream=True
        )
    
        generator = create_answer_generator(
            response,
            finish_word=configs['answer']['finish_word']
        )

        def stream():
            print()
            for data in generator:
                print(data, end='', flush=True)
                data = data.replace('\n', configs['answer']['break_word'])
                data = data.replace('\r', configs['answer']['break_word'])
                yield format_sse(data)
            print()
            
        return Response(stream(), mimetype='text/event-stream')
    except:
        logger.exception('Connection error!')
        
        def except_stream():
            sent = 'Kết nối không ổn định. Vui lòng thử lại sau.[DONE]'
            words = sent.split(' ')
            
            for word in words:
                data = word + ' '
                print(data, end='', flush=True)
                yield format_sse(data)
                
        return Response(except_stream(), mimetype='text/event-stream')
    
    
# Stable stream: multiple trials
@module.route('/stable', methods=['POST'])
def stream_answer_stable():
    start = time.time()
    
    # Get face image
    if 'face' not in request.files:
        return format_response(
            success=False,
            message='Face not found!',
            data=None
        ), 400
    face = Image.open(request.files['face'])
    
    # Convert face to base64
    face_b64 = image_to_base64(face)
    
    # Get params
    content = request.form
    if 'question' in content and 'system_id' in content:
        query = content['question']
        system_id = content['system_id']
        logger.info('Recieve question from system "{}": "{}"'.format(system_id, query))
    else:
        logger.error('Question or System ID not found!')
        return format_response(
            success=False,
            message='Question/System ID not found!',
            data=None
        ), 400          
    
    # Streaming result from ChatGPT
    logger.info('Streaming answer:')
    url, header, body = prepare_streaming_request(
        query, 
        API_KEY, 
        model_name=configs['answer']['model_name'],
        role=configs['answer']['role'],
        temperature=configs['answer']['temperature'],
        max_tokens=configs['answer']['max_tokens'],
    )
    
    # Prepare answer queue
    word_queue = queue.Queue()
    retry_time = configs['answer']['retry']
    finish_word = configs['answer']['finish_word']
    timeout = configs['answer']['timeout']
    error_statement = configs['answer']['statement']['connection_error']
    
    # Recieve thread
    def chatgpt_reciever(
        url, header, body, 
        word_queue, retry_time, timeout, 
        finish_word, error_statement
    ):
        # Try to establish connection
        for i in range(retry_time):
            try:
                logger.info('Try to connect to ChatGPT. Trial {}...'.format(i + 1))
                
                # Sending request
                sess = requests.Session()
                sess.mount(
                    'https://api.openai.com.com', 
                    HTTPAdapter(max_retries=0)
                )
                response = sess.post(
                    url,
                    headers=header,
                    json=body,
                    stream=True,
                    timeout=timeout
                )
                
                # Establish SSE connection
                client = sseclient.SSEClient(response)
                has_sent = False
                for event in client.events():
                    if event.data != finish_word:
                        data = json.loads(event.data)
                        if 'content' in data['choices'][0]['delta']:
                            word = data['choices'][0]['delta']['content']
                            word_queue.put(word)
                            has_sent = True
                    else:
                        word_queue.put(finish_word)
                        has_sent = True
                
                print()
                if has_sent:    
                    logger.success('Success in the {}th trial!'.format(i + 1))        
                    break
                else:
                    logger.error('Recieve empty message!')
                    raise Exception("Recieve empty message!")
            
            except:
                logger.exception('ChatGPT connection error')
                # Retry
                if i + 1 < retry_time:
                    logger.info('Try to reconnect...')
                else:
                    logger.info('Reconnection trials exceeded. Failed after {} trial!'.format(retry_time))
                    
                    # If exceed trial times, return error
                    sent = error_statement
                    words = sent.split(' ')
                    
                    for word in words:
                        data = word + ' '
                        word_queue.put(data)
            
            finally:
                if 'client' in locals():
                    client.close()
    
    recieve_thread = Thread(
        name='ChatGPT recieve thread',
        target=chatgpt_reciever,
        args=(
            url, header, body,
            word_queue,
            retry_time,
            timeout,
            finish_word,
            error_statement
        )
    )
    recieve_thread.start()
    
    # Create stream to send answer
    def stream(word_queue, finish_word):
        result = ''
        while True:
            # Get words from queue
            data = word_queue.get()
            result += data
            print(data, end='', flush=True)
            
            # Reformat and return
            data = data.replace('\n', configs['answer']['break_word'])
            data = data.replace('\r', '')
            yield format_sse(data)
            
            # Break if meet finish word
            if data == finish_word:
                print()
                logger.info('Meet finish word {}. Stop responding!'.format(finish_word))
                
                # Save data to mongo
                try:
                    # Get collection
                    history = database[configs['mongo']['cols']['history']]
                    
                    # Insert new sample
                    document = {
                        "system_id": system_id,
                        "question": query,
                        "answer": result,
                        "face": face_b64,
                        "start": start,
                        "end": time.time()
                    }
                    history.insert_one(document)
                    
                    logger.success('Saved conversation data to DB')
                except:
                    logger.exception('Fail to insert conversation data to DB')
                
                break
        
    return Response(stream(word_queue, finish_word), mimetype='text/event-stream')


# Custom HUST stable stream answer
@module.route('/stable/hust', methods=['POST'])
def custom_stream_answer():
    # Get params
    content = request.get_json()
    if 'question' in content:
        query = content['question']
        logger.info('[ANSWER] Recieve question: "{}"'.format(query))
    else:
        logger.error('Question not found!')
        return format_response(
            success=False,
            message='Question not found!',
            data=None
        ), 400
        
    # Streaming result from ChatGPT
    logger.info('[ANSWER] Streaming answer:')
    
    # Prepare request info
    url = 'http://{}:{}/stream_questions'.format(
        configs['answer']['server']['address'],
        configs['answer']['server']['port']
    )
    
    body = {
        'text': query
    }
    
    # Prepare answer queue
    word_queue = queue.Queue()
    retry_time = configs['answer']['retry']
    finish_word = configs['answer']['finish_word']
    timeout = configs['answer']['timeout']
    error_statement = configs['answer']['statement']['connection_error']
    
    def custom_reciever(
        url, body, 
        word_queue, retry_time, timeout, 
        finish_word, error_statement
    ):
        # Try to establish connection
        for i in range(retry_time):
            try:
                logger.info('Try to connect to server. Trial {}...'.format(i + 1))
                
                # Sending request
                response = requests.post(
                    url,
                    json=body,
                    stream=True,
                    timeout=timeout
                )
                
                if response.status_code != 200:
                    raise requests.exceptions.ConnectionError('Connection error!')
                
                # Establish SSE connection
                client = sseclient.SSEClient(response)
                has_sent = False
                for event in client.events():
                    if event.data != finish_word:
                        word = event.data
                        word_queue.put(word)
                        has_sent = True
                    else:
                        word_queue.put(finish_word)
                        has_sent = True

                print()
                if has_sent:    
                    logger.success('Success in the {}th trial!'.format(i + 1))        
                    break
                else:
                    logger.error('Recieve empty message!')
                    raise Exception("Recieve empty message!")
            
            except:
                logger.exception('ChatGPT connection error')
                # Retry
                if i + 1 < retry_time:
                    logger.info('Try to reconnect...')
                else:
                    logger.info('Reconnection trials exceeded. Failed after {} trial!'.format(retry_time))
                    
                    # If exceed trial times, return error
                    sent = error_statement
                    words = sent.split(' ')
                    
                    for word in words:
                        data = word + ' '
                        word_queue.put(data)
            
            finally:
                if 'client' in locals():
                    client.close()
    
    recieve_thread = Thread(
        name='ChatGPT recieve thread',
        target=custom_reciever,
        args=(
            url, body,
            word_queue,
            retry_time,
            timeout,
            finish_word,
            error_statement
        )
    )
    recieve_thread.start()
    
    # Create stream to send answer
    def stream(word_queue, finish_word):
        while True:
            # Get words from queue
            data = word_queue.get()
            print(data, end='', flush=True)
            
            # Reformat and return
            # data = data.replace('\n', configs['answer']['break_word'])
            # data = data.replace('\r', '')
            yield format_sse(data)
            
            # Break if meet finish word
            if data == finish_word:
                print()
                logger.info('Meet finish word {}. Stop responding!'.format(finish_word))
                break
        
    return Response(stream(word_queue, finish_word), mimetype='text/event-stream')