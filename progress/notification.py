import requests

def send_notification_to_user(user, title, body):
    token = user.firebase_token  
    if token:
        payload = {
            "to": token,
            "notification": {
                "title": title,
                "body": body,
            }
        }
        headers = {
            "Authorization": "key=YOUR_FIREBASE_SERVER_KEY",
            "Content-Type": "application/json"
        }
        requests.post("https://fcm.googleapis.com/fcm/send", json=payload, headers=headers)
