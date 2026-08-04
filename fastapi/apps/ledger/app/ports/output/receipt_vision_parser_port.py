from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ExtractedReceiptItem:
    name: str
    quantity: float
    unit_price: float
    amount: float


@dataclass(frozen=True)
class ReceiptExtraction:
    store_name: str
    purchase_date: date
    total_amount: float
    category: str
    items: list[ExtractedReceiptItem]


class ReceiptVisionParserPort(ABC):
    """Outbound 출력 포트 — 영수증 이미지에서 구조화된 가계부 정보를 추출한다."""

    @abstractmethod
    async def parse(self, data: bytes, content_type: str) -> ReceiptExtraction:
        pass
