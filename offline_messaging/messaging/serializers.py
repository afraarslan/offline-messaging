from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class RegisterSerializer(serializers.HyperlinkedModelSerializer):
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    @property
    def save(self):
        user = User(
            username=self.validated_data['username'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
        )
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']

        if password != confirm_password:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        user.set_password(password)
        user.save()
        return user
