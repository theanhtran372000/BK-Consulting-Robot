import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

from flask import Blueprint

# Submodules
from . import log, info

# Utils
from utils.token import validate

# Create module system
module = Blueprint('system', __name__)

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

    # Configs submodules
    log.configure(SECRETE_KEY, configs, database)
    info.configure(SECRETE_KEY, configs, database)
    
# Register submodules
module.register_blueprint(info.module, url_prefix='/info')
module.register_blueprint(log.module, url_prefix='/log')

# Validate token
@module.before_request
def validate_token():
    return validate(SECRETE_KEY, configs['token']['algorithm'])

