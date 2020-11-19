from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response

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
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return profile.user == request.user


class AnonymousCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsAdminUser | IsOwnerOrReadOnly | AnonymousCreate]

    def get_queryset(self):
        team = self.request.query_params.get("team", None)

        queryset = self.queryset.filter()
        if team is not None:
            queryset.filter(team__slugname=team)

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        if request.user.is_staff:
            serializer = serializers.ProfileSerializer(queryset, many=True)
        else:
            serializer = serializers.PublicProfileSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        if request.user.is_staff:
            serializer = serializers.ProfileSerializer(obj)
        else:
            serializer = serializers.PublicProfileSerializer(obj)
        return Response(serializer.data)
