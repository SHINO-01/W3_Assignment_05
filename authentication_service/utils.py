import jwt
import datetime
from shared.config import Config

def generate_token(email, role):
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

def validate_token(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"message": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"message": "Invalid token"}
