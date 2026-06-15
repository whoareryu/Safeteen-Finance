"""검색 자동완성 — 로그 + 주제 키워드."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from restaurant.data.category_topics import COMMON_TOPICS
from restaurant.data.search_keywords import expand_search_terms
from restaurant.adapter.outbound.orm.search_query_log_orm import SearchQueryLog
from restaurant.app.ports.input.search_suggest_use_case import SearchSuggestUseCase
from restaurant.adapter.inbound.api.schemas.search_suggest_schema import SearchSuggestSchema
from restaurant.app.dtos.search_suggest_dto import SearchSuggestQuery, SearchSuggestResponse
from restaurant.app.ports.output.search_suggest_repository import SearchSuggestRepository


def suggest_search(db: Session, q: str, *, limit: int = 12) -> list[dict]:
    raw = (q or "").strip()
    terms = expand_search_terms(raw) if raw else []
    needle = terms[0].lower() if terms else raw.lower()

    out: list[dict] = []
    seen: set[str] = set()

    def add(text: str, source: str) -> None:
        t = text.strip()
        if not t or t.lower() in seen:
            return
        if needle and needle not in t.lower():
            return
        seen.add(t.lower())
        out.append({"text": t, "source": source})

    if raw:
        stmt = (
            select(
                SearchQueryLog.query,
                func.count().label("cnt"),
            )
            .where(SearchQueryLog.query_normalized.ilike(f"%{needle}%"))
            .group_by(SearchQueryLog.query)
            .order_by(func.count().desc())
            .limit(limit)
        )
        for row in db.execute(stmt).all():
            add(str(row[0]), "log")
            if len(out) >= limit:
                return out[:limit]

    for t in COMMON_TOPICS:
        add(t.title, "topic")
        for kw in t.keywords[:3]:
            add(kw, "topic")
        if len(out) >= limit:
            break

    chips = ["여름", "해장", "데이트", "혼밥", "가성비", "비 오는 날"]
    for c in chips:
        add(c, "chip")
        if len(out) >= limit:
            break

    return out[:limit]


class SearchSuggestInteractor(SearchSuggestUseCase):
    def __init__(self, repository: SearchSuggestRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: SearchSuggestSchema) -> SearchSuggestResponse:
        return await self.repository.introduce_myself(
            SearchSuggestQuery(id=schema.id, name=schema.name)
        )
