from django.urls import path

from . import views

urlpatterns = [
    path("cases/", views.DisputeCaseListView.as_view(), name="dispute-case-list"),
    path("contracts/<int:contract_id>/", views.ContractDisputeCreateView.as_view(), name="contract-dispute-create"),
    path("cases/<int:case_id>/", views.DisputeCaseDetailView.as_view(), name="dispute-case-detail"),
    path("cases/<int:case_id>/evidence/", views.DisputeEvidenceUploadView.as_view(), name="dispute-evidence-upload"),
    path("cases/<int:case_id>/status/", views.DisputeStatusUpdateView.as_view(), name="dispute-status-update"),
    path("cases/<int:case_id>/outcome/", views.DisputeOutcomeView.as_view(), name="dispute-outcome"),
]
