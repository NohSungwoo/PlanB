from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = "__all__"


class LoginSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password")


class ProfileSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "nickname",
            "gender",
            "birthday",
            "photo",
            "created_at",
        )
