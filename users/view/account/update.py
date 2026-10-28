from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import firebase_admin
from firebase_admin import auth

@csrf_exempt
def update_account(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            current_email = data.get("current_email")
            new_email = data.get("new_email")
            new_password = data.get("new_password")

            if not current_email:
                return JsonResponse({"error": "Email actuel requis"}, status=400)

            # Trouver l'utilisateur Firebase par email
            user = auth.get_user_by_email(current_email)

            # Mettre à jour l'email si fourni
            if new_email:
                auth.update_user(user.uid, email=new_email)

            # Mettre à jour le mot de passe si fourni
            if new_password:
                auth.update_user(user.uid, password=new_password)

            return JsonResponse({"message": "Compte mis à jour avec succès"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
