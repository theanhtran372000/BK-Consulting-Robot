import pika

def connect(host, username, password):
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(
        host,
        5672,
        '/',
        credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    return channel

def create_queue(channel, queue):
    channel.queue_declare(queue=queue)

def publish(channel, queue, text):
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=text
    )
    
def consume(channel, queue, callback):
    channel.basic_consume(
        queue=queue,
        auto_ack=True,
        on_message_callback=callback
    )
    
    channel.start_consuming()
    