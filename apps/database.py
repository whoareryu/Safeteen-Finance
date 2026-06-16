"""apps.database — core.database 재익스포트 + 스크립트 호환 레이어."""

from __future__ import annotations

from core.matrix.gird_oracle_database_manager import (  # noqa: F401
    AsyncSessionDep,
    AsyncSessionLocal,
    Base,
    DATABASE_INIT_ERROR,
    DATABASE_URL,
    IntIdPrimaryKeyMixin,
    SyncSessionDep,
    SyncSessionLocal,
    async_session_maker,
    dispose_engine,
    engine,
    ensure_tables,
    get_async_database_url,
    get_db,
    get_sync_db,
    import_models,
    init_db,
    init_engine,
    sync_engine,
)

ensure_sync_tables = ensure_tables


def get_sync_database_url() -> str:
    """동기 드라이버용 DB URL (asyncpg → psycopg2 호환)."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL이 설정되지 않았습니다.")
    url = DATABASE_URL
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgresql+psycopg://", "postgresql://")
    return url


__all__ = [
    "AsyncSessionDep",
    "AsyncSessionLocal",
    "Base",
    "DATABASE_INIT_ERROR",
    "DATABASE_URL",
    "IntIdPrimaryKeyMixin",
    "SyncSessionDep",
    "SyncSessionLocal",
    "async_session_maker",
    "dispose_engine",
    "engine",
    "ensure_sync_tables",
    "ensure_tables",
    "get_async_database_url",
    "get_db",
    "get_sync_database_url",
    "get_sync_db",
    "import_models",
    "init_db",
    "init_engine",
    "sync_engine",
]
