from rest_framework import serializers
from . import models


class MyVacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vacation
        fields = ("type", "start", "end")


class VacationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vacation
        fields = ("user", "type", "start", "end")
