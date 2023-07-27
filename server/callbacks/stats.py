import json
import pprint
from loguru import logger
from threading import currentThread


def stats_callback_generator(configs, database, log=True):
    def callback(
        ch, method, 
        properties, body
    ):
        # Load content
        content = json.loads(body.decode('utf-8'))
        if log:
            logger.info('{}: Recieve data: {}'.format(currentThread().getName(), pprint.pformat(content)))
        
        # Insert to collection
        collection = database[
            configs['mongo']['cols']['stats']
        ]
        collection.insert_one(content)
        if log:
            logger.info('{}: Saved data to MongoDB!'.format(currentThread().getName()))
        
    return callback