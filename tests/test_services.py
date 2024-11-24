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
import sys
import os

# Dynamically add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


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
    login_response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    token = login_response.get_json()["access_token"]
    response = user_client.get(
        "/profile", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.get_json()["email"] == USER_EMAIL


# ==========================================
# TESTS FOR DESTINATION SERVICE
# ==========================================

def test_dest_home(dest_client):
    response = dest_client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Destination Service!" in response.data


def test_get_destinations_as_user(dest_client, user_client):
    # Login as user and fetch token
    login_response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    token = login_response.get_json()["access_token"]

    response = dest_client.get(
        "/destinations", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_add_destination_as_admin(dest_client, user_client):
    # Login as admin and fetch token
    admin_response = user_client.post(
        "/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    token = admin_response.get_json()["access_token"]

    response = dest_client.post(
        "/destinations",
        headers={"Authorization": f"Bearer {token}"},
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


def test_add_destination_as_user(dest_client, user_client):
    # Login as user and fetch token
    login_response = user_client.post(
        "/login", json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )
    token = login_response.get_json()["access_token"]

    response = dest_client.post(
        "/destinations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": "SWZ",
            "name": "Mountain Retreat",
            "description": "A serene mountain retreat.",
            "location": "Switzerland",
            "price_per_night": 200,
        },
    )
    assert response.status_code == 403
    assert response.get_json()["message"] == "Unauthorized action: Admins only"
