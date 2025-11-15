"""Custom exception handlers for the Obsidian backend."""

from __future__ import annotations

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    """Wrap DRF's default handler to normalize authentication failures."""

    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    if isinstance(detail, ErrorDetail) and detail.code == "not_authenticated":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.setdefault("WWW-Authenticate", "Bearer")
    return response


__all__ = ["exception_handler"]
