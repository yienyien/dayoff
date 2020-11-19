from django.contrib import admin

from . import models


@admin.register(models.Vacation)
class VacationAdmin(admin.ModelAdmin):
    pass
