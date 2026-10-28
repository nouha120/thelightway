import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
import requests

API_KEY = os.environ.get("FIREBASE_API_KEY", "")

def get_firebase_token(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json().get("idToken")
    else:
        return response.json()

# Test avec ton email/mot de passe Firebase
email = os.environ.get("FIREBASE_TEST_EMAIL", "")
password = os.environ.get("FIREBASE_TEST_PASSWORD", "")
if __name__ == "__main__":
    token = get_firebase_token(email, password)
    print("Firebase ID Token:", token)
