from dataclasses import dataclass


@dataclass
class LensQueryDto:
    query: str
    collection: str
    limit: int = 5


@dataclass
class LensResultDto:
    hits: list[dict]  # [{score, payload}]
