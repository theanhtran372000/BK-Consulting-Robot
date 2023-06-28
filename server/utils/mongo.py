import pymongo

def get_mongo_client(host, port=27017):
    # Connect to Mongo DB
    client = pymongo.MongoClient('mongodb://{}:{}'.format(host, port))
    
    return client