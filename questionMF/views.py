
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Question, QuizManager, UserQuizSubmission
from rest_framework.response import Response
from firebase_admin import firestore

@api_view(['GET'])
def get_quiz_questions(request):
    questions = Question.objects.all()
    serialized_questions = []
    for q in questions:
        serialized_questions.append({
            "question": q.question_text,
            "options": q.options,
        })
    return Response({"quiz_questions": serialized_questions})
@api_view(['POST'])
def submit_quiz(request):
    try:
        username = request.data.get('username', 'anonymous')
        user_id = request.data.get('user_id', '')  # UID من Firebase
        email = request.data.get('email', '')
        user_answers = request.data.get('answers', {})

        questions = Question.objects.all()
        total_score = 0
        quiz_details = []

        for question in questions:
            question_text = question.question_text
            options = question.options
            user_answer = user_answers.get(question_text, "")

            quiz_details.append({
                "question": question_text,
                "options": options,
                "user_answer": user_answer
            })

            if user_answer and user_answer in options:
                total_score += options[user_answer]

        # Enregistrement local
        UserQuizSubmission.objects.create(
            username=username,
            submitted_answers=user_answers,
            total_score=total_score
        )

        # Enregistrement dans Firestore
        firestore_db = firestore.client()

        firestore_db.collection('quiz_results').add({
            'username': username,
            'user_id': user_id,
            'email': email,
            'score': total_score,
            'assessment': evaluate_score(total_score),
            'timestamp': firestore.SERVER_TIMESTAMP,
            'answers': quiz_details,  # هذا يحتوي على تفاصيل الأسئلة مع الإجابات
            'submitted_answers': user_answers 
        })

        return Response({
            "total_score": total_score,
            "assessment": evaluate_score(total_score),
            "details": quiz_details
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

def evaluate_score(score):
    if score <= 10:
        return "Faible addiction"
    elif score <= 20:
        return "Addiction modérée"
    else:
        return "Addiction sévère"

@api_view(['GET'])
def list_submissions(request):
    submissions = UserQuizSubmission.objects.all().order_by('-submitted_at')
    data = [
        {
            "username": sub.username,
            "total_score": sub.total_score,
            "submitted_at": sub.submitted_at,
        }
        for sub in submissions
    ]
    return Response(data)

