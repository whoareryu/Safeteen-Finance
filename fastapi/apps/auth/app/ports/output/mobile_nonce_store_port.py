from __future__ import annotations

from abc import ABC, abstractmethod


class NonceStorePort(ABC):

    @abstractmethod
    async def consume_once(self, nonce: str) -> bool:
        """nonce를 1회용으로 소비한다. 이미 소비됐거나 존재하지 않으면 False."""
