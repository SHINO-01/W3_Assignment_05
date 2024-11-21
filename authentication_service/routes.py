from flask import request, jsonify
import jwt
import datetime
from shared.config import Config
from . import app

@app.route("/")
def home():
    return "Welcome to the Authentication Service!"

@app.route("/generate_token", methods=["POST"])
def generate_token():
    """
    Generate a JWT token.
    """
    data = request.get_json()
    email = data.get("email")
    role = data.get("role")

    if not email or not role:
        return jsonify({"message": "Email and role are required"}), 400

    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return jsonify({"access_token": token}), 200

@app.route("/validate", methods=["GET"])
def validate():
    """
    Validate the provided JWT token.
    """
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401

    token = token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return jsonify(payload), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
