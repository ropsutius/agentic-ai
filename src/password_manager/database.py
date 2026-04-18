import json, os
from auth import verify_password

PASSWORD_FILE = 'app_password.json'
USERS_FILE = 'master_login.json'

# Function to read the stored passwords from the file
def read_passwords():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as file:
            return json.load(file)
    return {}

# Function to write the passwords to the file
def write_passwords(username, data):
    app_passwords = read_passwords()

    app_passwords[username] = data

    with open(PASSWORD_FILE, 'w') as file:
        json.dump(app_passwords, file, indent=4)

def register_user(username, password):
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            users = json.load(file)
            users[username] = password
        with open(USERS_FILE, "w") as file:
            json.dump(users, file, indent=4)

def login_user(username, password):
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            users = json.load(file)

            if username in users and verify_password(password, users[username]):
                return True
            else:
                return False