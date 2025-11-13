from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    LogoutView,
    NotificationViewSet,
    ProfileViewSet,
    RegisterView,
    VerificationRequestViewSet,
    WalletViewSet,
)

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profile")
router.register("verifications", VerificationRequestViewSet, basename="verification")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("wallets", WalletViewSet, basename="wallet")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(router.urls)),
]
