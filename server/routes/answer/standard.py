import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

import time
from loguru import logger
from flask import Blueprint, request

from utils.openai import get_chatgpt_answer
from utils.format import format_response

module = Blueprint('answer_standard', __name__)

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

# Get Answer from ChatGPT
@module.route('/', methods=['POST'])
def answer():
    start = time.time()
    
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
    
    # Get answer
    try:
        answer = get_chatgpt_answer(query)
    except:
        logger.error('Failed to get answer!')
        return format_response(
            success=False,
            message='Failed to get answer!',
            data=None
        ), 400
    
    
    logger.success('[ANSWER] Generate answer: "{}"'.format(answer))
    logger.success('[ANSWER] Done after {:.2f}s!'.format(time.time() - start))
    
    return format_response(
        success=True,
        message = 'Operation success!',
        data = {
            'answer': answer
        }
    ), 200
    
# Get Answer from ChatGPT
@module.route('/extract', methods=['POST'])
def extract():
    start = time.time()
    
    # Get params
    content = request.get_json()
    if 'data' in content:
        data = content['data']
        logger.info('[ANSWER] Recieve data: "{}"'.format(data))
    else:
        logger.error('Question not found!')
        return format_response(
            success=False,
            message='Question not found!',
            data=None
        ), 400
    
    # Get answer
    try:
        # Apply prompts
        with open(configs['prompts']['extract'], 'r') as f:
            prompt = f.read()
            
        result = get_chatgpt_answer(prompt.format(data))
        
        logger.success('[EXTRACT] Result: "{}"'.format(result))
        logger.success('[EXTRACT] Done after {:.2f}s!'.format(time.time() - start))
        
        return format_response(
            success=True,
            message = 'Operation success!',
            data = {
                'result': result
            }
        ), 200
    
    except:
        logger.exception('Fail to extract!')
        return format_response(
            success=False,
            message='Failed to extract!',
            data=None
        ), 400