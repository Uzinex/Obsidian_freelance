from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS

from . import rbac


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
