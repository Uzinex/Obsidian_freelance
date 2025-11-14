from __future__ import annotations

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def send_auth_email(*, template: str, subject: str, to_email: str, context: dict) -> None:
    body = render_to_string(template, context)
    send_mail(subject, body, None, [to_email], fail_silently=True)
