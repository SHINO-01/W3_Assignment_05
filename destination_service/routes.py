from flask import request, jsonify
import requests
from . import app
from .models import destinations

AUTH_SERVICE_URL = "http://localhost:5001"
USER_SERVICE_URL = "http://localhost:5000"

def fetch_token_from_user_service():
    """
    Fetch the token from the User Service's hidden internal endpoint.
    """
    try:
        response = requests.get(f"{USER_SERVICE_URL}/_internal/get_token", headers={"X-Internal-Request": "true"})
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                return f"Bearer {token}"
            else:
                raise Exception("No active token returned by User Service.")
        else:
            response_text = response.text if isinstance(response.text, str) else str(response.text)
            raise Exception(f"Failed to fetch token from User Service: {response_text}")
    except Exception as e:
        raise Exception(f"Token fetch failed: {str(e)}")


def validate_token(required_role=None):
    try:
        token = fetch_token_from_user_service().replace("Bearer ", "")
        response = requests.get(f"{AUTH_SERVICE_URL}/validate", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise Exception("Invalid or expired token")
        user_info = response.json()
        if required_role and user_info.get("role") != required_role:
            raise Exception(f"Unauthorized action: {required_role}s only")
        return user_info
    except Exception as e:
        print(f"Token validation error: {e}")
        raise


@app.route("/")
def home():
    """
    Welcome route for the service.
    """
    return "Welcome to the Destination Service!"


@app.route("/destinations", methods=["GET"])
def get_destinations():
    """
     Retrieve all destinations.
    - ID field is visible only to admins.
    ---
    tags:
      - Destinations
    summary: Retrieve all destinations
    description: Retrieve a list of all destinations. Admins see the `id` field, while regular users do not.
    parameters:
      - in: header
        name: Authorization
        required: false
        type: string
        description: Bearer token for authentication
    responses:
      200:
        description: List of destinations
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                example: "dest1"
              name:
                type: string
                example: "Beach Resort"
              description:
                type: string
                example: "A beautiful beach resort."
              location:
                type: string
                example: "Maldives"
              price_per_night:
                type: number
                example: 150
    """
    # Validate token if present
    try:
        user_info = validate_token()
        role = user_info.get("role")
    except Exception as e:
        print(f"Error in GET /destinations: {e}")
        return jsonify({"message": str(e)}), 401

    if role == "Admin":
        return jsonify(list(destinations.values())), 200
    else:
        filtered_destinations = [
            {key: value for key, value in dest.items() if key != "id"}
            for dest in destinations.values()
        ]
        return jsonify(filtered_destinations), 200


@app.route("/destinations", methods=["POST"])
def add_destination():
    """
    Add a new destination (Admin only).
    ---
    tags:
      - Destinations
    summary: Add a new destination
    description: Admins can add a new destination to the service.
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        default: "Bearer "
        description: Bearer token for authentication
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            id:
              type: string
              example: "SWZ"
            name:
              type: string
              example: "Mountain Retreat"
            description:
              type: string
              example: "A serene mountain retreat."
            location:
              type: string
              example: "Switzerland"
            price_per_night:
              type: number
              example: 200
    responses:
      201:
        description: Destination added successfully
      400:
        description: Missing required fields or duplicate destination ID
      401:
        description: Missing or invalid token
      403:
        description: Unauthorized action
    """
    try:
        # Validate token and ensure the user is an admin
        user_info = validate_token(required_role="Admin")
    except Exception as e:
        return jsonify({"message": str(e)}), 403

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
    ---
    tags:
      - Destinations
    summary: Delete a destination
    description: Admins can delete a destination from the service.
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        default: "Bearer "
        description: Bearer token for authentication
      - in: path
        name: destination_id
        required: true
        type: string
        defaul: "SWZ"
        description: ID of the destination to delete
    responses:
      200:
        description: Destination deleted successfully
      401:
        description: Missing or invalid token
      403:
        description: Unauthorized action
      404:
        description: Destination not found
    """
    try:
        # Validate token and ensure the user is an admin
        validate_token(required_role="Admin")
    except Exception as e:
        return jsonify({"message": str(e)}), 403

    if destination_id not in destinations:
        return jsonify({"message": "Destination not found"}), 404

    del destinations[destination_id]
    return jsonify({"message": "Destination deleted successfully"}), 200
