from __future__ import annotations

from typing import Any

from apps.titanic.app.use_cases.james_command import JamesCommand, JamesUploadResult


class JamesUseCase:

    def __init__(self) -> None:
        self._command = JamesCommand()

    """james_router 에서 전달받은 업로드 데이터를 처리한다."""

    async def handle_uploaded_rows(
        self,
        *,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> JamesUploadResult:
        return await self._command.move_uploaded_rows(
            columns=columns,
            rows=rows,
        )
