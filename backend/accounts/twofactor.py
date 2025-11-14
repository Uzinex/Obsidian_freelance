from __future__ import annotations

import secrets
from typing import List, Tuple

import pyotp
from django.utils import timezone

from .models import TwoFactorBackupCode, TwoFactorConfig


def ensure_config(user) -> TwoFactorConfig:
    config, _created = TwoFactorConfig.objects.get_or_create(
        user=user,
        defaults={"secret": TwoFactorConfig.generate_secret()},
    )
    if not config.secret:
        config.secret = TwoFactorConfig.generate_secret()
        config.save(update_fields=["secret", "updated_at"])
    return config


def generate_provisioning_uri(user) -> Tuple[TwoFactorConfig, str]:
    config = ensure_config(user)
    totp = pyotp.TOTP(config.secret)
    uri = totp.provisioning_uri(name=user.email or user.nickname, issuer_name="Obsidian Platform")
    return config, uri


def verify_totp(config: TwoFactorConfig, code: str) -> bool:
    config.ensure_ready()
    totp = pyotp.TOTP(config.secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(config: TwoFactorConfig, count: int = 10) -> List[str]:
    config.backup_codes.all().delete()
    codes: List[str] = []
    for _ in range(count):
        code = secrets.token_hex(4)
        codes.append(code)
        TwoFactorBackupCode.objects.create(
            config=config,
            code_hash=TwoFactorBackupCode.hash_code(code),
        )
    config.backup_codes_generated_at = timezone.now()
    config.save(update_fields=["backup_codes_generated_at", "updated_at"])
    return codes


def use_backup_code(config: TwoFactorConfig, code: str) -> bool:
    code_hash = TwoFactorBackupCode.hash_code(code)
    try:
        record = config.backup_codes.get(code_hash=code_hash, used_at__isnull=True)
    except TwoFactorBackupCode.DoesNotExist:
        return False
    record.used_at = timezone.now()
    record.save(update_fields=["used_at"])
    return True
