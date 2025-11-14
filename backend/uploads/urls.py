from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SecureDocumentDownloadViewSet, SecureDocumentViewSet

router = DefaultRouter()
router.register("documents", SecureDocumentViewSet, basename="secure-document")
router.register("downloads", SecureDocumentDownloadViewSet, basename="secure-document-download")

urlpatterns = [
    path("", include(router.urls)),
]
