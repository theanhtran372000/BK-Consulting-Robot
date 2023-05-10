import requests
import json
import sseclient
import time

API_KEY = open('save/keys/openai.txt', 'r').read().strip()

def performRequestWithStreaming():
    reqUrl = 'https://api.openai.com/v1/completions'
    reqHeaders = {
        'Accept': 'text/event-stream',
        'Authorization': 'Bearer ' + API_KEY
    }
    reqBody = {
        'model': 'text-davinci-003',
        'prompt': 'What is Python?',
        'max_tokens': 100,
        'temperature': 0,
        'stream': True
    }
    
    request = requests.post(
        reqUrl,
        stream=True,
        headers=reqHeaders,
        json=reqBody
    )
    
    client = sseclient.SSEClient(request)
    for event in client.events():
        time.sleep(0.5)
        if event.data != '[DONE]':
            print(json.loads(event.data)['choices'][0]['text'], end='', flush=True)


def test_api(prompt):
    reqUrl = 'http://localhost:9000/stream_answer'
    
    reqBody = {
        'question': 'What is Python?',
    }

    request = requests.post(
        reqUrl,
        stream=True,
        json=reqBody
    )
    
    client = sseclient.SSEClient(request)
    for event in client.events():
        if event.data != '[DONE]':
            print(event.data, end='', flush=True)
        
    print()

def recieve_sse():
    client = sseclient.SSEClient(
        requests.get('http://localhost:5000/listen', stream=True)
    )

    for event in client.events():
        print(event.data, end=' ', flush=True)
        
    print('Done!')
    
if __name__ == '__main__':
    # recieve_sse()
    test_api('What is Python?')
    