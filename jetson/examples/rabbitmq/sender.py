import pika

# Connect to RabbitMQ
credentials = pika.PlainCredentials('theanh', '123456')
parameters = pika.ConnectionParameters(
    '169.254.234.10',
    5672,
    '/',
    credentials
)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()


# Public
channel.basic_publish(exchange='',
                      routing_key='test',
                      body='Hello World!')
print(" [x] Sent 'Hello World!'")

connection.close()

