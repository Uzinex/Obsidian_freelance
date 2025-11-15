from rest_framework.permissions import BasePermission

from accounts import rbac


class IsModerator(BasePermission):
    message = "Требуются права модератора"

    def has_permission(self, request, view):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff or rbac.user_has_role(user, rbac.Role.MODERATOR)


class IsFinance(BasePermission):
    message = "Требуются права finance"

    def has_permission(self, request, view):
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return False
        return user.is_staff or rbac.user_has_role(user, rbac.Role.FINANCE)
