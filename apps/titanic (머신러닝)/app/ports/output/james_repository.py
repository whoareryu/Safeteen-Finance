from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.titanic.adapter.outbound.pg.james_pg_repository import JamesPgRepository

@dataclass
class JamesRepositoryResult:
    ok: bool
    message: str
    count: int
    columns: list[str]
    rows: list[dict[str, Any]]


class JamesRepository:
    """JamesCommand가 전달한 업로드 데이터를 출력 포트에서 처리한다."""

    def __init__(self) -> None:
        self.pg_repository = JamesPgRepository()

    def send_uploaded_rows(
        self,
        *,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> JamesRepositoryResult:
        pg_result = self.pg_repository.send_uploaded_rows_to_pg(
            columns=columns,
            rows=rows,
        )
        return JamesRepositoryResult(
            ok=pg_result.ok,
            message=pg_result.message,
            count=pg_result.count,
            columns=pg_result.columns,
            rows=pg_result.rows,
        )
