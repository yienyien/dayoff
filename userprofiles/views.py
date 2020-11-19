from rest_framework import viewsets
from rest_framework import permissions

from . import models
from . import serializers


class IsAdminUser(permissions.IsAdminUser):
    def has_object_permission(self, request, view, profile):
        return bool(request.user and request.user.is_staff)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, profile):
        if request.method in permissions.SAFE_METHODS:
            return True

        return profile.user == request.user


class AnonymousCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    permission_classes = [IsAdminUser | IsOwnerOrReadOnly | AnonymousCreate]

    def get_queryset(self):
        team = self.request.query_params.get("team", None)

        queryset = self.queryset.filter()
        if team is not None:
            queryset.filter(team__slugname=team)

        return queryset

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return serializers.ProfileSerializer
        else:
            return serializers.PublicProfileSerializer
