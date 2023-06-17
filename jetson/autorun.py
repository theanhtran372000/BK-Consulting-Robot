import time
import psutil
import subprocess
from loguru import logger

while True:
  try:
    start = time.time()
    
    # Start the program
    proc = subprocess.Popen(['bash', 'scripts/run.sh'])
    p = psutil.Process(proc.pid)
    logger.info('Program running with pid {}'.format(proc.pid))
    
    # Wait the process to end
    p.wait()
    logger.info('AUTO RESTART: Main process terminated after {:.2f}s!'.format(time.time() - start))
    
    # Restart program after minor sleep
    time.sleep(1)
    logger.info('AUTO RESTART: Restart the program automatically')
    
  except KeyboardInterrupt:
    
    # Kill process in case being interrupted by user
    p.terminate()
    print('AUTO RESTART: Terminate process due to user interrupt')
    break
  