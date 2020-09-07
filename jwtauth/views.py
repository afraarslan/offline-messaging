from django.shortcuts import render
from rest_framework import response, decorators, permissions, status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

from messaging.views import IsOwner
from .models import UserBlacklist
from .serializers import UserCreateSerializer


# Create your views here.


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
    serializer = UserCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    res = {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
    return response.Response(res, status.HTTP_201_CREATED)


@decorators.api_view(["POST"])
@decorators.permission_classes([IsOwner, ])
def block_a_user(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            blocked_user = User.objects.get(pk=request.data['blockedId'])
            if UserBlacklist.objects.filter(userId=user, blockedId=blocked_user).exists():
                raise serializers.ValidationError(
                    {"blockedUser": "User is already blocked."}
                )
            blocked_instance = UserBlacklist(userId=user, blockedId=blocked_user)
            blocked_instance.save()
            return response.Response('blocked_instance', status.HTTP_201_CREATED)
    return response.Response({'key': 'value'}, status=status.HTTP_200_OK)
