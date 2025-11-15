from decimal import Decimal

from django.conf import settings
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts import rbac
from accounts.models import Profile
from notifications.models import NotificationEvent
from accounts.permissions import RoleBasedAccessPermission
from accounts.utils import create_notification
from .models import Category, Contract, Order, OrderApplication, Skill
from .serializers import (
    CategorySerializer,
    ContractSerializer,
    OrderApplicationSerializer,
    OrderSerializer,
    SkillSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Skill.objects.select_related("category")
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [RoleBasedAccessPermission]
    queryset = (
        Order.objects.select_related("client", "client__user")
        .prefetch_related("required_skills")
        .all()
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "deadline", "budget")
    ordering = ("-created_at",)
    rbac_action_map = {
        "list": "orders:view",
        "retrieve": "orders:view",
        "create": "orders:create",
        "update": "orders:edit",
        "partial_update": "orders:edit",
        "destroy": "orders:delete",
        "featured": "orders:view",
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        skill = self.request.query_params.get("skill")
        order_type = self.request.query_params.get("order_type")
        client = self.request.query_params.get("client")
        if category:
            queryset = queryset.filter(required_skills__category__slug=category)
        if skill:
            queryset = queryset.filter(required_skills__slug=skill)
        if order_type:
            queryset = queryset.filter(order_type=order_type)
        if client:
            queryset = queryset.filter(client__id=client)
        return queryset.distinct()

    def perform_create(self, serializer):
        profile, _created = Profile.objects.get_or_create(
            user=self.request.user, defaults={"role": Profile.ROLE_CLIENT}
        )
        if profile.role != Profile.ROLE_CLIENT and not rbac.user_has_role(
            self.request.user, rbac.Role.STAFF
        ):
            raise permissions.PermissionDenied(
                "Only clients can publish orders."
            )
        if (
            profile.role == Profile.ROLE_CLIENT
            and not profile.is_verified
            and not rbac.user_has_role(self.request.user, rbac.Role.STAFF)
        ):
            raise PermissionDenied("Ваша заявка на верификацию ещё не одобрена.")
        serializer.save(client=profile)

    @action(detail=False, methods=["get"])
    def featured(self, request):
        queryset = self.get_queryset().filter(order_type=Order.ORDER_TYPE_PREMIUM)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class OrderApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = OrderApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        profile, _created = Profile.objects.get_or_create(
            user=self.request.user, defaults={"role": Profile.ROLE_FREELANCER}
        )
        if profile.role == Profile.ROLE_FREELANCER:
            return OrderApplication.objects.filter(
                freelancer=profile
            ).select_related("order", "freelancer", "freelancer__user").prefetch_related(
                "contracts"
            )
        return OrderApplication.objects.filter(
            order__client=profile
        ).select_related("order", "freelancer", "freelancer__user").prefetch_related(
            "contracts"
        )

    def perform_create(self, serializer):
        profile, _created = Profile.objects.get_or_create(user=self.request.user)
        if profile.role != Profile.ROLE_FREELANCER:
            raise permissions.PermissionDenied("Only freelancers can apply to orders.")
        if not profile.is_verified:
            raise PermissionDenied("Для отклика необходимо пройти верификацию.")
        order = self._get_order()
        if OrderApplication.objects.filter(order=order, freelancer=profile).exists():
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "You have already applied to this order.",
                    ]
                }
            )
        application = serializer.save(order=order, freelancer=profile)
        create_notification(
            order.client,
            title="Новый отклик на заказ",
            message=f"{profile.user.nickname} откликнулся на заказ '{order.title}'.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_APPLICATION_SUBMITTED,
            data={"order_id": order.id, "application_id": application.id},
        )

    def _get_order(self):
        order_id = self.request.data.get("order")
        return get_object_or_404(Order, id=order_id)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def approve(self, request, pk=None):
        application = self.get_object()
        profile, _ = Profile.objects.get_or_create(
            user=request.user, defaults={"role": Profile.ROLE_CLIENT}
        )
        if profile != application.order.client:
            raise permissions.PermissionDenied("Вы можете одобрять только свои заказы.")
        if application.status != OrderApplication.STATUS_PENDING:
            return Response(
                {"detail": "Отклик уже обработан."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.status = OrderApplication.STATUS_ACCEPTED
        application.save(update_fields=["status"])
        OrderApplication.objects.filter(order=application.order).exclude(
            pk=application.pk
        ).update(status=OrderApplication.STATUS_REJECTED)
        contract, _ = Contract.objects.update_or_create(
            order=application.order,
            freelancer=application.freelancer,
            defaults={
                "application": application,
                "client": application.order.client,
                "status": Contract.STATUS_PENDING,
                "budget_snapshot": application.order.budget,
                "currency": application.order.currency,
            },
        )
        create_notification(
            application.freelancer,
            title="Отклик одобрен",
            message=f"Заказчик одобрил ваш отклик на заказ '{application.order.title}'. Подпишите контракт, чтобы приступить к работе.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_APPLICATION_DECISION,
            data={"order_id": application.order.id, "contract_id": contract.id},
        )
        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        application = self.get_object()
        profile, _ = Profile.objects.get_or_create(
            user=request.user, defaults={"role": Profile.ROLE_CLIENT}
        )
        if profile != application.order.client:
            raise permissions.PermissionDenied("Вы можете отклонять только свои заказы.")
        if application.status == OrderApplication.STATUS_REJECTED:
            return Response(
                {"detail": "Отклик уже отклонён."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application.status = OrderApplication.STATUS_REJECTED
        application.save(update_fields=["status"])
        create_notification(
            application.freelancer,
            title="Отклик отклонён",
            message=f"Заказчик отклонил ваш отклик на заказ '{application.order.title}'.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_APPLICATION_DECISION,
            data={"order_id": application.order.id, "application_id": application.id},
        )
        serializer = self.get_serializer(application)
        return Response(serializer.data)


class ContractViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedAccessPermission]
    rbac_action_map = {
        "list": "contracts:view",
        "retrieve": "contracts:view",
        "sign": "contracts:edit",
        "complete": "contracts:edit",
        "request_termination": "contracts:edit",
        "approve_termination": "finance:manage",
        "communications": "contracts:view",
    }

    def get_queryset(self):
        queryset = Contract.objects.select_related(
            "order",
            "client",
            "client__user",
            "freelancer",
            "freelancer__user",
        )
        user = self.request.user
        if rbac.user_has_role(user, rbac.Role.STAFF) or rbac.user_has_role(
            user, rbac.Role.FINANCE
        ) or rbac.user_has_role(user, rbac.Role.MODERATOR):
            return queryset
        profile = getattr(user, "profile", None)
        if profile is None:
            return queryset.none()
        return queryset.filter(Q(client=profile) | Q(freelancer=profile))

    def _get_profile(self):
        profile = getattr(self.request.user, "profile", None)
        if profile is None:
            profile, _ = Profile.objects.get_or_create(
                user=self.request.user,
                defaults={"role": Profile.ROLE_CLIENT},
            )
        return profile

    def _get_other_party(self, contract: Contract, actor: Profile) -> Profile:
        return contract.freelancer if actor == contract.client else contract.client

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, RoleBasedAccessPermission])
    def sign(self, request, pk=None):
        contract = self.get_object()
        profile = self._get_profile()
        if profile not in {contract.client, contract.freelancer}:
            raise permissions.PermissionDenied("Вы не участник контракта.")
        try:
            contract.sign(profile)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        contract.refresh_from_db()
        other_party = self._get_other_party(contract, profile)
        role_text = "Фрилансер" if profile == contract.freelancer else "Заказчик"
        create_notification(
            other_party,
            title="Подписание контракта",
            message=f"{role_text} подписал контракт по заказу '{contract.order.title}'.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_SIGNED,
            data={"contract_id": contract.id, "order_id": contract.order.id},
        )
        if contract.status == Contract.STATUS_ACTIVE:
            create_notification(
                contract.client,
                title="Контракт активирован",
                message=f"Контракт по заказу '{contract.order.title}' подписан обеими сторонами.",
                category=NotificationEvent.CATEGORY_CONTRACT,
                event_type=NotificationEvent.EventType.CONTRACT_CREATED,
                data={"contract_id": contract.id},
            )
            create_notification(
                contract.freelancer,
                title="Контракт активирован",
                message=f"Контракт по заказу '{contract.order.title}' подписан обеими сторонами.",
                category=NotificationEvent.CATEGORY_CONTRACT,
                event_type=NotificationEvent.EventType.CONTRACT_CREATED,
                data={"contract_id": contract.id},
            )
        serializer = self.get_serializer(contract)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, RoleBasedAccessPermission])
    def complete(self, request, pk=None):
        contract = self.get_object()
        profile = self._get_profile()
        if profile != contract.client:
            raise permissions.PermissionDenied("Только заказчик может завершить контракт.")
        try:
            contract.complete()
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        contract.refresh_from_db()
        amount = Decimal(contract.budget_snapshot)
        create_notification(
            contract.freelancer,
            title="Выплата по контракту",
            message=f"Заказчик подтвердил выполнение заказа '{contract.order.title}'. {amount} {contract.currency} перечислены на ваш кошелёк.",
            category=NotificationEvent.CATEGORY_PAYMENTS,
            event_type=NotificationEvent.EventType.PAYMENTS_PAYOUT,
            data={
                "contract_id": contract.id,
                "amount": str(amount),
                "currency": contract.currency,
            },
        )
        create_notification(
            contract.client,
            title="Заказ закрыт",
            message=f"Вы завершили заказ '{contract.order.title}'. Средства автоматически перечислены исполнителю.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_COMPLETED,
            data={"contract_id": contract.id},
        )
        serializer = self.get_serializer(contract)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, RoleBasedAccessPermission])
    def request_termination(self, request, pk=None):
        contract = self.get_object()
        profile = self._get_profile()
        if profile not in {contract.client, contract.freelancer}:
            raise permissions.PermissionDenied("Вы не участник контракта.")
        reason = request.data.get("reason", "")
        if not reason:
            return Response(
                {"detail": "Укажите причину расторжения."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            contract.request_termination(profile, reason)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        contract.refresh_from_db()
        other_party = self._get_other_party(contract, profile)
        actor_label = "Заказчик" if profile == contract.client else "Фрилансер"
        create_notification(
            other_party,
            title="Запрос на расторжение",
            message=f"{actor_label} инициировал расторжение контракта по заказу '{contract.order.title}'. Ожидайте решение администрации.",
            category=NotificationEvent.CATEGORY_CONTRACT,
            event_type=NotificationEvent.EventType.CONTRACT_TERMINATION_REQUESTED,
            data={"contract_id": contract.id},
        )
        serializer = self.get_serializer(contract)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated, RoleBasedAccessPermission],
    )
    def approve_termination(self, request, pk=None):
        contract = self.get_object()
        try:
            compensation = contract.approve_termination()
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        contract.refresh_from_db()
        compensation_str = f"{compensation} {contract.currency}"
        create_notification(
            contract.freelancer,
            title="Расторжение контракта",
            message=f"Администратор одобрил расторжение контракта по заказу '{contract.order.title}'. Вам выплачена компенсация {compensation_str}.",
            category=NotificationEvent.CATEGORY_PAYMENTS,
            event_type=NotificationEvent.EventType.PAYMENTS_PAYOUT,
            data={
                "contract_id": contract.id,
                "amount": str(compensation),
                "currency": contract.currency,
            },
        )
        create_notification(
            contract.client,
            title="Расторжение контракта",
            message=f"Администратор одобрил расторжение контракта по заказу '{contract.order.title}'. С вашего кошелька списана компенсация {compensation_str}.",
            category=NotificationEvent.CATEGORY_PAYMENTS,
            event_type=NotificationEvent.EventType.PAYMENTS_RELEASE,
            data={
                "contract_id": contract.id,
                "amount": str(compensation),
                "currency": contract.currency,
            },
        )
        serializer = self.get_serializer(contract)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[permissions.IsAuthenticated, RoleBasedAccessPermission],
    )
    def communications(self, request, pk=None):
        contract = self.get_object()
        dispute_allowed_statuses = {
            Contract.STATUS_PENDING,
            Contract.STATUS_ACTIVE,
            Contract.STATUS_COMPLETED,
            Contract.STATUS_TERMINATION_REQUESTED,
        }
        dispute_enabled = settings.DISPUTE_ENABLED and (
            contract.status in dispute_allowed_statuses
        )
        payload = {
            "contract_id": contract.id,
            "chat": {
                "enabled": settings.CHAT_ENABLED,
                "attachments": settings.CHAT_ATTACHMENTS_ENABLED,
                "presence": settings.CHAT_PRESENCE_ENABLED,
            },
            "dispute": {
                "enabled": dispute_enabled,
                "requires_contract": True,
            },
            "notifications": {
                "email": settings.NOTIFY_EMAIL_ENABLED,
                "webpush": settings.NOTIFY_WEBPUSH_ENABLED,
            },
        }
        return Response(payload)
