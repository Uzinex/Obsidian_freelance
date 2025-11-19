from __future__ import annotations

import httpx
from django.utils.translation import gettext_lazy as _


class GmailValidationError(Exception):
    """Raised when Gmail validation fails."""


_GMAIL_EXISTENCE_ENDPOINT = "https://mail.google.com/mail/gxlu"


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
    except httpx.HTTPError as exc:  # pragma: no cover - network failures
        raise GmailValidationError(_("Не удалось проверить Gmail. Попробуйте ещё раз.")) from exc
    has_cookie = bool(response.cookies.get("GMAIL_AT"))
    if not has_cookie:
        raise GmailValidationError(
            _("Указанный Gmail не существует или недоступен. Проверьте адрес.")
        )
