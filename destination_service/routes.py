from flask import request, jsonify
import requests

from . import app
from .models import destinations

@app.route('/')
def home():
    return "Welcome to the Destination Service!"

@app.route('/destinations', methods=['GET'])
def get_destinations():
    
    return jsonify(list(destinations.values())), 200

@app.route('/destinations', methods=['POST'])
def add_destination():
    
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
    if user_info['role'] != 'Admin':
        return jsonify({'message': 'Unauthorized action'}), 403

    data = request.get_json()
    required_fields = ['id', 'name', 'description', 'location', 'price_per_night']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing fields in destination data'}), 400

    dest_id = data['id']
    if dest_id in destinations:
        return jsonify({'message': 'Destination ID already exists'}), 400

    destinations[dest_id] = {
        'id': dest_id,
        'name': data['name'],
        'description': data['description'],
        'location': data['location'],
        'price_per_night': data['price_per_night']
    }

    return jsonify({'message': 'Destination added successfully', 'id': dest_id}), 201

@app.route('/destinations/<destination_id>', methods=['DELETE'])
def delete_destination(destination_id):
    
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
    if user_info['role'] != 'Admin':
        return jsonify({'message': 'Unauthorized action'}), 403

    if destination_id in destinations:
        del destinations[destination_id]
        return jsonify({'message': 'Destination deleted successfully'}), 200
    else:
        return jsonify({'message': 'Destination not found'}), 404
