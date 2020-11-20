import dateutil.parser
from dateutil.parser import ParserError as ParserError


from django.db.models import Q

from rest_framework import viewsets, permissions
from rest_framework import mixins
from rest_framework.exceptions import ParseError

from . import models
from . import serializers
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
        else:
            serializer.save()


class Filter:
    DATE = "date"

    def __init__(self, query_params):
        self.query_params = query_params
        self.query = Q()

    def __parse(self, value, parser):
        if parser == Filter.DATE:
            try:
                return dateutil.parser.parse(value)
            except ParserError:
                raise ParseError()
        return value

    def vacations(self, key, operator, param, parser=None):
        value = self.query_params.get(param, None)
        if value is not None:
            value = self.__parse(value, parser)
            if operator != "eq":
                key += "__" + operator
            kwargs = {key: value}
            self.query &= Q(**kwargs)

    def dvacations(self, *args, **kwargs):
        kwargs["parser"] = Filter.DATE
        self.vacations(*args, **kwargs)


class ListUsers(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.QueryResultSerializer

    def get_queryset(self):

        filters = Filter(self.request.query_params)
        filters.dvacations("start", "gte", "start_after")
        filters.dvacations("start", "lte", "start_before")
        filters.dvacations("end", "gte", "end_after")
        filters.dvacations("end", "lte", "end_before")
        filters.vacations("type", "eq", "type")
        filters.vacations("__user__team", "eq", "team")

        vacations = models.Vacation.objects.filter(filters.query)

        counts = dict()
        for vac in vacations:
            user_count = counts.setdefault(vac.user.pk, {"R": 0, "U": 0, "N": 0})
            count = user_count.get(vac.type, 0)
            count += (vac.end - vac.start).days
            user_count[vac.type] = count

        profiles = user_models.UserProfile.objects.filter(
            user__pk__in=counts.keys()
        ).order_by("pk")
        for profile in profiles:
            profile.counts = counts[profile.user.pk]

        return profiles
