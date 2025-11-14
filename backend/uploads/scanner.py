from __future__ import annotations

import logging

from obsidian_backend import jwt_settings as jwt_conf

logger = logging.getLogger(__name__)

_FEATURE_FLAG = "upload.scanner"


def scanner_enabled() -> bool:
    return jwt_conf.FEATURE_FLAGS.get(_FEATURE_FLAG, False)


def scan_bytes(data: bytes, *, filename: str) -> None:
    """Placeholder antivirus scanner hook."""

    if not scanner_enabled():
        return
    # In production this should call out to the configured antivirus engine.
    # For now we log the attempt to ensure the integration point is covered.
    logger.info("Antivirus scan requested for %%s (%%d bytes)", filename, len(data))
    # Raise if integration missing to avoid silently allowing unscanned files.
    raise RuntimeError("Antivirus scanner feature flag enabled but no scanner is configured")


__all__ = ["scan_bytes", "scanner_enabled"]
