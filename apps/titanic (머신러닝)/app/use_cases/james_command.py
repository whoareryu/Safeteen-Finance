from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.titanic.app.ports.output.james_repository import JamesRepository


@dataclass
class JamesUploadResult:

    def __init__(self, ok: bool, message: str, count: int, columns: list[str], rows: list[dict[str, Any]]) -> None:
        self.ok = ok
        self.message = message
        self.count = count
        self.columns = columns
        self.rows = rows


class JamesCommand:

    def __init__(self) -> None:
        self.repository = JamesRepository()

    """james_use_case 에서 전달받은 업로드 데이터를 처리한다."""

    def move_uploaded_rows(
        self,
        *,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> JamesUploadResult:
        repo_result = self.repository.send_uploaded_rows(columns=columns, rows=rows)
        return JamesUploadResult(
            ok=repo_result.ok,
            message=repo_result.message,
            count=repo_result.count,
            columns=repo_result.columns,
            rows=repo_result.rows,
        )
