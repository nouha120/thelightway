
from django.db import models
from datetime import date
from users.models import User  
from django.utils import timezone 
class RecoveryProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(default=timezone.now)
    last_relapse_date = models.DateField(null=True, blank=True)
    challenges_completed = models.IntegerField(default=0)
    challenge_start_date = models.DateField(null=True, blank=True)

    def days_without_relapse(self):
        today = timezone.now().date()
        if self.last_relapse_date:
            return (today - self.last_relapse_date).days
        return (today - self.start_date.date()).days

    def __str__(self):
        return f"{self.user.username} - {self.days_without_relapse()} jours propres"
from django.db import models
from users.models import User

class Challenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    scheduled_datetime = models.DateTimeField(null=True, blank=True)  # ⬅️ التاريخ والوقت
    is_completed = models.BooleanField(default=False)
    date_completed = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def is_time_to_notify(self):
        notify_time = self.scheduled_datetime + timezone.timedelta(minutes=15)
        return timezone.now() >= notify_time and not self.is_completed
class Badge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    earned_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.user.username}'
