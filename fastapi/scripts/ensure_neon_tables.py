"""Neon 에 통합 users 테이블 생성.

사용:
  cd backend
  python scripts/ensure_neon_tables.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from sqlalchemy import inspect, text

from apps.database import DATABASE_URL, ensure_sync_tables, sync_engine


def main() -> None:
    if not DATABASE_URL or sync_engine is None:
        print("DATABASE_URL 이 없거나 엔진 초기화에 실패했습니다. backend/.env 를 확인하세요.")
        sys.exit(1)

    host = urlparse(DATABASE_URL).hostname
    print(f"연결 대상 Neon host: {host}")

    ensure_sync_tables()

    insp = inspect(sync_engine)
    tables = sorted(insp.get_table_names())
    print("public 스키마 테이블:", tables)

    if "users" in tables:
        with sync_engine.connect() as conn:
            n = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
            print(f"  users: {n} rows")
    if "secom_users" in tables:
        print("  (참고) secom_users 가 남아 있습니다. alembic upgrade head 로 제거할 수 있습니다.")


if __name__ == "__main__":
    main()
