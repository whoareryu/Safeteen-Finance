from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ledger.adapter.outbound.orm.receipt_item_orm import ReceiptItemORM
from ledger.adapter.outbound.orm.receipt_orm import ReceiptORM
from ledger.adapter.outbound.orm_mappers.receipt_orm_mapper import item_to_orm, to_entity, to_orm
from ledger.app.ports.output.receipt_repository import ReceiptRepository
from ledger.domain.entities.receipt_entity import ReceiptEntity


class ReceiptPgRepository(ReceiptRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: ReceiptEntity) -> ReceiptEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()

        item_orms = [item_to_orm(item, orm.id) for item in entity.items]  # type: ignore[arg-type]
        for item_orm in item_orms:
            self.session.add(item_orm)
        await self.session.flush()

        return to_entity(orm, item_orms)

    async def get(self, receipt_id: int) -> ReceiptEntity:
        orm = await self.session.get(ReceiptORM, receipt_id)
        if orm is None:
            raise ValueError(f"Receipt {receipt_id} not found")
        item_orms = (
            (
                await self.session.execute(
                    select(ReceiptItemORM).where(ReceiptItemORM.receipt_id == receipt_id)
                )
            )
            .scalars()
            .all()
        )
        return to_entity(orm, list(item_orms))

    async def list_by_owner(self, owner_user_id: int) -> list[ReceiptEntity]:
        receipt_orms = (
            (
                await self.session.execute(
                    select(ReceiptORM)
                    .where(ReceiptORM.owner_user_id == owner_user_id)
                    .order_by(ReceiptORM.purchase_date.desc(), ReceiptORM.id.desc())
                )
            )
            .scalars()
            .all()
        )
        if not receipt_orms:
            return []

        receipt_ids = [r.id for r in receipt_orms]
        item_orms = (
            (
                await self.session.execute(
                    select(ReceiptItemORM).where(ReceiptItemORM.receipt_id.in_(receipt_ids))
                )
            )
            .scalars()
            .all()
        )
        items_by_receipt: dict[int, list[ReceiptItemORM]] = {}
        for item in item_orms:
            items_by_receipt.setdefault(item.receipt_id, []).append(item)

        return [to_entity(r, items_by_receipt.get(r.id, [])) for r in receipt_orms]
