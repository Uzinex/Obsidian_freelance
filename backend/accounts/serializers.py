import secrets
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from marketplace.models import Skill
from obsidian_backend.ai import tldr as tldr_cache

from .models import (
    AuditEvent,
    AuthSession,
    OneTimeToken,
    PendingRegistration,
    Profile,
    User,
    UsedRefreshToken,
    VerificationRequest,
    Wallet,
    WalletTransaction,
    generate_token_hash,
)
from .otp import generate_otp
from .recaptcha import RecaptchaVerificationError, verify_recaptcha
from .emails import send_registration_code_email
from .security import captcha_required
from .twofactor import ensure_config, use_backup_code, verify_totp


REGISTRATION_LIMIT_WINDOW = timedelta(hours=24)


def _normalize_gmail(email: str) -> str:
    local_part, _, domain = email.partition("@")
    domain_lower = domain.lower()
    if domain_lower not in {"gmail.com", "googlemail.com"}:
        return ""
    normalized_local = local_part.split("+", 1)[0].replace(".", "")
    return f"{normalized_local}@gmail.com"


def _registration_counter_key(prefix: str, identifier: str) -> str:
    return f"register:{prefix}:{identifier}".lower()


def _increment_registration_counter(prefix: str, identifier: str) -> bool:
    if not identifier:
        return True
    limit = getattr(settings, "ACCOUNTS_REGISTRATION_DAILY_LIMIT", 5)
    if limit <= 0:
        return True
    window_seconds = int(
        getattr(settings, "ACCOUNTS_REGISTRATION_TTL_SECONDS", 60 * 60 * 24)
    )
    key = _registration_counter_key(prefix, identifier)
    now = timezone.now()
    payload = cache.get(key)
    if not payload:
        cache.set(
            key,
            {"count": 1, "expires": now.timestamp() + window_seconds},
            timeout=window_seconds,
        )
        return True
    expires = payload.get("expires", 0)
    remaining = expires - now.timestamp()
    if remaining <= 0:
        cache.set(
            key,
            {"count": 1, "expires": now.timestamp() + window_seconds},
            timeout=window_seconds,
        )
        return True
    count = int(payload.get("count", 0))
    if count >= limit:
        return False
    payload["count"] = count + 1
    cache.set(key, payload, timeout=int(max(1, remaining)))
    return True


def _client_ip_from_request(request) -> str:
    if not request:
        return ""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "nickname",
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "birth_year",
            "email_verified",
            "email_verified_at",
        )
        read_only_fields = ("id", "email_verified", "email_verified_at")


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "nickname",
            "email",
            "first_name",
            "last_name",
            "patronymic",
            "birth_year",
            "password",
            "password_confirm",
        )

    def validate_birth_year(self, value):
        current_year = date.today().year
        if value and current_year - value < 16:
            raise serializers.ValidationError(
                _("Users must be at least 16 years old to register.")
            )
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.pop("password_confirm", None):
            raise serializers.ValidationError({"password": _("Passwords do not match")})
        try:
            validate_password(attrs["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegistrationStartSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    patronymic = serializers.CharField(max_length=150, required=False, allow_blank=True)
    nickname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    birth_year = serializers.IntegerField(required=False)
    password = serializers.CharField(write_only=True)
    captcha = serializers.CharField(write_only=True)
    locale = serializers.ChoiceField(choices=[("ru", "ru"), ("uz", "uz")], default="ru")
    terms_accepted = serializers.BooleanField()

    default_message = _(
        "Если e-mail корректен, мы отправили код подтверждения на указанную почту."
    )

    def validate_birth_year(self, value):
        if not value:
            return value
        current_year = date.today().year
        if current_year - value < 16:
            raise serializers.ValidationError(
                _("Users must be at least 16 years old to register."),
            )
        return value

    def validate_terms_accepted(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(
                _("Consent to the Terms and Privacy Policy is required."),
            )
        return value

    def validate_nickname(self, value: str) -> str:
        if User.objects.filter(nickname__iexact=value).exists():
            raise serializers.ValidationError(_("This nickname is already taken."))
        return value

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        captcha_token = attrs.get("captcha")
        try:
            verify_recaptcha(token=captcha_token, remote_ip=_client_ip_from_request(request))
        except RecaptchaVerificationError as exc:
            raise serializers.ValidationError({"captcha": str(exc)}) from exc
        email = attrs.get("email", "").strip().lower()
        attrs["email"] = email
        attrs["normalized_email"] = _normalize_gmail(email)
        attrs["client_ip"] = _client_ip_from_request(request)
        attrs["user_agent"] = request.META.get("HTTP_USER_AGENT", "") if request else ""
        attrs["email_exists"] = User.objects.filter(email__iexact=email).exists()
        return attrs

    def save(self, **kwargs):
        cooldown = getattr(
            settings, "ACCOUNTS_REGISTRATION_RESEND_COOLDOWN_SECONDS", 60
        )
        if self.validated_data.get("email_exists"):
            return {"email_sent": False, "message": self.default_message, "cooldown": cooldown}
        email = self.validated_data["email"]
        ip_address = self.validated_data.get("client_ip", "")
        now = timezone.now()
        ttl = getattr(settings, "ACCOUNTS_REGISTRATION_TTL_SECONDS", 60 * 60 * 24)
        otp_payload = generate_otp()
        locale = self.validated_data.get("locale", "ru")
        with transaction.atomic():
            password_hash = make_password(self.validated_data["password"])
            max_attempts = getattr(settings, "ACCOUNTS_OTP_MAX_ATTEMPTS", 5)
            defaults = {
                "normalized_email": self.validated_data.get("normalized_email", ""),
                "nickname": self.validated_data["nickname"],
                "first_name": self.validated_data["first_name"],
                "last_name": self.validated_data["last_name"],
                "patronymic": self.validated_data.get("patronymic", ""),
                "birth_year": self.validated_data.get("birth_year"),
                "locale": locale,
                "ip_address": ip_address or None,
                "user_agent": self.validated_data.get("user_agent", ""),
                "expires_at": now + timedelta(seconds=ttl),
                "password_hash": password_hash,
                "otp_hash": otp_payload.hash,
                "otp_salt": otp_payload.salt,
                "otp_expires_at": otp_payload.expires_at,
                "attempts_left": max_attempts,
            }
            pending, created = PendingRegistration.objects.select_for_update().get_or_create(
                email=email,
                defaults=defaults,
            )
            if not created and pending.is_expired:
                for field, value in defaults.items():
                    setattr(pending, field, value)
                pending.send_count = 0
            if pending.send_count >= getattr(settings, "ACCOUNTS_REGISTRATION_DAILY_LIMIT", 5):
                raise serializers.ValidationError(
                    {"detail": _("Лимит отправок кода исчерпан. Повторите попытку завтра.")}
                )
            if pending.resend_available_at and pending.resend_available_at > now:
                remaining = int((pending.resend_available_at - now).total_seconds())
                raise serializers.ValidationError(
                    {
                        "detail": _("Запрос уже отправлен. Подождите %(seconds)s секунд.")
                        % {"seconds": remaining}
                    }
                )
            if not _increment_registration_counter("email", email):
                raise serializers.ValidationError(
                    {"detail": _("Превышено количество кодов на этот e-mail. Попробуйте позже.")}
                )
            if not _increment_registration_counter("ip", ip_address):
                raise serializers.ValidationError(
                    {"detail": _("С этого адреса отправлено слишком много кодов. Попробуйте позже.")}
                )
            for field, value in defaults.items():
                setattr(pending, field, value)
            pending.set_otp(otp_payload)
            pending.mark_code_sent(sent_at=now)
            pending.expires_at = now + timedelta(seconds=ttl)
            pending.save()
        send_registration_code_email(
            to_email=email,
            code=otp_payload.code,
            locale=locale,
        )
        return {
            "email_sent": True,
            "message": self.default_message,
            "cooldown": cooldown,
        }


class RegistrationResendSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField(write_only=True)

    def validate(self, attrs):
        request = self.context.get("request")
        try:
            verify_recaptcha(token=attrs.get("captcha"), remote_ip=_client_ip_from_request(request))
        except RecaptchaVerificationError as exc:
            raise serializers.ValidationError({"captcha": str(exc)}) from exc
        email = attrs.get("email", "").strip().lower()
        attrs["email"] = email
        attrs["client_ip"] = _client_ip_from_request(request)
        return attrs

    def save(self, **kwargs):
        email = self.validated_data["email"]
        now = timezone.now()
        ip_address = self.validated_data.get("client_ip", "")
        with transaction.atomic():
            try:
                pending = PendingRegistration.objects.select_for_update().get(email=email)
            except PendingRegistration.DoesNotExist:
                return {"email_sent": False}
            if pending.is_expired:
                pending.delete()
                return {"email_sent": False}
            if pending.resend_available_at and pending.resend_available_at > now:
                remaining = int((pending.resend_available_at - now).total_seconds())
                raise serializers.ValidationError(
                    {
                        "detail": _("Запрос уже отправлен. Подождите %(seconds)s секунд.")
                        % {"seconds": remaining}
                    }
                )
            if pending.send_count >= getattr(settings, "ACCOUNTS_REGISTRATION_DAILY_LIMIT", 5):
                raise serializers.ValidationError(
                    {"detail": _("Лимит отправок кода исчерпан. Повторите попытку завтра.")}
                )
            if not _increment_registration_counter("email", email):
                raise serializers.ValidationError(
                    {"detail": _("Превышено количество кодов на этот e-mail. Попробуйте позже.")}
                )
            if not _increment_registration_counter("ip", ip_address):
                raise serializers.ValidationError(
                    {"detail": _("С этого адреса отправлено слишком много кодов. Попробуйте позже.")}
                )
            otp_payload = generate_otp()
            pending.set_otp(otp_payload)
            pending.mark_code_sent(sent_at=now)
            pending.save()
        send_registration_code_email(
            to_email=pending.email,
            code=otp_payload.code,
            locale=pending.locale,
        )
        cooldown = getattr(
            settings, "ACCOUNTS_REGISTRATION_RESEND_COOLDOWN_SECONDS", 60
        )
        return {
            "email_sent": True,
            "cooldown": cooldown,
        }


class RegistrationVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    auto_login = serializers.BooleanField(default=True)
    device_id = serializers.CharField(max_length=128, required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        code = attrs.get("code")
        attrs["email"] = email
        with transaction.atomic():
            try:
                pending = (
                    PendingRegistration.objects.select_for_update().get(email=email)
                )
            except PendingRegistration.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"code": _("Неверный код подтверждения.")}
                ) from exc
            if pending.is_expired:
                pending.delete()
                raise serializers.ValidationError({"code": _("Код истёк. Запросите новый.")})
            if pending.is_locked:
                raise serializers.ValidationError(
                    {"code": _("Слишком много неверных попыток. Попробуйте позже.")}
                )
            if not pending.verify_code(code):
                raise serializers.ValidationError({"code": _("Неверный код подтверждения.")})
        attrs["pending"] = pending
        attrs.setdefault("device_id", secrets.token_hex(16))
        return attrs

    def save(self, **kwargs):
        pending: PendingRegistration = self.validated_data["pending"]
        now = timezone.now()
        with transaction.atomic():
            if User.objects.filter(email__iexact=pending.email).exists():
                pending.delete()
                raise serializers.ValidationError(
                    {"detail": _("Такой e-mail уже используется. Попробуйте войти.")}
                )
            if User.objects.filter(nickname__iexact=pending.nickname).exists():
                pending.delete()
                raise serializers.ValidationError(
                    {"detail": _("Никнейм уже занят. Начните регистрацию заново.")}
                )
            user = User(
                nickname=pending.nickname,
                email=pending.email,
                first_name=pending.first_name,
                last_name=pending.last_name,
                patronymic=pending.patronymic,
                birth_year=pending.birth_year,
                email_verified=True,
                email_verified_at=now,
            )
            user.password = pending.password_hash
            user.save()
            pending.delete()
        return {
            "user": user,
            "device_id": self.validated_data.get("device_id"),
            "auto_login": self.validated_data.get("auto_login", True),
        }


class LoginSerializer(serializers.Serializer):
    credential = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})
    device_id = serializers.CharField(max_length=128, required=False, allow_blank=True)
    otp_code = serializers.CharField(required=False, allow_blank=True)
    backup_code = serializers.CharField(required=False, allow_blank=True)
    captcha = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        request = self.context.get("request")
        credential = attrs.get("credential")
        password = attrs.get("password")
        if captcha_required():
            captcha_value = attrs.get("captcha")
            if not captcha_value:
                raise serializers.ValidationError(
                    {"captcha": _("Captcha challenge is required.")}
                )
            from .security import captcha_hook  # local import to avoid circular deps

            captcha_hook({"credential": credential, "request": request})
        if not credential or not password:
            raise serializers.ValidationError(
                _("Must include 'credential' and 'password'."),
                code="authorization",
            )
        user = authenticate(
            request=request,
            nickname=credential,
            password=password,
        )
        if not user:
            try:
                user_obj = User.objects.get(email__iexact=credential)
            except User.DoesNotExist as exc:
                raise serializers.ValidationError(
                    _("Unable to log in with provided credentials."),
                    code="authorization",
                ) from exc
            user = authenticate(
                request=request,
                nickname=user_obj.nickname,
                password=password,
            )
        if not user:
            raise serializers.ValidationError(
                _("Unable to log in with provided credentials."),
                code="authorization",
            )
        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": _("User account is disabled.")}
            )
        device_id = attrs.get("device_id") or secrets.token_hex(16)
        attrs["user"] = user
        attrs["credential"] = credential
        attrs["device_id"] = device_id
        two_factor_required = False
        two_factor_verified = False
        used_backup_code = False
        if hasattr(user, "two_factor") and user.two_factor.is_enabled:
            two_factor_required = True
            otp_code = attrs.get("otp_code")
            backup_code = attrs.get("backup_code")
            config = user.two_factor
            if otp_code and verify_totp(config, otp_code):
                two_factor_verified = True
            elif backup_code and use_backup_code(config, backup_code):
                two_factor_verified = True
                used_backup_code = True
            else:
                raise serializers.ValidationError(
                    {"otp_code": _("Invalid or missing two-factor authentication code.")}
                )
        attrs["two_factor_required"] = two_factor_required
        attrs["two_factor_verified"] = two_factor_verified
        attrs["used_backup_code"] = used_backup_code
        return attrs


class AuthSessionSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField()
    two_factor_verified = serializers.SerializerMethodField()

    class Meta:
        model = AuthSession
        fields = (
            "id",
            "device_id",
            "user_agent",
            "ip_address",
            "created_at",
            "last_refreshed_at",
            "refresh_token_expires_at",
            "absolute_expiration_at",
            "revoked_at",
            "is_active",
            "two_factor_verified",
        )
        read_only_fields = fields

    def get_is_active(self, obj: AuthSession) -> bool:
        return obj.is_active

    def get_two_factor_verified(self, obj: AuthSession) -> bool:
        return obj.extra.get("two_factor_verified", False)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class EmailTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class EmailVerificationRequestSerializer(serializers.Serializer):
    pass


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value: str) -> str:
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value


class EmailChangeRequestSerializer(serializers.Serializer):
    new_email = serializers.EmailField()


class EmailChangeConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()


class TwoFactorSetupSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=True)


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Skill.objects.none()
    )
    wallet = serializers.SerializerMethodField()
    contracts = serializers.SerializerMethodField()
    staff_roles = serializers.SerializerMethodField()
    tldr = serializers.SerializerMethodField()
    NULLABLE_STRING_FIELDS = {
        "freelancer_type",
        "company_name",
        "company_country",
        "company_city",
        "company_street",
        "company_tax_id",
        "phone_number",
        "country",
        "city",
        "street",
        "house",
        "headline",
    }

    class Meta:
        model = Profile
        fields = (
            "id",
            "slug",
            "user",
            "role",
            "headline",
            "bio",
            "freelancer_type",
            "company_name",
            "company_country",
            "company_city",
            "company_street",
            "company_registered_as",
            "company_tax_id",
            "phone_number",
            "avatar",
            "skills",
            "hourly_rate",
            "min_budget",
            "availability",
            "timezone",
            "languages",
            "location",
            "links",
            "visibility",
            "country",
            "city",
            "street",
            "house",
            "is_completed",
            "is_verified",
            "last_activity_at",
            "wallet",
            "contracts",
            "staff_roles",
            "tldr",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "is_verified",
            "last_activity_at",
            "created_at",
            "updated_at",
            "wallet",
            "contracts",
            "staff_roles",
            "tldr",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        skills_field = self.fields.get("skills")
        if skills_field is not None:
            skills_queryset = Skill.objects.all()
            if hasattr(skills_field, "child_relation"):
                skills_field.child_relation.queryset = skills_queryset
            else:  # pragma: no cover - fallback for unexpected field types
                skills_field.queryset = skills_queryset

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user
        skills = validated_data.pop("skills", [])
        profile = super().create(validated_data)
        if skills:
            profile.skills.set(skills)
        profile.is_completed = True
        profile.save(update_fields=["is_completed"])
        return profile

    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        freelancer_type = attrs.get(
            "freelancer_type", getattr(self.instance, "freelancer_type", None)
        )
        company_name = attrs.get("company_name")
        if role == Profile.ROLE_FREELANCER and freelancer_type == Profile.FREELANCER_TYPE_COMPANY:
            if not company_name:
                raise serializers.ValidationError(
                    {"company_name": _("Company freelancers must provide a company name.")}
                )
        return attrs

    def update(self, instance, validated_data):
        skills = validated_data.pop("skills", None)
        profile = super().update(instance, validated_data)
        if skills is not None:
            profile.skills.set(skills)
        profile.is_completed = True
        profile.save()
        return profile

    def to_internal_value(self, data):
        mutable_data = data.copy() if hasattr(data, "copy") else dict(data)
        for field in self.NULLABLE_STRING_FIELDS:
            if mutable_data.get(field, serializers.empty) is None:
                mutable_data[field] = ""
        company_registered_as = mutable_data.get("company_registered_as", serializers.empty)
        if company_registered_as in {None, ""}:
            mutable_data["company_registered_as"] = Profile.REGISTRATION_TYPE_NONE
        return super().to_internal_value(mutable_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.skills.exists():
            data["skill_details"] = [
                {"id": skill.id, "name": skill.name, "category": skill.category.name}
                for skill in instance.skills.all()
            ]
        else:
            data["skill_details"] = []
        return data

    def _resolve_locale(self) -> str:
        request = self.context.get("request")
        if request is not None:
            header = request.headers.get("Accept-Language")
            if header:
                return header.split(",")[0].strip() or "ru"
        return self.context.get("locale", "ru")

    def get_tldr(self, instance: Profile) -> str | None:
        locale = self._resolve_locale()
        return tldr_cache.get_tldr(
            entity="profile",
            pk=instance.pk,
            locale=locale,
            fetcher=instance.get_tldr,
        )

    def get_wallet(self, instance: Profile):
        wallet: Wallet | None = getattr(instance, "wallet", None)
        if wallet is None:
            return None
        serializer = WalletSerializer(wallet, context=self.context)
        return serializer.data

    def get_staff_roles(self, instance: Profile):
        from accounts import rbac

        return sorted(rbac.get_user_roles(instance.user))

    def get_contracts(self, instance: Profile):
        from marketplace.models import Contract

        request = self.context.get("request")
        contracts = Contract.objects.filter(
            models.Q(client=instance) | models.Q(freelancer=instance)
        ).select_related("order")
        summary = []
        for contract in contracts:
            role = "client" if contract.client_id == instance.id else "freelancer"
            summary.append(
                {
                    "id": contract.id,
                    "order_id": contract.order_id,
                    "order_title": contract.order.title,
                    "status": contract.status,
                    "budget": str(contract.budget_snapshot),
                    "currency": contract.currency,
                    "role": role,
                    "client_signed_at": contract.client_signed_at,
                    "freelancer_signed_at": contract.freelancer_signed_at,
                    "signed_at": contract.signed_at,
                    "termination_requested_by": contract.termination_requested_by,
                    "termination_reason": contract.termination_reason,
                    "termination_requested_at": contract.termination_requested_at,
                }
            )
        if request is not None:
            # Ensure datetimes are rendered using DRF settings
            dt_field = serializers.DateTimeField()
            for item in summary:
                for key in (
                    "client_signed_at",
                    "freelancer_signed_at",
                    "signed_at",
                    "termination_requested_at",
                ):
                    if item[key] is not None:
                        item[key] = dt_field.to_representation(item[key])
        return summary


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = (
            "id",
            "amount",
            "balance_after",
            "type",
            "description",
            "created_at",
            "related_contract",
        )
        read_only_fields = fields


class WalletSerializer(serializers.ModelSerializer):
    transactions = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ("id", "balance", "currency", "transactions")
        read_only_fields = fields

    def get_transactions(self, obj: Wallet):
        limit = self.context.get("transaction_limit", 10)
        queryset = obj.transactions.all()[:limit]
        return WalletTransactionSerializer(queryset, many=True).data
class VerificationRequestSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    profile_details = ProfileSerializer(source="profile", read_only=True)
    reviewer = UserSerializer(source="reviewed_by", read_only=True)

    class Meta:
        model = VerificationRequest
        fields = (
            "id",
            "profile",
            "profile_details",
            "document_type",
            "document_series",
            "document_number",
            "document_image",
            "status",
            "created_at",
            "reviewed_at",
            "reviewer_note",
            "reviewer",
        )
        read_only_fields = (
            "status",
            "created_at",
            "reviewed_at",
            "reviewer_note",
            "reviewer",
            "profile_details",
        )

    def _get_profile(self) -> Profile:
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            raise serializers.ValidationError(
                {
                    "detail": [
                        _("Authentication credentials were not provided."),
                    ]
                }
            )
        try:
            return user.profile
        except Profile.DoesNotExist as exc:
            raise serializers.ValidationError(
                {
                    "profile": [
                        _(
                            "Перед отправкой заявки заполните профиль пользователя."
                        )
                    ]
                }
            ) from exc

    def validate(self, attrs):
        profile = self._get_profile()
        if profile.verification_requests.filter(
            status=VerificationRequest.STATUS_PENDING
        ).exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        _(
                            "У вас уже есть заявка на рассмотрении. Дождитесь решения администратора."
                        )
                    ]
                }
            )
        attrs["profile"] = profile
        return attrs

    def create(self, validated_data):
        profile = validated_data["profile"]
        profile.is_verified = False
        profile.save(update_fields=["is_verified"])
        return super().create(validated_data)
