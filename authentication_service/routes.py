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
    ---
    tags:
      - Authentication Service
    summary: Generate a JWT token
    description: Generate a JWT token for authentication using email and role.
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "user@example.com"
            role:
              type: string
              example: "Admin"
          required:
            - email
            - role
    responses:
      200:
        description: JWT token generated successfully
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      400:
        description: Missing email or role
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Email and role are required"
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
    ---
    tags:
      - Authentication Service
    summary: Validate a JWT token
    description: Validate a JWT token to verify its authenticity and extract the payload.
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        default: "Bearer "
        description: Bearer token for validation
    responses:
      200:
        description: Token is valid
        schema:
          type: object
          properties:
            email:
              type: string
              example: "user@example.com"
            role:
              type: string
              example: "Admin"
            exp:
              type: number
              example: 1732485898
      401:
        description: Missing, expired, or invalid token
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Token has expired"
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
