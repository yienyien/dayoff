from rest_framework import serializers
from . import models
from django.db.models import Q

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from userprofiles import serializers as userprofile_serializers
from userprofiles import models as userprofile_models


def get_overlaps(start, end):
    # must at most single
    overlaps = models.Vacation.objects.filter(
        (
            (Q(start__lte=start) & Q(end__gte=start))
            | (Q(start__gte=start) & Q(start__lte=end))
        )
    )

    return overlaps


class MyVacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vacation
        fields = ("type", "start", "end", "uid")
        extra_kwargs = {"uid": {"read_only": True}}

    def update(self, instance, validated_data):
        start = validated_data.get("start", instance.start)
        end = validated_data.get("end", instance.end)
        type = validated_data.get("type", instance.type)
        user = None
        try:
            user = instance.user
        except User.DoesNotExist:
            pass
        user = validated_data.pop("user", user)

        overlaps = get_overlaps(start, end)
        overlaps = overlaps.filter(user=user)

        if instance.pk:
            overlaps.exclude(pk=instance.pk)

        if overlaps.count() == 0:
            instance.user = user
            instance.type = type
            instance.start = start
            instance.end = end
            instance.save()
            return instance

        if instance.pk:
            instance.delete()

        if overlaps.exclude(type=type).count() > 0:
            # Overlap with other type
            raise PermissionDenied("Overlap with other type vacations")

        overlap = overlaps.first()
        overlap.start = min(start, overlap.start)
        overlap.end = max(end, overlap.end)
        overlap.save()
        return overlap

    def create(self, validated_data):
        return self.update(models.Vacation(), validated_data)


class VacationSerializer(MyVacationSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = models.Vacation
        fields = ("uid", "user", "type", "start", "end")
        extra_kwargs = {"uid": {"read_only": True}, "user": {"read_only": True}}

    def get_user(self, obj):
        return str(obj.user)
