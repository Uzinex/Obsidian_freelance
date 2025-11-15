from __future__ import annotations

from typing import Optional, Tuple

from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions

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
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed("Invalid authorization header")
        token = parts[1]
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
