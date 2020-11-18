from django.db import models


class Team(models.Model):
    """
    Team is the representation of a compagny team.
    All employees belong to a team. There can be many teams.
    """
    slugname = models.CharField(max_length=5, primary_key=True)
    fullname = models.CharField(max_length=256)

    description = models.TextField()
    icones = models.ImageField()


class UserProfile(models.Model):
    """
    Profile is a new table to extend native django user.

    """
    # we authorize a profile without team
    team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True, blank=True)
