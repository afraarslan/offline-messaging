from rest_framework import serializers
from .models import Message, UserMessage


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "content", "is_deleted")


class UserMessageSerializer(serializers.ModelSerializer):
    messageId = MessageSerializer()

    class Meta:
        model = UserMessage
        fields = ("id", "messageId", "fromId", "toId", "is_deleted")
