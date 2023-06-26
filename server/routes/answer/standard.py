import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

import time
from loguru import logger
from flask import Blueprint, request

from utils.openai import get_chatgpt_answer
from utils.format import format_response

module_standard = Blueprint('answer_standard', __name__)
def standard_configure():
    pass


# Get Answer from ChatGPT
@module_standard.route('/', methods=['POST'])
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
            'error',
            'Question not found!',
            None
        )
    
    # Get answer
    try:
        answer = get_chatgpt_answer(query)
    except:
        logger.error('Failed to get answer!')
        return format_response(
            'error',
            'Failed to get answer!',
            None
        )
    
    
    logger.success('[ANSWER] Generate answer: "{}"'.format(answer))
    logger.success('[ANSWER] Done after {:.2f}s!'.format(time.time() - start))
    
    return format_response(
        'success',
        'Operation success!',
        {
            'answer': answer
        }
    )