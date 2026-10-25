"""Validated local storage for vehicle image uploads."""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

UPLOAD_DIRECTORY = Path(__file__).resolve().parents[2] / "uploads"
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}


async def save_vehicle_image(image: UploadFile) -> str:
    """Validate an uploaded vehicle image and save it under a generated filename."""
    extension = ALLOWED_CONTENT_TYPES.get(image.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Image must be a PNG, JPEG, or WebP file",
        )

    content = await image.read(MAX_IMAGE_SIZE + 1)
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must be 5 MB or smaller",
        )

    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}{extension}"
    (UPLOAD_DIRECTORY / filename).write_bytes(content)
    return filename
