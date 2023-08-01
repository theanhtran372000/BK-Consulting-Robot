import argparse
import subprocess
from loguru import logger

parser = argparse.ArgumentParser()
parser.add_argument('--device-name', required=True, type=str, help='Device name to restart')
args = parser.parse_args()

# Get list USB device
devices = subprocess.check_output('lsusb', shell=True).decode('utf-8')
devices = devices.split('\n')

for device in devices:
    if args.device_name in device:
        logger.info('Matched device: ' + device)
        parts = device.split(' ')
        bus_id = parts[1]
        dev_id = parts[3][:-1]
        
        # Restart device
        params = ['tools/usbreset', '/dev/bus/usb/{}/{}'.format(bus_id, dev_id)]
        logger.info('Run: ' + ' '.join(params))
        output = subprocess.check_output(params)
        print('Output: ', output.decode('utf-8'))
        logger.success('Restart successfully!')