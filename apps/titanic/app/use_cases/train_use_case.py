"""타이타닉 조회·채팅 컨텍스트 유스케이스 (JackService + 채팅 컨텍스트 통합)."""

from __future__ import annotations

import json
import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.titanic.app.models.rose_model import RoseModel
from apps.titanic.app.use_cases.reader_use_case import ReaderUseCase

logger = logging.getLogger(__name__)

TITANIC_DB_TABLE = "titanic_passengers"
_CONTEXT_ROW_CAP = 8


class TrainUseCase:
    """Train Use Case."""

    def __init__(self) -> None:
        self.reader = ReaderUseCase()
        self.trainer = TrainerUseCase()


    def train(self) -> None:
        self.trainer.train()


def _context_from_db(db: Session) -> str | None:
    """``titanic_passengers`` 테이블이 있으면 DB 기반 요약."""
    try:
        sample = db.execute(
            text(
                f"SELECT * FROM {TITANIC_DB_TABLE} ORDER BY passenger_id LIMIT :lim"
            ),
            {"lim": _CONTEXT_ROW_CAP},
        ).mappings().all()
        rows = [dict(r) for r in sample]
        return (
            f"[데이터 출처: PostgreSQL 테이블 `{TITANIC_DB_TABLE}`]\n"
            f"- 전체 승객 수: {total}\n"
            f"- 생존(Survived=1): {survived}\n"
            f"- 사망: {total - survived}\n"
            f"- 샘플 {_CONTEXT_ROW_CAP}행:\n{json.dumps(rows, ensure_ascii=False, default=str)}"
        )
    except Exception:
        db.rollback()
        return None


def build_titanic_chat_context(db: Session | None = None) -> str:
    """Gemini에 넣을 데이터 컨텍스트."""
    if db is not None:
        db_ctx = _context_from_db(db)
        if db_ctx:
            logger.info("[titanic chat] 컨텍스트 — DB `%s`", TITANIC_DB_TABLE)
            return db_ctx

    logger.info("[titanic chat] 컨텍스트 — 없음")
    return (
        f"[데이터 출처: 없음]\n"
        f"- `{TITANIC_DB_TABLE}` 테이블이 없거나 비어 있습니다.\n"
        f"- 먼저 CSV를 업로드하거나(기능이 있다면) DB에 데이터를 적재한 뒤 다시 시도하세요."
    )


def augment_user_message_with_context(
    user_content: str,
    context: str,
) -> str:
    return (
        "당신은 타이타닉 승객 데이터 분석 도우미입니다. "
        "아래 [데이터 컨텍스트]에 있는 수치·표본만 근거로 답하고, "
        "컨텍스트에 없는 내용은 추측하지 말고 '데이터에 없습니다'라고 말하세요.\n\n"
        f"[데이터 컨텍스트]\n{context}\n\n"
        f"[사용자 질문]\n{user_content.strip()}"
    )
