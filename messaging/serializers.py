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


class UserMessageCreateSerializer(serializers.ModelSerializer):
    is_deleted = serializers.BooleanField(default=False)

    class Meta:
        model = UserMessage
        fields = [
            "id",
            "messageId",
            "fromId",
            "toId",
            "is_deleted"
        ]

    def create(self, validated_data):
        messageId = validated_data["messageId"]
        fromId = validated_data["fromId"]
        toId = validated_data["toId"]
        userMessage = UserMessage(fromId=fromId, toId=toId, messageId=messageId)
        userMessage.save()
        print(userMessage)
        return 1