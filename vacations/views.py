from rest_framework import viewsets, permissions

from . import models
from . import serializers


class IsAdminUser(permissions.IsAdminUser):
    def has_object_permission(self, request, view, profile):
        return bool(request.user and request.user.is_staff)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, vacation):
        return vacation.user == request.user


class VacationViewSet(viewsets.ModelViewSet):
    queryset = models.Vacation.objects.all()
    serializer_class = serializers.VacationSerializer
    permission_classes = [IsAdminUser | IsOwner]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset

        queryset = self.queryset.filter(user=self.request.user)

        return queryset

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return serializers.VacationSerializer
        else:
            return serializers.MyVacationSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(user=self.request.user)
