"""레거시 ``restaurant`` (Sgma) 테이블 DROP — ``restaurants`` 가 채워진 뒤 실행.

사용:
  cd backend
  python scripts/drop_legacy_restaurant_table.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

from dotenv import load_dotenv

load_dotenv(_backend_root / ".env")

from sqlalchemy import text

from apps.database import SyncSessionLocal, ensure_sync_tables


def main() -> None:
    ensure_sync_tables()
    db = SyncSessionLocal()
    try:
        cnt = db.execute(
            text("SELECT COUNT(*) FROM restaurants")
        ).scalar_one()
        print(f"restaurants 행 수: {cnt}")
        if int(cnt or 0) < 1:
            print("restaurants 가 비어 있습니다. CSV import 후 다시 실행하세요.")
            sys.exit(1)
        db.execute(text('DROP TABLE IF EXISTS restaurant CASCADE'))
        db.commit()
        print("DROP TABLE restaurant 완료")
    finally:
        db.close()


if __name__ == "__main__":
    main()
