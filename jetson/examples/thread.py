# Test thread

import random
import time
from threading import Thread, currentThread

sleep_time = 0.001

# numlist = []
cur_num = 0
stop = False

def append():
    # global numlist
    global cur_num
    global stop
    
    while not stop:
        num = random.randint(0, 100)
        cur_num = num
        # numlist.append(num)
        # print('Thread [{}]: Add {} to list!'.format(currentThread().getName(), num))
        print('Thread [{}]: Update to {}!'.format(currentThread().getName(), num))
        time.sleep(1)
        
    print('Thread [{}]: Stopped!'.format(currentThread().getName()))
        
bgthread = Thread(name='Background thread', target=append)
bgthread.start()

currentThread().setName('Main thread')

try:
    while True:
        
        print('Thread [{}]:'.format(currentThread().getName()), cur_num)
        time.sleep(1)
except:
    print('Thread [{}]: Interrupted!'.format(currentThread().getName()))

finally:
    stop = True
    bgthread.join()
    
print('Done!')
    
    