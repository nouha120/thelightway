from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from firebase_admin import auth
from users.models import User


@csrf_exempt
def delete_account(request):
    """Supprimer un compte utilisateur (Firebase et Django)"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "Email requis"}, status=400)

            # Supprimer l'utilisateur de Firebase
            user_firebase = auth.get_user_by_email(email)
            auth.delete_user(user_firebase.uid)

            # Supprimer l'utilisateur en base Django
            user = User.objects.filter(email=email).first()
            if user:
                user.delete()

            return JsonResponse({"message": "Compte supprimé avec succès"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
