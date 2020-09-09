from django.contrib.auth import get_user_model
from rest_framework import serializers
from authentication.models import UserBlacklist

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'last_login', 'date_joined']


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True, required=True)
    username = serializers.CharField(style={"input_type": "text"}, required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password"
        ]


class BlockSerializer(serializers.ModelSerializer):
    blocked_id = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = [
            "blocked_id"
        ]

    def validate(self, data):
        if not User.objects.filter(pk=data['blocked_id']).exists():
            raise serializers.ValidationError({'blocked_id': 'not exists'})
        return User.objects.get(pk=data['blocked_id'])


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True, required=True)
    password2 = serializers.CharField(
        style={"input_type": "password"}, write_only=True, label="Confirm password")

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]
        password2 = validated_data["password2"]
        if password != password2:
            raise serializers.ValidationError(
                {"password": "Passwords should be same."})
        user = User(username=username)
        user.set_password(password)
        user.save()
        return user


class UserBlackListSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserBlacklist
        fields = [
            "user",
            "blocked_user"
        ]

    def create(self, validated_data):
        user = validated_data["user"]
        blocked_user = validated_data["blocked_user"]
        if UserBlacklist.objects.filter(user=user, blocked_user=blocked_user).exists():
            raise serializers.ValidationError({'blocked_id': 'already blocked'})

        user = UserBlacklist(user=user, blocked_user=blocked_user)
        user.save()
        return user
