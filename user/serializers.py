from rest_framework import serializers

from .models import User

EXISITING_EMAIL_ERROR = "Email already exists"
from rest_framework.validators import ValidationError


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True, required=True)

    class Meta:
        model = User
        fields = '__all__'

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

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        user = super().update(instance, validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
