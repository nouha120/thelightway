from django.db import models

# Create your models here.

class DangerZone(models.Model):
    id_location = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    risk_level = models.IntegerField(choices=[(1, "Faible"), (2, "Moyen"), (3, "Élevé")])
    
     
    def __str__(self):
        return self.name
