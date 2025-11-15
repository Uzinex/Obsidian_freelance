from django.conf import settings
from decimal import Decimal

from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .audit import audit_logger
from .models import AuditEvent, Notification, Profile, VerificationRequest, Wallet
from .permissions import IsVerificationAdmin
from .serializers import (
    NotificationSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    VerificationRequestSerializer,
    WalletSerializer,
)
from .utils import create_notification


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "register"

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = (
        Profile.objects.select_related("user", "wallet")
        .prefetch_related("skills")
        .all()
    )

    def get_queryset(self):
        queryset = self.queryset
        role = self.request.query_params.get("role")
        skill = self.request.query_params.get("skill")
        if role:
            queryset = queryset.filter(role=role)
        if skill:
            queryset = queryset.filter(skills__id=skill)
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        previous_role = getattr(serializer.instance, "role", None)
        profile = serializer.save()
        if previous_role and profile.role != previous_role:
            audit_logger.log_event(
                event_type=AuditEvent.TYPE_ROLE_CHANGE,
                user=self.request.user,
                request=self.request,
                metadata={
                    "profile_id": profile.id,
                    "old_role": previous_role,
                    "new_role": profile.role,
                    "target_user_id": profile.user_id,
                },
            )
        if profile.verification_requests.filter(
            status=VerificationRequest.STATUS_APPROVED
        ).exists():
            profile.is_verified = True
            profile.save(update_fields=["is_verified"])

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        profile, _created = Profile.objects.get_or_create(
            user=request.user,
            defaults={"role": Profile.ROLE_CLIENT},
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            profile__user=self.request.user
        ).order_by("-created_at")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        queryset = self.get_queryset().filter(is_read=False)
        updated = queryset.update(is_read=True, read_at=timezone.now())
        return Response({"updated": updated})


class WalletViewSet(viewsets.GenericViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # pragma: no cover - not used but required by router
        return Wallet.objects.filter(profile__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        limit = self.request.query_params.get("limit")
        if limit is not None:
            try:
                context["transaction_limit"] = max(1, int(limit))
            except (TypeError, ValueError):  # pragma: no cover - defensive
                pass
        return context

    def _get_profile(self) -> Profile:
        profile, _ = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={"role": Profile.ROLE_CLIENT},
        )
        return profile

    def _get_wallet(self) -> Wallet:
        profile = self._get_profile()
        wallet, _ = Wallet.objects.get_or_create(profile=profile)
        return wallet

    def list(self, request, *args, **kwargs):
        wallet = self._get_wallet()
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def deposit(self, request):
        wallet = self._get_wallet()
        amount = request.data.get("amount", "0")
        description = request.data.get("description", "Пополнение кошелька")
        try:
            amount_decimal = Decimal(str(amount))
            wallet.deposit(amount_decimal, description=description)
        except (ValueError, ArithmeticError) as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        create_notification(
            wallet.profile,
            title="Пополнение кошелька",
            message=f"На ваш баланс зачислено {amount_decimal} {wallet.currency}.",
            category=Notification.CATEGORY_FINANCE,
        )
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def withdraw(self, request):
        wallet = self._get_wallet()
        amount = request.data.get("amount", "0")
        description = request.data.get("description", "Списание средств")
        try:
            amount_decimal = Decimal(str(amount))
            wallet.withdraw(amount_decimal, description=description)
        except (ValueError, ArithmeticError) as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        create_notification(
            wallet.profile,
            title="Списание с кошелька",
            message=f"С вашего баланса списано {amount_decimal} {wallet.currency}.",
            category=Notification.CATEGORY_FINANCE,
        )
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)


class VerificationRequestViewSet(viewsets.ModelViewSet):
    serializer_class = VerificationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        admin_email = getattr(settings, "VERIFICATION_ADMIN_EMAIL", "").lower()
        if (
            user.is_authenticated
            and user.is_staff
            and user.email.lower() == admin_email
        ):
            return VerificationRequest.objects.select_related(
                "profile", "profile__user", "reviewed_by"
            )
        return VerificationRequest.objects.filter(
            profile__user=user
        ).select_related("profile", "profile__user", "reviewed_by")

    def get_permissions(self):
        if self.action in {"approve", "reject"}:
            return [permissions.IsAuthenticated(), IsVerificationAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsVerificationAdmin])
    def approve(self, request, pk=None):
        verification = self.get_object()
        if verification.status != VerificationRequest.STATUS_PENDING:
            return Response(
                {"detail": "Заявка уже обработана."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        note = request.data.get("note", "")
        verification.status = VerificationRequest.STATUS_APPROVED
        verification.reviewed_at = timezone.now()
        verification.reviewer_note = note
        verification.reviewed_by = request.user
        verification.save(update_fields=[
            "status",
            "reviewed_at",
            "reviewer_note",
            "reviewed_by",
        ])
        profile = verification.profile
        if not profile.is_verified:
            profile.is_verified = True
            profile.save(update_fields=["is_verified"])
        create_notification(
            profile,
            title="Верификация одобрена",
            message="Администратор подтвердил вашу заявку на верификацию профиля.",
            category=Notification.CATEGORY_VERIFICATION,
        )
        serializer = self.get_serializer(verification)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsVerificationAdmin])
    def reject(self, request, pk=None):
        verification = self.get_object()
        if verification.status != VerificationRequest.STATUS_PENDING:
            return Response(
                {"detail": "Заявка уже обработана."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        note = request.data.get("note", "")
        verification.status = VerificationRequest.STATUS_REJECTED
        verification.reviewed_at = timezone.now()
        verification.reviewer_note = note
        verification.reviewed_by = request.user
        verification.save(update_fields=[
            "status",
            "reviewed_at",
            "reviewer_note",
            "reviewed_by",
        ])
        profile = verification.profile
        if profile.is_verified:
            profile.is_verified = False
            profile.save(update_fields=["is_verified"])
        create_notification(
            profile,
            title="Верификация отклонена",
            message="Администратор отклонил заявку на верификацию. Проверьте комментарий и подайте новую заявку.",
            category=Notification.CATEGORY_VERIFICATION,
        )
        serializer = self.get_serializer(verification)
        return Response(serializer.data)
