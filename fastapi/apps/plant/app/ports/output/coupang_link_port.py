from __future__ import annotations

from abc import ABC, abstractmethod


class CoupangLinkPort(ABC):

    @abstractmethod
    def build_link(self, keyword: str) -> str:
        pass
