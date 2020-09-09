from rest_framework import serializers
from .models import UserLog


class UserLogSerializer(serializers.ModelSerializer):
    action = serializers.CharField()

    class Meta:
        model = UserLog
        fields = [
            "user",
            "action",
        ]

    def create(self, validated_data):
        user = validated_data["user"]
        action = validated_data["action"]

        user_log = UserLog(user=user, action=action)
        user_log.save()
        return 1