# tasks/apps.py
from django.apps import AppConfig
import os

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'

    def ready(self):
        # Local startup must not send reminders to existing Firebase users.
        if os.environ.get('ENABLE_TASK_REMINDERS') != '1':
            return
        from tasks import scheduler
        scheduler.start()
