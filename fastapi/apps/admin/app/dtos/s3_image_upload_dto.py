from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageUploadCommand:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class ImageUploadResult:
    url: str
