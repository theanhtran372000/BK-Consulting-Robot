from loguru import logger
from flask import request, g

from .format import format_response
from .jwt import decode

def validate(secrete_key, algorithm):
    # Validate token
    token = None
    if "Authorization" in request.headers:
        parts = request.headers["Authorization"].split(" ")
        if len(parts) > 0:
            token = parts[1]
            
    if not token:
        logger.error('Access token not found!')
        return format_response(
            success=False,
            message='Access token not found!',
            data=None
        ), 401
    
    # Check token validation
    result = decode(token, secrete_key=secrete_key, algorithms=[algorithm])
    
    if not result['success']:
        return result
    
    else:
        logger.success('User authorized!')
        g.user = result['data']
        return None