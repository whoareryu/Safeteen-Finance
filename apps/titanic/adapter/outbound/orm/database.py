"""Titanic outbound — Neon PostgreSQL sync 세션 (apps.database 위임)."""

from core.database import Base, SyncSessionLocal, sync_engine

engine = sync_engine
SessionLocal = SyncSessionLocal

__all__ = ["Base", "SessionLocal", "engine"]
