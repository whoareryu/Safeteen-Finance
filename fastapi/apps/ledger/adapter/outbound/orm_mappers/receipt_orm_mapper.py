from __future__ import annotations

from ledger.adapter.outbound.orm.receipt_item_orm import ReceiptItemORM
from ledger.adapter.outbound.orm.receipt_orm import ReceiptORM
from ledger.domain.entities.receipt_entity import ReceiptEntity, ReceiptItemEntity


def item_to_entity(orm: ReceiptItemORM) -> ReceiptItemEntity:
    return ReceiptItemEntity(
        id=orm.id,
        name=orm.name,
        quantity=orm.quantity,
        unit_price=orm.unit_price,
        amount=orm.amount,
    )


def item_to_orm(entity: ReceiptItemEntity, receipt_id: int) -> ReceiptItemORM:
    return ReceiptItemORM(
        receipt_id=receipt_id,
        name=entity.name,
        quantity=entity.quantity,
        unit_price=entity.unit_price,
        amount=entity.amount,
    )


def to_entity(orm: ReceiptORM, item_orms: list[ReceiptItemORM]) -> ReceiptEntity:
    return ReceiptEntity(
        id=orm.id,
        owner_user_id=orm.owner_user_id,
        image_url=orm.image_url,
        store_name=orm.store_name,
        purchase_date=orm.purchase_date,
        total_amount=orm.total_amount,
        category=orm.category,
        items=[item_to_entity(item) for item in item_orms],
        created_at=orm.created_at,
    )


def to_orm(entity: ReceiptEntity) -> ReceiptORM:
    return ReceiptORM(
        owner_user_id=entity.owner_user_id,
        image_url=entity.image_url,
        store_name=entity.store_name,
        purchase_date=entity.purchase_date,
        total_amount=entity.total_amount,
        category=entity.category,
    )
