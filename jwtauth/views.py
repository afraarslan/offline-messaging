from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import response, decorators, permissions, status, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User, update_last_login
from user_logging.models import UserLog
from messaging.views import IsOwner
from .models import UserBlacklist
from .serializers import UserCreateSerializer, UserSerializer


# Create your views here.


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
    if request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        update_last_login(None, user)
        user_log = UserLog(
            userId=user,
            action="register"
        )
        user_log.save()
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer
        serialized_user = serializer(user)
        res = {
            "user": serialized_user.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return response.Response(res, status.HTTP_201_CREATED)
    return response.Response({'key': 'value'}, status=status.HTTP_200_OK)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def login(request):
    if request.method == "POST":
        if len(request.data) > 1:
            username = request.data['username']
            password = request.data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                update_last_login(None, user)
                serializer = UserSerializer
                serialized_user = serializer(user)
                refresh = RefreshToken.for_user(user)
                res = {
                    "user": serialized_user.data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
                user_log = UserLog(
                    userId=user,
                    action="login"
                )
                user_log.save()
                return response.Response(res, status.HTTP_201_CREATED)
            else:
                return response.Response({'user': 'Not authenticated'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response({'request_data': 'Please fill the required fields'}, status=status.HTTP_400_BAD_REQUEST)
    return response.Response({'key': 'value'}, status=status.HTTP_200_OK)


@decorators.api_view(["POST"])
@decorators.permission_classes([IsOwner, ])
def block_a_user(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            if request.data:
                blocked_user = User.objects.get(pk=request.data['blockedId'])
                if UserBlacklist.objects.filter(userId=user, blockedId=blocked_user).exists():
                    raise serializers.ValidationError(
                        {"blockedUser": "User is already blocked."}
                    )
                blocked_instance = UserBlacklist(userId=user, blockedId=blocked_user)
                blocked_instance.save()
                user_log = UserLog(
                    userId=user,
                    action="block_user"
                )
                user_log.save()
                return response.Response('blocked_instance', status.HTTP_201_CREATED)
            else:
                return response.Response({'blockedId': 'Please give a blockedId'}, status=status.HTTP_400_BAD_REQUEST)
    return response.Response({'key': 'value'}, status=status.HTTP_200_OK)
