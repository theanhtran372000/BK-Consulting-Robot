# Libs
import yaml
import openai
import pprint
import argparse
from pathlib import Path
from loguru import logger
from threading import Thread

# Flask
from flask import Flask, request, make_response
from flask_cors import CORS

# Submodules
from routes import answer
from routes import user
from routes import system

# Callbacks
from callbacks import face_callback_generator, stats_callback_generator

# Utils
from utils.mongo import get_mongo_client
from utils.rabbitmq import consumer_thread


# CLI Parser
def get_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--config', type=str, default='configs.yml', help='Path to config file')
    
    return parser


# Flask app
app = Flask(__name__)
cors = CORS(app) # Enable CORS
app.config['CORS_HEADERS'] = 'Content-Type'

# Preflight requests
@app.before_request
def before_request():
    
    # If the request method is OPTIONS (a preflight request)
    if request.method == 'OPTIONS':
        
        # Create a 200 response and add the necessary headers
        response = make_response('OK')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        
        # Return the response
        return response

# Main function
def main():
    
    ### === CLI === ###
    parser = get_parser()
    args = parser.parse_args()
    
    ### === Preparation === ###
    # Read config
    with open(args.config, 'r') as f:
        configs = yaml.load(f, yaml.FullLoader)
    
    logger.info('Configs: {}'.format(
        pprint.pformat(configs)
    ))  
    
    # Create dir
    logger.info('All temporary files saved at {}'.format(
        configs['app']['save_dir']
    ))
    Path(configs['app']['save_dir']).mkdir(parents=True, exist_ok=True)
    
    ### === Open AI === ###
    logger.info('Config OpenAI')  
    API_KEY = open(configs['answer']['openai_key_path'], 'r').read().strip()
    openai.api_key = API_KEY
    
    ### === MongoDB === ###
    # Connect to mongodb
    logger.info('Connect to MongoDB at {}:{}'.format(
        configs['mongo']['host'],
        configs['mongo']['port']
    ))
    mongo = get_mongo_client(
        configs['mongo']['host'],
        configs['mongo']['port']
    )
    
    # Create or get db object
    database = mongo[configs['mongo']['name']]
    
    ### === Secrete key === ###
    with open(configs['token']['secrete_key_path'], 'rb') as f:
        SECRETE_KEY = f.read()
    
    ### === APIs === ###
    logger.info('Setup APIs')
    # Register submodule
    # Answer submodule
    answer.configure(API_KEY, configs, database)
    app.register_blueprint(answer.module, url_prefix='/answer')
    
    # User submodule
    user.configure(SECRETE_KEY, configs, database)
    app.register_blueprint(user.module, url_prefix='/user')
    
    # System submodule
    system.configure(SECRETE_KEY, configs, database)
    app.register_blueprint(system.module, url_prefix='/system')
    
    ### === RabbitMQ === ###
    # Start consuming message in background
    log_state = configs['rabbitmq']['log_state']
    
    # Face track consumer
    face_thread = Thread(
        name='Face Track Consume Thread',
        target=consumer_thread,
        args=(
            configs,
            configs['rabbitmq']['queues']['log_face_track'],
            face_callback_generator(configs, database, log_state)
        )
    )
    face_thread.start()
    logger.info('Running consumer for queue {} in background thread...'.format(configs['rabbitmq']['queues']['log_face_track']))
    
    # Stats log consumer
    stats_thread = Thread(
        name='Stats Consume Thread',
        target=consumer_thread,
        args=(
            configs,
            configs['rabbitmq']['queues']['log_stats'],
            stats_callback_generator(configs, database, log_state)
        )
    )
    stats_thread.start()
    logger.info('Running consumer for queue {} in background thread...'.format(configs['rabbitmq']['queues']['log_stats']))

    ### === Flask Server === ###
    # Run server
    logger.info('Server is listening at {}!'.format(configs['app']['port']))
    app.run(host=configs['app']['host'], port=configs['app']['port'], threaded=configs['app']['multithread'])


if __name__ == '__main__':
    main()