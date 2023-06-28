import time
import yaml
import psutil
import argparse
import subprocess
from loguru import logger

# Auto start loop
while True:
  try:
    start = time.time()
    
    # Start the program
    proc = subprocess.Popen(['bash', 'scripts/run.sh'])
    p = psutil.Process(proc.pid)
    logger.info('Program running with pid {}'.format(proc.pid))
    
    # Wait the process to end
    exit_code = p.wait()
    logger.info('AUTO RESTART: Main process terminated after {:.2f}s!'.format(time.time() - start))
    logger.info('AUTO RESTART: Exit code {}'.format(exit_code))
    
    # Break autorestart if meet user stop command
    if exit_code == 143: # SIGTERM
      logger.info('AUTO RESTART: Meet user stop command. Program stopped!')
      logger.info('============== STOP ==============')
      break
    
    # Else: Restart
    # Restart program after minor sleep
    time.sleep(1)
    logger.info('AUTO RESTART: Restart the program automatically')
    
  except KeyboardInterrupt:
    
    # Kill process in case being interrupted by user
    p.terminate()
    print('AUTO RESTART: Terminate process due to user interrupt')
    logger.info('============== STOP ==============')
    break
  