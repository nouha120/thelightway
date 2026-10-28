from django.db import models
from backend_thelightway.settings import firestore_db as db 
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
]
class User(models.Model):
    id = models.AutoField(primary_key=True)
    firebase_uid = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True) 
    lastname = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    avatar = models.URLField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)  # ✅ جديد
    city = models.CharField(max_length=100, blank=True, null=True)      # ✅ جديد
    state = models.CharField(max_length=100, blank=True, null=True)     # ✅ جديد
    zip_code = models.CharField(max_length=20, blank=True, null=True)   # ✅ جديد
    date_inscription = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save_to_firestore(self):
        """Ajoute l'utilisateur à Firestore après sa création"""
        user_data = {
            "id_user": self.id,
            "firebase_uid": self.firebase_uid,
            "username": self.username,
            "firstname": self.firstname,
            "middle_name": self.middle_name,   # ✅ ajouté
            "lastname": self.lastname,
            "email": self.email,
            "phone_number": self.phone_number,
            "birthdate": str(self.birthdate) if self.birthdate else None,
            "gender": self.get_gender_display() if self.gender else None,
            "avatar": self.avatar,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "date_inscription": self.date_inscription,
            "is_active": self.is_active,
        }
        db.collection("users").document(self.firebase_uid).set(user_data)
    def __str__(self):
        return self.username


