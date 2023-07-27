import pymongo

# Connect to Mongo DB
client = pymongo.MongoClient('mongodb://172.20.80.1:27017')

# Create a new DB
db_name = 'test'
db = client[db_name]

# Check if db exists
if db_name in client.list_database_names():
    print('DB {} exists!'.format(db_name))

# Create a collection
col_name = 'customer'
collection = db[col_name]

# # Check if col_name exists
# if col_name in db.list_collection_names():
#     print('Collection {} exists!'.format(col_name))
    
# # Insert a record
# record = {
#     'name': 'John',
#     'address': '37 Highway'
# }

# # Insert one record: return _id
# # Mongo will assign an unique _id for each document (record) if not specified
# x = collection.insert_one(record)
# print('Record id: ' + str(x.inserted_id))


# # Insert many records
# records = [
#   { "name": "Amy", "address": "Apple st 652"},
#   { "name": "Hannah", "address": "Mountain 21"},
#   { "name": "Michael", "address": "Valley 345"},
#   { "name": "Sandy", "address": "Ocean blvd 2"},
#   { "name": "Betty", "address": "Green Grass 1"},
#   { "name": "Richard", "address": "Sky st 331"},
#   { "name": "Susan", "address": "One way 98"},
#   { "name": "Vicky", "address": "Yellow Garden 2"},
#   { "name": "Ben", "address": "Park Lane 38"},
#   { "name": "William", "address": "Central st 954"},
#   { "name": "Chuck", "address": "Main Road 989"},
#   { "name": "Viola", "address": "Sideway 1633"}
# ]

# x = collection.insert_many(records)
# print('Record ids: {}'.format(x.inserted_ids))

# Find document

# Find first document
x = collection.find_one({
    '_id': '0'
})
# print('First doc: ', x)
print('Not found: ', x)
print('Type: ', type(x))

# Find all
x = collection.find()
print('All docs: ')
for doc in x:
    print('-', doc)
    
# Find specific
result = collection.find(
    {
        "address": "Highway 37" # Find
    }, 
    {
        'name': 0   # Exclude name from result
    }
)
print('Result for address "hway 3": ', result[0])
print('Length: ', len(list(result)))
for doc in result:
    print('-', doc)

# Query
print('Result for person name start with S:')
query = { "name": { "$regex": "^S" } }
for x in collection.find(query):
    print('-', x)
    
# Sort
print('Sort by name')
for doc in collection.find().sort('name', 1): # -1 for descending
    print('-', doc)
    
# Delete
x = collection.delete_many({
    "address": {
        '$regex': '^O'
    }
})
print('Delete: {} rows'.format(x.deleted_count))

# Delete all
# collection.delete_many({})

# Drop collection
# collection.drop()

result = collection.update_one({
    'address': 'Green Grass 1'
}, {
    '$set': {
        'address': 'Green Grass 12'
    }
})

print('Update result: ', result)

# Limit: first 5 rows
for x in collection.find().limit(5):
    print(x)
