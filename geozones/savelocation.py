from geozones.placename import get_place_name_from_coordinates
from .models import VisitedLocation
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def save_visited_location(request):
    data = request.data
    firebase_uid = data.get('firebase_uid')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    place_name = get_place_name_from_coordinates(latitude,longitude)

    if not firebase_uid or not latitude or not longitude:
        return Response({"error": "Missing required fields"}, status=400)

    location = VisitedLocation.objects.create(
        firebase_uid=firebase_uid,
        latitude=latitude,
        longitude=longitude,
        place_name=place_name
    )

    return Response({
        "message": "Location saved successfully",
        "location_id": location.id
    })

@api_view(['GET'])
def get_visited_locations(request, firebase_uid):
    locations = VisitedLocation.objects.filter(firebase_uid=firebase_uid).order_by('-timestamp')

    data = [{
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'place_name': loc.place_name,
        "timestamp": loc.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
    } for loc in locations]

    return Response(data)

@api_view(['GET'])
def get_user_locations(request, firebase_uid):
    locations = VisitedLocation.objects.filter(firebase_uid=firebase_uid).order_by('-timestamp')
    data = [
        {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "place_name": loc.place_name,
            "timestamp": loc.timestamp.strftime("%Y-%m-%d %H:%M")
        }
        for loc in locations
    ]
    return Response(data)
