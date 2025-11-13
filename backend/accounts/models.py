from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


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

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Profile of {self.user.nickname}"

    @property
    def display_role(self) -> str:
        return dict(self.ROLE_CHOICES).get(self.role, self.role)


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
