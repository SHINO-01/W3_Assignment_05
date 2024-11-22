from werkzeug.security import generate_password_hash

# In-memory storage for user data
users = {
    # Predefined Master Admin record
    "masteradmin@example.com": {
        "name": "Master Admin",
        "email": "masteradmin@example.com",
        "password": generate_password_hash("Master@123"),  # Use a secure password
        "role": "Admin"
    }
}