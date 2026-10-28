from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from firebase_admin import auth

@csrf_exempt
def reset_password(request):
    """Envoyer un email de réinitialisation de mot de passe via Firebase"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "Email requis"}, status=400)

            # Envoyer un email de réinitialisation via Firebase
            auth.generate_password_reset_link(email)

            return JsonResponse({"message": "Email de réinitialisation envoyé"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
