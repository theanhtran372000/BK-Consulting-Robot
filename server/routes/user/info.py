import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

from bson.objectid import ObjectId
from flask import Blueprint, request, g

# Utils
from utils.format import format_response
from utils.hash import hash_sha1
from utils.token import validate

module = Blueprint('user_info', __name__)

# Configs
SECRETE_KEY = ''
configs = {}
database = None


# Configure function
def configure(_SECRETE_KEY, _configs, _database):
    global SECRETE_KEY
    global configs
    global database
    
    # Local configs
    SECRETE_KEY = _SECRETE_KEY
    configs = _configs
    database = _database


@module.before_request
def validate_token():
    return validate(SECRETE_KEY, configs['token']['algorithm'])


@module.route('/get', methods=['GET'])
def get_user():
    
    return format_response(
        success=True, 
        message='Get user info success!',
        data=g.user
    ), 200
    
    
@module.route('/update', methods=['POST'])
def update_user():
    
    # Get user info from decoded access token
    current_user = g.user
    
    # Get new info
    new_values = {}
    if 'name' in request.form:
        new_values['name'] = request.form['name']
        
    if 'password' in request.form:
        new_values['password'] = hash_sha1(request.form['password'])
    
    
    # Update user info
    collection = database[configs['mongo']['cols']['user']]
    collection.update_one(
        {
            '_id': ObjectId(current_user['_id'])
        },
        {
            '$set': new_values
        }
    )
    
    # Return updated sample
    doc = collection.find_one({
        '_id': ObjectId(current_user['_id'])
    },{
        'password': 0
    })
    
    doc['_id'] = str(doc['_id'])

    return format_response(
        success=True,
        message="Update success!",
        data=doc
    ), 200
    
@module.route('/delete', methods=['DELETE'])
def delete_user():
    # Get user info from decoded access token
    current_user = g.user
    
    # Delete user
    collection = database[configs['mongo']['cols']['user']]
    collection.delete_one({
        '_id': ObjectId(current_user['_id'])
    })
    
    return format_response(
        success=True,
        message="Delete success!",
        data=None
    ), 200
