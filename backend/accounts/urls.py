from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ProfileViewSet,
    VerificationRequestViewSet,
    WalletViewSet,
)
from .views_auth import (
    EmailChangeConfirmView,
    EmailChangeRequestView,
    EmailVerifyConfirmView,
    EmailVerifyRequestView,
    LoginView,
    LogoutAllView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegistrationResendView,
    RegistrationStartView,
    RegistrationVerifyView,
    RefreshView,
    SessionListView,
    TwoFactorBackupCodesView,
    TwoFactorConfirmView,
    TwoFactorDisableView,
    TwoFactorSetupView,
)

router = DefaultRouter()
router.register("profiles", ProfileViewSet, basename="profile")
router.register("verifications", VerificationRequestViewSet, basename="verification")
router.register("wallets", WalletViewSet, basename="wallet")

urlpatterns = [
    path("register/", RegistrationStartView.as_view(), name="register"),
    path("register/verify/", RegistrationVerifyView.as_view(), name="register-verify"),
    path("register/resend/", RegistrationResendView.as_view(), name="register-resend"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logout-all/", LogoutAllView.as_view(), name="logout-all"),
    path("session-list/", SessionListView.as_view(), name="session-list"),
    path("email/verify/request/", EmailVerifyRequestView.as_view(), name="email-verify-request"),
    path("email/verify/confirm/", EmailVerifyConfirmView.as_view(), name="email-verify-confirm"),
    path("password/reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("email/change/request/", EmailChangeRequestView.as_view(), name="email-change-request"),
    path("email/change/confirm/", EmailChangeConfirmView.as_view(), name="email-change-confirm"),
    path("2fa/setup/", TwoFactorSetupView.as_view(), name="2fa-setup"),
    path("2fa/confirm/", TwoFactorConfirmView.as_view(), name="2fa-confirm"),
    path("2fa/backup-codes/", TwoFactorBackupCodesView.as_view(), name="2fa-backup-codes"),
    path("2fa/disable/", TwoFactorDisableView.as_view(), name="2fa-disable"),
    path("", include(router.urls)),
]
