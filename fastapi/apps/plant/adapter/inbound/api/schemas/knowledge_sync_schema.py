from __future__ import annotations

from pydantic import BaseModel


class KnowledgeSyncResponse(BaseModel):
    species_upserted: int
    sources: list[str]
