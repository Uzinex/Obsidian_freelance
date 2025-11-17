from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ContractViewSet,
    FreelancerRecommendationView,
    InviteRecommendationView,
    OrderApplicationViewSet,
    OrderViewSet,
    SemanticSearchView,
    SkillViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("skills", SkillViewSet, basename="skill")
router.register("orders", OrderViewSet, basename="order")
router.register("applications", OrderApplicationViewSet, basename="application")
router.register("contracts", ContractViewSet, basename="contract")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "recommendations/invite/",
        InviteRecommendationView.as_view(),
        name="invite-recommendations",
    ),
    path(
        "recommendations/orders/",
        FreelancerRecommendationView.as_view(),
        name="order-recommendations",
    ),
    path("semantic-search/", SemanticSearchView.as_view(), name="semantic-search"),
]
