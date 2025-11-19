from __future__ import annotations

import logging

import httpx
from django.utils.translation import gettext_lazy as _


class GmailValidationError(Exception):
    """Raised when Gmail validation fails."""


_GMAIL_EXISTENCE_ENDPOINT = "https://mail.google.com/mail/gxlu"


logger = logging.getLogger(__name__)


def ensure_gmail_exists(email: str) -> None:
    """Validate that a Gmail address resolves to an existing mailbox."""

    normalized = (email or "").strip().lower()
    if not normalized:
        raise GmailValidationError(_("Укажите Gmail."))
    if not (normalized.endswith("@gmail.com") or normalized.endswith("@googlemail.com")):
        raise GmailValidationError(_("Допустимы только адреса @gmail.com."))
    params = {"email": normalized}
    try:
        response = httpx.get(
            _GMAIL_EXISTENCE_ENDPOINT,
            params=params,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=5.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise GmailValidationError(
                _("Указанный Gmail не существует или недоступен. Проверьте адрес.")
            ) from exc
        logger.warning("Gmail lookup request failed: %s", exc)
        return
    except httpx.HTTPError as exc:  # pragma: no cover - network failures
        logger.warning("Unable to verify Gmail due to network error: %s", exc)
        return

    has_cookie = bool(response.cookies.get("GMAIL_AT"))
    if not has_cookie:
        logger.info(
            "Gmail existence cookie is missing for %s; assuming the address is valid.",
            normalized,
        )
