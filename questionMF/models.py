from firebase_admin import db

class QuizManager:
    @staticmethod
    def get_questions():
        ref = db.reference("quiz_questions")
        questions = ref.get()  # Récupérer les questions
        print("Firebase Data:", questions)  # Debug: voir ce que Firebase retourne
        return questions
    @staticmethod
    def save_questions(data):
        ref = db.reference("quiz_questions")
        ref.set(data)  # Stocker les questions


from django.db import models

class Question(models.Model):
    question_text = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.question_text
    
class UserQuizSubmission(models.Model):
    username = models.CharField(max_length=255)
    submitted_answers = models.JSONField()
    total_score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.total_score}"

