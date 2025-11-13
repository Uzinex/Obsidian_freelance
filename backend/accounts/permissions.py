from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileVerifiedOrReadOnly(BasePermission):
    message = "Для выполнения этого действия необходимо пройти верификацию."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, "profile", None)
        return bool(profile and profile.is_verified)


class IsVerificationAdmin(BasePermission):
    message = "Только администратор верификации может выполнить это действие."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        admin_email = getattr(settings, "VERIFICATION_ADMIN_EMAIL", "").lower()
        return user.is_staff and user.email.lower() == admin_email
