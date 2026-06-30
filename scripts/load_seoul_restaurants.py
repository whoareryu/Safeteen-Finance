"""서울 식당 CSV → 기존 정규화 ``restaurants`` 스키마 적재 (GourmetMate).

CSV 컬럼: name, genre, category, road_address, jibun_address, phone,
          latitude, longitude

매핑:
  genre     → food_categories (slug)          → restaurants.category_id
  주소의 구 → sigungu_districts                → restaurants.sigungu_id
  category  → biz_classifications (biz_minor)  → restaurants.biz_classification_id
  phone     → restaurant_contacts
  biz_number → "SEOUL-000001" 합성 (CSV에 없음)

기본은 **dry-run** (파싱·집계만). 실제 적재는 ``--execute``.
``--execute`` 는 기존 restaurants 및 식당 참조 자식행을 모두 지우고 교체한다.

사용:
    python scripts/load_seoul_restaurants.py            # dry-run
    python scripts/load_seoul_restaurants.py --execute  # Neon 적재
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
import re
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parent.parent

# genre(한글) → (slug, label)
GENRE_TO_CATEGORY: dict[str, tuple[str, str]] = {
    "한식": ("hansik", "한식"),
    "중식": ("jungsik", "중식"),
    "일식": ("ilsik", "일식"),
    "양식": ("yangsik", "양식"),
    "분식": ("bunsik", "분식"),
    "아시안": ("asian", "아시안"),
    "술집": ("bar", "바"),
    "카페": ("cafe-dessert", "카페·디저트"),
    "기타": ("etc", "기타"),
}
FALLBACK_CATEGORY = ("etc", "기타")

_GU_RE = re.compile(r"(\S+구)\b")

# restaurants 의 자식·참조 테이블 (삭제 순서: 자식 먼저)
CHILD_TABLES = (
    "restaurant_contacts",
    "restaurant_menus",
    "restaurant_prices",
    "restaurant_tags",
    "restaurant_operating_hours",
    "restaurant_view_stats",
    "restaurant_visits",
    "daily_recommendations",
    "daily_picks",
    "meal_plan_expenses",
)

RESTAURANT_COLUMNS = [
    "id",
    "biz_number",
    "name",
    "store_name",
    "branch_name",
    "road_address",
    "parcel_address",
    "latitude",
    "longitude",
    "description",
    "image_url",
    "category_id",
    "sigungu_id",
    "biz_classification_id",
]


def _env_database_url() -> str:
    # 환경변수 우선 (Docker 컨테이너 내부)
    env_url = os.getenv("DATABASE_URL", "").strip()
    if env_url:
        return env_url.replace("postgresql+asyncpg://", "postgresql://").split("?")[0]
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("DATABASE_URL"):
            raw = line.split("=", 1)[1].strip()
            return raw.replace("postgresql+asyncpg://", "postgresql://").split("?")[0]
    raise RuntimeError("DATABASE_URL 없음")


def _csv_path() -> Path:
    raw = os.getenv("RESTAURANTS_CSV")
    if not raw:
        for line in (ROOT / ".env").read_text().splitlines():
            if line.startswith("RESTAURANTS_CSV"):
                raw = line.split("=", 1)[1].strip()
                break
    if not raw:
        raise RuntimeError("RESTAURANTS_CSV 없음")
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT / p
    return p


def _to_float(cell: str) -> float | None:
    t = (cell or "").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _gu(road: str, jibun: str) -> str:
    for addr in (road, jibun):
        m = _GU_RE.search(addr or "")
        if m:
            return m.group(1)
    return ""


def parse_rows(csv_path: Path) -> list[dict]:
    out: list[dict] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip() or "상호 미상"
            genre = (row.get("genre") or "").strip()
            slug, label = GENRE_TO_CATEGORY.get(genre, FALLBACK_CATEGORY)
            road = (row.get("road_address") or "").strip()
            jibun = (row.get("jibun_address") or "").strip()
            gu = _gu(road, jibun)
            out.append(
                {
                    "name": name,
                    "slug": slug,
                    "label": label,
                    "biz_minor": (row.get("category") or "").strip(),
                    "gu": gu,
                    "road": road,
                    "jibun": jibun,
                    "phone": (row.get("phone") or "").strip(),
                    "lat": _to_float(row.get("latitude") or ""),
                    "lng": _to_float(row.get("longitude") or ""),
                }
            )
    return out


async def _ensure_masters(conn: asyncpg.Connection, rows: list[dict]) -> tuple[dict, dict, dict]:
    # food_categories
    cats = {(r["slug"], r["label"]) for r in rows}
    await conn.executemany(
        "INSERT INTO food_categories(slug, label) VALUES($1,$2) ON CONFLICT (slug) DO NOTHING",
        list(cats),
    )
    cat_map = {
        r["slug"]: r["id"] for r in await conn.fetch("SELECT id, slug FROM food_categories")
    }

    # sigungu_districts (sigungu_name=구, district_label="서울특별시 구")
    sigungus = {r["gu"] for r in rows}
    sig_records = [
        (gu or "서울특별시", f"서울특별시 {gu}".strip()) for gu in sigungus
    ]
    await conn.executemany(
        "INSERT INTO sigungu_districts(sigungu_name, district_label) VALUES($1,$2) "
        "ON CONFLICT (sigungu_name, district_label) DO NOTHING",
        sig_records,
    )
    sig_map = {
        r["sigungu_name"]: r["id"]
        for r in await conn.fetch("SELECT id, sigungu_name, district_label FROM sigungu_districts")
        if r["district_label"].startswith("서울특별시")
    }

    # biz_classifications (biz_minor_name=category)
    bizes = {r["biz_minor"] for r in rows}
    await conn.executemany(
        "INSERT INTO biz_classifications(biz_mid_name, biz_minor_name, ksic_name) "
        "VALUES('', $1, '') ON CONFLICT (biz_mid_name, biz_minor_name, ksic_name) DO NOTHING",
        [(b,) for b in bizes],
    )
    biz_map = {
        r["biz_minor_name"]: r["id"]
        for r in await conn.fetch(
            "SELECT id, biz_minor_name FROM biz_classifications WHERE biz_mid_name='' AND ksic_name=''"
        )
    }
    return cat_map, sig_map, biz_map


async def run(execute: bool) -> None:
    csv_path = _csv_path()
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    rows = parse_rows(csv_path)
    print(f"[csv] {csv_path.name}: {len(rows):,}행 파싱")

    from collections import Counter

    genre_counts = Counter(r["label"] for r in rows)
    print("[genre]", dict(genre_counts))
    with_phone = sum(1 for r in rows if r["phone"])
    with_gu = sum(1 for r in rows if r["gu"])
    print(f"[map] 구 추출 {with_gu:,} · 전화 {with_phone:,}")

    if not execute:
        print("[dry-run] DB 미변경. 적재하려면 --execute")
        return

    db_url = _env_database_url()
    # 로컬 Docker 컨테이너는 SSL 불필요
    use_ssl = "neon.tech" in db_url or os.getenv("DB_SSL", "") == "require"
    conn = await asyncpg.connect(db_url, ssl="require" if use_ssl else False)
    try:
        async with conn.transaction():
            cat_map, sig_map, biz_map = await _ensure_masters(conn, rows)

            restaurant_records = []
            contact_records = []
            for i, r in enumerate(rows, start=1):
                restaurant_records.append(
                    (
                        i,
                        f"SEOUL-{i:06d}",
                        r["name"],
                        r["name"],
                        "",
                        r["road"],
                        r["jibun"],
                        r["lat"],
                        r["lng"],
                        "",
                        "",
                        cat_map[r["slug"]],
                        sig_map.get(r["gu"] or "서울특별시", sig_map.get("서울특별시")),
                        biz_map[r["biz_minor"]],
                    )
                )
                if r["phone"]:
                    contact_records.append((i, r["phone"]))

            for t in CHILD_TABLES:
                await conn.execute(f"DELETE FROM {t}")
            await conn.execute("DELETE FROM restaurants")

            await conn.copy_records_to_table(
                "restaurants", records=restaurant_records, columns=RESTAURANT_COLUMNS
            )
            if contact_records:
                await conn.copy_records_to_table(
                    "restaurant_contacts",
                    records=contact_records,
                    columns=["restaurant_id", "phone"],
                )
            await conn.execute(
                "SELECT setval('restaurants_id_seq', (SELECT max(id) FROM restaurants))"
            )
        total = await conn.fetchval("SELECT count(*) FROM restaurants")
        contacts = await conn.fetchval("SELECT count(*) FROM restaurant_contacts")
        print(f"[done] restaurants={total:,} · restaurant_contacts={contacts:,}")
    finally:
        await conn.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="서울 식당 CSV 적재")
    ap.add_argument("--execute", action="store_true", help="실제 Neon 적재 (기본 dry-run)")
    args = ap.parse_args()
    asyncio.run(run(args.execute))


if __name__ == "__main__":
    main()
