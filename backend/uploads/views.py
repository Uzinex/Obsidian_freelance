from __future__ import annotations

from django.http import FileResponse, Http404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts import rbac
from accounts.permissions import RoleBasedAccessPermission
from .models import SecureDocument, SecureDocumentLink
from .scanner import scan_bytes
from .serializers import (
    SecureDocumentLinkSerializer,
    SecureDocumentSerializer,
    SecureDocumentUploadSerializer,
)
from .validators import detect_mime_type, ensure_size_within_limits, scrub_exif_if_image


class SecureDocumentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SecureDocumentSerializer
    queryset = SecureDocument.objects.select_related("owner")
    permission_classes = [IsAuthenticated, RoleBasedAccessPermission]
    rbac_action_map = {
        "list": "uploads:manage",
        "retrieve": "uploads:manage",
        "destroy": "uploads:manage",
        "upload": "uploads:manage",
        "presign": "uploads:link",
    }

    def get_queryset(self):
        user = self.request.user
        if rbac.user_has_role(user, rbac.Role.STAFF):
            return self.queryset
        return self.queryset.filter(owner=user)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated, RoleBasedAccessPermission])
    def upload(self, request):
        serializer = SecureDocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file_obj = serializer.validated_data["file"]
        ensure_size_within_limits(file_obj.size)
        data = file_obj.read()
        mime_type = detect_mime_type(data)
        cleaned_data = scrub_exif_if_image(data, mime_type)
        if cleaned_data is not data:
            data = cleaned_data
        ensure_size_within_limits(len(data))
        scan_bytes(data, filename=file_obj.name)

        document = SecureDocument.objects.create(
            owner=request.user,
            category=serializer.validated_data["category"],
        )
        document.attach_file(
            data=data,
            name=file_obj.name,
            mime_type=mime_type,
        )
        document.refresh_from_db()
        output = self.get_serializer(document)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, RoleBasedAccessPermission])
    def presign(self, request, pk=None):
        document = self.get_object()
        try:
            ttl = int(request.data.get("ttl", 300))
        except (TypeError, ValueError):
            ttl = 300
        link = document.build_presigned_token(ttl_seconds=max(60, min(ttl, 3600)))
        serializer = SecureDocumentLinkSerializer(link)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SecureDocumentDownloadViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, RoleBasedAccessPermission]
    rbac_action_map = {
        "retrieve": "uploads:link",
    }

    def retrieve(self, request, pk=None):
        token = request.query_params.get("token")
        if not token:
            raise Http404
        try:
            link = SecureDocumentLink.objects.select_related("document", "document__owner").get(
                document_id=pk,
                token=token,
            )
        except SecureDocumentLink.DoesNotExist as exc:  # pragma: no cover - invalid token
            raise Http404 from exc
        if not link.is_valid():
            raise Http404
        document = link.document
        if not rbac.can(request.user, "uploads:link", obj=document):
            return Response(status=status.HTTP_403_FORBIDDEN)
        response = FileResponse(document.file.open("rb"), as_attachment=True, filename=document.original_name)
        response["Content-Type"] = document.mime_type
        response["X-Content-Type-Options"] = "nosniff"
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{document.original_name}"
        return response
