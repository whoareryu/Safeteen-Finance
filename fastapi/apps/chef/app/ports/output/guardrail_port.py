from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class GuardrailVerdict:
    violates: bool
    score: float
    matched: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)


class GuardrailPort(ABC):
    @abstractmethod
    def score(self, text: str) -> GuardrailVerdict: ...
