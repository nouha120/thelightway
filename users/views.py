
# Create your views here.
from django.http import JsonResponse
import requests

def get_relapse_prediction(request):
    response = requests.get("http://127.0.0.1:8001/predict-relapse/")
    return JsonResponse(response.json())




