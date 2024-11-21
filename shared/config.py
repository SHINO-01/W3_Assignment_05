import os
import secrets

class Config:
    # Path to store the generated SECRET_KEY
    SECRET_KEY_FILE = 'secret.key'

    if os.path.exists(SECRET_KEY_FILE):
        # Load the existing SECRET_KEY from the file
        with open(SECRET_KEY_FILE, 'r') as f:
            SECRET_KEY = f.read()
    else:
        # Generate a new SECRET_KEY and save it to the file
        SECRET_KEY = secrets.token_urlsafe(32)
        with open(SECRET_KEY_FILE, 'w') as f:
            f.write(SECRET_KEY)
