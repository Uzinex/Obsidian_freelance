from __future__ import annotations

import logging

from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class GmailValidationError(Exception):
    """Raised when Gmail validation fails."""


logger = logging.getLogger(__name__)


def ensure_gmail_exists(email: str) -> None:
    """Validate Gmail format without blocking on existence checks."""

    normalized = (email or "").strip().lower()
    validator = EmailValidator(message=_("Некорректный email"))
    try:
        validator(normalized)
    except ValidationError as exc:
        raise GmailValidationError(str(exc.message)) from exc
    if not (normalized.endswith("@gmail.com") or normalized.endswith("@googlemail.com")):
        raise GmailValidationError(_("Некорректный email"))
    logger.info("Skipping Gmail existence lookup; proceeding with provided address.")
