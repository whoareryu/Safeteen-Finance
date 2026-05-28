"""Neon PostgreSQL 연결·세션·FastAPI DI."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from typing import Annotated, Optional

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import Integer, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

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
sync_engine = None
SyncSessionLocal: Optional[sessionmaker[Session]] = None


def _normalize_async_url(url: str) -> str:
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "+psycopg", 1)
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _normalize_sync_url(url: str) -> str:
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "+psycopg", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_async_database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "DATABASE_URL이 설정되지 않았습니다."
        )
    return _normalize_async_url(DATABASE_URL)


def get_sync_database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "DATABASE_URL이 설정되지 않았습니다."
        )
    return _normalize_sync_url(DATABASE_URL)


if not DATABASE_URL:
    DATABASE_INIT_ERROR = "에러: DATABASE_URL이 환경 변수에 설정되지 않았습니다."
    logger.error(DATABASE_INIT_ERROR)
else:
    try:
        sync_url = get_sync_database_url()
        sync_engine = create_engine(sync_url, pool_pre_ping=True)
        SyncSessionLocal = sessionmaker(
            bind=sync_engine,
            expire_on_commit=False,
        )
        logger.info("Neon PostgreSQL 동기 엔진 초기화 완료")
    except Exception as e:
        DATABASE_INIT_ERROR = (
            f"에러: 동기 DB 엔진 생성 중 오류가 발생했습니다. ({type(e).__name__}: {e})"
        )
        logger.exception(DATABASE_INIT_ERROR)

    try:
        async_url = get_async_database_url()
        engine = create_async_engine(
            async_url,
            echo=False,
            pool_pre_ping=True,
        )
        async_session_maker = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )
        logger.info("Neon PostgreSQL 비동기 엔진 초기화 완료")
    except Exception as e:
        logger.warning(
            "비동기 DB 엔진 스킵 (%s: %s). 동기 세션은 계속 사용 가능.",
            type(e).__name__,
            e,
        )


def _register_orm_models() -> None:
    try:
        from apps.auth.user_model import User  # noqa: F401
    except ImportError:
        pass
    try:
        from apps.secom.app.models.user_model import SecUser  # noqa: F401
    except ImportError:
        pass
    try:
        from apps.gourmet.app.models.restaurant import Restaurant  # noqa: F401
    except ImportError:
        pass
    try:
        from apps.titanic.adapter.outbound.orm.models import (  # noqa: F401
            TitanicPassengerModel,
        )
    except ImportError:
        pass


def ensure_sync_tables() -> None:
    if sync_engine is None:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "동기 DB 엔진이 초기화되지 않았습니다."
        )
    _register_orm_models()
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Neon DB 테이블 확인 완료 (sync create_all)")


async def init_db() -> None:
    if engine is None:
        return
    _register_orm_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Neon DB 테이블 확인 완료 (async create_all)")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if DATABASE_INIT_ERROR or async_session_maker is None:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "데이터베이스를 초기화할 수 없습니다."
        )
    async with async_session_maker() as session:
        yield session


def get_sync_db():
    if DATABASE_INIT_ERROR or sync_engine is None or SyncSessionLocal is None:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "데이터베이스를 초기화할 수 없습니다."
        )
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


AsyncSessionLocal = async_session_maker

# --- FastAPI Dependency Injection ---

SyncSessionDep = Annotated[Session, Depends(get_sync_db)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_db)]

try:
    from apps.secom.app.repositories.user_repository import UserRepository
    from apps.secom.app.services.user_service import UserService

    def get_user_repository(db: SyncSessionDep) -> UserRepository:
        return UserRepository(db)

    def get_user_service(db: SyncSessionDep) -> UserService:
        return UserService(db)

    UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
    UserServiceDep = Annotated[UserService, Depends(get_user_service)]
except ImportError:
    UserRepository = None  # type: ignore[misc, assignment]
    UserService = None  # type: ignore[misc, assignment]
    UserRepositoryDep = None  # type: ignore[misc, assignment]
    UserServiceDep = None  # type: ignore[misc, assignment]

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
    "ensure_sync_tables",
    "get_async_database_url",
    "get_db",
    "get_sync_database_url",
    "get_sync_db",
    "init_db",
    "sync_engine",
]
