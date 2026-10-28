from rest_framework import serializers
from .models import MotivationMessage

class MotivationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotivationMessage
        fields = ["date", "message", "image_url"]
