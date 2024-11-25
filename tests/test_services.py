import sys
import os

# Dynamically add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import json
from destination_service import app as dest_app
from user_service import app as user_app
from authentication_service import app as auth_app
from shared.config import Config
import jwt
import datetime
from unittest.mock import patch, Mock
import user_service.routes
import destination_service.routes

# Test clients for each service
@pytest.fixture
def auth_client():
    auth_app.testing = True
    return auth_app.test_client()

@pytest.fixture
def user_client():
    user_app.testing = True
    return user_app.test_client()

@pytest.fixture
def dest_client():
    dest_app.testing = True
    return dest_app.test_client()

# Reset current_token before each test
@pytest.fixture(autouse=True)
def reset_current_token():
    user_service.routes.current_token = None

# Test constants
ADMIN_EMAIL = "masteradmin@example.com"
ADMIN_PASSWORD = "Master@123"
USER_EMAIL = "user@example.com"
USER_PASSWORD = "userpass"
DEFAULT_ROLE = "User"

# Helper: Generate a token
def generate_token(email, role):
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")

# ==========================================
# TESTS FOR AUTHENTICATION SERVICE
# ==========================================

def test_auth_home(auth_client):
    response = auth_client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Authentication Service!" in response.data

def test_generate_token(auth_client):
    response = auth_client.post(
        "/generate_token", json={"email": ADMIN_EMAIL, "role": "Admin"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data

def test_generate_token_missing_fields(auth_client):
    response = auth_client.post("/generate_token", json={"email": ADMIN_EMAIL})
    assert response.status_code == 400
    data = response.get_json()
    assert data["message"] == "Email and role are required"

def test_validate_token(auth_client):
    token = generate_token(ADMIN_EMAIL, "Admin")
    response = auth_client.get(
        "/validate", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == ADMIN_EMAIL
    assert data["role"] == "Admin"

def test_validate_token_invalid(auth_client):
    response = auth_client.get("/validate", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    assert response.get_json()["message"] == "Invalid token"

# ==========================================
# TESTS FOR USER SERVICE
# ==========================================

def test_user_home(user_client):
    response = user_client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the User Service!" in response.data

def test_register_user(user_client):
    response = user_client.post(
        "/register",
        json={"name": "Test User", "email": USER_EMAIL, "password": USER_PASSWORD, "role": "User"},
    )
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"

def test_register_duplicate_user(user_client):
    response = user_client.post(
        "/register",
        json={"name": "Test User", "email": USER_EMAIL, "password": USER_PASSWORD, "role": "User"},
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "User already exists"

def test_login_user(user_client):
    response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_login_invalid_credentials(user_client):
    response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": "wrongpass"}
    )
    assert response.status_code == 401
    assert response.get_json()["message"] == "Invalid email or password"

def test_profile_user(user_client):
    # Ensure master admin account exists
    user_client.post(
        "/register",
        json={"name": "Master Admin", "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "role": "Admin"},
    )

    login_response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    token = login_response.get_json()["access_token"]
    response = user_client.get(
        "/profile", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.get_json()["email"] == USER_EMAIL

def test_profile_without_token(user_client):
    response = user_client.get("/profile")
    assert response.status_code == 401
    assert response.get_json()["message"] == "Not logged in or token missing"

# ==========================================
# TESTS FOR DESTINATION SERVICE
# ==========================================

@patch('destination_service.routes.requests.get')
def test_get_destinations_as_user(mock_get, dest_client, user_client):
    # Login as user and fetch token
    login_response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    token = login_response.get_json()["access_token"]

    # Prepare mock responses
    # First, for fetching token from user service
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {'access_token': token}

    # Second, for validating the token
    mock_validate_response = Mock()
    mock_validate_response.status_code = 200
    mock_validate_response.json.return_value = {'email': USER_EMAIL, 'role': 'User'}

    # Set the side effects
    mock_get.side_effect = [mock_token_response, mock_validate_response]

    # Now perform the test
    response = dest_client.get("/destinations")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

@patch('destination_service.routes.requests.get')
def test_get_destinations_without_token(mock_get, dest_client):
    # Simulate failure to fetch token from user service
    mock_token_response = Mock()
    mock_token_response.status_code = 401
    mock_token_response.text = 'Unauthorized'
    mock_get.return_value = mock_token_response

    response = dest_client.get("/destinations")
    assert response.status_code == 401
    assert "Token fetch failed" in response.get_json()["message"]

@patch('destination_service.routes.requests.get')
def test_add_destination_as_admin(mock_get, dest_client, user_client):
    # Ensure master admin account exists
    user_client.post(
        "/register",
        json={"name": "Master Admin", "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD, "role": "Admin"},
    )

    # Login as admin and fetch token
    admin_response = user_client.post(
        "/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    token = admin_response.get_json()["access_token"]

    # Prepare mock responses
    # First, for fetching token from user service
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {'access_token': token}

    # Second, for validating the token
    mock_validate_response = Mock()
    mock_validate_response.status_code = 200
    mock_validate_response.json.return_value = {'email': ADMIN_EMAIL, 'role': 'Admin'}

    # Set the side effects
    mock_get.side_effect = [mock_token_response, mock_validate_response]

    # Now perform the test
    response = dest_client.post(
        "/destinations",
        json={
            "id": "SWZ",
            "name": "Mountain Retreat",
            "description": "A serene mountain retreat.",
            "location": "Switzerland",
            "price_per_night": 200,
        },
    )
    assert response.status_code == 201
    assert response.get_json()["message"] == "Destination added successfully"

@patch('destination_service.routes.requests.get')
def test_add_destination_as_user(mock_get, dest_client, user_client):
    # Login as user and fetch token
    login_response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    token = login_response.get_json()["access_token"]

    # Prepare mock responses
    # First, for fetching token from user service
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {'access_token': token}

    # Second, for validating the token
    mock_validate_response = Mock()
    mock_validate_response.status_code = 200
    mock_validate_response.json.return_value = {'email': USER_EMAIL, 'role': 'User'}

    # Set the side effects
    mock_get.side_effect = [mock_token_response, mock_validate_response]

    # Now perform the test
    response = dest_client.post(
        "/destinations",
        json={
            "id": "SWZ",
            "name": "Mountain Retreat",
            "description": "A serene mountain retreat.",
            "location": "Switzerland",
            "price_per_night": 200,
        },
    )
    assert response.status_code == 403
    assert "Unauthorized action" in response.get_json()["message"]

def test_generate_token_utility():
    token = generate_token(ADMIN_EMAIL, "Admin")
    assert isinstance(token, str)

@patch('destination_service.routes.requests.get')
def test_delete_destination_as_admin(mock_get, dest_client, user_client):
    # Ensure master admin account exists and login
    user_client.post(
        "/register",
        json={
            "name": "Master Admin",
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "role": "Admin",
        },
    )
    admin_response = user_client.post(
        "/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    token = admin_response.get_json()["access_token"]

    # Prepare mock responses for token validation
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {"access_token": token}
    mock_token_response.text = "Success"

    mock_validate_response = Mock()
    mock_validate_response.status_code = 200
    mock_validate_response.json.return_value = {
        "email": ADMIN_EMAIL,
        "role": "Admin",
    }
    mock_validate_response.text = "Success"

    # Since multiple requests.get calls are made, we need to have enough responses
    mock_get.side_effect = [
        # Adding destination
        mock_token_response,      # Fetch token from User Service
        mock_validate_response,   # Validate token with Auth Service
        # Deleting destination
        mock_token_response,      # Fetch token from User Service
        mock_validate_response,   # Validate token with Auth Service
    ]

    # Add a destination first, including the Authorization header
    add_response = dest_client.post(
        "/destinations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": "DEL_DEST",
            "name": "To be deleted",
            "description": "This destination will be deleted.",
            "location": "Nowhere",
            "price_per_night": 0,
        },
    )
    assert add_response.status_code == 201
    assert add_response.get_json()["message"] == "Destination added successfully"

    # Delete the destination, including the Authorization header
    delete_response = dest_client.delete(
        f"/destinations/DEL_DEST",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200
    assert delete_response.get_json()["message"] == "Destination deleted successfully"
    

@patch('destination_service.routes.requests.get')
def test_delete_destination_as_user(mock_get, dest_client, user_client):
    # Login as user and fetch token
    login_response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    token = login_response.get_json()["access_token"]

    # Prepare mock responses
    mock_token_response = Mock()
    mock_token_response.status_code = 200
    mock_token_response.json.return_value = {'access_token': token}

    mock_validate_response = Mock()
    mock_validate_response.status_code = 200
    mock_validate_response.json.return_value = {'email': USER_EMAIL, 'role': 'User'}

    mock_get.side_effect = [mock_token_response, mock_validate_response]

    # Attempt to delete a destination
    response = dest_client.delete("/destinations/SWZ")
    assert response.status_code == 403
    assert "Unauthorized action" in response.get_json()["message"]

def test_register_missing_fields(user_client):
    response = user_client.post(
        "/register",
        json={"name": "Incomplete User", "email": "incomplete@example.com"}
    )
    assert response.status_code == 400
    assert response.get_json()["message"] == "Missing required fields"

def test_register_admin_without_login(user_client):
    response = user_client.post(
        "/register",
        json={"name": "Unauthorized Admin", "email": "unauthadmin@example.com", "password": "adminpass", "role": "Admin"},
    )
    assert response.status_code == 403
    assert response.get_json()["message"] == "Only admins can create admin accounts"
