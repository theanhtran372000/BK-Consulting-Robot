import threading
from playsound import playsound

def play_sound_async(path):
    """Play sound in background thread

    Args:
        path (str): Path to sound file
    """
    threading.Thread(target=playsound, args=(path,)).start()
    
def play_sound_sync(path):
    """Play sound in background thread

    Args:
        path (str): Path to sound file
    """
    playsound(path)