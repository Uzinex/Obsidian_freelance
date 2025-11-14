from __future__ import annotations

import re
from typing import Iterable

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .passwords import COMMON_PASSWORDS


class PasswordComplexityValidator:
    """Require passwords to contain multiple character classes."""

    def __init__(self, min_length: int = 12) -> None:
        self.min_length = min_length
        self.patterns = {
            "uppercase": re.compile(r"[A-Z]"),
            "lowercase": re.compile(r"[a-z]"),
            "digit": re.compile(r"[0-9]"),
            "symbol": re.compile(r"[^A-Za-z0-9]"),
        }

    def validate(self, password: str, user=None) -> None:  # pragma: no cover - thin wrapper
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )
        missing = [
            name
            for name, pattern in self.patterns.items()
            if not pattern.search(password or "")
        ]
        if missing:
            raise ValidationError(
                _("Password must include characters from these categories: %(categories)s."),
                code="password_missing_character_types",
                params={"categories": ", ".join(missing)},
            )

    def get_help_text(self) -> str:
        return _(
            "Your password must contain at least %(min_length)d characters and include upper, lower, numeric, and symbol characters."
        ) % {"min_length": self.min_length}


class CommonPasswordListValidator:
    """Reject passwords that appear in a local deny-list."""

    def __init__(self, bad_passwords: Iterable[str] | None = None) -> None:
        self.bad_passwords = set(password.lower() for password in (bad_passwords or COMMON_PASSWORDS))

    def validate(self, password: str, user=None) -> None:  # pragma: no cover - thin wrapper
        if password.lower() in self.bad_passwords:
            raise ValidationError(
                _("This password is too common."),
                code="password_too_common",
            )

    def get_help_text(self) -> str:
        return _("Avoid using passwords from common lists.")
