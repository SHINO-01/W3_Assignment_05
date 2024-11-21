from flask import request, jsonify
from werkzeug.security import check_password_hash
import requests

from . import app
from .utils import generate_token, validate_token

@app.route('/')
def home():
    return "Welcome to the Authentication Service!"

@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    required_fields = ['email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing email or password'}), 400

    email = data['email']
    password = data['password']

    # Get user info from User Service
    user_service_url = 'http://localhost:5000/get_user'
    response = requests.post(user_service_url, json={'email': email})
    if response.status_code != 200:
        return jsonify({'message': 'User not found'}), 404

    user = response.json()
    hashed_password = user['password']
    if not check_password_hash(hashed_password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = generate_token(user)
    return jsonify({'access_token': token}), 200

@app.route('/validate', methods=['GET'])
def validate():
    
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    payload = validate_token(token)
    if not payload:
        return jsonify({'message': 'Token is invalid or expired'}), 401

    user_info = {
        'email': payload['email'],
        'role': payload['role']
    }
    return jsonify(user_info), 200
