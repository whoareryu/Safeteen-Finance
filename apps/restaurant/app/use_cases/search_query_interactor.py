"""검색어 저장."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.search_query_log_orm import SearchQueryLog
from restaurant.app.ports.input.search_query_use_case import SearchQueryUseCase
from restaurant.adapter.inbound.api.schemas.search_query_schema import SearchQuerySchema
from restaurant.app.dtos.search_query_dto import SearchQueryQuery, SearchQueryResponse
from restaurant.app.ports.output.search_query_repository import SearchQueryRepository


logger = logging.getLogger(__name__)


def normalize_query(q: str) -> str:
    return " ".join(q.strip().split()).lower()


def record_search_query(db: Session, query: str, *, result_count: int = 0) -> None:
    """검색 실행 시 로그 1건 저장."""
    raw = query.strip()
    if not raw:
        return
    norm = normalize_query(raw)
    db.add(
        SearchQueryLog(
            query=raw[:128],
            query_normalized=norm[:128],
            result_count=max(0, result_count),
        )
    )
    db.commit()
    logger.info("[gourmet] search log — q=%s results=%s", raw, result_count)


class SearchQueryInteractor(SearchQueryUseCase):
    def __init__(self, repository: SearchQueryRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: SearchQuerySchema) -> SearchQueryResponse:
        return await self.repository.introduce_myself(
            SearchQueryQuery(id=schema.id, name=schema.name)
        )
