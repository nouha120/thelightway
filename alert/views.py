from django.http import JsonResponse
from .models import DangerZone

def get_danger_zones(request):
    """Retourne la liste des zones à risque"""
    zones = DangerZone.objects.all().values("name", "latitude", "longitude", "risk_level")
    return JsonResponse(list(zones), safe=False)
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from geopy.distance import geodesic
from .models import DangerZone

@csrf_exempt
def check_user_location(request):
    """Vérifie si l'utilisateur est dans une zone à risque"""
    if request.method == "POST":
        data = json.loads(request.body)
        user_lat = data.get("latitude")
        user_lon = data.get("longitude")

        danger_zones = DangerZone.objects.all()
        for zone in danger_zones:
            zone_coords = (zone.latitude, zone.longitude)
            user_coords = (user_lat, user_lon)
            distance = geodesic(zone_coords, user_coords).meters
            
            if distance < 100:  # Seuil de 100 mètres
                return JsonResponse({"alert": True, "zone": zone.name, "risk_level": zone.risk_level}, status=200)

        return JsonResponse({"alert": False}, status=200)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
