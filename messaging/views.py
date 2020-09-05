from django.shortcuts import render
from rest_framework import viewsets, response, decorators, permissions, status
from .models import Message, UserMessage
from .serializers import MessageSerializer, UserMessageSerializer
from django.contrib.auth.models import User


# Create your views here.

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class UserMessageViewSet(viewsets.ModelViewSet):
    serializer_class = UserMessageSerializer
    permission_classes = (IsOwner,)

    # Ensure a user sees only own Message objects.
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            msg = UserMessage.objects.filter(fromId=user)
            return msg
        raise permissions.PermissionDenied()

    # Set user as owner of a Message object.
    def perform_create(self, serializer):
        serializer.save(fromId=self.request.user)
        