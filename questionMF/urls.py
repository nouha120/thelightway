from django.urls import path
from questionMF.views import get_quiz_questions, list_submissions, submit_quiz



urlpatterns = [
   path('questions/', get_quiz_questions, name='get_questions'),
   path('submit/', submit_quiz, name='submit_quiz'),
   path('submissions/', list_submissions, name='list_submissions'),


]


