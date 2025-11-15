from django.urls import path

from . import views

urlpatterns = [
    path("cases/", views.ModerationCaseListView.as_view(), name="moderation-case-list"),
    path("cases/<int:pk>/", views.ModerationCaseDetailView.as_view(), name="moderation-case-detail"),
    path("cases/<int:case_id>/update/", views.ModerationCaseUpdateView.as_view(), name="moderation-case-update"),
]
