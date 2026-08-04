from __future__ import annotations

from ledger.adapter.inbound.api.schemas.receipt_schema import ReceiptItemResponse, ReceiptResponse
from ledger.app.dtos.receipt_dto import ReceiptResult


def to_response(result: ReceiptResult) -> ReceiptResponse:
    return ReceiptResponse(
        id=result.id,
        owner_user_id=result.owner_user_id,
        image_url=result.image_url,
        store_name=result.store_name,
        purchase_date=result.purchase_date,
        total_amount=result.total_amount,
        category=result.category,
        items=[
            ReceiptItemResponse(
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                amount=item.amount,
            )
            for item in result.items
        ],
        created_at=result.created_at,
    )
