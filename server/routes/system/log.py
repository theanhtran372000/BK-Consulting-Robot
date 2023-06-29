import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

from bson.objectid import ObjectId
from flask import Blueprint, request, g

# Utils
from utils.format import format_response

# Create module system
module = Blueprint('system_log', __name__)

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
    
### === Conversation History === ###
@module.route('/history', methods=['POST'])
def get_history():
    
    # Get system code
    if 'history_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        history_id = request.form['history_id']
    
    # Get system
    collection = database[configs['mongo']['cols']['history']]
    doc = collection.find_one({
        '_id': ObjectId(history_id)
    })
    
    if doc is not None:
        doc['_id'] = str(doc['_id'])
            
    return format_response(
        success=True,
        message='Get history success!',
        data=doc
    ), 200



@module.route('/list_history', methods=['POST'])
def list_history():
    
    # Get system code
    if 'system_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        system_id = request.form['system_id']
    
    # Get system
    collection = database[configs['mongo']['cols']['history']]
    found = collection.find({
        'system_id': system_id
    })
    
    histories = []
    for hist in found:
        # Convert id to str
        hist['_id'] = str(hist['_id'])
        histories.append(hist)
        
    return format_response(
        success=True,
        message='Find {} conversation on system {}'.format(len(histories), system_id),
        data=histories
    ), 200
    

### === Stats === ###
@module.route('/stats', methods=['POST'])
def get_stats():
    
    # Get system code
    if 'stats_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        stats_id = request.form['stats_id']
    
    # Get system
    collection = database[configs['mongo']['cols']['stats']]
    doc = collection.find_one({
        '_id': ObjectId(stats_id)
    })
    
    if doc is not None:
        doc['_id'] = str(doc['_id'])
            
    return format_response(
        success=True,
        message='Get stats success!',
        data=doc
    ), 200



@module.route('/list_stats', methods=['POST'])
def list_stats():
    
    # Get system code
    if 'system_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        system_id = request.form['system_id']
    
    # Get system
    collection = database[configs['mongo']['cols']['stats']]
    found = collection.find({
        'system_id': system_id
    })
    
    list_stats = []
    for stats in found:
        # Convert id to str
        stats['_id'] = str(stats['_id'])
        list_stats.append(stats)
        
    return format_response(
        success=True,
        message='Find {} stats on system {}'.format(len(list_stats), system_id),
        data=list_stats
    ), 200


### === Face Track === ###
@module.route('/face_track', methods=['POST'])
def get_face_track():
    
    # Get system code
    if 'face_track_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        face_track_id = request.form['face_track_id']
    
    # Get system
    collection = database[configs['mongo']['cols']['face_track']]
    doc = collection.find_one({
        '_id': ObjectId(face_track_id)
    })
    
    if doc is not None:
        doc['_id'] = str(doc['_id'])
            
    return format_response(
        success=True,
        message='Get face track state success!',
        data=doc
    ), 200



@module.route('/list_face_track', methods=['POST'])
def list_face_track():
    
    # Get system code
    if 'system_id' not in request.form:
        return format_response(
            success=False,
            message='Insufficient information!',
            data=None
        ), 400
        
    else:
        system_id = request.form['system_id']
    
    # Get system
    collection = database[configs['mongo']['cols']['face_track']]
    found = collection.find({
        'system_id': system_id
    })
    
    list_face_track = []
    for face_track in found:
        # Convert id to str
        face_track['_id'] = str(face_track['_id'])
        list_face_track.append(face_track)
        
    return format_response(
        success=True,
        message='Find {} face track states on system {}'.format(len(list_face_track), system_id),
        data=list_face_track
    ), 200