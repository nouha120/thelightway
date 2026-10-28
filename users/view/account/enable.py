from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from firebase_admin import auth
from users.models import User

@csrf_exempt
def enable_account(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "Email requis"}, status=400)

            # استرجاع المستخدم من Firebase
            user_firebase = auth.get_user_by_email(email)
            auth.update_user(user_firebase.uid, disabled=False)

            # تفعيل المستخدم في قاعدة بيانات Django
            user = User.objects.filter(email=email).first()
            if user:
                user.is_active = True
                user.save()

            return JsonResponse({"message": "Compte réactivé avec succès"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
