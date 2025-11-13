from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import Profile
from .models import Category, Order, OrderApplication, Skill
from .serializers import (
    CategorySerializer,
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = (
        Order.objects.select_related("client", "client__user")
        .prefetch_related("required_skills")
        .all()
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ("title", "description")
    ordering_fields = ("created_at", "deadline", "budget")
    ordering = ("-created_at",)

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
        if profile.role != Profile.ROLE_CLIENT:
            raise permissions.PermissionDenied(
                "Only clients can publish orders."
            )
        if not profile.is_verified:
            raise PermissionDenied("Ваша заявка на верификацию ещё не одобрена.")
        serializer.save(client=profile)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        queryset = self.get_queryset().filter(order_type=Order.ORDER_TYPE_PREMIUM)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_update(self, serializer):
        profile, _created = Profile.objects.get_or_create(
            user=self.request.user, defaults={"role": Profile.ROLE_FREELANCER}
        )
        if serializer.instance.client != profile:
            raise permissions.PermissionDenied("You can only update your own orders.")
        if not profile.is_verified:
            raise PermissionDenied("Ваша заявка на верификацию ещё не одобрена.")
        serializer.save()

    def perform_destroy(self, instance):
        profile, _created = Profile.objects.get_or_create(
            user=self.request.user, defaults={"role": Profile.ROLE_FREELANCER}
        )
        if instance.client != profile:
            raise permissions.PermissionDenied("You can only delete your own orders.")
        if not profile.is_verified:
            raise PermissionDenied("Ваша заявка на верификацию ещё не одобрена.")
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
            ).select_related("order", "freelancer", "freelancer__user")
        return OrderApplication.objects.filter(
            order__client=profile
        ).select_related("order", "freelancer", "freelancer__user")

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
        serializer.save(order=order, freelancer=profile)

    def _get_order(self):
        order_id = self.request.data.get("order")
        return get_object_or_404(Order, id=order_id)
