from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from . import models
from userprofiles import models as profile_models


def vac(client, start, end, type):
    v = dict(start=start, end=end, type=type)
    return client.post("/api/1/vacations", v)


class VacationCreateTestCase(APITestCase):
    def setUp(self):
        team = profile_models.Team.objects.create(
            slugname="PHOE", fullname="Phoenix", description="Example"
        )

        self.client.post(
            "/api/1/users",
            {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john.doe@company.com",
                "team": team.pk,
                "password": "foobar",
            },
        )
        self.client.login(username="johndoe", password="foobar")

    def test_create(self):
        resp = vac(self.client, "2020-11-03", "2020-11-05", "U")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["start"], "2020-11-03")
        self.assertEqual(resp.data["end"], "2020-11-05")
        self.assertEqual(models.Vacation.objects.all().count(), 1)

        resp = vac(self.client, "2020-11-10", "2020-11-20", "R")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["start"], "2020-11-10")
        self.assertEqual(resp.data["end"], "2020-11-20")
        self.assertEqual(models.Vacation.objects.all().count(), 2)

        resp = vac(self.client, "2020-12-04", "2020-12-20", "N")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["start"], "2020-12-04")
        self.assertEqual(resp.data["end"], "2020-12-20")
        self.assertEqual(models.Vacation.objects.all().count(), 3)


class VacationOverlapTestCase(APITestCase):
    def setUp(self):
        team = profile_models.Team.objects.create(
            slugname="PHOE", fullname="Phoenix", description="Example"
        )

        self.client.post(
            "/api/1/users",
            {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john.doe@company.com",
                "team": team.pk,
                "password": "foobar",
            },
        )
        self.client.login(username="johndoe", password="foobar")
        vac(self.client, "2020-11-03", "2020-11-05", "U")
        vac(self.client, "2020-11-10", "2020-11-20", "R")
        vac(self.client, "2020-12-04", "2020-12-20", "N")

    def test_overlap_before(self):
        resp = vac(self.client, "2020-11-01", "2020-11-04", "U")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["start"], "2020-11-01")
        self.assertEqual(resp.data["end"], "2020-11-05")
        self.assertEqual(models.Vacation.objects.all().count(), 3)

    def test_overlap_after(self):
        resp = vac(self.client, "2020-11-04", "2020-11-07", "U")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["start"], "2020-11-03")
        self.assertEqual(resp.data["end"], "2020-11-07")
        self.assertEqual(models.Vacation.objects.all().count(), 3)

    def test_overlap_in(self):
        resp = vac(self.client, "2020-11-04", "2020-11-04", "U")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["start"], "2020-11-03")
        self.assertEqual(resp.data["end"], "2020-11-05")
        self.assertEqual(models.Vacation.objects.all().count(), 3)

    def test_not_overlap(self):
        resp = vac(self.client, "2020-11-06", "2020-11-07", "U")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["start"], "2020-11-06")
        self.assertEqual(resp.data["end"], "2020-11-07")
        self.assertEqual(models.Vacation.objects.all().count(), 4)

    def test_overlap_other(self):
        resp = vac(self.client, "2020-11-11", "2020-11-19", "U")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(models.Vacation.objects.all().count(), 3)


class VacationQueryTestCase(APITestCase):
    def setUp(self):
        team = profile_models.Team.objects.create(
            slugname="PHOE", fullname="Phoenix", description="Example"
        )

        resp = self.client.post(
            "/api/1/users",
            {
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "email": "john.doe@company.com",
                "team": team.pk,
                "password": "foobar",
            },
        )
        self.user_a = resp.data["uid"]

        resp = self.client.post(
            "/api/1/users",
            {
                "first_name": "Jean",
                "last_name": "Dupont",
                "username": "jean",
                "email": "jean.dupont@company.com",
                "team": team.pk,
                "password": "foobar",
            },
        )
        self.user_b = resp.data["uid"]

        self.client.login(username="johndoe", password="foobar")
        vac(self.client, "2020-11-03", "2020-11-05", "U")
        vac(self.client, "2020-11-10", "2020-11-20", "R")
        vac(self.client, "2020-12-04", "2020-12-20", "N")

        self.client.login(username="jean", password="foobar")
        vac(self.client, "2020-11-03", "2020-11-12", "U")
        vac(self.client, "2021-01-04", "2021-01-24", "R")

        User.objects.create_superuser("admin", "myemail@test.com", "admin")
        self.client.login(username="admin", password="admin")

    def test_query_start_after(self):
        resp = self.client.get("/api/1/queries", {"start_after": "2020-11-12"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 2)

        resp = self.client.get("/api/1/queries", {"start_after": "2021-01-01"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

        resp = self.client.get(
            "/api/1/queries", {"start_after": "2021-01-01", "type": "U"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)

    def test_query_start_before(self):
        resp = self.client.get("/api/1/queries", {"start_before": "2021-01-01"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 2)

    def test_query_end_before(self):
        resp = self.client.get("/api/1/queries", {"end_before": "2020-11-06"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_query_complex(self):
        resp = self.client.get(
            "/api/1/queries",
            {"end_before": "2021-01-01", "start_after": "2020-11-06", "type": "U"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 0)

        resp = self.client.get(
            "/api/1/queries",
            {"end_before": "2021-01-01", "start_after": "2020-11-02", "type": "R"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 1)

    def test_compare(self):
        resp = self.client.get(
            "/api/1/compare",
            {
                "start": "2020-11-01",
                "end": "2021-11-01",
                "user_a": self.user_a,
                "user_b": self.user_b,
            },
        )
