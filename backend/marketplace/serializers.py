from rest_framework import serializers

from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from .models import Category, Order, OrderApplication, Skill


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")


class SkillSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only=True
    )

    class Meta:
        model = Skill
        fields = ("id", "name", "slug", "category", "category_id")
        read_only_fields = ("id", "category")


class OrderSerializer(serializers.ModelSerializer):
    client = ProfileSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        source="client",
        queryset=Profile.objects.none(),
        write_only=True,
        required=False,
    )
    required_skills = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), required=False
    )
    required_skill_details = SkillSerializer(
        many=True, source="required_skills", read_only=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "title",
            "description",
            "deadline",
            "payment_type",
            "budget",
            "required_skills",
            "required_skill_details",
            "order_type",
            "status",
            "client",
            "client_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("status", "created_at", "updated_at", "client")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client_id"].queryset = Profile.objects.filter(
            role=Profile.ROLE_CLIENT
        )

    def create(self, validated_data):
        skills = validated_data.pop("required_skills", [])
        order = super().create(validated_data)
        if skills:
            order.required_skills.set(skills)
        return order

    def update(self, instance, validated_data):
        skills = validated_data.pop("required_skills", None)
        order = super().update(instance, validated_data)
        if skills is not None:
            order.required_skills.set(skills)
        return order


class OrderApplicationSerializer(serializers.ModelSerializer):
    freelancer = ProfileSerializer(read_only=True)
    freelancer_id = serializers.PrimaryKeyRelatedField(
        source="freelancer",
        queryset=Profile.objects.none(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = OrderApplication
        fields = (
            "id",
            "order",
            "freelancer",
            "freelancer_id",
            "cover_letter",
            "status",
            "created_at",
        )
        read_only_fields = ("status", "created_at", "freelancer")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Profile

        self.fields["freelancer_id"].queryset = Profile.objects.filter(
            role=Profile.ROLE_FREELANCER
        )

    def create(self, validated_data):
        return super().create(validated_data)
