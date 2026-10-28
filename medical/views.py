from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.models import User
from medical.firestorequizrzsult import get_quiz_results, update_quiz_results
from medical.models import MedicalCategory, MedicalQuestionAnswer, MedicalRecord

@api_view(['GET'])
def get_fiche_medicale(request, firebase_uid):
    try:
        # 🔥 Step 1: استرجاع المستخدم
        user = User.objects.get(firebase_uid=firebase_uid)

        # 🔥 Step 2: استرجاع نتائج الكويز من Firestore
        quiz_data = get_quiz_results(firebase_uid)

        if not quiz_data:
            quiz_data = {
                "assessment": "No assessment",
                "score": 0,
                "medical_history": "Not provided",
                "medications": "Not provided",
                "allergies": "Not provided",
            }

        # 🔥 Step 3: استرجاع إجابات الأسئلة الطبية
        answers = MedicalQuestionAnswer.objects.filter(user=user)
        answer_list = [
            {
                "category": a.category,
                "question": a.question,
                "answer": a.answer,
            }
            for a in answers
        ]

        return Response({
            "user_info": {
                "firebase_uid": user.firebase_uid,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "birthdate": str(user.birthdate) if user.birthdate else None,
                "gender": user.get_gender_display() if user.gender else None,
            },
            "quiz_result": {
                "assessment": quiz_data.get("assessment", "No assessment"),
                "total_score": quiz_data.get("score", 0),
                "medical_history": quiz_data.get("medical_history", "Not provided"),
                "medications": quiz_data.get("medications", "Not provided"),
                "allergies": quiz_data.get("allergies", "Not provided"),
            },
            "medical_answers": answer_list,
        })

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
def fiche_medicale(request, firebase_uid):
    try:
        user = User.objects.get(firebase_uid=firebase_uid)
        
        # استرجاع معلومات الكويز
        quiz_result = get_quiz_results(firebase_uid) or {}
        
        # استرجاع الإجابات الطبية
        medical_answers = MedicalQuestionAnswer.objects.filter(user=user)
        
        medical_data = []
        for answer in medical_answers:
            medical_data.append({
                "category": answer.category,
                "question": answer.question,
                "answer": answer.answer,
                "created_at": answer.created_at,
            })

        return Response({
            "user_info": {
                "firebase_uid": user.firebase_uid,
                "username": user.username,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "phone_number": user.phone_number,
                "birthdate": user.birthdate,
                "gender": user.get_gender_display() if user.gender else None,
            },
            "quiz_result": quiz_result,
            "medical_answers": medical_data,
        })

    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

@api_view(['PUT'])
def update_fichier_medical(request, user_id):
    """
    Update quiz_results in Firestore and create/update MedicalRecord in Django.
    """
    try:
        # 🔥 Ensure user exists in Django
        user, _ = User.objects.get_or_create(username=user_id)

        # 🔹 Get data from request body
        data = request.data

        # 🔥 Update Firestore
        success = update_quiz_results(user_id, data)

        # ✅ If Firestore update successful ➔ Update or Create MedicalRecord locally
        if success:
            # 🔥 Extract useful fields from data
            full_name = data.get("full_name", "Unknown Name")
            age = int(data.get("age", 0))
            gender = data.get("gender", "Unknown")
            medical_history = data.get("medical_history", "")
            medications = data.get("medications", "")
            allergies = data.get("allergies", "")

            # 🔥 Create or update the MedicalRecord
            MedicalRecord.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": full_name,
                    "age": age,
                    "gender": gender,
                    "medical_history": medical_history,
                    "medications": medications,
                    "allergies": allergies,
                }
            )

            return Response({"message": "Quiz results and medical record updated successfully.", "updated_data": data})
        else:
            return Response({"error": "Failed to update Firestore."}, status=500)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    


@api_view(['POST'])
def save_medical_answers(request):
    try:
        data = request.data
        print("🟡 Received data:", data)  # DEBUG

        firebase_uid = data.get('firebase_uid')
        answers = data.get('answers', [])

        if not firebase_uid or not answers:
            return Response({"error": "Missing firebase_uid or answers."}, status=400)

        user = User.objects.filter(firebase_uid=firebase_uid).first()
        if not user:
            return Response({"error": "User not found."}, status=404)

        MedicalQuestionAnswer.objects.filter(user=user).delete()

        for entry in answers:
            print("🟢 Saving entry:", entry)  # DEBUG
            MedicalQuestionAnswer.objects.create(
                user=user,
                category=entry.get("category", "Other"),
                question=entry.get("question", ""),
                answer=entry.get("answer", ""),
            )

        return Response({"message": "Medical answers saved successfully."}, status=200)

    except Exception as e:
        import traceback
        print("❌ Exception occurred:", traceback.format_exc())
        return Response({"error": str(e)}, status=500)

    


from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import User
from django.http import JsonResponse

@api_view(['GET'])
def fetch_patient_data(request, firebase_uid):
    try:
        # ✅ نبحث عن المستخدم
        user = User.objects.get(firebase_uid=firebase_uid)

        # ✅ نبحث عن سجله الطبي (MedicalRecord) لو موجود
        medical_record = MedicalRecord.objects.filter(user=user).first()
        raw_quiz_result = get_quiz_results(firebase_uid) or {}

        quiz_result = {
            "assessment": raw_quiz_result.get("assessment", ""),
            "total_score": raw_quiz_result.get("score", 0),
        }


        
        # استرجاع الإجابات الطبية
        medical_answers = MedicalQuestionAnswer.objects.filter(user=user)
        
        medical_data = []
        for answer in medical_answers:
            medical_data.append({
                "category": answer.category,
                "question": answer.question,
                "answer": answer.answer,
            })
        if medical_record is None:
            return JsonResponse({"error": "Medical record not found"}, status=404)

        # ✅ نرجع المعلومات كلها
        data = {
            "first_name": user.firstname or '',
            "middle_name": '',  # لو عندك حقل middle name في User زوده هنا
            "family_name": user.lastname or '',
            "birth_date": str(user.birthdate) if user.birthdate else '',
            "phone_number": user.phone_number or '',
            "email": user.email,
            "address": '',  # إذا عندك حقل Address في User
            "city": '',     # إذا عندك City
            "state": '',    # State
            "zip_code": '', # Zip

            # بيانات الطوارئ Emergency
            "emergency_contact_name": '',
            "emergency_contact_relation": '',
            "emergency_contact_phone": '',

            # بيانات التأمين Insurance
            "insurance_company": '',
            "subscriber_name": '',
            "policy_number": '',
            "group_number": '',

            # استخدام المواد
            "primary_substance": '',
            "substance_specify": '',
            "age_first_use": '',
            "frequency_of_use": '',
            "last_use_date": '',
            "previous_treatment": '',

            # التاريخ الطبي
            "medical_conditions": medical_record.medical_conditions or '',
            "medications": medical_record.medications or '',
            "mental_health_history": '',
            "mental_health_specify": '',
            "allergies": medical_record.allergies or '',

            # التاريخ القانوني
            "legal_issues": '',
            "legal_issues_explain": '',

            # الحالة الاجتماعية
            "employment_status": '',
            "living_situation": '',

            # الجنس
            "gender": user.gender or 'M',  # 'M' or 'F'
            # 🔹 Ajouter les résultats du quiz
            "quiz_result": quiz_result,
            "medical_answers": medical_data,

        }

        return Response(data)

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
# medical-questions    
@api_view(['GET'])
def get_medical_questions(request):
    """
    Return all categories and questions from the database.
    """
    categories = MedicalCategory.objects.all()
    result = []

    for category in categories:
        questions = category.questions.all().values_list('text', flat=True)
        result.append({
            "category_name": category.name,
            "questions": list(questions),
        })

    return Response(result)

