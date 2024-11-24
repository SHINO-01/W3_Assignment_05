from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from . import app
from .models import users

current_token = None

AUTH_SERVICE_URL = "http://localhost:5001"

@app.route("/")
def home():
    return "Welcome to the User Service!"

#===============================================/REGISTER======================================================
@app.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    ---
    tags:
      - User Service
    summary: Create new user
    description: Register a new user with name, email, password and role
    parameters:
      - in: body
        name: body
        description: User object that needs to be registered
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
            role:
              type: string
              example: "User"
          required:
            - name
            - email
            - password
            - role
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User registered successfully"
      400:
        description: Missing required fields or user already exists
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User already exists"
      403:
        description: "PROTECTION VIOLATION: Only Admins can create Admin Accounts"
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Forbidden Action: Not Logged in as Admin"         
    """

    role = None
    global current_token
    if current_token:
        current_token = current_token.replace("Bearer ", "")
        # Validate token via Authentication Service
        response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers={"Authorization": f"Bearer {current_token}"})
        if response.status_code != 200:
            return jsonify({"message": "Invalid or expired token"}), 401

        # Decode user role from the token
        user_info = response.json()
        role = user_info.get("role")

    # Get the request body
    data = request.get_json()
    required_fields = ["name", "email", "password", "role"]

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    # Prevent duplicate user creation
    email = data["email"]
    if email in users:
        return jsonify({"message": "User already exists"}), 400

    # Check if attempting to create an admin account
    if data["role"] == "Admin":
        if not current_token or role != "Admin":
            return jsonify({"message": "Only admins can create admin accounts"}), 403

    # Create the new user
    users[email] = {
        "name": data["name"],
        "email": email,
        "password": generate_password_hash(data["password"]),
        "role": data["role"]
    }

    return jsonify({"message": "User registered successfully"}), 201

#============================================/LOGIN=========================================================

@app.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and get token from the authentication server
    ---
    tags:
      - User Service
    summary: Login user
    description: Authenticate with email and password to receive JWT token
    parameters:
      - in: body
        name: body
        description: User credentials
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "password123"
          required:
            - email
            - password
    responses:
      200:
        description: Successfully authenticated
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      400:
        description: Missing email or password
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Email and password are required"
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid email or password"
    """
    global current_token
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = users.get(email)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid email or password"}), 401

    # Request token from the authentication server
    auth_response = requests.post(f"{AUTH_SERVICE_URL}/generate_token", json={
        "email": user["email"],
        "role": user["role"]
    })

    if auth_response.status_code == 200:
        # Extract and store the token
        #global current_token
        current_token = auth_response.json().get("access_token")
        if current_token:
            return jsonify({"access_token": current_token}), 200
        else:
            return jsonify({"message": "Token generation failed"}), 500
    elif auth_response.status_code == 401:
        return jsonify({"message": "Invalid email or password"}), 401
    else:
        return jsonify({"message": "Authentication server error"}), 500

#======================================================/PROFILE================================================

@app.route("/profile", methods=["GET"])
def profile():
    """
    Get user profile information
    ---
    tags:
      - User Service
    summary: Get user profile
    description: Retrieve the authenticated user's profile information
    parameters:
      - in: header
        name: Authorization
        description: JWT token
        required: true
        type: string
        default: "Bearer "
    responses:
      200:
        description: Successfully retrieved user profile
        schema:
          type: object
          properties:
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              example: "john@example.com"
            role:
              type: string
              example: "User"
      401:
        description: Missing authentication token
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Token is missing"
      403:
        description: Invalid token
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Token is invalid"
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User not found"
    """
    global current_token
    if not current_token:
        return jsonify({"message": "Not logged in or token missing"}), 401

    # Validate token via Authentication Service
    response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers={"Authorization": f"Bearer {current_token}"})

    if response.status_code != 200:
        current_token = None  # Clear invalid token
        return jsonify({"message": "Token is invalid"}), 401

    user_info = response.json()
    email = user_info.get("email")
    user = users.get(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Filter the response to include only name, email, and role
    filtered_user = {
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }

    return jsonify(filtered_user), 200
#=======================================================Internal==============================================================
@app.route("/_internal/get_token", methods=["GET"])
def _internal_get_token():
    """
    Hidden internal endpoint to get the current token.
    """
    if request.headers.get("X-Internal-Request") != "true":
        return jsonify({"message": "Unauthorized"}), 403

    global current_token
    if not current_token:
        return jsonify({"message": "No active token"}), 401

    return jsonify({"access_token": current_token}), 200