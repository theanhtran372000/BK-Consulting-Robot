import flask
import queue
import time

def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg

class MessageAnnouncer:

    def __init__(self):
        self.listeners = []

    def listen(self):
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

announcer = MessageAnnouncer()
app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/ping')
def ping():
    msg = format_sse(data='pong')
    announcer.announce(msg=msg)
    return {}, 200

txt = 'Python is a high-level, interpreted, general-purpose programming language. It is a powerful and versatile language that is used for a wide range of applications, from web development to data science. Python is known for its readability and ease of use, making it a great language for beginners. It also has a large and active community of developers who contribute to the language and its libraries.'

@app.route('/listen', methods=['GET'])
def listen():

    def stream():
        # messages = announcer.listen()  # returns a queue.Queue
        
        msgs = txt.split(' ')    
        
        for msg in msgs:
            # msg = messages.get()  # blocks until a new message arrives
            time.sleep(0.5)
            yield format_sse(data=msg)

    return flask.Response(stream(), mimetype='text/event-stream')


app.run(threaded=True)