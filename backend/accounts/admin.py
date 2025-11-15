from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User, VerificationRequest, Wallet, WalletTransaction


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("nickname",)
    list_display = (
        "nickname",
        "email",
        "first_name",
        "last_name",
        "patronymic",
        "birth_year",
        "is_staff",
    )
    search_fields = ("nickname", "email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("nickname", "email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "patronymic",
                    "birth_year",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "nickname",
                    "email",
                    "first_name",
                    "last_name",
                    "patronymic",
                    "birth_year",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "freelancer_type",
        "company_name",
        "company_registered_as",
        "is_completed",
        "is_verified",
    )
    list_filter = ("role", "freelancer_type", "company_registered_as", "is_verified")
    search_fields = ("user__nickname", "company_name")


@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "document_type",
        "status",
        "created_at",
        "reviewed_at",
    )
    list_filter = ("document_type", "status")
    search_fields = (
        "profile__user__nickname",
        "document_series",
        "document_number",
    )


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("profile", "balance", "currency")
    search_fields = ("profile__user__nickname",)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "wallet",
        "amount",
        "balance_after",
        "type",
        "created_at",
    )
    list_filter = ("type", "created_at")
    search_fields = ("wallet__profile__user__nickname",)


