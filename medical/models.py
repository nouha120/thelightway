from django.db import models
from users.models import User  

class MedicalRecord(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, to_field="firebase_uid")
    
    # 🧍 معلومات المستخدم
    firstname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255, blank=True, null=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    birthdate = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    # 👨‍👩‍👧 جهة الطوارئ
    emergency_name = models.CharField(max_length=255, blank=True, null=True)
    emergency_relation = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)

    # 🍷 تاريخ الإدمان
    primary_substance = models.CharField(max_length=100, null=True, blank=True)
    substance_specify = models.CharField(max_length=255, blank=True, null=True)
    age_first_use = models.CharField(max_length=10, blank=True, null=True)
    frequency_of_use = models.CharField(max_length=50, null=True, blank=True)
    last_use_date = models.CharField(max_length=20, blank=True, null=True)
    previous_treatment = models.CharField(max_length=10, null=True, blank=True)

    # 🏥 معلومات طبية
    medical_conditions = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    mental_health_history = models.CharField(max_length=10 ,null=True, blank=True)
    mental_health_specify = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)

    # ⚖️ قضايا قانونية
    legal_issues = models.CharField(max_length=10 ,null=True, blank=True)
    legal_issues_explain = models.TextField(blank=True, null=True)

    # 🏡 الحياة الاجتماعية
    employment_status = models.CharField(max_length=255, default="Employed Full-Time")
    living_situation = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f"{self.user.username}  - Fiche Médicale"
        #return f"{self.user.username} - ({self.user.firebase_uid}) - Fiche Médicale"

class MedicalCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class MedicalQuestion(models.Model):
    category = models.ForeignKey(MedicalCategory, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"{self.category.name} - {self.text[:50]}"
    category = models.ForeignKey(MedicalCategory, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return f"{self.category.name} - {self.text[:50]}"
    
    
class MedicalQuestionAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field="firebase_uid")  # ✅ ForeignKey وليس OneToOneField
    category = models.CharField(max_length=255)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.question[:30]}"

class MedicalFile(models.Model):
    firebase_uid = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    type_of_substance = models.CharField(max_length=255)
    duration_of_use = models.CharField(max_length=255)
    frequency_of_use = models.CharField(max_length=255)
    chronic_diseases = models.TextField(null=True, blank=True)
    mental_health_disorders = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    current_medications = models.TextField(null=True, blank=True)
    family_support = models.BooleanField(default=False)
    employment_status = models.CharField(max_length=255, null=True, blank=True)
    legal_issues = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name