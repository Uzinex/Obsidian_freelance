from django.contrib import admin

from .models import Category, Order, OrderApplication, Skill


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug")
    list_filter = ("category",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class OrderApplicationInline(admin.TabularInline):
    model = OrderApplication
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "client",
        "order_type",
        "payment_type",
        "budget",
        "deadline",
        "status",
    )
    list_filter = ("order_type", "payment_type", "status", "required_skills")
    search_fields = ("title", "description", "client__user__nickname")
    inlines = [OrderApplicationInline]


@admin.register(OrderApplication)
class OrderApplicationAdmin(admin.ModelAdmin):
    list_display = ("order", "freelancer", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("order__title", "freelancer__user__nickname")
