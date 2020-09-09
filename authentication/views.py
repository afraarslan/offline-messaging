from django.contrib.auth import authenticate
from rest_framework import response, decorators, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User, update_last_login
from messaging.views import IsOwner
from user_logging.serializers import UserLogSerializer
from .serializers import UserCreateSerializer, UserSerializer, LoginSerializer, BlockSerializer, UserBlackListSerializer


def response_validation_error(error):
    return response.Response(error, status.HTTP_400_BAD_REQUEST)


def response_created(data):
    return response.Response(data, status.HTTP_201_CREATED)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
    if request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return response_validation_error(serializer.errors)

        user = serializer.save()
        update_last_login(None, user)

        log = {
            'user': user.id,
            'action': "register"
        }
        log_serializer = UserLogSerializer(data=log)
        if not log_serializer.is_valid():
            return response_validation_error(log_serializer.errors)
        log_serializer.save()

        refresh = RefreshToken.for_user(user)
        serialized_user = UserSerializer(user)
        data = {
            "user": serialized_user.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return response_created(data)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        data = {'username': username, 'password': password}

        login_serializer = LoginSerializer(data=data)
        if not login_serializer.is_valid():
            return response_validation_error(login_serializer.errors)

        user = authenticate(username=username, password=password)
        if user is None:
            return response_validation_error({'user':"username or password is invalid"})
        else:
            update_last_login(None, user)

            serialized_user = UserSerializer(user)
            refresh = RefreshToken.for_user(user)
            data = {
                "user": serialized_user.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            log = {
                'user': user.id,
                'action': "login"
            }
            log_serializer = UserLogSerializer(data=log)
            if not log_serializer.is_valid():
                return response_validation_error(log_serializer.errors)
            log_serializer.save()

            return response_created(data)


@decorators.api_view(["POST"])
@decorators.permission_classes([IsOwner, ])
def block_a_user(request):
    if request.method == "POST":
        user = request.user
        block = BlockSerializer(data=request.data)

        if not block.is_valid():
            return response_validation_error(block.errors)
        block_user = User.objects.get(pk=request.POST.get('blocked_id'))
        data = {
            'user': user.id,
            'blocked_user': block_user.id
        }

        blocked_serializer = UserBlackListSerializer(data=data)
        if not blocked_serializer.is_valid():
            return response_validation_error(blocked_serializer.errors)
        blocked_serializer.save()

        log = {
            'user': user.id,
            'action': "block"
        }
        log_serializer = UserLogSerializer(data=log)
        if not log_serializer.is_valid():
            return response_validation_error(log_serializer.errors)
        log_serializer.save()

        return response_created({'blocked'})
