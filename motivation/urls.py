from django.urls import path
from .views import daily_motivation

urlpatterns = [
    path("daily/", daily_motivation, name="daily_motivation"),
]
