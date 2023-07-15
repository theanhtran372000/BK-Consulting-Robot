import pymongo
import urllib.parse

def get_mongo_client(host, port, username, password, ):
    
    # Preprocess username password
    username = urllib.parse.quote_plus(username)
    password = urllib.parse.quote_plus(password)
    
    # Connect to Mongo DB
    client = pymongo.MongoClient('mongodb://%s:%s@%s:%s' % (username, password, host, str(port)))
    
    return client