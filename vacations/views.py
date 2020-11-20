import datetime
import dateutil.parser
from dateutil.parser import ParserError as ParserError


from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.exceptions import ParseError

from . import models
from . import serializers
from userprofiles import serializers as user_serializers
from userprofiles import models as user_models


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


class UserFilter:
    DATE = "date"

    def __init__(self, query_params):
        self.query_params = query_params
        self.query = Q()
        value = self.query_params.get("team", None)
        self.types = dict(models.Vacation.LEAVE)
        if value is not None:
            self.query &= Q(team=value)

    def __parse(self, value, parser):
        if parser == UserFilter.DATE:
            try:
                return dateutil.parser.parse(value)
            except ParserError:
                raise ParseError()
        return value

    def vacations(self, key, operator, param, parser=None):
        value = self.query_params.get(param, None)
        if value is not None:
            value = self.__parse(value, parser)
            key = "user__vacations__" + key
            if operator != "eq":
                key += "__" + operator
            kwargs = {key: value}
            print(kwargs)
            self.query &= Q(**kwargs)

    def dvacations(self, *args, **kwargs):
        kwargs["parser"] = UserFilter.DATE
        self.vacations(*args, **kwargs)


class ListUsers(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = user_serializers.ProfileSerializer

    def get_queryset(self):

        # TODO: parse date
        filters = UserFilter(self.request.query_params)
        filters.dvacations("start", "gte", "start_after")
        filters.dvacations("start", "lte", "start_before")
        filters.dvacations("end", "gte", "end_after")
        filters.dvacations("end", "lte", "end_before")
        filters.vacations("type", "eq", "type")

        profiles = user_models.UserProfile.objects.all()
        profiles = profiles.filter(filters.query)

        return profiles
