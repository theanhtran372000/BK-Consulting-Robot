#!/usr/bin/python3
import time
import json
import serial

ser = serial.Serial(port='/dev/ttyACM0', baudrate=115200)
time.sleep(2)

try:
    while True:
        hDelta = -10
        vDelta = 10
        reset = False
        data = json.dumps(
            {
                "hDelta": int(hDelta),
                "vDelta": int(vDelta),
                "reset": reset
            }
        )
        
        ser.write(bytes(data, 'UTF-8'))
        print('Send: ', data)
        time.sleep(0.03)
        
        # Read data if needed
        while ser.inWaiting() > 0:
            data = ser.readline()
            # print('Receive data:', data.decode('utf-8').strip())
            
except KeyboardInterrupt:
    print("Exiting Program")

except Exception as exception_error:
    print("Error occurred. Exiting Program")
    print("Error: " + str(exception_error))
    
finally:
    ser.close()