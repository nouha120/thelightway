import requests

def get_place_name_from_coordinates(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'TheLightWay-App/1.0'}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get("display_name", "Unknown")
        else:
            return "❌ Nominatim Error"
    except Exception as e:
        return f"❌ Error: {e}"
