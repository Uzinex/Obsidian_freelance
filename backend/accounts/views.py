from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, VerificationRequest
from .permissions import IsVerificationAdmin
from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    UserSerializer,
    VerificationRequestSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = self.get_queryset().model.objects.get(nickname=response.data["nickname"])
        token, _created = Token.objects.get_or_create(user=user)
        response.data = {"token": token.key, "user": UserSerializer(user).data}
        return response

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Profile.objects.select_related("user").prefetch_related("skills")

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
        profile = serializer.save()
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
        profile = serializer.validated_data.get("profile")
        if profile.user != self.request.user:
            raise permissions.PermissionDenied("You can only verify your own profile.")
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
        serializer = self.get_serializer(verification)
        return Response(serializer.data)
