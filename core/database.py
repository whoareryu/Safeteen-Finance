"""Neon PostgreSQL 연결·세션·FastAPI DI (async only)."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from typing import Annotated, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_INIT_ERROR: Optional[str] = None


class Base(DeclarativeBase):
    pass


class IntIdPrimaryKeyMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_async_database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError(DATABASE_INIT_ERROR or "DATABASE_URL이 설정되지 않았습니다.")
    async_url = DATABASE_URL
    if "+psycopg" in async_url:
        async_url = async_url.replace("+psycopg", "+asyncpg", 1)
    elif async_url.startswith("postgresql://") and "+" not in async_url.split("://", 1)[0]:
        async_url = async_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parts = urlsplit(async_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))

    # asyncpg 호환 파라미터만 남긴다.
    if "sslmode" in query:
        if query["sslmode"] == "require":
            query["ssl"] = "require"
        query.pop("sslmode", None)
    query.pop("channel_binding", None)

    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


if not DATABASE_URL:
    DATABASE_INIT_ERROR = "에러: DATABASE_URL이 환경 변수에 설정되지 않았습니다."
    logger.error(DATABASE_INIT_ERROR)
else:
    try:
        async_url = get_async_database_url()
        engine = create_async_engine(async_url, echo=False, pool_pre_ping=True)
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
        logger.info("Neon PostgreSQL 비동기 엔진 초기화 완료")
    except Exception as e:
        DATABASE_INIT_ERROR = f"에러: 비동기 DB 엔진 생성 중 오류가 발생했습니다. ({type(e).__name__}: {e})"
        logger.exception(DATABASE_INIT_ERROR)


def _register_orm_models() -> None:
    try:
        from apps.friday_13th.auth.user_model import User  # noqa: F401
    except ImportError:
        pass
    try:
        from apps.friday_13th.domain.entities.user import SecUser  # noqa: F401
    except ImportError:
        pass
    try:
        from apps.gourmet.app.models.restaurant import Restaurant  # noqa: F401
    except ImportError:
        pass
    try:
        from apps.titanic.adapter.outbound.orm.models import TitanicPassengerModel  # noqa: F401
    except ImportError:
        pass
    try:
        from apps.titanic.adapter.outbound.orm.titanic_model import TitanicRecord  # noqa: F401
    except ImportError:
        pass


async def ensure_tables() -> None:
    if engine is None:
        raise RuntimeError(DATABASE_INIT_ERROR or "비동기 DB 엔진이 초기화되지 않았습니다.")
    _register_orm_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Neon DB 테이블 확인 완료 (async create_all)")


async def init_db() -> None:
    if engine is None:
        return
    await ensure_tables()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if DATABASE_INIT_ERROR or async_session_maker is None:
        raise RuntimeError(DATABASE_INIT_ERROR or "데이터베이스를 초기화할 수 없습니다.")
    async with async_session_maker() as session:
        yield session


# legacy compatibility exports (removed sync path)
AsyncSessionLocal = async_session_maker
SyncSessionLocal = None
sync_engine = None


async def get_sync_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]
SyncSessionDep = AsyncSessionDep

UserRepositoryDep = None
UserServiceDep = None

__all__ = [
    "AsyncSessionDep",
    "AsyncSessionLocal",
    "Base",
    "DATABASE_INIT_ERROR",
    "DATABASE_URL",
    "IntIdPrimaryKeyMixin",
    "SyncSessionDep",
    "SyncSessionLocal",
    "UserRepositoryDep",
    "UserServiceDep",
    "async_session_maker",
    "engine",
    "ensure_tables",
    "get_async_database_url",
    "get_db",
    "get_sync_db",
    "init_db",
    "sync_engine",
]
