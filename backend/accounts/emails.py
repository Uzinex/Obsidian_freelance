from __future__ import annotations

from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


class EmailDeliveryError(Exception):
    """Raised when transactional emails cannot be delivered."""

    default_message = _(
        "Не удалось отправить код проверки. Проверьте действительность вашего Gmail."
    )

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


def send_auth_email(*, template: str, subject: str, to_email: str, context: dict) -> None:
    body = render_to_string(template, context)
    from_email = settings.DEFAULT_FROM_EMAIL or "obsidianfreelance@gmail.com"
    try:
        send_mail(subject, body, from_email, [to_email], fail_silently=False)
    except (SMTPException, BadHeaderError, OSError) as exc:
        raise EmailDeliveryError() from exc


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
