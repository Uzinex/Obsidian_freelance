from __future__ import annotations

from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from accounts import rbac
from moderation.permissions import IsFinance, IsModerator

from .models import DisputeCase
from .serializers import (
    DisputeCaseCreateSerializer,
    DisputeCaseSerializer,
    DisputeEvidenceUploadSerializer,
    DisputeOutcomeSerializer,
    DisputeStatusSerializer,
)


class DisputeAccessMixin:
    def get_accessible_cases(self, request):
        queryset = DisputeCase.objects.all().select_related("outcome").prefetch_related("evidence", "participants", "events")
        user = request.user
        if not getattr(user, "is_authenticated", False):
            return queryset.none()
        if user.is_staff or rbac.user_has_role(user, rbac.Role.STAFF) or rbac.user_has_role(user, rbac.Role.MODERATOR):
            return queryset
        profile = getattr(user, "profile", None)
        if not profile:
            return queryset.none()
        return queryset.filter(
            Q(contract__client=profile)
            | Q(contract__freelancer=profile)
            | Q(participants__profile=profile)
        ).distinct()

    def get_case_or_403(self, request, case_id):
        queryset = self.get_accessible_cases(request)
        try:
            return queryset.get(pk=case_id)
        except DisputeCase.DoesNotExist as exc:
            raise PermissionDenied("Недостаточно прав для просмотра спора") from exc


class DisputeCaseListView(DisputeAccessMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DisputeCaseSerializer

    def get_queryset(self):
        queryset = self.get_accessible_cases(self.request)
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)
        priority = self.request.query_params.get("priority")
        if priority:
            queryset = queryset.filter(priority=priority)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        min_amount = self.request.query_params.get("min_amount")
        if min_amount:
            queryset = queryset.filter(amount_under_review__gte=min_amount)
        max_amount = self.request.query_params.get("max_amount")
        if max_amount:
            queryset = queryset.filter(amount_under_review__lte=max_amount)
        overdue = self.request.query_params.get("overdue")
        if overdue in {"1", "true", "yes"}:
            from django.utils import timezone

            queryset = queryset.filter(sla_due_at__lt=timezone.now(), status__in=[DisputeCase.STATUS_OPENED, DisputeCase.STATUS_EVIDENCE, DisputeCase.STATUS_IN_REVIEW])
        return queryset


class ContractDisputeCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DisputeCaseCreateSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        from marketplace.models import Contract

        contract = Contract.objects.select_related("client", "freelancer").get(pk=self.kwargs["contract_id"])
        user = self.request.user
        profile = getattr(user, "profile", None)
        if not (
            getattr(user, "is_staff", False)
            or (profile and profile.id in {contract.client_id, contract.freelancer_id})
        ):
            raise PermissionDenied("Недостаточно прав для открытия спора")
        context["contract"] = contract
        return context


class DisputeCaseDetailView(DisputeAccessMixin, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DisputeCaseSerializer
    lookup_url_kwarg = "case_id"

    def get_queryset(self):
        return self.get_accessible_cases(self.request)


class DisputeEvidenceUploadView(DisputeAccessMixin, generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DisputeEvidenceUploadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        case = self.get_case_or_403(self.request, self.kwargs["case_id"])
        context["case"] = case
        return context


class DisputeStatusUpdateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsModerator]
    serializer_class = DisputeStatusSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        from .models import DisputeCase

        case = DisputeCase.objects.get(pk=self.kwargs["case_id"])
        context["case"] = case
        return context


class DisputeOutcomeView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsFinance]
    serializer_class = DisputeOutcomeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        from .models import DisputeCase

        case = DisputeCase.objects.get(pk=self.kwargs["case_id"])
        context["case"] = case
        return context
