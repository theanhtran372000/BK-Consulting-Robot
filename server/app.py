import os
import sys
sys.path.insert(0, os.path.abspath('stt'))


import time
import yaml
import uuid
import json
import queue
import argparse
from pathlib import Path


from flask import Flask, request, after_this_request, send_file, Response
from loguru import logger


import requests
import librosa
import openai
import sseclient
from requests.adapters import HTTPAdapter
from threading import Thread, currentThread


from gtts import gTTS
from infer import VietASR
from utils import format_sse
from utils import create_answer_generator
from utils import get_chatgpt_answer
from utils import prepare_streaming_request


# Helper fucntions
def get_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--config', type=str, default='configs.yml', help='Path to config file')
    
    return parser

def create_response(state, msg, result):
    return {
        'state': state,
        'message': msg,
        'result': result
    }

# Flask app
app = Flask(__name__)


@app.route("/hello")
def hello():
    return "Hello, World!"

# Speech recognition
@app.route('/stt', methods=['POST'])
def stt():
    start = time.time()
    
    # Get audio file
    _file = request.files['audio']
    if _file.filename == '':
        return create_response(
            'error',
            'File name is empty!',
            None
        )
    
    ext = _file.filename.split('.')[-1]
    if ext not in ['wav', 'mp3']:
        return create_response(
            'error',
            'File type {} not supported!'.format(ext),
            None
        )
        
    logger.info('Recieve file {}'.format(_file.filename))
    
    # Save file to local
    localpath = os.path.join(configs['app']['save_dir'], '{}.{}'.format(str(uuid.uuid4()), ext))
    _file.save(localpath)
    
    # Load file with librosa
    audio_signal, _ = librosa.load(localpath, sr=16000)
    
    # Forward through model
    try:
        transcript = vietasr.transcribe(audio_signal)
        logger.success('[SST] Transcript: ' + transcript)
        logger.success('[SST] Done after {:.2f}s!'.format(time.time() - start))
    except:
        logger.error('Transcribe error!')
        return create_response(
            'error',
            'Unknown transcribe error!',
            None
        )
    
    # Clean
    @after_this_request
    def remove_file(response):
        try:
            os.remove(localpath)
            logger.info('{} removed!'.format(localpath))
            
        except Exception as error:
            logger.error('Fail to remove {}'.format(localpath))
            logger.error('Error message: ' + str(error))
            
        return response
     
    return create_response(
        'success',
        'Operation success!',
        {
            'transcript': transcript
        }
    )
    

# Get Answer
@app.route('/answer', methods=['POST'])
def answer():
    start = time.time()
    
    # Get params
    content = request.form
    if 'question' in content:
        query = content['question']
        logger.info('[ANSWER] Recieve question: "{}"'.format(query))
    else:
        logger.error('Question not found!')
        return create_response(
            'error',
            'Question not found!',
            None
        )
    
    # Get answer
    try:
        answer = get_chatgpt_answer(query)
    except:
        logger.error('Failed to get answer!')
        return create_response(
            'error',
            'Failed to get answer!',
            None
        )
    
    
    logger.success('[ANSWER] Generate answer: "{}"'.format(answer))
    logger.success('[ANSWER] Done after {:.2f}s!'.format(time.time() - start))
    
    return create_response(
        'success',
        'Operation success!',
        {
            'answer': answer
        }
    )
    

@app.route('/stream_answer', methods=['POST'])
def stream_answer():
    
    # Get params
    content = request.get_json()
    if 'question' in content:
        query = content['question']
        logger.info('[ANSWER] Recieve question: "{}"'.format(query))
    else:
        logger.error('Question not found!')
        return create_response(
            'error',
            'Question not found!',
            None
        )
    
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


@app.route('/stream_answer_stable', methods=['POST'])
def stream_answer_stable():
    # Get params
    content = request.get_json()
    if 'question' in content:
        query = content['question']
        logger.info('[ANSWER] Recieve question: "{}"'.format(query))
    else:
        logger.error('Question not found!')
        return create_response(
            'error',
            'Question not found!',
            None
        )
        
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
    
    # Prepare answer queue
    word_queue = queue.Queue()
    retry_time = configs['answer']['retry']
    finish_word = configs['answer']['finish_word']
    timeout = configs['answer']['timeout']
    error_statement = configs['answer']['statement']['connection_error']
    
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
        while True:
            # Get words from queue
            data = word_queue.get()
            print(data, end='', flush=True)
            
            # Reformat and return
            data = data.replace('\n', configs['answer']['break_word'])
            data = data.replace('\r', '')
            yield format_sse(data)
            
            # Break if meet finish word
            if data == finish_word:
                print()
                logger.info('Meet finish word {}. Stop responding!'.format(finish_word))
                break
        
    return Response(stream(word_queue, finish_word), mimetype='text/event-stream')


@app.route('/custom_stream_answer', methods=['POST'])
def custom_stream_answer():
    # Get params
    content = request.get_json()
    if 'question' in content:
        query = content['question']
        logger.info('[ANSWER] Recieve question: "{}"'.format(query))
    else:
        logger.error('Question not found!')
        return create_response(
            'error',
            'Question not found!',
            None
        )
        
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


@app.route('/tts', methods=['POST'])
def tts():
    start = time.time()
    
    # Get params
    content = request.form
    if 'text' in content:
        text = content['text']
        logger.info('[TTS] Recieve text: "{}"'.format(text))
    else:
        logger.error('Text not found!')
        return create_response(
            'error',
            'Text not found!',
            None
        )
        
    # Convert to speech
    speech = gTTS(
        text=text, 
        lang=configs['tts']['language'], 
        slow=configs['tts']['slow']
    )
    
    # Save file
    localpath = os.path.join(
        configs['app']['save_dir'], 
        '{}.mp3'.format(uuid.uuid4())
    )
    speech.save(localpath)
    logger.success('[TTS] Speech file generate successfully!')
    logger.success('[TTS] Done after {:.2f}s!'.format(time.time() - start))
    
    # Clean
    @after_this_request
    def remove_file(response):
        try:
            os.remove(localpath)
            logger.info('{} removed!'.format(localpath))
            
        except Exception as error:
            logger.error('Fail to remove {}'.format(localpath))
            logger.error('Error message: ' + str(error))
            
        return response
    
    return send_file(localpath)
    

if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    
    # Read config
    with open(args.config, 'r') as f:
        configs = yaml.load(f, yaml.FullLoader)
    
    logger.info('Configs: ' + str(configs))  
    
    # Create dir
    logger.info('All temporary files saved at {}'.format(configs['app']['save_dir']))
    Path(configs['app']['save_dir']).mkdir(parents=True, exist_ok=True)
    
    # Init Open AI
    logger.info('Config OpenAI')  
    API_KEY = open(configs['answer']['openai_key_path'], 'r').read().strip()
    openai.api_key = API_KEY
    
    
    # Init STT model (VietASR)
    vietasr = VietASR(
        config_file=configs['stt']['config'],
        encoder_checkpoint=configs['stt']['encoder_checkpoint'],
        decoder_checkpoint=configs['stt']['decoder_checkpoint'],
        lm_path=configs['stt']['lm_path'],
        beam_width=configs['stt']['beam_width'],
        device=configs['stt']['device']
    )
    
    logger.info('Server is listening at {}!'.format(configs['app']['port']))
    app.run(host=configs['app']['host'], port=configs['app']['port'], threaded=configs['app']['multithread'])