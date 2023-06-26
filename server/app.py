# Libs
import yaml
import openai
import argparse
from pathlib import Path
from loguru import logger

# Flask
from flask import Flask
from flask_cors import CORS

# Submodules
from routes import answer


# CLI Parser
def get_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--config', type=str, default='configs.yml', help='Path to config file')
    
    return parser


# Flask app
app = Flask(__name__)
cors = CORS(app) # Enable CORS
app.config['CORS_HEADERS'] = 'Content-Type'


# Main function
def main():
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
    
    # Register submodule
    answer.configure(API_KEY, configs)
    app.register_blueprint(answer.module_answer, url_prefix='/answer')
    
    # Run server
    logger.info('Server is listening at {}!'.format(configs['app']['port']))
    app.run(host=configs['app']['host'], port=configs['app']['port'], threaded=configs['app']['multithread'])


if __name__ == '__main__':
    main()