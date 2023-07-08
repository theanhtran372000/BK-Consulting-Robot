import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

from flask import Blueprint, request, g

# Utils
from utils.format import format_response

# Create module system
module = Blueprint('system_info', __name__)

# Module configs
# Configs
SECRETE_KEY = ''
configs = None
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
    

@module.route('/add', methods=['POST'])
def add_system():
    
    # User info
    current_user = g.user
    
    # Get system code
    if 'system_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        system_id = request.form['system_id']
        
    # Get system collection
    collection = database[configs['mongo']['cols']['system']]
    result = list(collection.find({
        'system_id': system_id,
        'user_id': current_user['_id']
    }))
    
    # System existed
    if len(result) != 0:
        return format_response(
            success=False,
            message='System Id exists!',
            data=None
        ), 400
    
    # Insert new system
    inserted = collection.insert_one({
        'system_id': system_id,
        'user_id': current_user['_id']
    })
    
    return format_response(
        success=True,
        message='Added system id {}'.format(system_id),
        data={
            '_id': str(inserted.inserted_id)
        }
    ), 200
    

@module.route('/list', methods=['GET'])
def list_system():
    
    # User info
    current_user = g.user
    
    # Find system id
    collection = database[configs['mongo']['cols']['system']]
    result = list(collection.find({
        'user_id': current_user['_id'] 
    }))
    
    systems = []
    
    for system in result:
        systems.append({
            '_id': str(system['_id']),
            'system_id': system['system_id']
        })
        
    return format_response(
        success=True,
        message='Find {} systems'.format(len(systems)),
        data=systems
    ), 200
    
@module.route('/delete', methods=['DELETE'])
def delete_user():
    # Get user info from decoded access token
    current_user = g.user
    
    # Get system code
    if 'system_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        system_id = request.form['system_id']
    
    # Delete system of user
    collection = database[configs['mongo']['cols']['system']]
    result = collection.delete_many({
        'user_id': current_user['_id'],
        'system_id': system_id
    })
    
    return format_response(
        success=True,
        message="Delete {} rows!".format(result.deleted_count),
        data=None
    ), 200

    
