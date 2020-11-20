import logging
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import User


class Vacation(models.Model):
    LEAVE_UNPAID = "U"
    LEAVE_PAID_RTT = "R"
    LEAVE_PAID_NORM = "N"

    LEAVE = [
        (LEAVE_UNPAID, "Sans solde"),
        (LEAVE_PAID_RTT, "RTT"),
        (LEAVE_PAID_NORM, "Congé payé"),
    ]

    DLEAVE = dict(LEAVE)

    uid = models.UUIDField(default=uuid4, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vacations")
    type = models.CharField(max_length=1, choices=LEAVE, default=LEAVE_PAID_NORM)

    start = models.DateField()
    end = models.DateField()

    def clean(self, *args, **kwargs):
        if self.end < self.start:
            raise ValidationError("The end date must be after the start date")

    def save(self, *args, **kwargs):
        self.start = kwargs.get("start", self.start)
        self.end = kwargs.get("end", self.end)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "{}, {} -> {}, {}".format(
            self.user, self.start, self.end, Vacation.DLEAVE[self.type]
        )
