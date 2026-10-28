from django.contrib import admin

# Register your models here.
from .models import Community, Post, Comment, Like, Notification, Follow, Reaction

admin.site.register(Community)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Notification)
admin.site.register(Follow)
admin.site.register(Reaction)