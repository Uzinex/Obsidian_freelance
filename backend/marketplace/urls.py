from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    OrderApplicationViewSet,
    OrderViewSet,
    SkillViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("skills", SkillViewSet, basename="skill")
router.register("orders", OrderViewSet, basename="order")
router.register("applications", OrderApplicationViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]
