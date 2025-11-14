"""Конфигурация JWT и refresh-токенов, управляемая через переменные окружения."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict

__all__ = [
    "JWT_ENVIRONMENT",
    "JWT_ACCESS_TTL_SECONDS",
    "JWT_REFRESH_TTL_SECONDS",
    "JWT_REFRESH_SLIDING_WINDOW_SECONDS",
    "JWT_REFRESH_ABSOLUTE_LIFETIME_SECONDS",
    "JWT_REFRESH_COOKIE",
    "JWT_ACCESS_KEYS",
    "JWT_REFRESH_KEYS",
    "JWT_KEYRINGS",
    "FEATURE_FLAGS",
]

_SUPPORTED_ENVIRONMENTS = {"dev", "stage", "prod"}


def _get_bool_env(var_name: str, default: bool = False) -> bool:
    value = os.getenv(var_name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int_env(var_name: str, default: int) -> int:
    value = os.getenv(var_name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Environment variable {var_name} must be an integer") from exc


def _get_env(var_name: str, default: str = "") -> str:
    value = os.getenv(var_name)
    if value is None:
        return default
    return value


JWT_ENVIRONMENT = os.getenv("JWT_ENVIRONMENT", os.getenv("SENTRY_ENVIRONMENT", "dev")).lower()
if JWT_ENVIRONMENT not in _SUPPORTED_ENVIRONMENTS:
    JWT_ENVIRONMENT = "dev"


@dataclass(frozen=True)
class JWTKeyPair:
    kid: str
    private_key: str
    public_key: str
    algorithm: str


@dataclass(frozen=True)
class JWTCookieSettings:
    name: str
    path: str
    secure: bool
    httponly: bool
    samesite: str


@dataclass(frozen=True)
class JWTKeyRing:
    current: JWTKeyPair
    additional_public_keys: Dict[str, str]


_ACCESS_PREFIX_TEMPLATE = "JWT_ACCESS_{env}_{suffix}"
_REFRESH_PREFIX_TEMPLATE = "JWT_REFRESH_{env}_{suffix}"


def _load_key_pair(prefix_template: str, environment: str) -> JWTKeyPair:
    prefix = prefix_template.format(env=environment.upper(), suffix="")
    kid = _get_env(f"{prefix}KID")
    private_key = _get_env(f"{prefix}PRIVATE_KEY")
    public_key = _get_env(f"{prefix}PUBLIC_KEY")
    algorithm = _get_env(f"{prefix}ALGORITHM", "RS256")
    return JWTKeyPair(kid=kid, private_key=private_key, public_key=public_key, algorithm=algorithm)


def _load_keyring(prefix_template: str, environment: str, additional_env: str) -> JWTKeyRing:
    keypair = _load_key_pair(prefix_template, environment)
    additional = {}
    additional_value = _get_env(additional_env)
    if additional_value:
        # Формат: kid1::public_key1||kid2::public_key2
        for item in additional_value.split("||"):
            if "::" not in item:
                continue
            kid, public_key = item.split("::", 1)
            additional[kid.strip()] = public_key.strip()
    return JWTKeyRing(current=keypair, additional_public_keys=additional)


JWT_ACCESS_KEYS = _load_key_pair(_ACCESS_PREFIX_TEMPLATE, JWT_ENVIRONMENT)
JWT_REFRESH_KEYS = _load_key_pair(_REFRESH_PREFIX_TEMPLATE, JWT_ENVIRONMENT)

JWT_KEYRINGS = {
    "access": _load_keyring(
        _ACCESS_PREFIX_TEMPLATE,
        JWT_ENVIRONMENT,
        "JWT_ACCESS_ADDITIONAL_PUBLIC_KEYS",
    ),
    "refresh": _load_keyring(
        _REFRESH_PREFIX_TEMPLATE,
        JWT_ENVIRONMENT,
        "JWT_REFRESH_ADDITIONAL_PUBLIC_KEYS",
    ),
}

JWT_ACCESS_TTL_SECONDS = _get_int_env("JWT_ACCESS_TTL_SECONDS", default=600)
JWT_REFRESH_TTL_SECONDS = _get_int_env("JWT_REFRESH_TTL_SECONDS", default=60 * 60 * 24 * 28)
JWT_REFRESH_SLIDING_WINDOW_SECONDS = _get_int_env(
    "JWT_REFRESH_SLIDING_WINDOW_SECONDS", default=60 * 60 * 24 * 14
)
JWT_REFRESH_ABSOLUTE_LIFETIME_SECONDS = _get_int_env(
    "JWT_REFRESH_ABSOLUTE_LIFETIME_SECONDS", default=60 * 60 * 24 * 30
)

JWT_REFRESH_COOKIE = JWTCookieSettings(
    name=_get_env("JWT_REFRESH_COOKIE_NAME", "refresh_token"),
    path=_get_env("JWT_REFRESH_COOKIE_PATH", "/"),
    secure=_get_bool_env("JWT_REFRESH_COOKIE_SECURE", True),
    httponly=True,
    samesite=_get_env("JWT_REFRESH_COOKIE_SAMESITE", "Strict"),
)

FEATURE_FLAGS = {
    "auth.jwt": _get_bool_env("FEATURE_AUTH_JWT", False),
    "auth.token_legacy": _get_bool_env("FEATURE_AUTH_TOKEN_LEGACY", True),
    "auth.2fa": _get_bool_env("FEATURE_AUTH_2FA", False),
    "upload.scanner": _get_bool_env("FEATURE_UPLOAD_SCANNER", False),
    "admin.hardening": _get_bool_env("FEATURE_ADMIN_HARDENING", False),
}
