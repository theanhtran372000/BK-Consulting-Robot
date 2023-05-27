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

def recieve_sse(question):
    start = time.time()
    client = sseclient.SSEClient(
        requests.post(
            'http://localhost:9000/stream_answer_stable', 
            json={
              "question"  : question
            },
            stream=True
        )
    )

    start_recieving = False
    for event in client.events():
        if not start_recieving:
            print('Establish connection done after {:.2f}s'.format(time.time() - start))
            start_recieving = True
        print(event.data, end='', flush=True)
    
    client.close()
    print()
    print('Done after {:.2f}s!'.format(time.time() - start))
    
if __name__ == '__main__':
    questions = [
        "Giới thiệu về đại học Bách Khoa Hà Nội",
        "Tại sao nước biển lại mặn",
        "Tại sao bầu trời lại màu xanh",
        "Tại sao cá lại thở được dưới nước",
        "Hoa thụ phấn như thế nào",
        "Cây quang hợp như thế nào",
        "Nhiệt độ nóng chảy của thủy ngân là bao nhiêu?",
        "Giải thích chỉ số BMI",
        "Thực phẩm biến đổi gen là gì?",
        "Hoang mạc lớn nhất thế giới là gì?"
    ]
    
    for question in questions:
        print('= ' * 5 + '[{}]'.format(question) + ' =' * 5)
        recieve_sse(question)
    # test_api('What is Python?')
    