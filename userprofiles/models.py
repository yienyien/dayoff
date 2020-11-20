from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models
from rest_framework.authtoken.models import Token


class Team(models.Model):
    """
    Team is the representation of a compagny team.
    All employees belong to a team. There can be many teams.
    """

    slugname = models.CharField(max_length=5, primary_key=True)
    fullname = models.CharField(max_length=256)

    description = models.TextField(null=True, blank=True)
    icones = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.fullname


class UserProfile(models.Model):
    """
    Profile is a new table to extend native django user.
    """

    # UUID is a good handler for API manipulation and data migration
    uid = models.UUIDField(primary_key=True, default=uuid4)
    # we authorize a profile without team
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Each user can be access to its data with a API key
    # Good for a frontend or an external web service.
    token = models.ForeignKey(Token, on_delete=models.SET_NULL, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        name = self.user.first_name + " " + self.user.last_name

        return self.user if (name == " ") else name
