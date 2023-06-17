import subprocess
import psutil
import time

while True:
  proc = subprocess.Popen(['python3', 'main.py'])
  print('Main process running with id {}'.format(proc.pid))
  
  try:
    p = psutil.Process(proc.pid)
    exit_code = p.wait()
    
    print('Main process exit with code {}!'.format(exit_code))
    time.sleep(1)
    
  except KeyboardInterrupt:
    p.terminate()
    print('Terminate process')
    break
  