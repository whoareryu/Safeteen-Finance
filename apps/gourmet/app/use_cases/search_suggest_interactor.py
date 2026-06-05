"""검색 자동완성 — 로그 + 주제 키워드."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from gourmet.data.category_topics import COMMON_TOPICS
from gourmet.data.search_keywords import expand_search_terms
from gourmet.adapter.outbound.orm.search_query_log import SearchQueryLog


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
