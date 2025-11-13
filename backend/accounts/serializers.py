from datetime import date

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from marketplace.models import Skill

from .models import Profile, User, VerificationRequest


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
        )
        read_only_fields = ("id",)


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
        Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    credential = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        credential = attrs.get("credential")
        password = attrs.get("password")
        if credential and password:
            user = authenticate(
                request=self.context.get("request"),
                nickname=credential,
                password=password,
            )
            if not user:
                # Try login with email
                try:
                    user_obj = User.objects.get(email__iexact=credential)
                except User.DoesNotExist as exc:  # pragma: no cover - handled by message
                    raise serializers.ValidationError(
                        _("Unable to log in with provided credentials."),
                        code="authorization",
                    ) from exc
                user = authenticate(
                    request=self.context.get("request"),
                    nickname=user_obj.nickname,
                    password=password,
                )
            if not user:
                raise serializers.ValidationError(
                    _("Unable to log in with provided credentials."),
                    code="authorization",
                )
        else:
            raise serializers.ValidationError(
                _("Must include 'credential' and 'password'."),
                code="authorization",
            )
        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Skill.objects.none()
    )

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "role",
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
            "country",
            "city",
            "street",
            "house",
            "is_completed",
            "is_verified",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "is_verified",
            "created_at",
            "updated_at",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skills"].queryset = Skill.objects.all()

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


class VerificationRequestSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        model = VerificationRequest
        fields = (
            "id",
            "profile",
            "document_type",
            "document_series",
            "document_number",
            "document_image",
            "status",
            "created_at",
            "reviewed_at",
            "reviewer_note",
        )
        read_only_fields = ("status", "created_at", "reviewed_at", "reviewer_note")

    def create(self, validated_data):
        profile = validated_data["profile"]
        profile.is_verified = False
        profile.save(update_fields=["is_verified"])
        return super().create(validated_data)
