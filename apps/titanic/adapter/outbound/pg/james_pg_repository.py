from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from apps.titanic.adapter.outbound.orm.database import SessionLocal
from apps.titanic.adapter.outbound.orm.models import TitanicPassengerModel

logger = logging.getLogger(__name__)


@dataclass
class JamesPgRepositoryResult:
    ok: bool
    message: str
    count: int
    columns: list[str]
    rows: list[dict[str, Any]]


def _parse_int(value: Any) -> int | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _parse_float(value: Any) -> float | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _row_to_model(row: dict[str, Any]) -> TitanicPassengerModel:
    return TitanicPassengerModel(
        passenger_id=str(row.get("passenger_id", "")).strip(),
        survived=_parse_int(row.get("survived")),
        pclass=_parse_int(row.get("pclass")),
        name=str(row.get("name", "")).strip() or "Unknown",
        gender=(str(row.get("gender", "")).strip() or None),
        age=_parse_float(row.get("age")),
        sib_sp=_parse_int(row.get("sib_sp")),
        parch=_parse_int(row.get("parch")),
        ticket=(str(row.get("ticket", "")).strip() or None),
        fare=_parse_float(row.get("fare")),
        cabin=(str(row.get("cabin", "")).strip() or None),
        embarked=(str(row.get("embarked", "")).strip() or None),
    )


class JamesPgRepository:
    """업로드된 타이타닉 CSV 행을 Neon PostgreSQL `titanic_passengers`에 저장."""

    async def send_uploaded_rows_to_pg(
        self,
        *,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> JamesPgRepositoryResult:
        if SessionLocal is None:
            return JamesPgRepositoryResult(
                ok=False,
                message="DATABASE_URL이 없어 PG 세션을 열 수 없습니다.",
                count=0,
                columns=columns,
                rows=rows,
            )

        if not rows:
            return JamesPgRepositoryResult(
                ok=True,
                message="저장할 행이 없습니다.",
                count=0,
                columns=columns,
                rows=rows,
            )

        async with SessionLocal() as db:
            try:
                db.add_all([_row_to_model(row) for row in rows])
                await db.commit()
                return JamesPgRepositoryResult(
                    ok=True,
                    message=f"Neon DB에 {len(rows)}행 저장 완료",
                    count=len(rows),
                    columns=columns,
                    rows=rows,
                )
            except Exception as exc:
                await db.rollback()
                logger.exception("Neon DB 전송 중 에러")
                return JamesPgRepositoryResult(
                    ok=False,
                    message=f"Neon DB 전송 실패: {exc}",
                    count=0,
                    columns=columns,
                    rows=rows,
                )
