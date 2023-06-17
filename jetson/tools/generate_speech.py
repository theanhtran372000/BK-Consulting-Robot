import os
import yaml
import pprint
import argparse
import requests
from pathlib import Path
from loguru import logger
from gtts import gTTS
from pydub import AudioSegment

def get_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--input-text', type=str, required=True, help='Text to be converted into speech')
    parser.add_argument('--output-path', type=str, required=True, help='Path to save sound file')
    parser.add_argument('--speech-config', type=str, default='configs/speechprocess.yml', help='Path to speech processing configs file')
    
    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()
    
    with open(args.speech_config, 'r') as f:
        configs = yaml.load(f, yaml.FullLoader)
    logger.info('Configs: ' + pprint.pformat(configs))
    
    # endpoint = 'http://{}:{}/tts'.format(
    #     configs['server']['address'],
    #     configs['server']['port']
    # )
    
    # logger.info('Endpoint: ' + endpoint)
    
    # form = {
    #     'text': args.input_text
    # }
    # logger.info('Input text: ' + args.input_text)
    
    # response = requests.post(endpoint, data=form)
    
    speech = gTTS(
        text=args.input_text, 
        lang=configs['tts']['lang'], 
        slow=configs['tts']['slow']
    )
    
    # Make dir if needed
    Path(os.path.sep.join(args.output_path.split(os.path.sep)[:-1])).mkdir(parents=True, exist_ok=True)
    
    if args.output_path[-3:] == 'mp3':
        speech.save(args.output_path)

    else:
        # Save mp3 file
        answerpath = args.output_path[:-3] + 'mp3'
        speech.save(answerpath)
        
        # Convert to wav file
        audio = AudioSegment.from_mp3(answerpath)
        audio.export(args.output_path, format='wav')
        os.remove(answerpath)
        
    logger.info('Voice file saved to: ' + args.output_path)
    

if __name__ == '__main__':
    main()

