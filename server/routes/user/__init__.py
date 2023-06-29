from flask import Blueprint

# Submodules
from . import auth, info

# Create module user
module = Blueprint('user', __name__)

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
    auth.configure(SECRETE_KEY, configs, database)
    info.configure(SECRETE_KEY, configs, database)

# Register submodule
module.register_blueprint(auth.module, url_prefix='/auth')
module.register_blueprint(info.module, url_prefix='/info')