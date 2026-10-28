from django.db import models
from users.models import User
# Create your models here.
from django.db import models

class Community(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    firebase_uid = models.CharField(max_length=255, null=True, blank=True) 
    #community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="posts")
    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Post #{self.id} by UID {self.firebase_uid}"

class Comment(models.Model):
    firebase_uid = models.CharField(max_length=255)  # UID المستخدم من Firebase
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")  # ربط مع المنشورات
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.firebase_uid} on {self.post.id}"
    
class Like(models.Model):
    firebase_uid = models.CharField(max_length=255)  # UID المستخدم من Firebase
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")  # ربط الإعجاب بالمنشور
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('firebase_uid', 'post')  # ✅ منع المستخدم من الإعجاب بنفس المنشور أكثر من مرة

    def __str__(self):
        return f"Like by {self.firebase_uid} on post {self.post.id}"
    
class Notification(models.Model):
    firebase_uid = models.CharField(max_length=255)  # المستخدم الذي سيستلم الإشعار
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    sender_uid = models.CharField(max_length=255, null=True, blank=True)  # من أرسل الإشعار
    message = models.TextField()  # نص الإشعار
    is_read = models.BooleanField(default=False)  # حالة قراءة الإشعار
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.firebase_uid} - {self.message}"
    
class Follow(models.Model):
    follower_uid = models.CharField(max_length=255)  # المستخدم الذي يقوم بالمتابعة
    following_uid = models.CharField(max_length=255)  # المستخدم الذي يتم متابعته
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower_uid', 'following_uid')  # ✅ منع المتابعة المكررة

    def __str__(self):
        return f"{self.follower_uid} follows {self.following_uid}"
    
class Reaction(models.Model):
    firebase_uid = models.CharField(max_length=255)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    emoji = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
