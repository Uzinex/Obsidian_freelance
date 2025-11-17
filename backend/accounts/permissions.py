from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS

from . import rbac


def is_verification_admin(user) -> bool:
    """Return True when the user can moderate verification requests."""

    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    admin_email = getattr(settings, "VERIFICATION_ADMIN_EMAIL", "").strip().lower()
    if admin_email and getattr(user, "email", None):
        if user.email.lower() == admin_email:
            # Keep backwards compatibility with the legacy single-admin flow.
            return True
    return getattr(user, "is_staff", False)


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
        return is_verification_admin(getattr(request, "user", None))


class RoleBasedAccessPermission(BasePermission):
    """Enforce role-based permissions declared on the view."""

    message = "Недостаточно прав для выполнения действия."

    def _resolve_action(self, request, view) -> str | None:
        if hasattr(view, "rbac_action"):
            return view.rbac_action
        action_map = getattr(view, "rbac_action_map", {})
        if isinstance(action_map, dict):
            if hasattr(view, "action") and view.action in action_map:
                return action_map.get(view.action)
            return action_map.get(request.method.upper())
        return None

    def has_permission(self, request, view):
        action = self._resolve_action(request, view)
        if not action:
            return True
        return rbac.can(request.user, action)

    def has_object_permission(self, request, view, obj):
        action = self._resolve_action(request, view)
        if not action:
            return True
        target = obj
        resolver = getattr(view, "get_rbac_object", None)
        if callable(resolver):
            target = resolver(obj=obj, request=request)
        return rbac.can(request.user, action, obj=target)
