import json
import openai
import sseclient

def get_chatgpt_answer(prompt, model_name='gpt-3.5-turbo', role='user'):
    completion = openai.ChatCompletion.create(
        model=model_name,
        messages=[{
            'role': role, # user/assistant (mean ChatGPT)/system
            'content': prompt
        }]
    )
    
    return completion['choices'][0]['message']['content']

# Temperature: 
# - Lower temperature will be more focused and conservative 
# - Higher temperature will be more creative and varied.
def prepare_streaming_request(
        prompt, 
        api_key, 
        model_name='gpt-3.5-turbo', 
        role='user', 
        temperature=0.7,
        max_tokens=1024
    ):
    reqUrl = 'https://api.openai.com/v1/chat/completions'
    reqHeader = {
        "Content-type": "application/json",
        'Authorization': 'Bearer ' + api_key
    }
    reqBody = {
        'model': model_name,
        "messages": 
            [{
                "role": role, 
                "content": prompt
            }],
        "temperature": temperature,
        'max_tokens': max_tokens,
        'stream': True
    }
    
    return  reqUrl, reqHeader, reqBody
    
def create_answer_generator(request, finish_word='[DONE]'):
    client = sseclient.SSEClient(request)
    
    for event in client.events():
        if event.data != finish_word:
            data = json.loads(event.data)
            if 'content' in data['choices'][0]['delta']:
                word = data['choices'][0]['delta']['content']
                yield word
        else:
            yield finish_word
            
    client.close()
        
def format_sse(data: str, event=None):
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg
    