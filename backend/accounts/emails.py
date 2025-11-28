from __future__ import annotations

import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    """Raised when transactional emails cannot be delivered."""

    default_message = _("Не удалось отправить код. Попробуйте позже.")

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


def send_auth_email(*, template: str, subject: str, to_email: str, context: dict) -> None:
    _ensure_email_backend_configured()
    body = render_to_string(template, context)
    from_email = (
        settings.DEFAULT_FROM_EMAIL
        or settings.EMAIL_HOST_USER
        or getattr(settings, "SERVER_EMAIL", "")
    )
    if not from_email:
        raise EmailDeliveryError(
            _("Неверная конфигурация отправки писем: отсутствует адрес отправителя."),
        )
    try:
        send_mail(subject, body, from_email, [to_email], fail_silently=False)
    except (SMTPException, BadHeaderError, OSError) as exc:
        logger.exception("Unable to deliver auth email to %s", to_email)
        raise EmailDeliveryError() from exc


def _ensure_email_backend_configured() -> None:
    """Validate that SMTP credentials are present before attempting delivery."""

    if settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend":
        return

    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        logger.error(
            "Email backend credentials are missing: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD"
        )
        raise EmailDeliveryError(
            _(
                "SMTP-настройки не заданы. Укажите EMAIL_HOST_USER и "
                "EMAIL_HOST_PASSWORD для отправки писем."
            )
        )


def _resolve_registration_template(locale: str) -> str:
    normalized = (locale or "ru").lower()
    if normalized.startswith("uz"):
        return "accounts/emails/registration_code_uz.txt"
    return "accounts/emails/registration_code_ru.txt"


def send_registration_code_email(*, to_email: str, code: str, locale: str = "ru") -> None:
    subject_map = {
        "ru": "Подтверждение почты — 6-значный код",
        "uz": "Pochta tasdiqlash — 6 xonali kod",
    }
    normalized = (locale or "ru").lower()
    subject = subject_map.get("uz" if normalized.startswith("uz") else "ru")
    template = _resolve_registration_template(locale)
    send_auth_email(
        template=template,
        subject=subject,
        to_email=to_email,
        context={"code": code},
    )

