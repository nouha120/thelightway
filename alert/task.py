import requests
import firebase_admin
from firebase_admin import firestore

db = firestore.client()
GOOGLE_PLACES_API_KEY = "VOTRE_CLÉ_API"

def fetch_risk_zones():
    """Récupère les zones à risque depuis Google Places API et les stocke dans Firebase."""
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=48.8566,2.3522&radius=5000&type=bar&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url)
    data = response.json()

    for place in data.get("results", []):
        place_id = place["place_id"]
        name = place["name"]
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]

        db.collection("risk_zones").document(place_id).set({
            "name": name,
            "latitude": lat,
            "longitude": lng,
            "risk_level": "élevé",
            "source": "Google Places"
        })

    return "Zones mises à jour"
