from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class ReceiptItemResponse(BaseModel):
    name: str
    quantity: float
    unit_price: float
    amount: float


class ReceiptResponse(BaseModel):
    id: int
    owner_user_id: int
    image_url: str
    store_name: str
    purchase_date: date
    total_amount: float
    category: str
    items: list[ReceiptItemResponse]
    created_at: datetime
