import json

# Send string with Serial
def send(ser, data, log=True):
    ser.write(bytes(data, 'UTF-8'))
    if log:
        print('[INFO] Send ', data)
    
def read(ser):
    data = []
    
    while ser.inWaiting() > 0:
        data.append(ser.readline().decode('utf-8').strip())
    
    return '\n'.join(data)
    
def send_angle(ser, h_delta, v_delta, reset=True, log=True):
    data = json.dumps(
        {
            "hDelta": int(h_delta),
            "vDelta": int(v_delta),
            "reset": reset
        }
    )
    
    # Send data to Arduino
    send(ser, data, log)
    
    # Read (empty buffer)
    response = read(ser)
    
    return response
    

