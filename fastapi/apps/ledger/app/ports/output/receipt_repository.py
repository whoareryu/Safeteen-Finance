from __future__ import annotations

from abc import ABC, abstractmethod

from ledger.domain.entities.receipt_entity import ReceiptEntity


class ReceiptRepository(ABC):

    @abstractmethod
    async def save(self, entity: ReceiptEntity) -> ReceiptEntity:
        pass

    @abstractmethod
    async def get(self, receipt_id: int) -> ReceiptEntity:
        pass

    @abstractmethod
    async def list_by_owner(self, owner_user_id: int) -> list[ReceiptEntity]:
        pass
