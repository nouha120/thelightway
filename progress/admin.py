from django.contrib import admin

from progress.models import Badge, Challenge, RecoveryProgress

admin.site.register(RecoveryProgress)
admin.site.register(Challenge)
admin.site.register(Badge)
