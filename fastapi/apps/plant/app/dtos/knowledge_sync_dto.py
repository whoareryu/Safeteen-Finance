from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlantKnowledgeFact:
    species_name: str
    source_api: str
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class KnowledgeSyncResult:
    species_upserted: int
    sources: list[str]
