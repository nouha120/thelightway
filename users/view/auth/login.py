from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from firebase_admin import auth
from users.models import User
from rest_framework.decorators import api_view

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from firebase_admin import auth
from users.models import User
from rest_framework.decorators import api_view

@csrf_exempt
@api_view(['POST'])
def login_or_register(request):
    """Inscription et Connexion via Firebase Authentication"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")

            if not token:
                return JsonResponse({"error": "Token is required"}, status=400)

            try:
                decoded_token = auth.verify_id_token(token)  # ✅ التحقق من التوكن
                firebase_uid = decoded_token.get("uid")
                email = decoded_token.get("email", None)

                if not firebase_uid:
                    return JsonResponse({"error": "Invalid Firebase Token"}, status=400)

                # تأمين إنشاء المستخدم حتى لو لم يكن لديه بريد إلكتروني
                user, created = User.objects.get_or_create(
                    firebase_uid=firebase_uid,
                    defaults={
                        "email": email if email else f"user_{firebase_uid}@example.com",
                        "username": f"user_{firebase_uid}"
                    }
                )

                return JsonResponse({
                    "message": "Connexion réussie" if not created else "Inscription réussie",
                    "user_id": user.id,
                    "firebase_uid": user.firebase_uid,
                    "email": user.email,
                }, status=200)

            except auth.InvalidIdTokenError:
                return JsonResponse({"error": "Invalid Firebase Token"}, status=400)
            except auth.ExpiredIdTokenError:
                return JsonResponse({"error": "Expired Firebase Token"}, status=401)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


@csrf_exempt
def login_with_google(request):
    """Connexion avec Google (Authentification via Firebase)"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")  # Jeton ID Firebase Google

            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token["uid"]
            email = decoded_token.get("email", "")

            # Vérifier si l'utilisateur existe déjà
            user = User.objects.filter(firebase_uid=firebase_uid).first()
            if not user:
                return JsonResponse({"error": "Utilisateur non inscrit"}, status=404)

            return JsonResponse({
                "message": "Connexion réussie avec Google",
                "user_id": user.id,
                "firebase_uid": user.firebase_uid,
                "email": user.email
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
