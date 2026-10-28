from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def logout(request):
    """Déconnexion utilisateur (Firebase ne gère pas directement la déconnexion côté serveur)"""
    print("Requête de déconnexion reçue")
    return JsonResponse({"message": "Déconnexion réussie (gérée côté client)"}, status=200)
