from datetime import timedelta
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .motivation_data import MOTIVATION_MESSAGES
from backend_thelightway.settings import firestore_db as db
import logging

logger = logging.getLogger(__name__)

@api_view(["GET"])
def daily_motivation(request):
    """Affiche la motivation du jour et tous les messages précédents depuis l'inscription"""
    try:
        firebase_uid = request.GET.get("firebase_uid")

        if not firebase_uid:
            logger.error("🔥 Firebase UID is missing!")
            return Response({"error": "Firebase UID is required"}, status=400)

        # 🔥 Récupérer l'utilisateur Firestore
        user_ref = db.collection("users").document(firebase_uid).get()
        
        if not user_ref.exists:
            logger.error(f"❌ User not found in Firestore for UID: {firebase_uid}")
            return Response({"error": "User not found in Firestore"}, status=404)

        user_data = user_ref.to_dict()
        signup_date_value = user_data.get("date_inscription")

        if not signup_date_value:
            logger.error(f"❌ Missing signup date for user: {firebase_uid}")
            return Response({"error": "Missing signup date"}, status=400)

        # ✅ Convertir proprement la date sans timezone
        signup_date = signup_date_value.replace(tzinfo=None).date()

        today = now().date()
        days_since_signup = (today - signup_date).days

        # 🔥 **Message du jour**
        motivation_index_today = days_since_signup % len(MOTIVATION_MESSAGES)
        today_message = {
            "date": today.strftime("%Y-%m-%d"),
            "message": MOTIVATION_MESSAGES[motivation_index_today],
            "image_url": "/media/motivation/default.jpg"
        }

        # 🔥 **Tous les messages précédents**
        previous_messages = []
        for i in range(1, days_since_signup + 1):  # 🔥 Inclure tous les jours précédents
            previous_date = today - timedelta(days=i)
            motivation_index_previous = (days_since_signup - i) % len(MOTIVATION_MESSAGES)
            previous_messages.append({
                "date": previous_date.strftime("%Y-%m-%d"),
                "message": MOTIVATION_MESSAGES[motivation_index_previous]
            })

        logger.info(f"✅ Motivation sent to {firebase_uid}: {today_message['message']} (Signup: {signup_date})")

        return Response({
            "today": today_message,
            "previous": previous_messages  # ✅ Tous les messages précédents
        })
    
    except Exception as e:
        logger.exception(f"🚨 Unexpected error in daily_motivation: {e}")
        return Response({"error": "Internal Server Error"}, status=500)
