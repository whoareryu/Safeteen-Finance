"""기존 ``restaurants`` 단일 테이블 → 2NF 분리 마이그레이션.

Neon 등에 레거시 컬럼(category_slug, avg_price, signature_menu)이 남아 있을 때 실행.

```bash
cd backend
python scripts/migrate_restaurants_to_2nf.py
```
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from alembic import command
from alembic.config import Config


def main() -> None:
    cfg = Config(str(_BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND / "alembic"))
    command.upgrade(cfg, "f8a9b0c1d2e3")
    print("마이그레이션 f8a9b0c1d2e3 적용 완료.")


if __name__ == "__main__":
    main()
