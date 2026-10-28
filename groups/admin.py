
from django.contrib import admin
from .models import GroupMember,GroupInvitation,Group

# Register your models here.
admin.site.register(GroupMember)
admin.site.register(GroupInvitation)
admin.site.register(Group)