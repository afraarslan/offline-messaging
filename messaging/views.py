from django.shortcuts import render
from rest_framework import viewsets, response, decorators, permissions, status, filters
from .models import Message, UserMessage
from .serializers import MessageSerializer, UserMessageSerializer
from django.contrib.auth.models import User


# Create your views here.

class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class UserMessageViewSet(viewsets.ModelViewSet):
    serializer_class = UserMessageSerializer
    permission_classes = (IsOwner,)

    # Ensure a user sees only own Message objects.
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            msgbox = UserMessage.objects.filter(fromId=user) | UserMessage.objects.filter(toId=user)
            return msgbox
        raise permissions.PermissionDenied()

    # def list(self, request):
    #     user = self.request.user
    #     if user.is_authenticated:
    #         inbox = UserMessage.objects.filter(fromId=user)
    #         sent = UserMessage.objects.filter(toId=user)
    #         serializer1 = self.serializer_class(inbox, many=True)
    #         serializer2 = self.serializer_class(sent, many=True)
    #         serializer_list = [serializer1.data, serializer2.data]
    #         return response.Response(serializer_list)
    #     return permissions.PermissionDenied()

    # Set user as owner of a Message object.
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


