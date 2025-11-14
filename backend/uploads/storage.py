from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage

_private_root = Path(getattr(settings, "PRIVATE_MEDIA_ROOT", settings.MEDIA_ROOT / "private"))
_private_root.mkdir(parents=True, exist_ok=True)

private_storage = FileSystemStorage(location=str(_private_root))

__all__ = ["private_storage"]
