from __future__ import annotations

from pydantic import BaseModel


class ImageUploadResponseSchema(BaseModel):
    url: str
