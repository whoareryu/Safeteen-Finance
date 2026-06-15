"""맛집 맥락 RAG — DB 메타를 Gemini 시스템 프롬프트에 주입."""

from __future__ import annotations

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.pg.restaurant_pg_repository import RestaurantRepository
from restaurant.app.use_cases.restaurant_search_interactor import search_restaurants


def build_gourmet_context(
    db: Session,
    *,
    restaurant_id: int | None = None,
    q: str | None = None,
) -> str:
    parts: list[str] = [
        "당신은 서울 맛집 앱 GourmetMate 의 AI 미식 가이드입니다.",
        "아래 [데이터]만 근거로 답하고, 없는 정보는 추측하지 말고 모른다고 하세요.",
    ]

    if restaurant_id is not None:
        row = RestaurantRepository().get_by_id(db, restaurant_id)
        if row is not None:
            slug, label = row.category_pair()
            menu_names = [
                m.name for m in (row.menus or []) if (m.name or "").strip()
            ][:8]
            menus = ", ".join(menu_names)
            parts.append("[데이터 — 선택 매장]")
            parts.append(f"- 이름: {row.display_name()}")
            parts.append(f"- 카테고리: {label} ({slug})")
            parts.append(f"- 지역: {row.district or row.sigungu_name}")
            if row.avg_price is not None:
                parts.append(f"- 1인 추정 식대: {row.avg_price:,}원")
            if menus:
                parts.append(f"- 메뉴: {menus}")
            tags = list(row.ai_tags or [])
            if tags:
                parts.append(f"- AI 태그: {', '.join(tags[:12])}")
            if row.description:
                parts.append(f"- 설명: {row.description[:400]}")

    if q and q.strip():
        result = search_restaurants(db, q.strip(), offset=0, limit=5)
        names = [r["name"] for r in (result.get("restaurants") or [])[:5]]
        if names:
            parts.append(f"[데이터 — '{q.strip()}' 검색 상위]")
            parts.append("- " + ", ".join(names))

    if len(parts) <= 2:
        parts.append("[데이터] 특정 매장이 지정되지 않았습니다. 일반적인 서울 외식 조언만 제공하세요.")

    return "\n".join(parts)
