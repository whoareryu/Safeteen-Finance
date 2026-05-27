import logging
import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# `python main.py` 를 backend/apps 에서 실행해도 backend/.env 를 읽도록 고정
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_ROOT / ".env")
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_INIT_ERROR: Optional[str] = None

# SQLAlchemy 2.0 — DeclarativeBase (모든 ORM 모델이 상속)
class Base(DeclarativeBase):
    pass


class IntIdPrimaryKeyMixin:
    """모든 테이블 공통 PK — `docs/DevOps/Backend/ENTITY_RULE.md`.

    int 자동 증가, DB 컬럼명·속성명 모두 ``id``.
    ``sort_order`` 로 서브클래스 컬럼보다 앞에 두어 물리 DDL에서도 id 가 선행되게 한다.
    새 모델: ``class Foo(IntIdPrimaryKeyMixin, Base):``
    """

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, sort_order=-1000
    )


engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None

# Alembic·기존 동기 라우트(auth, secom)용
sync_engine = None
SyncSessionLocal: Optional[sessionmaker[Session]] = None


def _normalize_async_url(url: str) -> str:
    """Neon PostgreSQL — 비동기 엔진용 URL (psycopg 3 async)."""
    if url.startswith("postgresql://") and "+" not in url.split("://", 1)[0]:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _normalize_sync_url(url: str) -> str:
    """Alembic·동기 세션용 URL."""
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
        async_url = get_async_database_url()
        sync_url = get_sync_database_url()

        # 1) Neon — 비동기 전용 엔진 (예제의 create_async_engine)
        engine = create_async_engine(
            async_url,
            echo=False,
            pool_pre_ping=True,
        )
        # 2) 비동기 세션 팩토리 (예제의 async_sessionmaker)
        async_session_maker = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )

        # Alembic / 동기 Depends(get_sync_db) 호환
        sync_engine = create_engine(sync_url, pool_pre_ping=True)
        SyncSessionLocal = sessionmaker(
            bind=sync_engine,
            expire_on_commit=False,
        )
        logger.info("Neon PostgreSQL 엔진 초기화 완료 (async + sync)")
    except Exception as e:
        DATABASE_INIT_ERROR = (
            f"에러: DB 엔진 생성 중 오류가 발생했습니다. ({type(e).__name__}: {e})"
        )
        logger.exception(DATABASE_INIT_ERROR)


def _register_orm_models() -> None:
    """create_all 전에 ORM 모델이 Base.metadata 에 등록되도록 import."""
    from apps.auth.user_model import User  # noqa: F401
    from apps.gourmet.app.models.daily_recommendation import DailyRecommendation  # noqa: F401
    from apps.gourmet.app.models.favorite import Favorite  # noqa: F401
    from apps.gourmet.app.models.meal_plan import MealPlan  # noqa: F401
    from apps.gourmet.app.models.biz_classification import BizClassification  # noqa: F401
    from apps.gourmet.app.models.food_category import FoodCategory  # noqa: F401
    from apps.gourmet.app.models.restaurant import Restaurant  # noqa: F401
    from apps.gourmet.app.models.restaurant_contact import RestaurantContact  # noqa: F401
    from apps.gourmet.app.models.restaurant_menu import RestaurantMenu  # noqa: F401
    from apps.gourmet.app.models.restaurant_operating_hour import (  # noqa: F401
        RestaurantOperatingHour,
    )
    from apps.gourmet.app.models.restaurant_price import RestaurantPrice  # noqa: F401
    from apps.gourmet.app.models.restaurant_tag import RestaurantTag  # noqa: F401
    from apps.gourmet.app.models.search_query_log import SearchQueryLog  # noqa: F401
    from apps.gourmet.app.models.sigungu_district import SigunguDistrict  # noqa: F401
    from apps.gourmet.app.models.tag import Tag  # noqa: F401
def ensure_sync_tables() -> None:
    """동기 엔진으로 users 테이블 생성 (없을 때만)."""
    if sync_engine is None:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "동기 엔진이 초기화되지 않았습니다."
        )
    _register_orm_models()
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Neon DB 테이블 확인 완료 (sync create_all)")


async def init_db() -> None:
    """비동기로 테이블 생성 (users)."""
    if engine is None:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "비동기 엔진이 초기화되지 않았습니다."
        )
    _register_orm_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Neon DB 테이블 확인 완료 (async create_all)")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends — 비동기 세션."""
    if DATABASE_INIT_ERROR or async_session_maker is None:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "데이터베이스를 초기화할 수 없습니다."
        )
    async with async_session_maker() as session:
        yield session


def get_sync_db():
    """FastAPI Depends — 동기 세션 (Alembic·레거시 라우트)."""
    if DATABASE_INIT_ERROR or sync_engine is None or SyncSessionLocal is None:
        raise RuntimeError(
            DATABASE_INIT_ERROR or "데이터베이스를 초기화할 수 없습니다."
        )
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# 기존 import 호환
AsyncSessionLocal = async_session_maker
