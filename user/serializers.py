from rest_framework import serializers

from .models import User

EXISITING_EMAIL_ERROR = "Email already exists"
from rest_framework.validators import ValidationError


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "fullname",
            "password",
            "username",
            "role",
            "image",
            "engineer_details",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "engineer_details": {"required": False},
            "image": {"required": False},
            "role": {"required": False},
            "username": {"required": False},
            "fullname": {"required": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def validate(self, attrs):
        email_exists = User.objects.filter(email=attrs["email"]).exists()

        if email_exists:
            raise ValidationError(EXISITING_EMAIL_ERROR)

        return super().validate(attrs)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "fullname",
            "username",
            "image",
            "engineer_details",
            "created_at",
            "updated_at",
        ]


class UpdateUserRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "role",
        ]
        extra_kwargs = {
            "role": {"required": True},
        }


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
