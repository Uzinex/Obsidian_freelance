from __future__ import annotations

from typing import Optional, Tuple

from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import SAFE_METHODS

from obsidian_backend import jwt_settings as jwt_conf

from .jwt import JWTDecodeError, decode_jwt
from .models import AuthSession


class JWTAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using JWT access tokens."""

    keyword = "Bearer"

    def authenticate_header(self, request):
        """Return the ``WWW-Authenticate`` header value for failed auth.

        DRF downgrades authentication errors to ``403 Forbidden`` responses
        when the authenticator does not provide a value for the
        ``WWW-Authenticate`` header.  Returning the keyword here ensures that
        callers receive a proper ``401 Unauthorized`` response, allowing
        clients to refresh or discard invalid tokens instead of treating the
        failure as a permission error.
        """

        return self.keyword

    def authenticate(self, request) -> Optional[Tuple[object, dict]]:
        auth = authentication.get_authorization_header(request).decode("utf-8")
        if not auth:
            return None
        parts = auth.split()
        if not parts:
            return None
        if parts[0] != self.keyword:
            # Ignore authorization schemes that we do not recognize instead of
            # failing with HTTP 401.  Older builds of the frontend may still
            # optimistically attach ``Token``/``JWT`` headers even for
            # unauthenticated users and raising here would effectively block
            # anonymous access to otherwise public endpoints.
            return None
        if len(parts) == 1:
            # ``Bearer`` header without an accompanying token should be treated
            # the same as if the header was not provided.  Browsers sometimes
            # serialize an empty string for optimistic auth attempts and we do
            # not want to spam clients with ``401`` errors on public endpoints.
            return None
        if len(parts) > 2:
            raise exceptions.AuthenticationFailed("Invalid authorization header")
        token = parts[1].strip()
        # Some browsers/extensions (or buggy frontend code) may optimistically
        # attach placeholder values such as ``null``/``undefined`` when a user
        # is not authenticated yet.  Treat those placeholders the same as the
        # header being absent so public endpoints keep working instead of
        # responding with spurious ``401`` errors.
        if token.lower() in {"", "null", "undefined", "none"}:
            return None
        try:
            payload = decode_jwt(token, token_type="access")
        except JWTDecodeError as exc:
            raise exceptions.AuthenticationFailed(str(exc)) from exc
        user_id = payload.get("sub")
        session_id = payload.get("session_id")
        if not user_id or not session_id:
            raise exceptions.AuthenticationFailed("Token missing required claims")
        try:
            session = AuthSession.objects.select_related("user").get(
                id=session_id,
                user_id=user_id,
            )
        except AuthSession.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed("Session not found") from exc
        if session.revoked_at:
            raise exceptions.AuthenticationFailed("Session revoked")
        if session.refresh_token_expires_at <= timezone.now():
            raise exceptions.AuthenticationFailed("Session expired")
        user = session.user
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User inactive or deleted")
        if (
            settings.AUTH_REQUIRE_2FA_FOR_STAFF
            and (user.is_staff or user.is_superuser)
            and not payload.get("two_factor_verified")
        ):
            raise exceptions.AuthenticationFailed("Two-factor authentication required")
        request.auth_payload = payload
        request.auth_session = session
        return user, payload


def legacy_token_authentication_enabled() -> bool:
    return jwt_conf.FEATURE_FLAGS.get("auth.token_legacy", False)


class LegacyTokenAuthentication(TokenAuthentication):
    """Backward-compatible token auth that tolerates invalid placeholders."""

    _PLACEHOLDER_VALUES = {"", "null", "undefined", "none"}

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth:
            return None
        if auth[0].lower() != b"token":
            return None
        if len(auth) == 1:
            return None
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed("Invalid token header")
        try:
            token = auth[1].decode("utf-8").strip()
        except UnicodeError as exc:  # pragma: no cover - defensive
            raise exceptions.AuthenticationFailed("Invalid token header") from exc
        if token.lower() in self._PLACEHOLDER_VALUES:
            return None
        try:
            return self.authenticate_credentials(token)
        except exceptions.AuthenticationFailed:
            if request.method in SAFE_METHODS:
                return None
            raise
