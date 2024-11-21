from flask import request, jsonify
import requests
from . import app
from .models import destinations

AUTH_SERVICE_URL = "http://localhost:5001"

@app.route("/")
def home():
    return "Welcome to the Destination Service!"

@app.route("/destinations", methods=["GET"])
def get_destinations():
    """
    Retrieve all destinations.
    """
    return jsonify(list(destinations.values())), 200

@app.route("/destinations", methods=["POST"])
def add_destination():
    """
    Add a new destination (Admin only).
    """
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401

    # Validate token via Authentication Service
    token = token.replace("Bearer ", "")
    response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers={"Authorization": token})

    if response.status_code != 200:
        return jsonify({"message": "Token is invalid"}), 401

    # Extract user details from the token payload
    user_info = response.json()
    if user_info["role"] != "Admin":
        return jsonify({"message": "Unauthorized action: Admins only"}), 403

    # Process the destination addition
    data = request.get_json()
    required_fields = ["id", "name", "description", "location", "price_per_night"]

    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    destination_id = data["id"]
    if destination_id in destinations:
        return jsonify({"message": "Destination ID already exists"}), 400

    destinations[destination_id] = {
        "id": destination_id,
        "name": data["name"],
        "description": data["description"],
        "location": data["location"],
        "price_per_night": data["price_per_night"]
    }
    return jsonify({"message": "Destination added successfully"}), 201

@app.route("/destinations/<destination_id>", methods=["DELETE"])
def delete_destination(destination_id):
    """
    Delete a destination (Admin only).
    """
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401

    # Validate token via Authentication Service
    token = token.replace("Bearer ", "")
    response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers={"Authorization": token})

    if response.status_code != 200:
        return jsonify({"message": "Token is invalid"}), 401

    # Extract user details from the token payload
    user_info = response.json()
    if user_info["role"] != "Admin":
        return jsonify({"message": "Unauthorized action: Admins only"}), 403

    # Process the destination deletion
    if destination_id not in destinations:
        return jsonify({"message": "Destination not found"}), 404

    del destinations[destination_id]
    return jsonify({"message": "Destination deleted successfully"}), 200
