from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from titanic.adapter.outbound.orm.database import SessionLocal
from titanic.adapter.outbound.orm.titanic_model import TitanicRecord
from titanic.app.ports.output.walter_roaster_repository import WalterRoasterRepository

_ROW_FIELDS = [
    "id", "passenger", "survived", "pclass", "name", "gender",
    "age", "sibsp", "parch", "ticket", "fare", "cabin", "embarked",
]


class WalterRoasterPgRepository(WalterRoasterRepository):
    async def list_paginated(self, page: int, page_size: int) -> tuple[int, list[dict[str, Any]]]:
        if SessionLocal is None:
            raise RuntimeError("DATABASE_URL is missing.")
        async with SessionLocal() as session:
            total = (await session.execute(select(func.count()).select_from(TitanicRecord))).scalar_one()
            rows = (await session.execute(
                select(TitanicRecord).order_by(TitanicRecord.id).offset((page - 1) * page_size).limit(page_size)
            )).scalars().all()
            items = [{f: getattr(r, f) for f in _ROW_FIELDS} for r in rows]
            return total, items