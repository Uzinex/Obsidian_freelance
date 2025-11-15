from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/chat/contracts/(?P<contract_id>\d+)/$", consumers.ContractChatConsumer.as_asgi()),
]
