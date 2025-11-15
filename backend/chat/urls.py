from django.urls import path

from . import views

urlpatterns = [
    path(
        "contracts/<int:contract_id>/thread/",
        views.ContractChatThreadView.as_view(),
        name="chat-thread",
    ),
    path(
        "contracts/<int:contract_id>/messages/",
        views.ContractChatMessagesView.as_view(),
        name="chat-messages",
    ),
    path(
        "contracts/<int:contract_id>/messages/<int:message_id>/status/",
        views.ChatMessageStatusView.as_view(),
        name="chat-message-status",
    ),
    path(
        "contracts/<int:contract_id>/events/",
        views.ChatEventPollView.as_view(),
        name="chat-events",
    ),
    path(
        "contracts/<int:contract_id>/attachments/",
        views.ChatAttachmentUploadView.as_view(),
        name="chat-attachment-upload",
    ),
    path(
        "contracts/<int:contract_id>/attachments/<uuid:attachment_id>/presign/",
        views.ChatAttachmentPresignView.as_view(),
        name="chat-attachment-presign",
    ),
    path(
        "attachments/<uuid:attachment_id>/download/",
        views.ChatAttachmentDownloadView.as_view(),
        name="chat-attachment-download",
    ),
]
