from rest_framework.routers import DefaultRouter

from .views import NotificationEventViewSet, NotificationPreferenceViewSet

router = DefaultRouter()
router.register("events", NotificationEventViewSet, basename="notification-event")
router.register(
    "preferences", NotificationPreferenceViewSet, basename="notification-preference"
)

urlpatterns = router.urls
