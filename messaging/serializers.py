from rest_framework import serializers
from .models import Message, UserMessage


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "content", "is_deleted")


class UserMessageSerializer(serializers.ModelSerializer):
    message = MessageSerializer()
    is_deleted = serializers.BooleanField(default=False)

    class Meta:
        model = UserMessage
        fields = [
            "id",
            "message",
            "from_user",
            "to_user",
            "is_deleted"
        ]

    def create(self, validated_data):
        msg_data = validated_data.pop('message')
        message = Message.objects.create(**msg_data)
        user_msg = UserMessage.objects.create(message=message, **validated_data)
        return user_msg


