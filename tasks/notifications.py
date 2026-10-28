# tasks/notifications.py

import json
import requests
from google.auth.transport.requests import Request
from backend_thelightway.settings import FIREBASE_CREDENTIALS
from google.oauth2 import service_account

def send_push_notification(fcm_token, title, body):
    """Send a push notification using Firebase Cloud Messaging V1 API"""
    try:
        # 🔐 Charger credentials depuis serviceAccountKey
        credentials = service_account.Credentials.from_service_account_file(
            FIREBASE_CREDENTIALS,
            scopes=['https://www.googleapis.com/auth/firebase.messaging']
        )
        credentials.refresh(Request())
        access_token = credentials.token
        project_id = credentials.project_id

        # 📨 Construire le message
        message = {
            "message": {
                "token": fcm_token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }

        # 📤 Envoi via FCM V1 endpoint
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; UTF-8"
        }

        url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

        response = requests.post(url, headers=headers, data=json.dumps(message))
        print(f"🔔 Response: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de la notification: {e}")
