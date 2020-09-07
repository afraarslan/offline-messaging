from django.shortcuts import render
from rest_framework import serializers, response, decorators, permissions, status

from jwtauth.models import UserBlacklist
from user_logging.models import UserLog
from .models import Message, UserMessage
from .serializers import MessageSerializer, UserMessageSerializer, UserMessageCreateSerializer
from django.contrib.auth.models import User


# Create your views here.

class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


@decorators.api_view(["GET"])
@decorators.permission_classes([IsOwner, ])
def get_inbox_messages(request):
    user = request.user
    if user.is_authenticated:
        msgbox = UserMessage.objects.filter(toId=user)
        serializer = UserMessageSerializer(msgbox, many=True)
        user_log = UserLog(
            userId=user,
            action="get_inbox"
        )
        user_log.save()
        return response.Response(serializer.data, status.HTTP_201_CREATED)
    return response.Response({'key': 'value'}, status=status.HTTP_200_OK)


@decorators.api_view(["GET"])
@decorators.permission_classes([IsOwner, ])
def get_sent_messages(request):
    user = request.user
    if user.is_authenticated:
        msgbox = UserMessage.objects.filter(fromId=user)
        serializer = UserMessageSerializer(msgbox, many=True)
        # if not serializer.is_valid():
        #     return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        user_log = UserLog(
            userId=user,
            action="get_sent"
        )
        user_log.save()
        return response.Response(serializer.data, status.HTTP_201_CREATED)
    return response.Response({'key': 'value'}, status=status.HTTP_200_OK)


@decorators.api_view(["POST"])
@decorators.permission_classes([IsOwner, ])
def send_message(request):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            username = request.data['to_user']
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError(
                    {"userid": "User should be exist."}
                )
            toUser = User.objects.get(username=username)
            if UserBlacklist.objects.filter(userId=toUser, blockedId=user).exists():
                raise serializers.ValidationError(
                    {"user": "You are blocked. You cannot send a message."}
                )
            newMessage = Message(content=request.data['text'])
            newMessage.save()
            data = {
                'fromId': user.id,
                'toId': toUser.id,
                'messageId': newMessage.id
            }
            serializer = UserMessageCreateSerializer(data=data)
            if not serializer.is_valid():
                return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
            userMessage = serializer.save()
            user_log = UserLog(
                userId=user,
                action="send_message"
            )
            user_log.save()
            return response.Response(userMessage, status.HTTP_201_CREATED)
    return response.Response({'key': 'value'}, status=status.HTTP_200_OK)


