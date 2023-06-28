import pika
from loguru import logger
from threading import currentThread

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
    
def consumer_thread(
    configs, queue, callback
):
    # Create connections
    logger.info('{}: Connect to RabbitMQ server at {}'.format(
        currentThread().getName(),
        configs['rabbitmq']['host']
    ))
    channel = connect(
        host=configs['rabbitmq']['host'],
        username=configs['rabbitmq']['user'],
        password=configs['rabbitmq']['pass']
    )
    
    # Create queue
    create_queue(channel, queue)
    
    # Start comsuming
    consume(channel, queue, callback)