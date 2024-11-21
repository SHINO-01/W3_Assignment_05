from flask import request, jsonify
from werkzeug.security import generate_password_hash
from uuid import uuid4
import requests

from . import app
from .models import users

@app.route('/')
def home():
    return "Welcome to the User Service!"

@app.route('/register', methods=['POST'])
def register():

    data = request.get_json()
    required_fields = ['name', 'email', 'password', 'role']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing fields in registration data'}), 400

    email = data['email']
    if email in users:
        return jsonify({'message': 'User already exists'}), 400

    user_id = str(uuid4())
    hashed_password = generate_password_hash(data['password'])
    users[email] = {
        'id': user_id,
        'name': data['name'],
        'email': email,
        'password': hashed_password,
        'role': data['role']
    }

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/profile', methods=['GET'])
def profile():

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    # Validate token with Authentication Service
    auth_service_url = 'http://localhost:5001/validate'
    headers = {'Authorization': token}
    auth_response = requests.get(auth_service_url, headers=headers)

    if auth_response.status_code != 200:
        return jsonify({'message': 'Token is invalid'}), 401

    user_info = auth_response.json()
    email = user_info['email']
    user = users.get(email)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user_data = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role']
    }
    return jsonify(user_data), 200

@app.route('/get_user', methods=['POST'])
def get_user():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is missing'}), 400
    user = users.get(email)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    user_data = {
        'email': user['email'],
        'password': user['password'],
        'role': user['role']
    }
    return jsonify(user_data), 200
