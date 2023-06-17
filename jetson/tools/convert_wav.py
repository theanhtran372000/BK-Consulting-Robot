import os
import time
from loguru import logger
from pydub import AudioSegment

_dir = 'assets/voices'

start = time.time()
for _file in os.listdir(_dir):
  answerpath = os.path.join(_dir, _file)
  audio = AudioSegment.from_mp3(answerpath)
  wavpath = answerpath.replace('mp3', 'wav')
  audio.export(wavpath, format='wav')
  logger.success('Convert done: {}'.format(wavpath))
  
logger.info('Done after {:.2f}s!'.format(time.time() - start))
  
