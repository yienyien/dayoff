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
    """
    Manage vacations: create, list, update, delete
    If not admin, only manipulates its own vacations.
    """

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
    """
    Helper class to filter vacation by dates
    """

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
    """
    A resource that filters vacation according to the query parameters.

    date format: 2020-11-01

    query parameters:
    * start_after: get only vacations start after this date
    * start_before: get only vacations start before this date
    * end_after: get only vacations end after this date
    * end_before: get only vacations end before this date
    * type: get vacations with this type (U=Unpaid, R=RTT, N=Normal)
    * user: get vacations for this user (uuid)
    * team: get vacations for this team (slugname)
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.QueryResultSerializer

    def get_queryset(self):

        filters = Filter(self.request.query_params)
        filters.dvacations("start", "gte", "start_after")
        filters.dvacations("start", "lte", "start_before")
        filters.dvacations("end", "gte", "end_after")
        filters.dvacations("end", "lte", "end_before")
        filters.vacations("type", "eq", "type")
        filters.vacations("__user__profile", "eq", "user")
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


class Compare(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Return all vacations that overlap between two employees.

    query parameters:
    * user_a: first employee UUID
    * user_b: second employee UUID
    """

    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.VacationSerializer

    def get_queryset(self):
        user_a = self.request.query_params.get("user_a", None)
        user_b = self.request.query_params.get("user_b", None)

        if None in [user_a, user_b]:
            raise ParseError()

        vac_a = models.Vacation.objects.filter(user__profile__pk=user_a)

        overlaps = models.Vacation.objects.none()

        for vac in vac_a:
            overlap = serializers.get_overlaps(vac.start, vac.end)
            overlap = overlap.filter(user__profile__pk=user_b)

            overlaps = overlaps.union(overlap)
            if overlap.count() == 0:
                vac_a.exclude(pk=vac.pk)

        overlaps = overlaps.union(vac_a)

        overlaps = overlaps.order_by("start")
        return overlaps
