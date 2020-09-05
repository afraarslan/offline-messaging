from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer, RegisterSerializer

# Create your views here.
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@api_view(['POST', ])
def register(request):
    print("kamıller/n")
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        print(request.data)
        data = {}
        if serializer.is_valid():
            user_account = serializer.save
            data['response'] = "Succesfull"
            data['username'] = user_account.username
            data['first_name'] = user_account.first_name
            data['last_name'] = user_account.last_name
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            data = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
    return Response({'key': 'value'})


from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework import response, decorators, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserCreateSerializer

User = get_user_model()

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
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

# @api_view(['POST', ])
# def login(request):
#     if request.method == 'POST':
#         username = request.data['username']
#         password = request.data['password']
#
#         user = authenticate(request=request, username=username, password=password)
#         if user is not None:
#             return Response("Welcome back ", username)
#         else:
#             return Response("Invalid Username or Password. Please make sure you enter them correct")
#     return Response({'key': 'value'})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
