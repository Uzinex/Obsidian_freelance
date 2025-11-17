from __future__ import annotations

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def send_auth_email(*, template: str, subject: str, to_email: str, context: dict) -> None:
    body = render_to_string(template, context)
    send_mail(subject, body, None, [to_email], fail_silently=True)


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
