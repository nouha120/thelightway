from django.urls import path

from medical.medicalrecord import save_medical_record
from medical.views import fetch_patient_data, fiche_medicale, get_fiche_medicale,get_medical_questions, save_medical_answers, update_fichier_medical
urlpatterns = [
    path('fiche-medicale/<str:firebase_uid>/', get_fiche_medicale),
    path('fichier_medical/update/<str:user_id>/', update_fichier_medical, name='update-fichier-medical'),
    path('medical-questions/', get_medical_questions),
    path('save-answers/', save_medical_answers),
    path('fiche-medicales/',  fiche_medicale),
    path('fetch-patient/<str:firebase_uid>/', fetch_patient_data, name='fetch_patient_data'),
    path("save-medical-record/", save_medical_record, name="save_medical_record"),
]