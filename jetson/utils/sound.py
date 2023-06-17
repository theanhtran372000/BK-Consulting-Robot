import os
import threading
import soundfile as sf
import pyrubberband as pyrb
from playsound import playsound

def play_sound_async(path, speed, tone):
    """Play sound in background thread

    Args:
        path (str): Path to sound file
    """
    threading.Thread(target=custom_play, args=(path, speed, tone)).start()
    
def play_sound_sync(path, speed, tone):
    """Play sound in background thread

    Args:
        path (str): Path to sound file
    """
    custom_play(path, speed, tone)
    
def custom_play(path, speed, tone):
    """Play wav file with different speed and tone.
    Input file must be in wav format
    
    Keyword arguments:
        speed: Play speed
        tone: Play tone
    """
    
    # Change origin speed and tone
    y, sr = sf.read(path)
    y_stretch = pyrb.time_stretch(y, sr, speed)
    y_shift = pyrb.pitch_shift(y_stretch, sr, tone)
    
    # Write down to new file
    newpath = path.replace('.wav', '') + '_{}_{}.wav'.format(
        str(speed).replace('.', ''),
        str(tone).replace('.', '')
    )
    sf.write(newpath, y_shift, sr, format='wav')
    
    # Play sound
    playsound(newpath)
    
    # Remove temp file
    os.remove(newpath)
    
    