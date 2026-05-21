"""Neon/PostgreSQL — ``users``, ``alembic_version`` 제외 테이블 삭제.

사용 (backend 루트에서):
  python scripts/drop_tables_except_users.py

확인만:
  python scripts/drop_tables_except_users.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from dotenv import load_dotenv

load_dotenv(_backend_root / ".env")

from sqlalchemy import create_engine, text

from apps.database import DATABASE_URL, get_sync_database_url

KEEP = frozenset({"users", "alembic_version"})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="삭제 대상만 출력하고 DROP 하지 않음",
    )
    args = parser.parse_args()

    if not DATABASE_URL:
        print("DATABASE_URL이 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(get_sync_database_url(), pool_pre_ping=True)

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
                """
            )
        ).fetchall()
        all_tables = [r[0] for r in rows]
        to_drop = [t for t in all_tables if t not in KEEP]

        print(f"유지: {sorted(KEEP & set(all_tables))}")
        print(f"삭제 예정 ({len(to_drop)}개): {to_drop}")

        if args.dry_run:
            print("--dry-run: DROP 실행 안 함")
            return

        if not to_drop:
            print("삭제할 테이블이 없습니다.")
            return

        for name in to_drop:
            conn.execute(text(f'DROP TABLE IF EXISTS public."{name}" CASCADE'))
            print(f"Dropped: {name}")

        conn.commit()

    print("완료.")


if __name__ == "__main__":
    main()
