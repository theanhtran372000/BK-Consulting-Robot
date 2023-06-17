from loguru import logger
import time

start = time.time()

while True:
  logger.info('Main thread')
  if time.time() - start > 5:
    exit(101)
    
  time.sleep(1)