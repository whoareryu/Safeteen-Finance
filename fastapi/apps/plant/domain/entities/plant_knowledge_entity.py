from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlantKnowledgeEntity:
    id: int
    category: str
    name: str
    description: str
