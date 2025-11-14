from __future__ import annotations

import io
from typing import Iterable, Tuple

from PIL import Image

ALLOWED_MIME_TYPES = {
    "image/jpeg": b"\xff\xd8\xff",
    "image/png": b"\x89PNG\r\n\x1a\n",
    "application/pdf": b"%PDF",
}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


class FileValidationError(ValueError):
    pass


def _matches_signature(data: bytes, signature: bytes) -> bool:
    return data.startswith(signature)


def detect_mime_type(data: bytes) -> str:
    for mime, signature in ALLOWED_MIME_TYPES.items():
        if _matches_signature(data, signature):
            return mime
    raise FileValidationError("Unsupported or untrusted file type")


def ensure_size_within_limits(size: int) -> None:
    if size > MAX_FILE_SIZE_BYTES:
        raise FileValidationError("File exceeds maximum allowed size of 20 MB")


def scrub_exif_if_image(data: bytes, mime_type: str) -> bytes:
    if not mime_type.startswith("image/"):
        return data
    with Image.open(io.BytesIO(data)) as image:
        image.info.pop("exif", None)
        output = io.BytesIO()
        image.save(output, format=image.format)
        return output.getvalue()
