from rest_framework import routers
from . import views


router = routers.DefaultRouter(trailing_slash=False)
router.register("vacations", views.VacationViewSet, basename="vacations")
router.register("queries", views.ListUsers, basename="queries")
router.register("compare", views.Compare, basename="compare")
