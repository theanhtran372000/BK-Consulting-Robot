import pika

# Connect to RabbitMQ server
credentials = pika.PlainCredentials('theanh', '123456')
parameters = pika.ConnectionParameters(
    '169.254.234.10',
    5672,
    '/',
    credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare queue
queue_name = 'stats'
channel.queue_declare(queue=queue_name)

# Callback
def callback(ch, method, properties, body):
    print(" [x] Received: {} - Data type: {}".format(body.decode('utf-8'), type(body)))
    
channel.basic_consume(
    queue=queue_name,
    auto_ack=True,
    on_message_callback=callback
)

print(' [*] Listen on queue {}'.format(queue_name))
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()