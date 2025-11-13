from rest_framework import generics, permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile, VerificationRequest
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
        user_data = response.data
        user = self.get_queryset().model.objects.get(nickname=user_data["nickname"])
        token, _created = Token.objects.get_or_create(user=user)
        user_data.update({"token": token.key})
        response.data = user_data
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

    def get_queryset(self):
        if self.request.user.is_staff:
            return VerificationRequest.objects.select_related("profile", "profile__user")
        return VerificationRequest.objects.filter(
            profile__user=self.request.user
        ).select_related("profile", "profile__user")

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("profile")
        if profile.user != self.request.user:
            raise permissions.PermissionDenied("You can only verify your own profile.")
        serializer.save()
