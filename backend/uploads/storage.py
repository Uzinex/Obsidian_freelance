from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage

_private_root = Path(
    getattr(settings, "PRIVATE_MEDIA_ROOT", settings.MEDIA_ROOT / "private")
)
_private_root.mkdir(parents=True, exist_ok=True)


class PrivateMediaStorage(FileSystemStorage):
    """Storage that always targets the configured private media root."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", str(_private_root))
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        path, args, kwargs = super().deconstruct()
        kwargs.pop("location", None)
        return path, args, kwargs


private_storage = PrivateMediaStorage()

__all__ = ["private_storage", "PrivateMediaStorage"]
