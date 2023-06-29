import jwt
from loguru import logger
from datetime import datetime, timedelta

def encode(
    data, 
    secrete_key, 
    algorithm='HS256', 
    expire={
        'days': 1,
        'hours': 0,
        'minutes': 0,
        'seconds': 0
    }
):
    try:
        return jwt.encode(
                {
                    'exp': datetime.utcnow() + timedelta(**expire),
                    'iat': datetime.utcnow(),
                    'data': data
                }, 
                secrete_key, 
                algorithm
            )
    except:
        logger.exception('Fail to generate access token!')
        return None


def decode(token, secrete_key, algorithms=['HS256']):
    try:
        payload = jwt.decode(
            token, 
            secrete_key,
            algorithms=algorithms
        )
        
        return {
            'success': True,
            'data': payload['data'],
            'message': 'Access token verified!'
        }
    
    except jwt.ExpiredSignatureError:
        logger.error('Access token expired!')
        return {
            'success': False,
            'data': None,
            'message': 'Access token expired!'
        }
        
    except jwt.InvalidTokenError:
        logger.error('Invalid token!')
        return {
            'success': False,
            'data': None,
            'message': 'Invalid token!'
        }
    