from decimal import Decimal, ROUND_HALF_UP

from django.db import models, transaction
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    title_ru = models.CharField(max_length=150, blank=True)
    title_uz = models.CharField(max_length=150, blank=True)
    description_ru = models.TextField(blank=True)
    description_uz = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="children", null=True, blank=True
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"], name="marketplace_category_slug_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="skills"
    )
    title_ru = models.CharField(max_length=150, blank=True)
    title_uz = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    description_ru = models.TextField(blank=True)
    description_uz = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    popularity = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"], name="marketplace_skill_slug_idx"),
            models.Index(fields=["category", "name"], name="marketplace_skill_category_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return self.name


class SkillSynonym(models.Model):
    LANGUAGE_RU = "ru"
    LANGUAGE_UZ = "uz"
    LANGUAGE_EN = "en"
    LANGUAGE_CHOICES = [
        (LANGUAGE_RU, "Russian"),
        (LANGUAGE_UZ, "Uzbek"),
        (LANGUAGE_EN, "English"),
    ]

    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name="synonyms"
    )
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    value = models.CharField(max_length=150)

    class Meta:
        unique_together = ("skill", "language", "value")
        indexes = [
            models.Index(fields=["language", "value"], name="skill_synonym_language_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Synonym({self.value} -> {self.skill.name})"


class Order(models.Model):
    CURRENCY_UZS = "UZS"

    PAYMENT_HOURLY = "hourly"
    PAYMENT_FIXED = "fixed"
    PAYMENT_CHOICES = [
        (PAYMENT_HOURLY, "Hourly"),
        (PAYMENT_FIXED, "Fixed"),
    ]

    ORDER_TYPE_URGENT = "urgent"
    ORDER_TYPE_NON_URGENT = "non_urgent"
    ORDER_TYPE_PREMIUM = "premium"
    ORDER_TYPE_STANDARD = "standard"
    ORDER_TYPE_COMPANY = "company_only"
    ORDER_TYPE_INDIVIDUAL = "individual_only"
    ORDER_TYPE_CHOICES = [
        (ORDER_TYPE_URGENT, "Urgent"),
        (ORDER_TYPE_NON_URGENT, "Non-urgent"),
        (ORDER_TYPE_PREMIUM, "Premium"),
        (ORDER_TYPE_STANDARD, "Standard"),
        (ORDER_TYPE_COMPANY, "Company freelancers only"),
        (ORDER_TYPE_INDIVIDUAL, "Individual freelancer only"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_IN_PROGRESS, "In progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    tldr_ru = models.TextField(blank=True)
    tldr_uz = models.TextField(blank=True)
    deadline = models.DateTimeField()
    payment_type = models.CharField(max_length=16, choices=PAYMENT_CHOICES)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default=CURRENCY_UZS)
    required_skills = models.ManyToManyField(
        Skill, related_name="orders", blank=True
    )
    order_type = models.CharField(max_length=32, choices=ORDER_TYPE_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PUBLISHED
    )
    client = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_active(self) -> bool:
        return self.status in {self.STATUS_PUBLISHED, self.STATUS_IN_PROGRESS}

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


class OrderApplication(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="applications"
    )
    freelancer = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="applications",
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("order", "freelancer")
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Application({self.freelancer.user.nickname} -> {self.order.title})"


class Contract(models.Model):
    STATUS_PENDING = "pending_signatures"
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_TERMINATION_REQUESTED = "termination_requested"
    STATUS_TERMINATED = "terminated"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает подписания"),
        (STATUS_ACTIVE, "Активен"),
        (STATUS_COMPLETED, "Завершён"),
        (STATUS_TERMINATION_REQUESTED, "Запрошено расторжение"),
        (STATUS_TERMINATED, "Расторгнут"),
        (STATUS_CANCELLED, "Отменён"),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="contracts"
    )
    application = models.ForeignKey(
        OrderApplication,
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    client = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="client_contracts",
    )
    freelancer = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="freelancer_contracts",
    )
    status = models.CharField(
        max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    client_signed_at = models.DateTimeField(blank=True, null=True)
    freelancer_signed_at = models.DateTimeField(blank=True, null=True)
    signed_at = models.DateTimeField(blank=True, null=True)
    termination_requested_by = models.CharField(max_length=20, blank=True)
    termination_reason = models.TextField(blank=True)
    termination_requested_at = models.DateTimeField(blank=True, null=True)
    termination_approved_at = models.DateTimeField(blank=True, null=True)
    compensation_paid = models.BooleanField(default=False)
    budget_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default=Order.CURRENCY_UZS)
    escrow_release_frozen = models.BooleanField(default=False)
    escrow_frozen_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("order", "freelancer")

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Contract({self.order.title} - {self.freelancer.user.nickname})"

    def _ensure_wallets(self):
        from accounts.models import Wallet

        Wallet.objects.get_or_create(profile=self.client)
        Wallet.objects.get_or_create(profile=self.freelancer)

    def _update_order_status(self, status: str) -> None:
        if self.order.status != status:
            self.order.status = status
            self.order.save(update_fields=["status"])

    def sign(self, actor) -> None:
        now = timezone.now()
        updated_fields = ["updated_at"]
        if actor == self.client and self.client_signed_at is None:
            self.client_signed_at = now
            updated_fields.append("client_signed_at")
        elif actor == self.freelancer and self.freelancer_signed_at is None:
            self.freelancer_signed_at = now
            updated_fields.append("freelancer_signed_at")
        else:
            raise ValueError("Недопустимое действие подписания")

        if self.client_signed_at and self.freelancer_signed_at:
            self.status = self.STATUS_ACTIVE
            self.signed_at = now
            updated_fields.extend(["status", "signed_at"])
            self._update_order_status(Order.STATUS_IN_PROGRESS)
        self.save(update_fields=updated_fields)

    def complete(self) -> None:
        if self.status not in {self.STATUS_ACTIVE, self.STATUS_TERMINATION_REQUESTED}:
            raise ValueError("Контракт нельзя завершить в текущем статусе")
        self._ensure_wallets()
        from accounts.models import WalletTransaction

        amount = Decimal(self.budget_snapshot)
        description = f"Выплата за заказ '{self.order.title}'"
        with transaction.atomic():
            client_wallet = self.client.wallet
            freelancer_wallet = self.freelancer.wallet
            client_wallet.transfer_to(
                freelancer_wallet,
                amount,
                description=description,
                related_contract=self,
                outgoing_type=WalletTransaction.TYPE_PAYOUT,
                incoming_type=WalletTransaction.TYPE_PAYOUT,
            )
            self.status = self.STATUS_COMPLETED
            self.updated_at = timezone.now()
            self.save(update_fields=["status", "updated_at"])
            self._update_order_status(Order.STATUS_COMPLETED)

    def request_termination(self, actor, reason: str) -> None:
        if self.status not in {self.STATUS_ACTIVE, self.STATUS_PENDING}:
            raise ValueError("Расторжение недоступно для данного контракта")
        self.termination_requested_by = (
            "client" if actor == self.client else "freelancer"
        )
        self.termination_reason = reason
        self.termination_requested_at = timezone.now()
        self.status = self.STATUS_TERMINATION_REQUESTED
        self.updated_at = timezone.now()
        self.save(
            update_fields=[
                "termination_requested_by",
                "termination_reason",
                "termination_requested_at",
                "status",
                "updated_at",
            ]
        )

    def approve_termination(self) -> Decimal:
        if self.status != self.STATUS_TERMINATION_REQUESTED:
            raise ValueError("Нет активного запроса на расторжение")
        self._ensure_wallets()
        from accounts.models import WalletTransaction

        compensation = Decimal(self.budget_snapshot) * Decimal("0.15")
        compensation = compensation.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        description = f"Компенсация за расторгнутый заказ '{self.order.title}'"
        with transaction.atomic():
            client_wallet = self.client.wallet
            freelancer_wallet = self.freelancer.wallet
            client_wallet.transfer_to(
                freelancer_wallet,
                compensation,
                description=description,
                related_contract=self,
                outgoing_type=WalletTransaction.TYPE_COMPENSATION,
                incoming_type=WalletTransaction.TYPE_COMPENSATION,
            )
            self.status = self.STATUS_TERMINATED
            self.termination_approved_at = timezone.now()
            self.compensation_paid = True
            self.save(
                update_fields=[
                    "status",
                    "termination_approved_at",
                    "compensation_paid",
                    "updated_at",
                ]
            )
            self._update_order_status(Order.STATUS_CANCELLED)
        return compensation
