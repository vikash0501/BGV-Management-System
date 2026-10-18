from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password2 = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'password2',
            'role',
            'phone',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        user = User.objects.create_user(
            **validated_data
        )

        return user

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Custom claims
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        }

        return data

class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'phone',
            'is_active',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'username',
            'role',
            'is_active',
            'date_joined',
        ]

class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        ]
        read_only_fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        ]