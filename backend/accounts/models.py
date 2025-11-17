from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
import hashlib
import secrets
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.postgres.indexes import GinIndex
from django.db import models, transaction
from django.utils import timezone


class User(AbstractUser):
    """Custom user model that uses a nickname instead of a username."""

    username = None
    nickname = models.CharField(max_length=150, unique=True)
    email = models.EmailField("Gmail address", unique=True)
    patronymic = models.CharField(max_length=150, blank=True)
    birth_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900)],
        null=True,
        blank=True,
        help_text="Year of birth (must be 16+ to use the platform)",
    )
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "nickname"
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return self.nickname

    @property
    def full_name(self) -> str:
        base = f"{self.last_name} {self.first_name}".strip()
        if self.patronymic:
            return f"{base} {self.patronymic}".strip()
        return base


class Profile(models.Model):
    ROLE_FREELANCER = "freelancer"
    ROLE_CLIENT = "client"
    ROLE_CHOICES = [
        (ROLE_FREELANCER, "Freelancer"),
        (ROLE_CLIENT, "Client"),
    ]

    FREELANCER_TYPE_COMPANY = "company"
    FREELANCER_TYPE_INDIVIDUAL = "individual"
    FREELANCER_TYPE_CHOICES = [
        (FREELANCER_TYPE_COMPANY, "Company"),
        (FREELANCER_TYPE_INDIVIDUAL, "Individual"),
    ]

    REGISTRATION_TYPE_NONE = "none"
    REGISTRATION_TYPE_MCHJ = "mchj"
    REGISTRATION_TYPE_YATT = "yatt"
    REGISTRATION_TYPE_CHOICES = [
        (REGISTRATION_TYPE_NONE, "Not registered"),
        (REGISTRATION_TYPE_MCHJ, "MCHJ"),
        (REGISTRATION_TYPE_YATT, "YATT"),
    ]

    CONTACT_PREF_PLATFORM = "platform"
    CONTACT_PREF_EMAIL = "email"
    CONTACT_PREF_PHONE = "phone"
    CONTACT_PREF_CHOICES = [
        (CONTACT_PREF_PLATFORM, "Platform"),
        (CONTACT_PREF_EMAIL, "Email"),
        (CONTACT_PREF_PHONE, "Phone"),
    ]

    AVAILABILITY_FULL_TIME = "full_time"
    AVAILABILITY_PART_TIME = "part_time"
    AVAILABILITY_PROJECT = "project"
    AVAILABILITY_CHOICES = [
        (AVAILABILITY_FULL_TIME, "Full-time"),
        (AVAILABILITY_PART_TIME, "Part-time"),
        (AVAILABILITY_PROJECT, "Project-based"),
    ]

    VISIBILITY_PUBLIC = "public"
    VISIBILITY_PRIVATE = "private"
    VISIBILITY_LINK_ONLY = "link_only"
    VISIBILITY_CHOICES = [
        (VISIBILITY_PUBLIC, "Public"),
        (VISIBILITY_PRIVATE, "Private"),
        (VISIBILITY_LINK_ONLY, "Link-only"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    slug = models.SlugField(
        max_length=160, unique=True, default=uuid.uuid4, db_index=False
    )
    headline = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    tldr_ru = models.TextField(blank=True)
    tldr_uz = models.TextField(blank=True)
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    min_budget = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, blank=True
    )
    timezone = models.CharField(max_length=64, blank=True)
    languages = models.JSONField(default=list, blank=True)
    location = models.JSONField(default=dict, blank=True)
    links = models.JSONField(default=list, blank=True)
    contact_pref = models.CharField(
        max_length=20,
        choices=CONTACT_PREF_CHOICES,
        default=CONTACT_PREF_PLATFORM,
    )
    visibility = models.CharField(
        max_length=20, choices=VISIBILITY_CHOICES, default=VISIBILITY_PUBLIC
    )
    freelancer_type = models.CharField(
        max_length=20, choices=FREELANCER_TYPE_CHOICES, blank=True
    )
    company_name = models.CharField(max_length=255, blank=True)
    company_country = models.CharField(max_length=120, blank=True)
    company_city = models.CharField(max_length=120, blank=True)
    company_street = models.CharField(max_length=120, blank=True)
    company_registered_as = models.CharField(
        max_length=20,
        choices=REGISTRATION_TYPE_CHOICES,
        default=REGISTRATION_TYPE_NONE,
    )
    company_tax_id = models.CharField(max_length=64, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    skills = models.ManyToManyField(
        "marketplace.Skill", blank=True, related_name="profiles"
    )
    country = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, blank=True)
    street = models.CharField(max_length=120, blank=True)
    house = models.CharField(max_length=120, blank=True)
    is_completed = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            GinIndex(fields=["languages"], name="profile_languages_gin"),
            models.Index(fields=["hourly_rate", "min_budget"], name="profile_rate_idx"),
            models.Index(fields=["is_verified", "visibility"], name="profile_verified_idx"),
            models.Index(fields=["last_activity_at"], name="profile_last_activity_idx"),
            models.Index(
                fields=["slug"],
                name="profile_slug_like_idx",
                opclasses=["varchar_pattern_ops"],
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Profile of {self.user.nickname}"

    @property
    def display_role(self) -> str:
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    def get_tldr(self, locale: str = "ru") -> str:
        normalized = (locale or "ru").lower()
        if normalized.startswith("uz"):
            return self.tldr_uz or self.tldr_ru
        return self.tldr_ru or self.tldr_uz

    def set_tldr(self, locale: str, value: str) -> None:
        normalized = (locale or "ru").lower()
        if normalized.startswith("uz"):
            self.tldr_uz = value
        else:
            self.tldr_ru = value


class Wallet(models.Model):
    """Simple wallet model that stores the balance in Uzbek sums."""

    CURRENCY_UZS = "UZS"

    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    currency = models.CharField(max_length=10, default=CURRENCY_UZS)

    class Meta:
        ordering = ["profile__user__nickname"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Wallet({self.profile.user.nickname}: {self.balance} {self.currency})"

    def _apply_change(
        self,
        amount: Decimal,
        *,
        transaction_type: str,
        description: str = "",
        related_contract: "marketplace.Contract" | None = None,
    ) -> "WalletTransaction":
        if amount == 0:
            raise ValueError("Amount must be non-zero for wallet operations")
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            new_balance = wallet.balance + amount
            if new_balance < Decimal("0.00"):
                raise ValueError("Insufficient funds in wallet")
            wallet.balance = new_balance
            wallet.save(update_fields=["balance"])
            transaction_record = wallet.transactions.create(
                amount=amount,
                balance_after=new_balance,
                type=transaction_type,
                description=description,
                related_contract=related_contract,
            )
        self.refresh_from_db(fields=["balance"])
        return transaction_record

    def deposit(
        self,
        amount: Decimal,
        *,
        description: str = "",
        related_contract: "marketplace.Contract" | None = None,
    ) -> "WalletTransaction":
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero")
        return self._apply_change(
            amount,
            transaction_type=WalletTransaction.TYPE_DEPOSIT,
            description=description,
            related_contract=related_contract,
        )

    def withdraw(
        self,
        amount: Decimal,
        *,
        description: str = "",
        related_contract: "marketplace.Contract" | None = None,
    ) -> "WalletTransaction":
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero")
        return self._apply_change(
            -amount,
            transaction_type=WalletTransaction.TYPE_WITHDRAW,
            description=description,
            related_contract=related_contract,
        )

    def transfer_to(
        self,
        target: "Wallet",
        amount: Decimal,
        *,
        description: str = "",
        related_contract: "marketplace.Contract" | None = None,
        outgoing_type: str | None = None,
        incoming_type: str | None = None,
    ) -> tuple["WalletTransaction", "WalletTransaction"]:
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("Transfer amount must be greater than zero")
        outgoing_type = outgoing_type or WalletTransaction.TYPE_TRANSFER_OUT
        incoming_type = incoming_type or WalletTransaction.TYPE_TRANSFER_IN
        with transaction.atomic():
            outgoing = self._apply_change(
                -amount,
                transaction_type=outgoing_type,
                description=description,
                related_contract=related_contract,
            )
            incoming = target._apply_change(
                amount,
                transaction_type=incoming_type,
                description=description,
                related_contract=related_contract,
            )
        return outgoing, incoming


class WalletTransaction(models.Model):
    TYPE_DEPOSIT = "deposit"
    TYPE_WITHDRAW = "withdraw"
    TYPE_TRANSFER_IN = "transfer_in"
    TYPE_TRANSFER_OUT = "transfer_out"
    TYPE_PAYOUT = "payout"
    TYPE_COMPENSATION = "compensation"
    TYPE_CHOICES = [
        (TYPE_DEPOSIT, "Deposit"),
        (TYPE_WITHDRAW, "Withdraw"),
        (TYPE_TRANSFER_IN, "Incoming transfer"),
        (TYPE_TRANSFER_OUT, "Outgoing transfer"),
        (TYPE_PAYOUT, "Contract payout"),
        (TYPE_COMPENSATION, "Contract compensation"),
    ]

    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2)
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    related_contract = models.ForeignKey(
        "marketplace.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="wallet_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"{self.wallet.profile.user.nickname}: {self.amount} ({self.type})"


class VerificationRequest(models.Model):
    DOCUMENT_DRIVER_LICENSE = "driver_license"
    DOCUMENT_PASSPORT = "passport"
    DOCUMENT_ID_CARD = "id_card"
    DOCUMENT_CHOICES = [
        (DOCUMENT_DRIVER_LICENSE, "Driver License"),
        (DOCUMENT_PASSPORT, "Passport"),
        (DOCUMENT_ID_CARD, "ID Card"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="verification_requests"
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_CHOICES)
    document_series = models.CharField(max_length=50)
    document_number = models.CharField(max_length=50)
    document_image = models.ImageField(upload_to="verifications/")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewer_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_verifications",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Verification request"
        verbose_name_plural = "Verification requests"

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Verification({self.profile.user.nickname}, {self.document_type})"


def generate_token_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


class AuthSession(models.Model):
    """Active refresh-token registry with session metadata."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auth_sessions",
    )
    device_id = models.CharField(max_length=128)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    refresh_token_hash = models.CharField(max_length=128)
    current_refresh_jti = models.CharField(max_length=64)
    refresh_token_expires_at = models.DateTimeField()
    absolute_expiration_at = models.DateTimeField()
    last_refreshed_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "device_id"]),
            models.Index(fields=["user", "revoked_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"AuthSession({self.user_id}, {self.device_id})"

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.refresh_token_expires_at > timezone.now()

    def revoke(self, *, commit: bool = True) -> None:
        if self.revoked_at:
            return
        self.revoked_at = timezone.now()
        if commit:
            self.save(update_fields=["revoked_at", "updated_at"])

    def update_refresh(self, *, token: str, jti: str, ttl_seconds: int) -> None:
        now = timezone.now()
        self.refresh_token_hash = generate_token_hash(token)
        self.current_refresh_jti = jti
        self.refresh_token_expires_at = min(
            self.absolute_expiration_at,
            now + timedelta(seconds=ttl_seconds),
        )
        self.last_refreshed_at = now
        self.save(
            update_fields=[
                "refresh_token_hash",
                "current_refresh_jti",
                "refresh_token_expires_at",
                "last_refreshed_at",
                "updated_at",
            ]
        )


class UsedRefreshToken(models.Model):
    """Store hashes of refresh tokens that were rotated to detect reuse."""

    session = models.ForeignKey(
        AuthSession,
        on_delete=models.CASCADE,
        related_name="used_tokens",
    )
    token_hash = models.CharField(max_length=128)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "token_hash")
        indexes = [models.Index(fields=["session", "token_hash"])]


class TwoFactorConfig(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="two_factor",
    )
    secret = models.CharField(max_length=32)
    is_enabled = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    backup_codes_generated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"TwoFactorConfig({self.user_id}, enabled={self.is_enabled})"

    @classmethod
    def generate_secret(cls) -> str:
        return secrets.token_hex(10)

    def ensure_ready(self) -> None:
        if not self.secret:
            raise ValidationError("TOTP secret is not configured")


class TwoFactorBackupCode(models.Model):
    config = models.ForeignKey(
        TwoFactorConfig,
        on_delete=models.CASCADE,
        related_name="backup_codes",
    )
    code_hash = models.CharField(max_length=128)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["config", "used_at"])]

    @staticmethod
    def hash_code(code: str) -> str:
        return generate_token_hash(code)


class OneTimeToken(models.Model):
    PURPOSE_EMAIL_VERIFY = "email_verify"
    PURPOSE_EMAIL_CHANGE = "email_change"
    PURPOSE_PASSWORD_RESET = "password_reset"

    PURPOSE_CHOICES = [
        (PURPOSE_EMAIL_VERIFY, "Email verification"),
        (PURPOSE_EMAIL_CHANGE, "Email change"),
        (PURPOSE_PASSWORD_RESET, "Password reset"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="one_time_tokens",
    )
    purpose = models.CharField(max_length=32, choices=PURPOSE_CHOICES)
    token_hash = models.CharField(max_length=128, unique=True)
    payload = models.JSONField(default=dict, blank=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    request_metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purpose"]),
            models.Index(fields=["purpose", "expires_at"]),
        ]

    def mark_used(self) -> None:
        if not self.used_at:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at > timezone.now()


class AuditEvent(models.Model):
    TYPE_LOGIN = "login"
    TYPE_LOGOUT = "logout"
    TYPE_LOGOUT_ALL = "logout_all"
    TYPE_REFRESH = "refresh"
    TYPE_2FA_ENABLED = "2fa_enabled"
    TYPE_2FA_DISABLED = "2fa_disabled"
    TYPE_PASSWORD_RESET_REQUEST = "password_reset_request"
    TYPE_PASSWORD_RESET_CONFIRM = "password_reset_confirm"
    TYPE_EMAIL_VERIFY_REQUEST = "email_verify_request"
    TYPE_EMAIL_VERIFY_CONFIRM = "email_verify_confirm"
    TYPE_EMAIL_CHANGE_REQUEST = "email_change_request"
    TYPE_EMAIL_CHANGE_CONFIRM = "email_change_confirm"
    TYPE_KYC_UPLOAD = "kyc_upload"
    TYPE_KYC_VIEW = "kyc_view"
    TYPE_ROLE_CHANGE = "role_change"
    TYPE_ACCESS_DENIED = "access_denied"

    EVENT_CHOICES = [
        (TYPE_LOGIN, "Login"),
        (TYPE_LOGOUT, "Logout"),
        (TYPE_LOGOUT_ALL, "Logout all"),
        (TYPE_REFRESH, "Token refresh"),
        (TYPE_2FA_ENABLED, "2FA enabled"),
        (TYPE_2FA_DISABLED, "2FA disabled"),
        (TYPE_PASSWORD_RESET_REQUEST, "Password reset requested"),
        (TYPE_PASSWORD_RESET_CONFIRM, "Password reset confirmed"),
        (TYPE_EMAIL_VERIFY_REQUEST, "Email verification requested"),
        (TYPE_EMAIL_VERIFY_CONFIRM, "Email verification confirmed"),
        (TYPE_EMAIL_CHANGE_REQUEST, "Email change requested"),
        (TYPE_EMAIL_CHANGE_CONFIRM, "Email change confirmed"),
        (TYPE_KYC_UPLOAD, "KYC document uploaded"),
        (TYPE_KYC_VIEW, "KYC document accessed"),
        (TYPE_ROLE_CHANGE, "Role changed"),
        (TYPE_ACCESS_DENIED, "Access denied"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="auth_events",
        null=True,
        blank=True,
    )
    session = models.ForeignKey(
        AuthSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    device_id = models.CharField(max_length=128, blank=True)
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    trace_id = models.CharField(max_length=128, blank=True)
    span_id = models.CharField(max_length=64, blank=True)
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "event_type"])]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"AuditEvent(user={self.user_id}, type={self.event_type})"
