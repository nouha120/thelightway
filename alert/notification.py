import firebase_admin
from firebase_admin import messaging

def send_alert_notification(user_token, zone_name):
    """Envoie une notification push lorsqu'un utilisateur entre dans une zone à risque"""
    message = messaging.Message(
        notification=messaging.Notification(
            title="⚠️ Zone à risque détectée !",
            body=f"Vous êtes entré dans une zone à risque : {zone_name}. Restez vigilant !"
        ),
        token=user_token
    )
    messaging.send(message)
