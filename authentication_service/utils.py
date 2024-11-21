from shared.config import Config
import jwt
import datetime

def generate_token(user_info):
    token = jwt.encode({
        'email': user_info['email'],
        'role': user_info['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, Config.SECRET_KEY, algorithm='HS256')
    return token

def validate_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
