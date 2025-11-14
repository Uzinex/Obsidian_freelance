from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional, Set

from django.contrib.auth import get_user_model

if False:  # pragma: nocover - type checking import
    from marketplace.models import Contract, Order

User = get_user_model()


class Role(str, Enum):
    GUEST = "guest"
    USER = "user"
    FREELANCER = "freelancer"
    CLIENT = "client"
    VERIFIED = "verified"
    STAFF = "staff"
    MODERATOR = "moderator"
    FINANCE = "finance"


@dataclass(frozen=True)
class Policy:
    roles: Set[Role]
    requires_verified: bool = False


Action = str
ActionGuard = Callable[[User, Any, Set[Role]], bool]


ACTION_POLICIES: Dict[Action, Policy] = {
    "orders:view": Policy({
        Role.GUEST,
        Role.USER,
        Role.CLIENT,
        Role.FREELANCER,
        Role.VERIFIED,
        Role.STAFF,
        Role.MODERATOR,
        Role.FINANCE,
    }),
    "orders:create": Policy({Role.CLIENT, Role.STAFF}, requires_verified=True),
    "orders:edit": Policy({Role.CLIENT, Role.STAFF}, requires_verified=True),
    "orders:delete": Policy({Role.CLIENT, Role.STAFF}, requires_verified=True),
    "contracts:view": Policy({
        Role.CLIENT,
        Role.FREELANCER,
        Role.STAFF,
        Role.MODERATOR,
        Role.FINANCE,
    }),
    "contracts:edit": Policy({Role.CLIENT, Role.FREELANCER, Role.STAFF}),
    "kyc:view": Policy({Role.USER, Role.VERIFIED, Role.STAFF, Role.MODERATOR}),
    "kyc:manage": Policy({Role.STAFF, Role.MODERATOR}),
    "finance:view": Policy({Role.FINANCE, Role.STAFF}),
    "finance:manage": Policy({Role.FINANCE}),
    "uploads:manage": Policy({Role.USER, Role.FREELANCER, Role.CLIENT, Role.VERIFIED, Role.STAFF}),
    "uploads:link": Policy({Role.USER, Role.FREELANCER, Role.CLIENT, Role.VERIFIED, Role.STAFF}),
}


def _get_profile(user: User):
    return getattr(user, "profile", None)


def get_user_roles(user: User) -> Set[str]:
    roles: Set[Role] = {Role.GUEST}
    if not getattr(user, "is_authenticated", False):
        return {role.value for role in roles}

    roles.add(Role.USER)
    profile = _get_profile(user)
    if profile:
        if profile.role == "freelancer":
            roles.add(Role.FREELANCER)
        if profile.role == "client":
            roles.add(Role.CLIENT)
        if getattr(profile, "is_verified", False):
            roles.add(Role.VERIFIED)
    if user.is_staff or user.is_superuser:
        roles.add(Role.STAFF)
    group_names = {group.name.lower() for group in user.groups.all()}
    if "moderator" in group_names or user.is_superuser:
        roles.add(Role.MODERATOR)
    if "finance" in group_names or user.is_superuser:
        roles.add(Role.FINANCE)
    return {role.value for role in roles}


def user_has_role(user: User, role: Role) -> bool:
    return role.value in get_user_roles(user)


OBJECT_GUARDS: Dict[Action, ActionGuard] = {}


def _register_guard(action: Action):
    def decorator(func: ActionGuard) -> ActionGuard:
        OBJECT_GUARDS[action] = func
        return func

    return decorator


@_register_guard("orders:edit")
@_register_guard("orders:delete")
def _guard_order_owner(user: User, obj: Any, roles: Set[Role]) -> bool:
    try:
        from marketplace.models import Order
    except Exception:  # pragma: no cover - fallback to avoid circular import errors
        return False
    if not isinstance(obj, Order):
        return False
    if Role.STAFF in roles:
        return True
    profile = _get_profile(user)
    return bool(profile and obj.client_id == profile.id)


@_register_guard("contracts:view")
@_register_guard("contracts:edit")
def _guard_contract_participant(user: User, obj: Any, roles: Set[Role]) -> bool:
    try:
        from marketplace.models import Contract
    except Exception:  # pragma: no cover
        return False
    if not isinstance(obj, Contract):
        return False
    if Role.STAFF in roles or Role.FINANCE in roles or Role.MODERATOR in roles:
        return True
    profile = _get_profile(user)
    if not profile:
        return False
    return obj.client_id == profile.id or obj.freelancer_id == profile.id


@_register_guard("uploads:manage")
@_register_guard("uploads:link")
def _guard_upload_owner(user: User, obj: Any, roles: Set[Role]) -> bool:
    if Role.STAFF in roles:
        return True
    return getattr(obj, "owner_id", None) == getattr(user, "id", None)


def can(user: User, action: Action, *, obj: Optional[Any] = None) -> bool:
    policy = ACTION_POLICIES.get(action)
    if policy is None:
        return True
    roles = {Role(value) for value in get_user_roles(user)}
    if not roles.intersection(policy.roles):
        return False
    if policy.requires_verified and Role.VERIFIED not in roles and Role.STAFF not in roles:
        return False
    guard = OBJECT_GUARDS.get(action)
    if guard and obj is not None:
        return guard(user, obj, roles)
    return True


__all__ = [
    "Role",
    "ACTION_POLICIES",
    "OBJECT_GUARDS",
    "can",
    "get_user_roles",
    "user_has_role",
]
