"""Neon PostgreSQL 연결·세션·FastAPI DI (async only)."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from typing import Annotated, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BACKEND_DIR / ".env")

logger = logging.getLogger(__name__)

DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
DATABASE_INIT_ERROR: Optional[str] = None


# ==============================================================================
# 1. SQLAlchemy 2.0 최신 Declarative Base & Mixin 선언
# ==============================================================================
class Base(DeclarativeBase):
    """SQLAlchemy 2.0 스타일 전역 선언형 베이스 클래스"""
    pass


class IntIdPrimaryKeyMixin:
    """SQLAlchemy 2.0 스타일 공통 PK 믹스인
    
    Mapped[int]를 통해 내부 데이터 타입(Integer)이 자동으로 추론되므로,
    mapped_column() 내부에 명시적인 Integer 선언을 생략합니다.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


# ==============================================================================
# 2. ORM 모델 동적 등록 (Alembic 및 create_all 감지용)
# ==============================================================================
def import_models() -> None:
    """분산된 도메인의 ORM 모델들을 Base.metadata에 등록하기 위해 명시적으로 임포트합니다.

    이 함수는 본 파일의 테이블 생성 시점뿐만 아니라,
    Alembic의 env.py 상단에서도 호출되어 autogenerate 감지를 보장합니다.
    """
    models_to_load = [
        # Titanic — 12개 ORM
        "titanic.adapter.outbound.orm.crew_andrews_architect_orm",
        "titanic.adapter.outbound.orm.crew_hartley_violin_orm",
        "titanic.adapter.outbound.orm.crew_james_director_orm",
        "titanic.adapter.outbound.orm.crew_lowe_boat_orm",
        "titanic.adapter.outbound.orm.crew_smith_captain_orm",
        "titanic.adapter.outbound.orm.crew_walter_roaster_orm",
        "titanic.adapter.outbound.orm.passenger_cal_tester_orm",
        "titanic.adapter.outbound.orm.passenger_isidor_couple_orm",
        "titanic.adapter.outbound.orm.passenger_jack_trainer_orm",
        "titanic.adapter.outbound.orm.passenger_molly_scaler_orm",
        "titanic.adapter.outbound.orm.passenger_rose_model_orm",
        "titanic.adapter.outbound.orm.passenger_ruth_survivor_orm",
    ]

    for model_path in models_to_load:
        try:
            __import__(model_path, fromlist=["*"])
        except ImportError as e:
            logger.warning("모델 로드 실패 (ImportError): %s -> %s", model_path, e)


# ==============================================================================
# 3. 비동기 데이터베이스 엔진 및 세션 팩토리 초기화
# ==============================================================================
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

    # asyncpg 전용 SSL/파라미터 호환성 패치
    if "sslmode" in query:
        if query["sslmode"] == "require":
            query["ssl"] = "require"
        query.pop("sslmode", None)
    query.pop("channel_binding", None)

    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def init_engine() -> None:
    """비동기 엔진·세션 팩토리를 지연 초기화합니다 (import 시점 연결 방지)."""
    global engine, async_session_maker, DATABASE_URL, DATABASE_INIT_ERROR

    if engine is not None:
        return

    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        DATABASE_INIT_ERROR = "에러: DATABASE_URL이 환경 변수에 설정되지 않았습니다."
        logger.error(DATABASE_INIT_ERROR)
        return

    try:
        async_url = get_async_database_url()
        echo_sql = os.getenv("SQL_ECHO", "").lower() in ("1", "true", "yes")
        engine = create_async_engine(async_url, echo=echo_sql, pool_pre_ping=True)
        async_session_maker = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            autoflush=False,
        )
        DATABASE_INIT_ERROR = None
        logger.info("Neon PostgreSQL 비동기 엔진 초기화 완료")
    except Exception as e:
        engine = None
        async_session_maker = None
        DATABASE_INIT_ERROR = (
            f"에러: 비동기 DB 엔진 생성 중 오류가 발생했습니다. ({type(e).__name__}: {e})"
        )
        logger.exception(DATABASE_INIT_ERROR)


async def dispose_engine() -> None:
    """앱 종료 시 엔진·세션 팩토리를 정리합니다."""
    global engine, async_session_maker

    if engine is not None:
        await engine.dispose()
    engine = None
    async_session_maker = None
    logger.info("비동기 DB 엔진 dispose 완료")


def _should_auto_create_tables() -> bool:
    """개발·명시 플래그에서만 create_all 실행 (Alembic과 이중 관리 완화)."""
    if os.getenv("AUTO_CREATE_TABLES", "").lower() in ("1", "true", "yes"):
        return True
    return os.getenv("ENV", "development").lower() == "development"


# ==============================================================================
# 4. 데이터베이스 생명주기 및 의존성 주입(DI) 관리
# ==============================================================================
async def ensure_tables() -> None:
    """개발 환경 등에서 선언된 모델을 기반으로 테이블을 자동 생성합니다."""
    init_engine()
    if engine is None:
        raise RuntimeError(DATABASE_INIT_ERROR or "비동기 DB 엔진이 초기화되지 않았습니다.")

    # 테이블 생성 전 모든 모델을 메타데이터에 등록
    import_models()

    from core.matrix.grid_neo_theone_base import Base as DomainBase
    async with engine.begin() as conn:
        await conn.run_sync(DomainBase.metadata.create_all)
    logger.info("Neon DB 테이블 확인 완료 (async create_all)")


async def init_db() -> None:
    init_engine()
    if engine is None:
        return
    if _should_auto_create_tables():
        await ensure_tables()
    else:
        logger.info("create_all 생략 (ENV/AUTO_CREATE_TABLES). Alembic 마이그레이션을 사용하세요.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 경로 연산자에서 사용할 SQLAlchemy 2.0 공식 비동기 세션 제너레이터"""
    if async_session_maker is None:
        init_engine()
    if DATABASE_INIT_ERROR or async_session_maker is None:
        raise RuntimeError(DATABASE_INIT_ERROR or "데이터베이스를 초기화할 수 없습니다.")

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ==============================================================================
# 5. 레거시 호환성 레이어 및 의존성 어노테이션 정의
# ==============================================================================
AsyncSessionLocal = async_session_maker
SyncSessionLocal = None
sync_engine = None


async def get_sync_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


# FastAPI 0.95+ 사양의 수려한 의존성 주입 타입 선언
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
    "dispose_engine",
    "ensure_tables",
    "get_async_database_url",
    "get_db",
    "get_sync_db",
    "init_db",
    "init_engine",
    "sync_engine",
    "import_models",
]