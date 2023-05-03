import numpy as np

def to_deg(rad):
    return rad / np.pi * 180

def to_rad(deg):
    return deg * np.pi / 180

def calculate_angle(cx, cy, w, h, ax, ay, grid=5):
    """Calculate delta in degree from bbox position
    
    Arguments:
        cx, cy: Box center
        w, h: Image shape
        ax, ay: Camera scope (in degree)
    
    Return: 
        Angle delta in degree (int)
        Direction: (Human)
            Right +     Left -
            Up +        Down -
    """
    
    center = (
        w // 2,
        h // 2
    )
    
    # X delta (always positive)
    x_delta = int(
        to_deg(
            np.arctan(
                np.abs(center[0] - cx) * np.tan(to_rad(ax / 2)) / center[0]
            )
        )
    )
    
    if cx > center[0]: # Left (-)
        x_delta = - x_delta
        
    # X delta (always positive)
    y_delta = int(
        to_deg(
            np.arctan(
                np.abs(center[1] - cy) * np.tan(to_rad(ay / 2)) / center[1]
            )
        )
    )
    
    if cy > center[1]: # Down (-)
        y_delta = - y_delta
        
    # Post process delta
    x_delta = grid * int(x_delta / float(grid))
    y_delta = grid * int(y_delta / float(grid))
        
    return x_delta, y_delta
