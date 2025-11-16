from django.db import models
from django.db.models import Q


class ProfileStats(models.Model):
    profile = models.OneToOneField(
        "accounts.Profile", on_delete=models.CASCADE, related_name="stats"
    )
    views = models.PositiveIntegerField(default=0)
    invites = models.PositiveIntegerField(default=0)
    hire_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    response_time = models.DurationField(null=True, blank=True)
    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    dispute_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    escrow_share = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Profile stats"
        verbose_name_plural = "Profile stats"

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return f"Stats({self.profile.user.nickname})"


class PortfolioItem(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_MODERATION = "moderation"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_MODERATION, "Moderation"),
        (STATUS_PUBLISHED, "Published"),
    ]

    PERMISSION_PUBLIC = "public"
    PERMISSION_PRIVATE = "private"
    PERMISSION_CLIENT_ONLY = "client_only"
    PERMISSION_CHOICES = [
        (PERMISSION_PUBLIC, "Public"),
        (PERMISSION_PRIVATE, "Private"),
        (PERMISSION_CLIENT_ONLY, "Client only"),
    ]

    profile = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="portfolio_items"
    )
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    problem = models.TextField()
    solution = models.TextField()
    result = models.TextField()
    media = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    featured = models.BooleanField(default=False)
    client_permission = models.CharField(
        max_length=20, choices=PERMISSION_CHOICES, default=PERMISSION_PUBLIC
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"], name="portfolio_status_idx"),
            models.Index(fields=["profile", "featured"], name="portfolio_featured_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"PortfolioItem({self.title})"


class Review(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_REMOVED = "removed"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_REMOVED, "Removed"),
    ]

    contract = models.ForeignKey(
        "marketplace.Contract", on_delete=models.CASCADE, related_name="reviews"
    )
    rater = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="reviews_written"
    )
    ratee = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="reviews_received"
    )
    sub_scores = models.JSONField(default=dict, blank=True)
    text = models.TextField()
    helpful_votes = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    blind_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["contract", "rater"], name="unique_contract_rater"
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Review({self.contract_id} -> {self.ratee_id})"


class ProfileBadge(models.Model):
    BADGE_TOP_RATED = "top_rated"
    BADGE_VERIFIED = "verified"
    BADGE_RISING_TALENT = "rising_talent"
    BADGE_CHOICES = [
        (BADGE_TOP_RATED, "Top Rated"),
        (BADGE_VERIFIED, "Verified"),
        (BADGE_RISING_TALENT, "Rising Talent"),
    ]

    profile = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="badges"
    )
    badge_type = models.CharField(max_length=50, choices=BADGE_CHOICES)
    rules_snapshot = models.JSONField(default=dict, blank=True)
    issued_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["badge_type"], name="profile_badge_type_idx"),
        ]
        unique_together = ("profile", "badge_type", "issued_at")

    def __str__(self) -> str:  # pragma: no cover
        return f"Badge({self.profile_id}, {self.badge_type})"


class FavoriteProfile(models.Model):
    client = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="favorites"
    )
    favorite = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="saved_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "favorite")
        indexes = [
            models.Index(fields=["client", "created_at"], name="favorite_created_idx"),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Favorite({self.client_id} -> {self.favorite_id})"


class Report(models.Model):
    STATUS_OPEN = "open"
    STATUS_UNDER_REVIEW = "under_review"
    STATUS_RESOLVED = "resolved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_UNDER_REVIEW, "Under review"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    reporter = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="reports_submitted"
    )
    target_profile = models.ForeignKey(
        "accounts.Profile",
        on_delete=models.CASCADE,
        related_name="reports_received",
        null=True,
        blank=True,
    )
    target_portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
    )
    target_review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
    )
    reason = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                name="report_has_target",
                check=(
                    Q(target_profile__isnull=False)
                    | Q(target_portfolio_item__isnull=False)
                    | Q(target_review__isnull=False)
                ),
            )
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Report({self.reporter_id})"
