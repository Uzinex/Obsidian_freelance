"""Utilities for issuing and validating JWT access and refresh tokens."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Dict, Optional, Tuple

import jwt
from django.conf import settings

from obsidian_backend import jwt_settings as jwt_conf


def _resolve_algorithm(keypair) -> str:
    """Return the effective algorithm for the given keypair.

    In local development environments we often rely on symmetric keys derived from
    ``SECRET_KEY`` instead of providing a full RSA key pair.  PyJWT requires the
    ``cryptography`` package to use the RS* algorithms and will raise a
    ``NotImplementedError`` if the dependency is missing.  To keep the login flow
    operational in such environments we gracefully fall back to HS256 when we
    detect that asymmetric signing is not viable.
    """

    algorithm = (keypair.algorithm or "HS256").upper()
    if algorithm.startswith("RS"):
        has_any_key = bool((keypair.private_key or "").strip() or (keypair.public_key or "").strip())
        if not has_any_key:
            return "HS256"
        try:  # pragma: no cover - optional dependency, defensive branch
            import cryptography  # type: ignore # noqa: F401  (import required for RS algorithms)
        except ModuleNotFoundError:  # pragma: no cover - defensive branch
            return "HS256"
    return algorithm


class JWTError(Exception):
    """Base class for JWT errors."""


class JWTDecodeError(JWTError):
    """Raised when a JWT cannot be decoded or verified."""


def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _get_private_key(keypair) -> Tuple[str, str]:
    algorithm = _resolve_algorithm(keypair)
    if algorithm.startswith("HS"):
        private_key = (keypair.private_key or settings.SECRET_KEY or "").strip()
    else:
        private_key = (keypair.private_key or "").strip()
    if not private_key:
        raise JWTError("Missing signing key")
    return private_key, algorithm


def _get_public_keys(keyring) -> Dict[str, str]:
    current = keyring.current
    keys: Dict[str, str] = {}
    algorithm = _resolve_algorithm(current)
    if algorithm.startswith("HS"):
        key_value = (current.private_key or settings.SECRET_KEY or "").strip()
        if not key_value:
            raise JWTError("Missing signing key for verification")
        keys[current.kid or "current"] = (key_value, algorithm)
    else:
        if not (current.public_key or "").strip():
            raise JWTError("Missing public key for verification")
        keys[current.kid or "current"] = (current.public_key.strip(), algorithm)
    for kid, public_key in keyring.additional_public_keys.items():
        keys[kid] = (public_key, algorithm)
    return keys


def _build_headers(keypair) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if keypair.kid:
        headers["kid"] = keypair.kid
    return headers


def issue_access_token(*, user, session, two_factor_verified: bool, expires_in: Optional[int] = None, extra_claims: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
    now = _now()
    ttl = expires_in or jwt_conf.JWT_ACCESS_TTL_SECONDS
    exp = now + timedelta(seconds=ttl)
    jti = uuid.uuid4().hex
    payload: Dict[str, Any] = {
        "iss": "obsidian-backend",
        "sub": str(user.pk),
        "session_id": str(session.id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
        "two_factor_verified": two_factor_verified,
    }
    if extra_claims:
        payload.update(extra_claims)
    key, algorithm = _get_private_key(jwt_conf.JWT_ACCESS_KEYS)
    token = jwt.encode(payload, key, algorithm=algorithm, headers=_build_headers(jwt_conf.JWT_ACCESS_KEYS))
    return token, jti


def issue_refresh_token(*, user, session, expires_in: Optional[int] = None, extra_claims: Optional[Dict[str, Any]] = None) -> Tuple[str, str]:
    now = _now()
    ttl = expires_in or jwt_conf.JWT_REFRESH_TTL_SECONDS
    exp = now + timedelta(seconds=ttl)
    jti = uuid.uuid4().hex
    payload: Dict[str, Any] = {
        "iss": "obsidian-backend",
        "sub": str(user.pk),
        "session_id": str(session.id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": jti,
        "device_id": session.device_id,
    }
    if extra_claims:
        payload.update(extra_claims)
    key, algorithm = _get_private_key(jwt_conf.JWT_REFRESH_KEYS)
    token = jwt.encode(payload, key, algorithm=algorithm, headers=_build_headers(jwt_conf.JWT_REFRESH_KEYS))
    return token, jti


def decode_jwt(token: str, *, token_type: str) -> Dict[str, Any]:
    try:
        unverified = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:  # pragma: no cover - defensive
        raise JWTDecodeError("Invalid token header") from exc
    kid = unverified.get("kid") or "current"
    keyring = jwt_conf.JWT_KEYRINGS.get(token_type)
    if not keyring:
        raise JWTDecodeError("Unknown token type")
    keys = _get_public_keys(keyring)
    key_info = keys.get(kid)
    if not key_info:
        raise JWTDecodeError("Unknown key identifier")
    key, algorithm = key_info
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[algorithm],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError as exc:
        raise JWTDecodeError("Token has expired") from exc
    except jwt.PyJWTError as exc:  # pragma: no cover - defensive
        raise JWTDecodeError("Token decode error") from exc
    if payload.get("type") != token_type:
        raise JWTDecodeError("Unexpected token type")
    return payload
