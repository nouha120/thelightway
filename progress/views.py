from datetime import date, datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Badge, Challenge, RecoveryProgress
from users.models import User 
from .serializers import RecoveryProgressSerializer

class RecoveryProgressByUIDView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        if not firebase_uid:
            return Response({"error": "Missing firebase_uid"}, status=400)

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        try:
            progress = RecoveryProgress.objects.get(user=user)
        except RecoveryProgress.DoesNotExist:
            return Response({"error": "Recovery not started"}, status=404)

        # ✅ منح الشارات تلقائيًا
        self.award_badges_if_needed(user, progress)

        # ✅ إرجاع البيانات + الشارات
        serializer = RecoveryProgressSerializer(progress)
        badges = Badge.objects.filter(user=user).values("name", "description", "earned_date")

        return Response({
            **serializer.data,
            "badges": list(badges)  # ✅ إرجاع قائمة الشارات
        })

    def award_badges_if_needed(self, user, progress):
        days_clean = progress.days_without_relapse()

        badges = {
            3: "3 Days Clean",
            7: "1 Week Strong",
            14: "2 Weeks Champion",
            30: "1 Month Survivor",
            90: "Quarter Hero",
            180: "Half-Year Fighter",
        }

        for days_required, badge_name in badges.items():
            if days_clean >= days_required:
                if not Badge.objects.filter(user=user, name=badge_name).exists():
                    Badge.objects.create(
                        user=user,
                        name=badge_name,
                        description=f"Stayed clean for {days_required} days!"
                    )

class StartRecoveryView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        if not firebase_uid:
            return Response({"error": "Missing firebase_uid"}, status=400)

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if RecoveryProgress.objects.filter(user=user).exists():
            return Response({"error": "Recovery already started"}, status=400)

        progress = RecoveryProgress.objects.create(user=user)
        return Response({"message": "Recovery started"}, status=201)

class RelapseView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")

        if not firebase_uid:
            return Response({"error": "Missing firebase_uid"}, status=400)

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        progress, created = RecoveryProgress.objects.get_or_create(user=user)

        # ✅ تحديث تاريخ الانتكاسة + إعادة التحديات
        progress.last_relapse_date = date.today()
        progress.challenges_completed = 0
        progress.start_date = date.today()  # إعادة ضبط اليوم الأول إذا رغبت
        progress.save()

        return Response({"message": "Relapse recorded and progress reset."}, status=200)

class CompleteChallengeView(APIView):    
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        challenge_id = request.data.get("challenge_id")

        if not firebase_uid or not challenge_id:
            return Response({"error": "firebase_uid and challenge_id are required"}, status=400)

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        try:
            challenge = Challenge.objects.get(id=challenge_id, user=user)
        except Challenge.DoesNotExist:
            return Response({"error": "Challenge not found"}, status=404)

        if not challenge.is_completed:
            challenge.is_completed = True
            challenge.date_completed = date.today()
            challenge.save()

            progress, created = RecoveryProgress.objects.get_or_create(user=user)
            progress.challenges_completed += 1
            progress.save()

            # ✅ منح الشارات بناءً على الأيام النظيفة
            self.award_badges_if_needed(user, progress)

        return Response({"message": "Challenge marked as completed."})

    def award_badges_if_needed(self, user, progress):
        days_clean = progress.days_without_relapse()

        badges = {
            3: "3 Days Clean",
            7: "1 Week Strong",
            14: "2 Weeks Champion",
            30: "1 Month Survivor",
            90: "Quarter Hero",
            180: "Half-Year Fighter",
        }

        for days_required, badge_name in badges.items():
            if days_clean >= days_required:
                if not Badge.objects.filter(user=user, name=badge_name).exists():
                    Badge.objects.create(
                        user=user,
                        name=badge_name,
                        description=f"Stayed clean for {days_required} days!"
                    )

            days_clean = progress.days_without_relapse()

            badges = {
                3: "3 Days Clean",
                7: "1 Week Strong",
                14: "2 Weeks Champion",
                30: "1 Month Survivor",
                90: "Quarter Hero",
                180: "Half-Year Fighter",
            }

            for days_required, badge_name in badges.items():
                if days_clean >= days_required:
                    if not Badge.objects.filter(user=user, name=badge_name).exists():
                        Badge.objects.create(
                            user=user,
                            name=badge_name,
                            description=f"Stayed clean for {days_required} days!"
                        )

class StartChallengeView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        if not firebase_uid:
            return Response({"error": "Missing firebase_uid"}, status=400)

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
            progress, _ = RecoveryProgress.objects.get_or_create(user=user)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        progress.challenge_start_date = date.today()
        progress.save()

        return Response({"message": "Challenge started", "start_date": progress.challenge_start_date})

class MyChallengesView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        if not firebase_uid:
            return Response({"error": "firebase_uid is required"}, status=400)

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        challenges = Challenge.objects.filter(user=user)
        data = [{
            "title": c.title,
            "is_completed": c.is_completed,
            "date_completed": c.date_completed,
            "scheduled_datetime": c.scheduled_datetime.isoformat() if c.scheduled_datetime else None
        } for c in challenges]

        return Response(data, status=200)

class CreateChallengeView(APIView):
    def post(self, request):
        firebase_uid = request.data.get("firebase_uid")
        title = request.data.get("title")
        scheduled_datetime = request.data.get("scheduled_datetime")  # ⬅️ وقت التنفيذ

        if not firebase_uid or not title or not scheduled_datetime:
            return Response({"error": "Missing data"}, status=400)

        try:
            user = User.objects.get(firebase_uid=firebase_uid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        try:
            scheduled = datetime.fromisoformat(scheduled_datetime)
        except Exception:
            return Response({"error": "Invalid datetime format"}, status=400)

        challenge = Challenge.objects.create(
            user=user,
            title=title,
            scheduled_datetime=scheduled
        )
        return Response({
            "message": "Challenge created",
            "challenge": {
                "id": challenge.id,
                "title": challenge.title,
                "scheduled_datetime": challenge.scheduled_datetime.isoformat()
            }
        }, status=201)
        
        
        
