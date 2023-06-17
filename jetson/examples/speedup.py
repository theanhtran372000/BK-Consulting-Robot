from pydub import AudioSegment
import soundfile as sf
import pyrubberband as pyrb
import time

path = 'assets/voices/greet.mp3'
speed = 1.3
tone = 1

start = time.time()
sound = AudioSegment.from_mp3(path)
sound.export("examples/file.wav", format="wav")
print('Convert to wav: {:.2f}s'.format(time.time() - start))


start = time.time()
y, sr = sf.read("examples/file.wav")
# Play back at extra low speed
y_stretch = pyrb.time_stretch(y, sr, speed)
# Play back extra low tones
y_shift = pyrb.pitch_shift(y, sr, tone)
sf.write("examples/result.wav", y_stretch, sr, format='wav')
print('Process: {:.2f}s'.format(time.time() - start))

start = time.time()
sound = AudioSegment.from_wav("examples/result.wav")
sound.export("examples/result.mp3", format="mp3")
print('Convert to mp3: {:.2f}s'.format(time.time() - start))