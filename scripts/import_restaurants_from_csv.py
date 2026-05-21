"""공공 CSV → ``restaurants`` 일괄 적재.

사용:
  cd backend
  python scripts/import_restaurants_from_csv.py
  python scripts/import_restaurants_from_csv.py --csv path/to/file.csv --no-replace
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

from apps.database import SyncSessionLocal, ensure_sync_tables
from apps.gourmet.app.services.restaurant_domain_service import RestaurantDomainService

_DEFAULT_CSV = (
    _backend_root
    / "apps/gourmet/app/data/소상공인시장진흥공단_음식분류정보_서울_202603.csv"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="GourmetMate restaurants CSV import")
    parser.add_argument("--csv", type=Path, default=_DEFAULT_CSV)
    parser.add_argument(
        "--no-replace",
        action="store_true",
        help="기존 restaurants 행을 지우지 않고 추가만 시도 (biz_number 중복 시 실패 가능)",
    )
    args = parser.parse_args()

    ensure_sync_tables()
    if SyncSessionLocal is None:
        print("DATABASE_URL / SyncSessionLocal 초기화 실패", file=sys.stderr)
        sys.exit(1)

    service = RestaurantDomainService()
    db = SyncSessionLocal()
    try:
        inserted, deleted = service.import_from_csv(
            db,
            args.csv.expanduser().resolve(),
            replace_all=not args.no_replace,
        )
        print(f"완료: inserted={inserted} deleted={deleted} csv={args.csv}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
