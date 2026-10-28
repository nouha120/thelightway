from rest_framework import serializers
from .models import RecoveryProgress
from datetime import date, datetime, timezone

class RecoveryProgressSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    last_relapse_date = serializers.SerializerMethodField()
    days_without_relapse = serializers.SerializerMethodField()
    elapsed_time = serializers.SerializerMethodField() 
    challenge_progress_days = serializers.SerializerMethodField()
    challenge_start_date = serializers.SerializerMethodField()
    class Meta:
        model = RecoveryProgress
        fields = ['start_date', 'last_relapse_date', 'challenges_completed', 'days_without_relapse','elapsed_time', 'challenge_progress_days','challenge_start_date', ]

    def get_start_date(self, obj):
        return obj.start_date.isoformat() if obj.start_date else None

    def get_last_relapse_date(self, obj):
        return obj.last_relapse_date.isoformat() if obj.last_relapse_date else None

    def get_days_without_relapse(self, obj):
        if obj.last_relapse_date:
            return (date.today() - obj.last_relapse_date).days
        return (date.today() - obj.start_date.date()).days

    def get_elapsed_time(self, obj):
        now = datetime.now(timezone.utc)
        start = obj.start_date

        # ✅ إذا الانتكاسة حصلت اليوم ⟶ نرجع كل شيء صفر
        if obj.last_relapse_date and obj.last_relapse_date == date.today():
            return {"hours": 0, "minutes": 0, "seconds": 0}

        if not start:
            return {"hours": 0, "minutes": 0, "seconds": 0}

        diff = now - start
        return {
            "hours": diff.seconds // 3600,
            "minutes": (diff.seconds % 3600) // 60,
            "seconds": diff.seconds % 60,
        }
    

    def get_challenge_progress_days(self, obj):
        if obj.challenge_start_date and obj.last_relapse_date != date.today():
            return (date.today() - obj.challenge_start_date).days
        return 0
   
    def get_challenge_start_date(self, obj):
       return obj.challenge_start_date.isoformat() if obj.challenge_start_date else None

