from flask import Blueprint

# Submodules
from . import stream, standard

# Create module answer
module = Blueprint('answer', __name__)

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
    stream.configure(API_KEY, configs, database)
    standard.configure()


# Register submodules
module.register_blueprint(stream.module, url_prefix='/stream')
module.register_blueprint(standard.module, url_prefix='/standard')