import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

from flask import Blueprint, request

# Utils
from utils.format import format_response
from utils.jwt import encode
from utils.hash import hash_sha1

module = Blueprint('user_auth', __name__)

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
    

@module.route('/register', methods=['POST'])
def register():
    
    # Get request data
    content = request.form
    
    # Validate
    if 'username' not in content or \
        'password' not in content or \
        'name' not in content:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    # Get register information
    username = content['username']
    password = content['password']
    name = content['name']
    
    # Get mongo collection
    collection = database[configs['mongo']['cols']['user']]
    
    # Check if user exists or not
    existed_users = list(collection.find({
        'username': username
    }))
    
    # User exists
    if len(existed_users) > 0:
        return format_response(
            success=False,
            message='User existed!',
            data=None
        ), 400
        
    # Add new user to db
    inserted = collection.insert_one({
        'name': name,
        'username': username,
        'password': hash_sha1(password)
    })
    
    # Create access token
    access_token = encode(
        {
            '_id': str(inserted.inserted_id),
            'name': name,
            'username': username
        },
        SECRETE_KEY,
        algorithm=configs['token']['algorithm'],
        expire=configs['token']['expire']
    )
    
    return format_response(
        success=True,
        message="Account created!",
        data={
            'access_token': access_token
        },
    ), 200
    
    
@module.route('/login', methods=['POST'])
def login():
    
    content = request.form
    
    # Validate request
    if 'username' not in content or \
        'password' not in content:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
    
    # Get register information
    username = content['username']
    password = content['password']
    
    # Get mongo collection
    collection = database[configs['mongo']['cols']['user']]
    
    # Check if user exists or not
    existed_users = list(collection.find({
        'username': username
    }))
    
    # User exists
    if len(existed_users) == 0:
        return format_response(
            success=False,
            message='User not existed!',
            data=None
        ), 400
        
    user = existed_users[0]
    
    # Check password
    if hash_sha1(password) != user['password']:
        return format_response(
            success=False,
            message='Password incorrect!',
            data=None
        ), 400
        
    else:
        # Create access token
        access_token = encode(
            {
                '_id': str(user['_id']),
                'name': user['name'],
                'username': user['username']
            },
            SECRETE_KEY,
            algorithm=configs['token']['algorithm'],
            expire=configs['token']['expire']
        )
        
        return format_response(
            success=True,
            message="Loginned!",
            data={
                'access_token': access_token
            },
        ), 200