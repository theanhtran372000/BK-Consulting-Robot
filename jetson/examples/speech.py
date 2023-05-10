import speech_recognition as sr

listener = sr.Recognizer()

with sr.Microphone(device_index=11) as mic:
    while True:
        
        listener.adjust_for_ambient_noise(mic)
        
        print('Say something ...')
        voice = listener.listen(mic)
        
        text = listener.recognize_google(voice, language='vi')
        print('Listen: ', text)