from rest_framework import serializers

from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from obsidian_backend.ai import tldr as tldr_cache

from .models import Category, Contract, Order, OrderApplication, Skill


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
    tldr = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "title",
            "description",
            "deadline",
            "payment_type",
            "budget",
            "currency",
            "required_skills",
            "required_skill_details",
            "order_type",
            "status",
            "client",
            "client_id",
            "created_at",
            "updated_at",
            "tldr",
        )
        read_only_fields = (
            "status",
            "created_at",
            "updated_at",
            "client",
            "currency",
            "tldr",
        )

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

    def _resolve_locale(self) -> str:
        request = self.context.get("request")
        if request is not None:
            header = request.headers.get("Accept-Language")
            if header:
                return header.split(",")[0].strip() or "ru"
        return self.context.get("locale", "ru")

    def get_tldr(self, obj: Order) -> str | None:
        locale = self._resolve_locale()
        return tldr_cache.get_tldr(
            entity="order",
            pk=obj.pk,
            locale=locale,
            fetcher=obj.get_tldr,
        )


class OrderApplicationSerializer(serializers.ModelSerializer):
    freelancer = ProfileSerializer(read_only=True)
    freelancer_id = serializers.PrimaryKeyRelatedField(
        source="freelancer",
        queryset=Profile.objects.none(),
        write_only=True,
        required=False,
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    contract = serializers.SerializerMethodField()

    class Meta:
        model = OrderApplication
        fields = (
            "id",
            "order",
            "freelancer",
            "freelancer_id",
            "cover_letter",
            "status",
            "status_display",
            "contract",
            "created_at",
        )
        read_only_fields = ("status", "created_at", "freelancer")
        validators = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from accounts.models import Profile

        self.fields["freelancer_id"].queryset = Profile.objects.filter(
            role=Profile.ROLE_FREELANCER
        )

    def create(self, validated_data):
        return super().create(validated_data)

    def validate(self, attrs):
        request = self.context.get("request")
        freelancer = attrs.get("freelancer")
        if freelancer is None and request is not None and request.user.is_authenticated:
            freelancer = getattr(request.user, "profile", None)

        order = attrs.get("order")
        if order is not None and freelancer is not None:
            if OrderApplication.objects.filter(order=order, freelancer=freelancer).exists():
                raise serializers.ValidationError(
                    {
                        "non_field_errors": [
                            "You have already applied to this order.",
                        ]
                    }
                )

        return attrs

    def get_contract(self, obj: OrderApplication):
        contract = obj.contracts.order_by("-created_at").first()
        if contract is None:
            return None
        serializer = ContractSerializer(contract, context=self.context)
        return serializer.data


class ContractSerializer(serializers.ModelSerializer):
    client = ProfileSerializer(read_only=True)
    freelancer = ProfileSerializer(read_only=True)
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    order_title = serializers.CharField(source="order.title", read_only=True)
    application_id = serializers.IntegerField(source="application.id", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    user_role = serializers.SerializerMethodField()
    client_signed = serializers.SerializerMethodField()
    freelancer_signed = serializers.SerializerMethodField()
    can_sign = serializers.SerializerMethodField()
    can_complete = serializers.SerializerMethodField()
    can_request_termination = serializers.SerializerMethodField()
    termination_requested = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = (
            "id",
            "order_id",
            "order_title",
            "application_id",
            "status",
            "status_display",
            "client",
            "freelancer",
            "budget_snapshot",
            "currency",
            "client_signed_at",
            "freelancer_signed_at",
            "signed_at",
            "termination_requested_by",
            "termination_reason",
            "termination_requested_at",
            "termination_approved_at",
            "compensation_paid",
            "user_role",
            "client_signed",
            "freelancer_signed",
            "can_sign",
            "can_complete",
            "can_request_termination",
            "termination_requested",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def _get_request_profile(self):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return None
        return getattr(request.user, "profile", None)

    def get_user_role(self, obj: Contract):
        profile = self._get_request_profile()
        if profile is None:
            return None
        if obj.client_id == getattr(profile, "id", None):
            return "client"
        if obj.freelancer_id == getattr(profile, "id", None):
            return "freelancer"
        return None

    def get_client_signed(self, obj: Contract) -> bool:
        return bool(obj.client_signed_at)

    def get_freelancer_signed(self, obj: Contract) -> bool:
        return bool(obj.freelancer_signed_at)

    def get_can_sign(self, obj: Contract) -> bool:
        profile = self._get_request_profile()
        if profile is None or obj.status != Contract.STATUS_PENDING:
            return False
        if obj.client_id == getattr(profile, "id", None):
            return obj.client_signed_at is None
        if obj.freelancer_id == getattr(profile, "id", None):
            return obj.freelancer_signed_at is None
        return False

    def get_can_complete(self, obj: Contract) -> bool:
        profile = self._get_request_profile()
        if profile is None:
            return False
        return (
            obj.status in {Contract.STATUS_ACTIVE, Contract.STATUS_TERMINATION_REQUESTED}
            and obj.client_id == getattr(profile, "id", None)
        )

    def get_can_request_termination(self, obj: Contract) -> bool:
        profile = self._get_request_profile()
        if profile is None or obj.status not in {Contract.STATUS_ACTIVE, Contract.STATUS_PENDING}:
            return False
        if obj.status == Contract.STATUS_PENDING and (
            obj.client_signed_at and obj.freelancer_signed_at
        ):
            return False
        if obj.termination_requested_by:
            return False
        return obj.client_id == getattr(profile, "id", None) or obj.freelancer_id == getattr(
            profile, "id", None
        )

    def get_termination_requested(self, obj: Contract) -> bool:
        return obj.status == Contract.STATUS_TERMINATION_REQUESTED
