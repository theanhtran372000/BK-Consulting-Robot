# Format user response
def format_response(success, message, data):
    return {
        'success': success,
        'message': message,
        'data': data
    }
  
        
# Format for SSE protocol
def format_sse(data: str, event=None):
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg
    