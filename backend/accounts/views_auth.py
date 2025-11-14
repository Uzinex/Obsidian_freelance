from __future__ import annotations

import secrets
import time
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from obsidian_backend import jwt_settings as jwt_conf

from .emails import send_auth_email
from .jwt import JWTDecodeError, decode_jwt, issue_access_token, issue_refresh_token
from .models import (
    AuditEvent,
    AuthSession,
    OneTimeToken,
    User,
    generate_token_hash,
)
from .security import register_login_failure, reset_login_failures
from .serializers import (
    AuthSessionSerializer,
    EmailChangeConfirmSerializer,
    EmailChangeRequestSerializer,
    EmailTokenSerializer,
    EmailVerificationRequestSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    TwoFactorSetupSerializer,
    UserSerializer,
)
from .token_service import consume_one_time_token, create_one_time_token
from .twofactor import ensure_config, generate_backup_codes, generate_provisioning_uri, verify_totp


def _client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class AuthCookieMixin:
    def set_refresh_cookie(self, response: Response, token: str, expires_at) -> None:
        cookie = jwt_conf.JWT_REFRESH_COOKIE
        response.set_cookie(
            cookie.name,
            token,
            max_age=jwt_conf.JWT_REFRESH_TTL_SECONDS,
            expires=expires_at,
            path=cookie.path,
            secure=cookie.secure,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )

    def clear_refresh_cookie(self, response: Response) -> None:
        cookie = jwt_conf.JWT_REFRESH_COOKIE
        response.delete_cookie(cookie.name, path=cookie.path, samesite=cookie.samesite)


class LoginView(AuthCookieMixin, APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "login"

    def _register_failure(self, request, credential: str | None) -> None:
        ip_identifier = f"ip:{_client_ip(request)}"
        delay_ip = register_login_failure(identifier=ip_identifier)
        delay_user = 0
        if credential:
            delay_user = register_login_failure(identifier=f"user:{credential.lower()}")
        delay = max(delay_ip, delay_user)
        if delay:
            time.sleep(delay)

    def _reset_failures(self, request, credential: str | None) -> None:
        reset_login_failures(identifier=f"ip:{_client_ip(request)}")
        if credential:
            reset_login_failures(identifier=f"user:{credential.lower()}")

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            self._register_failure(request, request.data.get("credential"))
            raise
        user = serializer.validated_data["user"]
        credential = serializer.validated_data.get("credential") or request.data.get("credential")
        if (
            settings.AUTH_REQUIRE_2FA_FOR_STAFF
            and (user.is_staff or user.is_superuser)
            and not (hasattr(user, "two_factor") and user.two_factor.is_enabled)
        ):
            raise ValidationError({"detail": "Two-factor authentication is required for staff accounts."})
        two_factor_verified = serializer.validated_data.get("two_factor_verified")
        device_id = serializer.validated_data["device_id"]
        now = timezone.now()
        absolute_expiration = now + timedelta(seconds=jwt_conf.JWT_REFRESH_ABSOLUTE_LIFETIME_SECONDS)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        ip_address = _client_ip(request)
        with transaction.atomic():
            session = AuthSession.objects.create(
                user=user,
                device_id=device_id,
                user_agent=user_agent,
                ip_address=ip_address,
                refresh_token_hash=generate_token_hash(secrets.token_urlsafe(16)),
                current_refresh_jti=secrets.token_hex(8),
                refresh_token_expires_at=absolute_expiration,
                absolute_expiration_at=absolute_expiration,
                last_refreshed_at=now,
                extra={"two_factor_verified": two_factor_verified},
            )
            refresh_token, refresh_jti = issue_refresh_token(user=user, session=session)
            session.update_refresh(
                token=refresh_token,
                jti=refresh_jti,
                ttl_seconds=jwt_conf.JWT_REFRESH_TTL_SECONDS,
            )
        access_token, _ = issue_access_token(
            user=user,
            session=session,
            two_factor_verified=two_factor_verified,
        )
        self._reset_failures(request, credential)
        AuditEvent.objects.create(
            user=user,
            session=session,
            device_id=device_id,
            event_type=AuditEvent.TYPE_LOGIN,
            ip_address=ip_address or None,
            user_agent=user_agent,
            metadata={"used_backup_code": serializer.validated_data.get("used_backup_code", False)},
        )
        response = Response(
            {
                "access": access_token,
                "access_expires_in": jwt_conf.JWT_ACCESS_TTL_SECONDS,
                "session": AuthSessionSerializer(session).data,
                "user": UserSerializer(user).data,
            }
        )
        self.set_refresh_cookie(response, refresh_token, session.refresh_token_expires_at)
        return response


class RefreshView(AuthCookieMixin, APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        cookie = jwt_conf.JWT_REFRESH_COOKIE
        refresh_token = request.COOKIES.get(cookie.name)
        if not refresh_token:
            raise NotAuthenticated("Refresh token cookie missing")
        try:
            payload = decode_jwt(refresh_token, token_type="refresh")
        except JWTDecodeError as exc:
            raise AuthenticationFailed(str(exc)) from exc
        session_id = payload.get("session_id")
        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not session_id or not user_id or not jti:
            raise AuthenticationFailed("Malformed refresh token")
        with transaction.atomic():
            try:
                session = (
                    AuthSession.objects.select_for_update()
                    .select_related("user")
                    .get(id=session_id, user_id=user_id)
                )
            except AuthSession.DoesNotExist as exc:
                raise AuthenticationFailed("Session not found") from exc
            if session.revoked_at:
                raise AuthenticationFailed("Session revoked")
            now = timezone.now()
            if session.absolute_expiration_at <= now:
                session.revoke()
                raise AuthenticationFailed("Session expired")
            incoming_hash = generate_token_hash(refresh_token)
            if (
                incoming_hash != session.refresh_token_hash
                or jti != session.current_refresh_jti
            ):
                if session.used_tokens.filter(token_hash=incoming_hash).exists():
                    session.revoke()
                raise AuthenticationFailed("Refresh token no longer valid")
            session.used_tokens.create(token_hash=incoming_hash)
            refresh_token, refresh_jti = issue_refresh_token(user=session.user, session=session)
            session.update_refresh(
                token=refresh_token,
                jti=refresh_jti,
                ttl_seconds=jwt_conf.JWT_REFRESH_TTL_SECONDS,
            )
        access_token, _ = issue_access_token(
            user=session.user,
            session=session,
            two_factor_verified=session.extra.get("two_factor_verified", False),
        )
        AuditEvent.objects.create(
            user=session.user,
            session=session,
            device_id=session.device_id,
            event_type=AuditEvent.TYPE_REFRESH,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
        )
        response = Response(
            {
                "access": access_token,
                "access_expires_in": jwt_conf.JWT_ACCESS_TTL_SECONDS,
                "session": AuthSessionSerializer(session).data,
            }
        )
        self.set_refresh_cookie(response, refresh_token, session.refresh_token_expires_at)
        return response


class LogoutView(AuthCookieMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        session: AuthSession = getattr(request, "auth_session", None)
        if not session:
            raise NotAuthenticated("No active session")
        session.revoke()
        AuditEvent.objects.create(
            user=request.user,
            session=session,
            device_id=session.device_id,
            event_type=AuditEvent.TYPE_LOGOUT,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
        )
        response = Response(status=status.HTTP_204_NO_CONTENT)
        self.clear_refresh_cookie(response)
        return response


class LogoutAllView(AuthCookieMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        now = timezone.now()
        sessions = AuthSession.objects.filter(user=request.user, revoked_at__isnull=True)
        sessions.update(revoked_at=now)
        AuditEvent.objects.create(
            user=request.user,
            session=None,
            device_id="*",
            event_type=AuditEvent.TYPE_LOGOUT_ALL,
            ip_address=_client_ip(request) or None,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        response = Response(status=status.HTTP_204_NO_CONTENT)
        self.clear_refresh_cookie(response)
        return response


class SessionListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sessions = AuthSession.objects.filter(user=request.user).order_by("-created_at")
        serializer = AuthSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class EmailVerifyRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = create_one_time_token(
            user=request.user,
            purpose=OneTimeToken.PURPOSE_EMAIL_VERIFY,
            lifetime_seconds=1800,
            metadata={"ip": _client_ip(request)},
        )
        send_auth_email(
            template="accounts/emails/email_verify.txt",
            subject="Email verification",
            to_email=request.user.email,
            context={"user": request.user, "token": token},
        )
        AuditEvent.objects.create(
            user=request.user,
            session=getattr(request, "auth_session", None),
            device_id=getattr(request, "auth_session", None).device_id if getattr(request, "auth_session", None) else "",
            event_type=AuditEvent.TYPE_EMAIL_VERIFY_REQUEST,
            ip_address=_client_ip(request) or None,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailVerifyConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                record = consume_one_time_token(
                    token=serializer.validated_data["token"],
                    purpose=OneTimeToken.PURPOSE_EMAIL_VERIFY,
                )
                user = record.user
                user.email_verified = True
                user.email_verified_at = timezone.now()
                user.save(update_fields=["email_verified", "email_verified_at"])
        except ValueError as exc:
            raise ValidationError({"token": str(exc)})
        AuditEvent.objects.create(
            user=user,
            session=None,
            device_id="",
            event_type=AuditEvent.TYPE_EMAIL_VERIFY_CONFIRM,
            ip_address=record.request_metadata.get("ip"),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        token = create_one_time_token(
            user=user,
            purpose=OneTimeToken.PURPOSE_PASSWORD_RESET,
            lifetime_seconds=1800,
            metadata={"ip": _client_ip(request)},
        )
        send_auth_email(
            template="accounts/emails/password_reset.txt",
            subject="Password reset",
            to_email=user.email,
            context={"user": user, "token": token},
        )
        AuditEvent.objects.create(
            user=user,
            session=None,
            device_id="",
            event_type=AuditEvent.TYPE_PASSWORD_RESET_REQUEST,
            ip_address=_client_ip(request) or None,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                record = consume_one_time_token(
                    token=serializer.validated_data["token"],
                    purpose=OneTimeToken.PURPOSE_PASSWORD_RESET,
                )
                user = record.user
                user.set_password(serializer.validated_data["new_password"])
                user.save(update_fields=["password"])
        except ValueError as exc:
            raise ValidationError({"token": str(exc)})
        AuditEvent.objects.create(
            user=user,
            session=None,
            device_id="",
            event_type=AuditEvent.TYPE_PASSWORD_RESET_CONFIRM,
            ip_address=record.request_metadata.get("ip"),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailChangeRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = EmailChangeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data["new_email"]
        token = create_one_time_token(
            user=request.user,
            purpose=OneTimeToken.PURPOSE_EMAIL_CHANGE,
            lifetime_seconds=1800,
            payload={"new_email": new_email},
            metadata={"ip": _client_ip(request)},
        )
        send_auth_email(
            template="accounts/emails/email_change.txt",
            subject="Email change confirmation",
            to_email=new_email,
            context={"user": request.user, "token": token},
        )
        AuditEvent.objects.create(
            user=request.user,
            session=getattr(request, "auth_session", None),
            device_id=getattr(request, "auth_session", None).device_id if getattr(request, "auth_session", None) else "",
            event_type=AuditEvent.TYPE_EMAIL_CHANGE_REQUEST,
            ip_address=_client_ip(request) or None,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            metadata={"new_email": new_email},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmailChangeConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = EmailChangeConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                record = consume_one_time_token(
                    token=serializer.validated_data["token"],
                    purpose=OneTimeToken.PURPOSE_EMAIL_CHANGE,
                )
                user = record.user
                payload = record.payload or {}
                new_email = payload.get("new_email")
                if not new_email:
                    raise ValueError("Token missing new email")
                user.email = new_email
                user.email_verified = False
                user.email_verified_at = None
                user.save(update_fields=["email", "email_verified", "email_verified_at"])
        except ValueError as exc:
            raise ValidationError({"token": str(exc)})
        AuditEvent.objects.create(
            user=user,
            session=None,
            device_id="",
            event_type=AuditEvent.TYPE_EMAIL_CHANGE_CONFIRM,
            ip_address=record.request_metadata.get("ip"),
            metadata={"new_email": new_email},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TwoFactorSetupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        config, uri = generate_provisioning_uri(request.user)
        return Response({"secret": config.secret, "provisioning_uri": uri})


class TwoFactorConfirmView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = TwoFactorSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        config = ensure_config(request.user)
        if not verify_totp(config, serializer.validated_data["otp_code"]):
            raise ValidationError({"otp_code": "Invalid TOTP code"})
        config.is_enabled = True
        config.confirmed_at = timezone.now()
        config.save(update_fields=["is_enabled", "confirmed_at", "updated_at"])
        AuditEvent.objects.create(
            user=request.user,
            session=getattr(request, "auth_session", None),
            device_id=getattr(request, "auth_session", None).device_id if getattr(request, "auth_session", None) else "",
            event_type=AuditEvent.TYPE_2FA_ENABLED,
            ip_address=_client_ip(request) or None,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TwoFactorBackupCodesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        config = ensure_config(request.user)
        available = config.backup_codes.filter(used_at__isnull=True).count()
        data = {
            "available": available,
            "generated_at": config.backup_codes_generated_at,
        }
        return Response(data)

    def post(self, request, *args, **kwargs):
        config = ensure_config(request.user)
        codes = generate_backup_codes(config)
        AuditEvent.objects.create(
            user=request.user,
            session=getattr(request, "auth_session", None),
            device_id=getattr(request, "auth_session", None).device_id if getattr(request, "auth_session", None) else "",
            event_type=AuditEvent.TYPE_2FA_ENABLED,
            ip_address=_client_ip(request) or None,
            metadata={"backup_codes_regenerated": True},
        )
        return Response({"codes": codes})


class TwoFactorDisableView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        config = ensure_config(request.user)
        config.is_enabled = False
        config.save(update_fields=["is_enabled", "updated_at"])
        config.backup_codes.all().delete()
        AuditEvent.objects.create(
            user=request.user,
            session=getattr(request, "auth_session", None),
            device_id=getattr(request, "auth_session", None).device_id if getattr(request, "auth_session", None) else "",
            event_type=AuditEvent.TYPE_2FA_DISABLED,
            ip_address=_client_ip(request) or None,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
