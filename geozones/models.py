from django.db import models

class VisitedLocation(models.Model):
    firebase_uid = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    place_name = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.place_name} at {self.timestamp}"
