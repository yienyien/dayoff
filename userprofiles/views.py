from rest_framework import viewsets
from rest_framework import permissions

from . import models
from . import serializers


class IsAdminUser(permissions.IsAdminUser):
    """
    By default IsAdminUser does not block the object access
    """

    def has_object_permission(self, request, view, profile):
        return bool(request.user and request.user.is_staff)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, profile):
        if request.method in permissions.SAFE_METHODS:
            return True

        return profile.user == request.user


class AnonymousCreate(permissions.BasePermission):
    """
    If you want to enable anonymous creation (vs admin), add this
    the permission_classes list in UserProfileViewSet
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    Manage users: create, list, update, delete
    Admin only for mutable actions, public view for anonymous

    query parameters:
    * team: filter by team
    """

    queryset = models.UserProfile.objects.all()
    permission_classes = [IsAdminUser | IsOwnerOrReadOnly]

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
