"""식당 보강 — 추정 식대(restaurant_prices) + 장르 태그(restaurant_tags) 일괄 생성.

서울 인허가 CSV에는 메뉴·가격·태그가 없다. 추천/버짓/카드 품질을 위해
카테고리(genre) 기반 **휴리스틱**으로 채운다(멱등: 이미 있으면 건너뜀).
메뉴명은 실제 데이터가 없어 생성하지 않는다.

기본 dry-run, 실제 적용은 ``--execute``.

    python scripts/enrich_restaurants.py            # 계획만
    python scripts/enrich_restaurants.py --execute  # Neon 적용
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parent.parent

# 카테고리 slug → 1인 추정 식대(원)
_PRICE_CASE = (
    "CASE fc.slug "
    "WHEN 'hansik' THEN 15000 WHEN 'ilsik' THEN 18000 WHEN 'jungsik' THEN 14000 "
    "WHEN 'yangsik' THEN 22000 WHEN 'asian' THEN 16000 WHEN 'bunsik' THEN 9000 "
    "WHEN 'cafe-dessert' THEN 8500 WHEN 'bar' THEN 25000 ELSE 13000 END"
)

# 태그 (slug, label)
_TAGS = [
    ("hearty", "든든한"),
    ("gasung", "가성비"),
    ("mood", "분위기"),
    ("solo", "혼밥"),
    ("date", "데이트"),
]
# 태그 slug → 적용 카테고리 slug 목록
_TAG_CATEGORIES: dict[str, list[str]] = {
    "hearty": ["hansik"],
    "gasung": ["jungsik", "bunsik", "etc"],
    "mood": ["yangsik", "asian", "cafe-dessert", "bar"],
    "solo": ["hansik", "ilsik", "bunsik"],
    "date": ["ilsik", "yangsik", "bar"],
}


def _db_url() -> str:
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("DATABASE_URL"):
            return (
                line.split("=", 1)[1]
                .strip()
                .replace("postgresql+asyncpg://", "postgresql://")
                .split("?")[0]
            )
    raise RuntimeError("DATABASE_URL 없음")


async def run(execute: bool) -> None:
    conn = await asyncpg.connect(_db_url(), ssl="require")
    try:
        need_price = await conn.fetchval(
            "SELECT count(*) FROM restaurants r "
            "WHERE NOT EXISTS (SELECT 1 FROM restaurant_prices p WHERE p.restaurant_id=r.id)"
        )
        print(f"[plan] 추정식대 추가 대상: {need_price:,}개 식당")
        print(f"[plan] 태그 {len(_TAGS)}종, 카테고리별 자동 연결")

        if not execute:
            print("[dry-run] DB 미변경. 적용하려면 --execute")
            return

        async with conn.transaction():
            # 1) 추정 식대
            await conn.execute(
                f"INSERT INTO restaurant_prices (restaurant_id, avg_price) "
                f"SELECT r.id, {_PRICE_CASE} "
                f"FROM restaurants r JOIN food_categories fc ON r.category_id=fc.id "
                f"WHERE NOT EXISTS (SELECT 1 FROM restaurant_prices p WHERE p.restaurant_id=r.id)"
            )
            # 2) 태그 마스터
            await conn.executemany(
                "INSERT INTO tags (slug, label) VALUES ($1,$2) ON CONFLICT (slug) DO NOTHING",
                _TAGS,
            )
            tag_id = {
                r["slug"]: r["id"]
                for r in await conn.fetch("SELECT id, slug FROM tags")
            }
            # 3) 카테고리 기반 연결
            for slug, cats in _TAG_CATEGORIES.items():
                await conn.execute(
                    "INSERT INTO restaurant_tags (restaurant_id, tag_id) "
                    "SELECT r.id, $1 FROM restaurants r "
                    "JOIN food_categories fc ON r.category_id=fc.id "
                    "WHERE fc.slug = ANY($2::text[]) "
                    "AND NOT EXISTS (SELECT 1 FROM restaurant_tags rt "
                    "WHERE rt.restaurant_id=r.id AND rt.tag_id=$1)",
                    tag_id[slug],
                    cats,
                )

        prices = await conn.fetchval("SELECT count(*) FROM restaurant_prices")
        links = await conn.fetchval("SELECT count(*) FROM restaurant_tags")
        print(f"[done] restaurant_prices={prices:,} · restaurant_tags={links:,}")
    finally:
        await conn.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="식당 보강 (추정식대·태그)")
    ap.add_argument("--execute", action="store_true", help="실제 Neon 적용 (기본 dry-run)")
    args = ap.parse_args()
    asyncio.run(run(args.execute))


if __name__ == "__main__":
    main()
