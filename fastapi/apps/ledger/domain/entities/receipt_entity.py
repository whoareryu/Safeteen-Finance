from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class ReceiptItemEntity:
    id: int | None
    name: str
    quantity: float
    unit_price: float
    amount: float


@dataclass
class ReceiptEntity:
    id: int | None
    owner_user_id: int
    image_url: str
    store_name: str
    purchase_date: date
    total_amount: float
    category: str
    items: list[ReceiptItemEntity] = field(default_factory=list)
    created_at: datetime | None = None
