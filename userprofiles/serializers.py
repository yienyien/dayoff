from django.contrib.auth.models import User
from rest_framework import serializers
from . import models
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for a native django user object
    """

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password")
        extra_kwargs = {"password": {"write_only": True}}


class TeamSerializer(serializers.ModelSerializer):
    """
    Team serializer
    """

    class Meta:
        model = models.Team


class PublicProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = models.UserProfile
        fields = ("uid", "first_name", "last_name", "email", "team")
        extra_kwargs = {"uid": {"read_only": True}}


USER_FIELDS = ("username", "first_name", "last_name", "email")


class ProfileSerializer(PublicProfileSerializer):
    username = serializers.CharField(source="user.username")
    password = serializers.CharField(source="user.password", write_only=True)
    token = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.UserProfile
        fields = (
            "uid",
            "username",
            "first_name",
            "last_name",
            "email",
            "team",
            "token",
            "password",
        )
        extra_kwargs = {"uid": {"read_only": True}}

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")

        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.user.save()
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Override default serializer create function to
        create django user, token and set the password
        """
        user_data = validated_data.pop("user")
        password = user_data.pop("password")

        user = User(**user_data)
        user.set_password(password)
        user.save()

        token = Token.objects.create(user=user)

        profile = models.UserProfile.objects.create(
            user=user, token=token, **validated_data
        )

        return profile
