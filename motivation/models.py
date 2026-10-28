from django.db import models

class MotivationMessage(models.Model):
    message = models.TextField()
    image_url = models.CharField(
        max_length=255, 
        default="/media/motivation/default.jpg"  # Image par défaut
    )
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.message}"
