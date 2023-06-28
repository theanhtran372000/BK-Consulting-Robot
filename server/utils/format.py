# Format user response
def format_response(state, msg, result):
    return {
        'state': state,
        'message': msg,
        'result': result
    }
  
        
# Format for SSE protocol
def format_sse(data: str, event=None):
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg
    