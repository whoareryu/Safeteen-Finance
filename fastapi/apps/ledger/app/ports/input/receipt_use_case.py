from __future__ import annotations

from abc import ABC, abstractmethod

from ledger.app.dtos.receipt_dto import ReceiptResult, ReceiptUploadCommand


class ReceiptUseCase(ABC):
    """Inbound 입력 포트 — 영수증 사진 업로드 기반 가계부 기록."""

    @abstractmethod
    async def upload(self, command: ReceiptUploadCommand) -> ReceiptResult:
        pass

    @abstractmethod
    async def list_by_owner(self, owner_user_id: int) -> list[ReceiptResult]:
        pass

    @abstractmethod
    async def get(self, receipt_id: int) -> ReceiptResult:
        pass
