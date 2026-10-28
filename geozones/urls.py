from django.urls import path

from geozones import views
from geozones import savelocation

urlpatterns = [
    path('predict-and-alert/', views.predict_and_alert),
    path('save-location/', savelocation.save_visited_location),
    path('get-locations/<str:firebase_uid>/', savelocation.get_visited_locations),
]