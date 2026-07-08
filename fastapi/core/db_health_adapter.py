from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DbHealthAdapter:
    @staticmethod
    async def neon_time_check(db: AsyncSession) -> dict[str, str | bool]:
        result = await db.execute(text("SELECT NOW() AS server_time"))
        return {"ok": True, "server_time": str(result.scalar_one())}
1