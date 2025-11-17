"""HTTP клиент для взаимодействия с сервисом ai-gateway."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from django.conf import settings


@dataclass(slots=True)
class AiGatewayError(Exception):
    """Базовое исключение для ошибок вызова AI-шлюза."""

    status_code: int
    payload: Any

    def __str__(self) -> str:  # pragma: no cover - простая репрезентация
        return f"AI gateway error {self.status_code}: {self.payload}"  # noqa: EM101


class AiGatewayClient:
    """Неблокирующий клиент ai-gateway с таймаутами и ретраями."""

    def __init__(self, *, timeout: float | None = None) -> None:
        self._timeout = timeout or settings.AI_GATEWAY_TIMEOUT
        self._base_url = settings.AI_GATEWAY_URL
        self._api_key = settings.AI_GATEWAY_API_KEY

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        if settings.AI_GATEWAY_ENABLE_TELEMETRY:
            headers["X-AI-Telemetry"] = "1"
        return headers

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        url = f"{self._base_url}{path}"
        with httpx.Client(timeout=self._timeout) as client:
            response = client.post(url, json=payload, headers=self._headers())
        if response.status_code >= 400:
            raise AiGatewayError(response.status_code, response.json())
        return response.json()

    def match(self, payload: dict[str, Any]) -> Any:
        """Вызов /match."""

        return self._post("/match", payload)

    def semantic_search(self, payload: dict[str, Any]) -> Any:
        """Вызов /semantic_search."""

        return self._post("/semantic_search", payload)

    def generate_tldr(self, payload: dict[str, Any]) -> Any:
        """Вызов /summaries/tldr."""

        return self._post("/summaries/tldr", payload)
