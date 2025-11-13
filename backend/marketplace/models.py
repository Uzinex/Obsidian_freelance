from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="skills"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - simple data representation
        return self.name


class Order(models.Model):
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
    deadline = models.DateTimeField()
    payment_type = models.CharField(max_length=16, choices=PAYMENT_CHOICES)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
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
