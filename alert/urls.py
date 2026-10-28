from django.urls import path

from alert.ml import detect_new_risky_zones
from alert.notification import send_alert_notification
from alert.views import check_user_location, get_danger_zones

urlpatterns = [
    path("zones/", get_danger_zones, name="get_danger_zones"),
    path("check-location/", check_user_location, name="check_user_location"),
    path("detect-risk/", detect_new_risky_zones, name="detect_new_risky_zones"),
    path("sendnotification/",send_alert_notification,name="send_alert_notification")
]
