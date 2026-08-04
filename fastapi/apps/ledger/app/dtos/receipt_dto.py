from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class ReceiptUploadCommand:
    owner_user_id: int
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class ReceiptItemResult:
    name: str
    quantity: float
    unit_price: float
    amount: float


@dataclass(frozen=True)
class ReceiptResult:
    id: int
    owner_user_id: int
    image_url: str
    store_name: str
    purchase_date: date
    total_amount: float
    category: str
    items: list[ReceiptItemResult]
    created_at: datetime
