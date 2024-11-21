from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from . import app
from .models import users

AUTH_SERVICE_URL = "http://localhost:5001"

@app.route("/")
def home():
    return "Welcome to the User Service!"

@app.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    """
    data = request.get_json()
    required_fields = ["name", "email", "password", "role"]

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    email = data["email"]
    if email in users:
        return jsonify({"message": "User already exists"}), 400

    users[email] = {
        "name": data["name"],
        "email": email,
        "password": generate_password_hash(data["password"]),
        "role": data["role"]
    }
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and request a JWT token from the Authentication Service.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = users.get(email)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Request token from Authentication Service
    response = requests.post(f"{AUTH_SERVICE_URL}/generate_token", json={
        "email": user["email"],
        "role": user["role"]
    })

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"message": "Error generating token"}), 500

@app.route("/profile", methods=["GET"])
def profile():
    """
    Get user profile information.
    """
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401

    token = token.replace("Bearer ", "")
    # Validate token via Authentication Service
    response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers={"Authorization": token})

    if response.status_code != 200:
        return jsonify({"message": "Token is invalid"}), 401

    user_info = response.json()
    email = user_info.get("email")
    user = users.get(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user), 200
