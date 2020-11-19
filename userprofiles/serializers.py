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
        fields = ("username", "email", "first_name", "last_name" "password")
        extra_kwargs = {"password": {"write_only": True}}


class TeamSerializer(serializers.ModelSerializer):
    """
    Team serializer
    """

    class Meta:
        model = models.Team


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for a user profile object and
    django user native object
    """

    user = UserSerializer()

    class Meta:
        model = models.UserProfile
        fields = ("uid", "user", "team", "token")
        extra_kwargs = {"uid": {"read_only": True}, "token": {"read_only": True}}

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
