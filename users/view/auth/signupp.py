from backend_thelightway.settings import firestore_db as db  # ✅ Import correct
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from firebase_admin import auth
from users.models import User
import firebase_admin



@csrf_exempt
def signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            username = data.get("username")
            password = data.get("password")
            confirm_password = data.get("confirm_password")
            
            if not email or not username or not password or not confirm_password:
                return JsonResponse({"error": "All fields are required"}, status=400)

            if password != confirm_password:
                return JsonResponse({"error": "Passwords don't match"}, status=400)

            # ✅ تحقق مما إذا كان المستخدم موجودًا في Firebase
            try:
                user_firebase = auth.get_user_by_email(email)  # 🔍 البحث عن المستخدم في Firebase
            except firebase_admin.auth.UserNotFoundError:
                # 🎯 إذا لم يكن موجودًا، نقوم بإنشائه في Firebase
                user_firebase = auth.create_user(
                    email=email,
                    password=password,
                    display_name=username,
                )

            # ✅ تحقق مما إذا كان المستخدم موجودًا في Django، وإذا لم يكن، أضفه
            user, created = User.objects.get_or_create(
                firebase_uid=user_firebase.uid,
                defaults={
                    "email": email,
                    "username": username,
                    "is_active": True,
                }
            )

            return JsonResponse({"message": "User created successfully", "user_id": user.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid method"}, status=405)

@csrf_exempt
def signup_with_google(request):
    """S'inscrire avec Google (Authentification via Firebase)"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")  # Jeton ID Firebase récupéré après connexion avec Google
            if not token:
                return JsonResponse({"error": "Le token Firebase est requis"}, status=400)

            # 🔹 Vérification du token et récupération des infos utilisateur Firebase
            
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token["uid"]
            email = decoded_token.get("email", "")
            username = decoded_token.get("name", "")

            # Enregistrer ou récupérer l'utilisateur dans la base de données
            user, created = User.objects.get_or_create(
                firebase_uid=firebase_uid,
                defaults={"email": email, "username": username}
            )
            
            if created:  # Ajouter uniquement si c'est un nouvel utilisateur
                user_data = {
                    "username": username,
                    "email": email,
                    "firebase_uid": firebase_uid,
                    "date_inscription": db.SERVER_TIMESTAMP,
                    "is_active": True
                }
                db.collection("users").document(firebase_uid).set(user_data)


            return JsonResponse({
                "message": "Inscription réussie avec Google",
                "user_id": user.id,
                "firebase_uid": user.firebase_uid,
                "email": user.email
            }, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
