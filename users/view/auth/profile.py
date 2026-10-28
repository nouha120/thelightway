
from django.http import JsonResponse
from backend_thelightway.settings import firestore_db
from django.views.decorators.csrf import csrf_exempt
import json
from questionMF.models import UserQuizSubmission
from users.models import User
import time

@csrf_exempt
def get_user_profile(request):
    """Récupérer le profil utilisateur en vérifiant Firestore en cas d'absence dans Django"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            firebase_uid = data.get("firebase_uid")

            # 🔄 1️⃣ **Tenter de récupérer l'utilisateur dans Django**
            user = User.objects.filter(firebase_uid=firebase_uid).first()

            if not user:
                # 🔄 2️⃣ **Attendre et réessayer pour permettre la synchronisation**
                time.sleep(2)
                user = User.objects.filter(firebase_uid=firebase_uid).first()

            if not user:
                return JsonResponse({"error": "Utilisateur non trouvé"}, status=404)

            # ✅ **L'utilisateur est trouvé, on prépare la réponse**
            phone_number = user.phone_number
            if phone_number and phone_number.startswith('+216'):
                phone_number = phone_number[4:]

            return JsonResponse({
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "avatar": user.avatar,
                "date_inscription": user.date_inscription.strftime("%Y-%m-%d %H:%M:%S"),
                "phone_number": phone_number if phone_number else None,
                "birthdate": user.birthdate.strftime("%Y-%m-%d") if user.birthdate else None,
                "gender": user.get_gender_display() if user.gender else None,
                "address": user.address if user.address else None,        # ✅
                "city": user.city if user.city else None,                 # ✅
                "state": user.state if user.state else None,              # ✅
                "zip_code": user.zip_code if user.zip_code else None,     # 
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


@csrf_exempt
def update_user_profile(request):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            firebase_uid = data.get("firebase_uid")
            user = User.objects.get(firebase_uid=firebase_uid)

            # Mise à jour des champs
            for field in ["username", "lastname", "firstname", "phone_number", "birthdate", "gender", "avatar", "address", "city", "state", "zip_code"]:
                if field in data:
                    setattr(user, field, data[field])

            user.save()
            user.save_to_firestore()

            # ✅ Mise à jour de UserQuizSubmission (Django DB)
            UserQuizSubmission.objects.filter(username=user.username).update(username=user.username)

            # ✅ Mise à jour de Firestore quiz_results
            quiz_results_ref = firestore_db.collection("quiz_results").document(firebase_uid)
            if quiz_results_ref.get().exists:
                quiz_results_ref.update({
                    "username": user.username
                })

            return JsonResponse({"success": "Profile updated successfully"}, status=200)

        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"error": "Method not allowed"}, status=405)
