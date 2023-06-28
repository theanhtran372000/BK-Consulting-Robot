from flask import Blueprint

from .stream import module_stream, stream_configure
from .standard import module_standard, standard_configure

# Create module answer
module_answer = Blueprint('answer', __name__)

# Module config

# Configs
API_KEY = ''
configs = None
database = None

# Configure function
def configure(_API_KEY, _configs, _database):
    global API_KEY
    global configs
    global database
    
    # Local configs
    API_KEY = _API_KEY
    configs = _configs
    database = _database

    # Configs submodules
    stream_configure(API_KEY, configs, database)
    standard_configure()

# Register submodules
module_answer.register_blueprint(module_stream, url_prefix='/stream')
module_answer.register_blueprint(module_standard, url_prefix='/standard')