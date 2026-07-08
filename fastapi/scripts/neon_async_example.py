"""
Neon PostgreSQL + SQLAlchemy 2.0 비동기 예제.

실행 (backend 디렉터리에서):
  python -m scripts.neon_async_example

.env 의 DATABASE_URL 이 설정되어 있어야 합니다.
"""

import asyncio
import sys
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from apps.auth.user_model import User  # noqa: F401 — Base.metadata
from apps.database import Base, get_async_database_url


async def main() -> None:
    engine = create_async_engine(get_async_database_url(), echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        stmt = select(User).limit(5)
        result = await session.execute(stmt)
        for u in result.scalars().all():
            print(f"users: {u.username} ({u.nickname}) role={u.role.value}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
